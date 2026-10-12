// SPDX-License-Identifier: GPL-3.0-or-later
// The builder for USB module sets: what loading a set onto an Octatrack with the Modwerk base sends. Modules the site
// publishes as runtime packages (public/octatrack-modules, made from source by `npm run octatrack:module-packages`)
// are installed from them; anything the set leaves out is removed with an empty package naming its module.
import manifest from '../assets/octatrack-module-packages.json' with { type: 'json' }
import { sha } from '../../../vendor/elekloader/kit/src/bytes.ts'
import { MODULES } from '../../catalog/modules.ts'
import { inventoryChanges, type Inventory, type InventoryTarget } from '../../config/inventory.ts'
import type { OctatrackLink, SetChange } from './octatrack-link.ts'
import type { MissingModule } from './upload-usb.ts'

/** Why a set cannot be loaded over USB, in the user's words. */
export class ModuleSetError extends Error {}
type Published = typeof manifest.packages[number]
const PUBLISHED = new Map(manifest.packages.map(entry => [entry.id, entry]))
/** The catalogue ids the site can load over USB. */
export const USB_MODULE_IDS = [...PUBLISHED.keys()]

/** A module's runtime id (sdk/runtime/loader/build.py module_id): the first four bytes of the SHA-256 of its catalogue
 * id, hex. The inventory names a module the catalogue does not know by this id. */
export const runtimeId = (id: string) => /^[0-9a-f]{8}$/.test(id) ? id : sha(new TextEncoder().encode(id)).slice(0, 8)
const BY_RUNTIME_ID = new Map(MODULES.map(module => [runtimeId(module.id), module.id]))
/** The package that removes a module: ABI 4, no image, hooks or sites (sdk/runtime/loader/README.md). */
export function removalPackage(id: string) {
  const data = Uint8Array.from([0x4d, 0x57, 0x52, 0x4d, 0, 4, ...new Array<number>(26).fill(0)])
  new DataView(data.buffer).setUint32(28, Number.parseInt(runtimeId(id), 16))
  return data
}
const moduleName = (id: string) => PUBLISHED.get(id)?.name ?? MODULES.find(module => module.id === id)?.name ?? id
const list = (items: string[]) => new Intl.ListFormat('en', { type: 'conjunction' }).format(items)

/** The site's copy of a published package, checked against the manifest. */
export async function fetchPackage(entry: Published): Promise<Uint8Array> {
  const response = await fetch(import.meta.env.BASE_URL + entry.path)
  const data = response.ok ? new Uint8Array(await response.arrayBuffer()) : undefined
  if (!data || data.length !== entry.bytes || sha(data) !== entry.sha256)
    throw new ModuleSetError(`The site couldn’t fetch ${entry.name} intact. Reload the page and try again.`)
  return data
}

/** What the INVENTORY request lists, as the site names it: catalogue ids, or the runtime id of a module the
 * catalogue does not know. shortcut: the base keeps no stock-effect state yet, so none are listed as removed. */
export const inventoryFrom = (modules: MissingModule[]): Inventory =>
  ({ moduleIds: modules.map(item => BY_RUNTIME_ID.get(item.module) ?? item.module), removedStockFx: [] })

/** The changes that make the unit (`current`) match `target`: removals first (they free memory and stock code for
 * what follows), then installs, each with the package that undoes it. shortcut: a module installs at the version the
 * site publishes now, not the set's pinned one; carry versions once the site publishes more than the latest. */
export async function prepareModuleSet(target: InventoryTarget, current: Inventory, load = fetchPackage): Promise<{ name: string; changes: SetChange[] }> {
  const changes = inventoryChanges(current, target)
  if (changes.stockOff.length || changes.stockOn.length)
    throw new ModuleSetError('The Octatrack can’t take stock effects out of its menus over USB yet. Keep every stock effect in this module set to load it.')
  const unpublished = changes.add.filter(id => !PUBLISHED.has(id))
  if (unpublished.length)
    throw new ModuleSetError(`${list(unpublished.map(moduleName))} can’t be loaded over USB yet. Download the .bin for the card instead.`)
  const published = [...changes.add, ...changes.remove].filter(id => PUBLISHED.has(id))
  const packages = new Map(await Promise.all(published.map(async id => [id, await load(PUBLISHED.get(id)!)] as const)))
  return { name: target.name, changes: [
    ...changes.remove.map(id => ({ module: moduleName(id), data: removalPackage(id), undo: packages.get(id) })),
    ...changes.add.map(id => ({ module: moduleName(id), data: packages.get(id)!, undo: removalPackage(id) })),
  ] }
}

/** The link's builder and inventory for the site's checkout card. */
export function moduleSetKit(link: OctatrackLink) {
  const readInventory = async () => {
    const modules = await link.inventory()
    // Only a base that doesn't know INVENTORY lands here; couldn't-ask-now rejects with LinkBusyError, which callers retry.
    if (!modules) throw new ModuleSetError('This Octatrack’s base doesn’t list its modules. Install the latest Modwerk base, then try again.')
    return inventoryFrom(modules)
  }
  return { readInventory, prepareUpdate: async (target: InventoryTarget) => prepareModuleSet(target, await readInventory()) }
}
