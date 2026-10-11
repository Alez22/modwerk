import { describe, expect, it } from 'vitest'
import { changeCount, inventoryChanges, unitState } from './inventory'

describe('making the unit match a module set', () => {
  it('adds and removes modules and switches stock effects both ways', () => {
    const changes = inventoryChanges({ moduleIds: ['everb', 'poly8'], removedStockFx: ['DARK REV'] },
      { name: 'Set', moduleIds: ['everb', 'air-chorus'], removedStockFx: ['SPRING REV'] })
    expect(changes).toEqual({ add: ['air-chorus'], remove: ['poly8'], stockOff: ['SPRING REV'], stockOn: ['DARK REV'] })
    expect(changeCount(changes)).toBe(4)
  })
  it('finds nothing to do when the unit already matches', () => {
    expect(changeCount(inventoryChanges({ moduleIds: ['everb'], removedStockFx: [] }, { name: 'Set', moduleIds: ['everb'] }))).toBe(0)
  })
  it('tells what is on the unit apart from what is only in the set', () => {
    const unit = { moduleIds: ['everb', 'poly8'], removedStockFx: [] }, set = ['everb', 'tapeecho']
    expect(['everb', 'tapeecho', 'poly8', 'repitch'].map(id => unitState(id, set, unit))).toEqual(['on', 'load', 'leaving', undefined])
    expect(unitState('everb', set)).toBeUndefined()
  })
})
