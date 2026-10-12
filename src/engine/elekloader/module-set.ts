// SPDX-License-Identifier: GPL-3.0-or-later
// The builder for USB module sets: what loading a set onto an Octatrack with the Modwerk base sends. Modules the site
// publishes as runtime packages (public/octatrack-modules, made from source by `npm run octatrack:module-packages`)
// are installed from them; anything the set leaves out is removed with an empty package naming its module. The stock
// effects the set leaves out of the FX menus go as one more package, kept with the set (elekloader/boot.c, fxpage.c).
import manifest from '../assets/octatrack-module-packages.json' with { type: 'json' }
import chooser from '../assets/chooser-metadata.json' with { type: 'json' }
import { STOCK_EFFECTS } from '../../catalog/stock-effects.ts'
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

/** Each stock effect's id: its bit in the base's mask of stock effects out of the FX menus. */
const STOCK_ID = new Map(chooser.stockEffects.map(effect => [effect.key, effect.fxId]))
/** The package that takes `keys` out of both FX menus and puts every other stock effect back: "MWSF", then the mask of
 * their effect ids, big-endian (elekloader/boot.c). A project that uses one keeps it; it only leaves the menus. */
export function stockPackage(keys: readonly string[]) {
  const data = Uint8Array.from([0x4d, 0x57, 0x53, 0x46, 0, 0, 0, 0])
  new DataView(data.buffer).setUint32(4, STOCK_EFFECTS.filter(key => keys.includes(key)).reduce((mask, key) => (mask | 1 << STOCK_ID.get(key)!) >>> 0, 0))
  return data
}

/** What the INVENTORY and STOCKFX requests list, as the site names it: catalogue ids, or the runtime id of a module the
 * catalogue does not know, and the stock effects out of the menus (`stockOff`, bit n for effect id n). */
export const inventoryFrom = (modules: MissingModule[], stockOff = 0): Inventory =>
  ({ moduleIds: modules.map(item => BY_RUNTIME_ID.get(item.module) ?? item.module),
    removedStockFx: STOCK_EFFECTS.filter(key => stockOff >>> STOCK_ID.get(key)! & 1) })

/** The changes that make the unit (`current`) match `target`: the stock effects in the menus, removals (they free
 * memory and stock code for what follows), then installs, each with the package that undoes it. `stockMenus` is false
 * for a base that keeps every stock effect in its menus. shortcut: a module installs at the version the site publishes
 * now, not the set's pinned one; carry versions once the site publishes more than the latest. */
export async function prepareModuleSet(target: InventoryTarget, current: Inventory, load = fetchPackage, stockMenus = true): Promise<{ name: string; changes: SetChange[] }> {
  const changes = inventoryChanges(current, target), stock = changes.stockOff.length + changes.stockOn.length > 0
  if (stock && !stockMenus)
    throw new ModuleSetError('This Octatrack’s base keeps every stock effect in its menus. Install the latest Modwerk base, or keep every stock effect in this module set.')
  const unpublished = changes.add.filter(id => !PUBLISHED.has(id))
  if (unpublished.length)
    throw new ModuleSetError(`${list(unpublished.map(moduleName))} can’t be loaded over USB yet. Download the .bin for the card instead.`)
  const published = [...changes.add, ...changes.remove].filter(id => PUBLISHED.has(id))
  const packages = new Map(await Promise.all(published.map(async id => [id, await load(PUBLISHED.get(id)!)] as const)))
  return { name: target.name, changes: [
    ...stock ? [{ module: 'Stock effects', data: stockPackage(target.removedStockFx ?? []), undo: stockPackage(current.removedStockFx) }] : [],
    ...changes.remove.map(id => ({ module: moduleName(id), data: removalPackage(id), undo: packages.get(id) })),
    ...changes.add.map(id => ({ module: moduleName(id), data: packages.get(id)!, undo: removalPackage(id) })),
  ] }
}

/** The link's builder and inventory for the site's checkout card. */
export function moduleSetKit(link: OctatrackLink) {
  const read = async () => {
    const modules = await link.inventory()
    // Only a base that doesn't know INVENTORY lands here; couldn't-ask-now rejects with LinkBusyError, which callers retry.
    if (!modules) throw new ModuleSetError('This Octatrack’s base doesn’t list its modules. Install the latest Modwerk base, then try again.')
    return { modules, stockOff: await link.stockFx() }
  }
  const readInventory = async () => { const { modules, stockOff } = await read(); return inventoryFrom(modules, stockOff) }
  return { readInventory, prepareUpdate: async (target: InventoryTarget) => {
    const { modules, stockOff } = await read()
    return prepareModuleSet(target, inventoryFrom(modules, stockOff), fetchPackage, stockOff !== undefined)
  } }
}
