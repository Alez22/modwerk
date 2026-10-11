import { MODULES } from '../catalog/modules'
import type { Inventory } from '../config/inventory'
import { Icon } from './Icon'
import { ModulePreview } from './ModulePreview'

const STATE = { on: 'On Octatrack', load: 'To load', leaving: 'Leaving' } as const

/**
 * The module set as a compact grid: what is on the Octatrack, what the next load adds and, with a
 * connected unit, what it removes (Keep adds it back). A tile opens the module without leaving the page.
 */
export function ModuleGrid({ ids, inventory, describe, onOpen, onRemove, onKeep, onSaveUnit }: { ids: string[]; inventory?: Inventory; describe: (id: string) => string; onOpen: (id: string) => void; onRemove: (id: string) => void; onKeep: (id: string) => void; onSaveUnit: () => void }) {
  const leaving = inventory ? inventory.moduleIds.filter(id => !ids.includes(id)) : []
  const tiles = [...ids.map(id => ({ id, state: inventory ? inventory.moduleIds.includes(id) ? 'on' as const : 'load' as const : undefined })), ...leaving.map(id => ({ id, state: 'leaving' as const }))]
  const count = (state: keyof typeof STATE) => tiles.filter(tile => tile.state === state).length
  return <section className="configuration-section module-grid-section" aria-labelledby="selection-title">
    <div className="section-title"><h2 id="selection-title">Modules <span className="subtle">{ids.length}</span></h2>
      {inventory && <span className="module-grid-summary">{count('on')} on Octatrack · {count('load')} to load · {count('leaving')} leaving</span>}</div>
    <ul className="module-tiles">
      {tiles.map(({ id, state }) => { const module = MODULES.find(item => item.id === id), name = module?.name ?? id
        return <li key={id} className={'module-tile' + (state ? ' is-' + state : '')}>
          <button type="button" className="module-tile-open" aria-haspopup="dialog" disabled={!module} onClick={() => onOpen(id)}><ModulePreview id={id} compact /><strong>{name}</strong><small>{module ? describe(id) : 'Not in the library'}</small></button>
          {state && <span className="module-tile-state">{STATE[state]}</span>}
          {state === 'leaving' ? module && <button type="button" className="module-tile-action text-button" onClick={() => onKeep(id)}>Keep</button>
            : <button type="button" className="module-tile-action icon-button" aria-label={'Remove ' + name} onClick={() => onRemove(id)}><Icon name="close" size={15} /></button>}
        </li> })}
      <li className="module-tile is-add"><a href="#library"><Icon name="plus" size={20} /><strong>Add modules</strong><small>From the library</small></a></li>
    </ul>
    {inventory && inventory.moduleIds.length > 0 && <button type="button" className="text-button module-grid-save" onClick={onSaveUnit}>Save what’s on your Octatrack as a module set <Icon name="plus" size={14} /></button>}
  </section>
}
