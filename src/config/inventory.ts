import { STOCK_EFFECTS } from '../catalog/stock-effects'

/** What an Octatrack running the Modwerk base has on it: its modules and the stock effects left out of the menus. */
export interface Inventory { moduleIds: string[]; removedStockFx: string[] }
/** What a load makes the unit match: a module set, or the device page's edits. */
export interface InventoryTarget { name: string; moduleIds: string[]; removedStockFx?: string[] }
export interface InventoryChanges { add: string[]; remove: string[]; stockOff: string[]; stockOn: string[] }

/** The changes that make `current` match `target`: the unit matches the set exactly, stock effects included. */
export function inventoryChanges(current: Inventory, target: InventoryTarget): InventoryChanges {
  const off = new Set(target.removedStockFx ?? [])
  return {
    add: target.moduleIds.filter(id => !current.moduleIds.includes(id)),
    remove: current.moduleIds.filter(id => !target.moduleIds.includes(id)),
    stockOff: STOCK_EFFECTS.filter(key => off.has(key) && !current.removedStockFx.includes(key)),
    stockOn: STOCK_EFFECTS.filter(key => !off.has(key) && current.removedStockFx.includes(key)),
  }
}
export const changeCount = (changes: InventoryChanges) => changes.add.length + changes.remove.length + changes.stockOff.length + changes.stockOn.length

export type UnitState = 'on' | 'load' | 'leaving'
export const UNIT_STATE: Record<UnitState, string> = { on: 'On your Octatrack', load: 'Not loaded yet', leaving: 'Leaves next load' }
/** Where a module stands against the unit: on it, only in the module set, or on it but leaving with the next load. */
export const unitState = (id: string, setIds: readonly string[], inventory?: Inventory): UnitState | undefined =>
  !inventory ? undefined : inventory.moduleIds.includes(id) ? setIds.includes(id) ? 'on' : 'leaving' : setIds.includes(id) ? 'load' : undefined
