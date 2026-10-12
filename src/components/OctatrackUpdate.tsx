import type { Inventory, InventoryTarget } from '../config/inventory'
import type { SetChange } from '../engine/elekloader/octatrack-link'
import './octatrack-link.css'

/** The builder: the target set as what the base loads, change by change. */
export type PrepareUpdate = (target: InventoryTarget) => Promise<{ name: string; changes: SetChange[] }>
/** The base: what is on the unit. */
export type ReadInventory = () => Promise<Inventory>
export type StressTest = () => Promise<string | null>
/** What the unit's project names that the unit lacks: library names, names the library does not know, and how to add
 * the ones this set does not have yet (absent when it has them all). */
export interface ProjectNeeds { names: string[]; unknown: string[]; add?: () => void }
const list = (items: string[]) => new Intl.ListFormat('en', { type: 'conjunction' }).format(items)
export function MissingNote({ needs }: { needs?: ProjectNeeds }) {
  if (!needs || !needs.names.length && !needs.unknown.length) return null
  const { names, unknown, add } = needs, verb = (n: number) => n === 1 ? 'isn’t' : 'aren’t'
  return <p className="usb-missing" role="status">
    {names.length > 0 && <>Your project uses {list(names)}, which {verb(names.length)} on your Octatrack. {add
      ? <button className="text-button" onClick={add}>Add to set</button> : `Sync to bring ${names.length === 1 ? 'it' : 'them'} back.`}</>}
    {unknown.length > 0 && <>{names.length ? ' It also uses ' : 'Your project uses '}{list(unknown)}, which {verb(unknown.length)} in the library.</>}
  </p>
}
