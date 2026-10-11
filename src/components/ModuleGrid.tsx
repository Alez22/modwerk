import type { ReactNode } from 'react'
import { MODULES } from '../catalog/modules'
import { UNIT_STATE, unitState, type Inventory, type UnitState } from '../config/inventory'
import { Icon } from './Icon'
import { ModulePreview } from './ModulePreview'

const SUMMARY: Record<UnitState, string> = { on: 'on your Octatrack', load: 'not loaded yet', leaving: 'leaving' }

/** A lit LED means it is on the Octatrack right now; an outlined one means it is only in the module set. */
export const StateChip = ({ state, className = '', children }: { state: string; className?: string; children: ReactNode }) =>
  <span className={'module-tile-state is-' + state + (className && ' ' + className)}><i aria-hidden="true" />{children}</span>

/**
 * The module set as a compact grid: what is on the Octatrack, what the next load adds and, with a
 * connected unit, what it removes (Keep adds it back). A tile opens the module without leaving the page.
 */
export function ModuleGrid({ ids, inventory, describe, onOpen, onRemove, onKeep, onSaveUnit }: { ids: string[]; inventory?: Inventory; describe: (id: string) => string; onOpen: (id: string) => void; onRemove: (id: string) => void; onKeep: (id: string) => void; onSaveUnit: () => void }) {
  const leaving = inventory ? inventory.moduleIds.filter(id => !ids.includes(id)) : []
  const tiles = [...ids, ...leaving].map(id => ({ id, state: unitState(id, ids, inventory) }))
  const count = (state: UnitState) => tiles.filter(tile => tile.state === state).length
  return <section className="configuration-section module-grid-section" aria-labelledby="selection-title">
    <div className="section-title"><h2 id="selection-title">Modules <span className="subtle">{ids.length}</span></h2>
      {inventory && <span className="module-grid-summary">{(['on', 'load', 'leaving'] as const).map(state => <StateChip key={state} state={state} className="is-legend">{count(state)} {SUMMARY[state]}</StateChip>)}</span>}</div>
    <ul className="module-tiles">
      {tiles.map(({ id, state }) => { const module = MODULES.find(item => item.id === id), name = module?.name ?? id
        return <li key={id} className={'module-tile' + (state ? ' is-' + state : '')}>
          <button type="button" className="module-tile-open" aria-haspopup="dialog" disabled={!module} onClick={() => onOpen(id)}><ModulePreview id={id} compact /><strong>{name}</strong><small>{module ? describe(id) : 'Not in the library'}</small></button>
          {state && <StateChip state={state}>{UNIT_STATE[state]}</StateChip>}
          {state === 'leaving' ? module && <button type="button" className="module-tile-action text-button" onClick={() => onKeep(id)}>Keep</button>
            : <button type="button" className="module-tile-action icon-button" aria-label={'Remove ' + name} onClick={() => onRemove(id)}><Icon name="close" size={15} /></button>}
        </li> })}
      <li className="module-tile is-add"><a href="#library"><Icon name="plus" size={20} /><strong>Add modules</strong><small>From the library</small></a></li>
    </ul>
    {inventory && inventory.moduleIds.length > 0 && <button type="button" className="text-button module-grid-save" onClick={onSaveUnit}>Save what’s on your Octatrack as a module set <Icon name="plus" size={14} /></button>}
  </section>
}
