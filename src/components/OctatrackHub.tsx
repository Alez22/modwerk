import { useRef, type KeyboardEvent, type ReactNode } from 'react'
import { MODULES } from '../catalog/modules'
import { lastInventory, listboxMove, sameModules, unitPreview, type Inventory, type UnitState } from '../config/inventory'
import type { Configuration } from '../config/workspace'
import { DeviceImage } from '../devices/DeviceImage'
import { DEVICES_BY_ID } from '../devices/registry'
import type { OctatrackLink } from '../engine/elekloader/octatrack-link'
import { useOctatrackLink } from '../hooks/useOctatrackLink'
import { Icon } from './Icon'
import { StateChip } from './ModuleGrid'
import { ModulePreview } from './ModulePreview'
import { MissingNote, type ProjectNeeds } from './OctatrackUpdate'
import './octatrack-link.css'

const moduleName = (id: string) => MODULES.find(module => module.id === id)?.name ?? id
const names = (ids: string[]) => new Intl.ListFormat('en', { type: 'conjunction' }).format(ids.map(moduleName))
const modules = (n: number) => n + (n === 1 ? ' module' : ' modules')
const BUSY = ['sending', 'testing', 'trial', 'finishing']
const CHIP: Record<UnitState, string> = { on: 'Stays', load: 'Adds', leaving: 'Leaves' }

/**
 * Your Octatrack, as a split view: your module sets on the leading side (selecting one makes it the set you edit,
 * the one the library adds to and the one Load sends) and the unit on the trailing side, its modules previewing what
 * loading the selected set changes. Nothing goes onto the unit without the guided load.
 */
export function OctatrackHub({ link, inventory, sets, selectedId, needs, onSelect, onOpen, onLoad, onEdit, onCreate, onDialog, onSaveUnit, onInstall }: {
  link: OctatrackLink | null; inventory?: Inventory; sets: Configuration[]; selectedId?: string; needs?: ProjectNeeds
  onSelect: (id: string) => void; onOpen: (id: string) => void; onLoad: (id: string) => void; onEdit: (id: string) => void; onCreate: () => void
  onDialog: (mode: 'rename' | 'duplicate' | 'delete') => void; onSaveUnit: () => void; onInstall: () => void
}) {
  const state = useOctatrackLink(link), { status, identity } = state
  const connected = !!identity?.canSubmit && status === 'ready', busy = BUSY.includes(status), usb = !!link && status !== 'unsupported'
  const last = connected || busy ? undefined : lastInventory()
  const unitIds = connected ? inventory?.moduleIds : last?.moduleIds
  const selected = sets.find(set => set.id === selectedId) ?? sets[0]
  const same = (set: Configuration) => !!unitIds && sameModules(set.moduleIds, unitIds)
  const onUnit = sets.find(same)
  const options = useRef<(HTMLLIElement | null)[]>([])
  function move(event: KeyboardEvent, index: number) {
    const next = listboxMove(event.key, index, sets.length)
    if (next === undefined) return
    event.preventDefault(); onSelect(sets[next].id); options.current[next]?.focus()
  }
  const changes = connected && inventory && selected && !same(selected) ? unitPreview(selected.moduleIds, inventory.moduleIds) : []
  const tiles = changes.length ? changes : (unitIds ?? []).map(id => ({ id, state: 'on' as UnitState }))
  const adds = changes.filter(tile => tile.state === 'load').map(tile => tile.id), leaves = changes.filter(tile => tile.state === 'leaving').map(tile => tile.id)
  const when = last && new Date(last.at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
  const [line, action]: [ReactNode, ReactNode] = !usb ? ['This browser can’t use USB. Install from the card, or open this page in Chrome or Edge on a computer.', null]
    : busy ? ['Loading…', null]
    : connected ? [<>Connected · {inventory ? modules(inventory.moduleIds.length) + ' on it' : 'reading what’s on it…'}{onUnit && <> · same as <b>{onUnit.name}</b></>}</>, null]
    : status === 'connecting' ? ['Looking for your Octatrack…', null]
    : status === 'busy' ? ['Another tab or app is using your Octatrack.', <button key="retry" className="button button-quiet" onClick={() => void link?.retry()}>Try again</button>]
    : status === 'stock' || status === 'ready' ? [status === 'stock' ? 'Connected · original OS' : 'Connected · a Modwerk base this site can’t talk to', <button key="install" className="button button-primary" onClick={onInstall}>Install the base</button>]
    : [<>Not connected{when && <> · last seen {when}</>}</>, <button key="connect" className="button button-quiet" onClick={() => void link?.connect()}>Connect</button>]
  return <div className="configuration-page octatrack-hub">
    <header className="page-heading"><div>
      <h1>Your Octatrack <span className="module-beta-badge">Beta</span></h1>
      <p>Pick a module set to edit. Nothing goes onto the Octatrack until you load it.</p>
    </div></header>
    <div className="hub-split">
      <section className="hub-sets" aria-labelledby="hub-sets-title">
        <div className="hub-pane-label"><h2 id="hub-sets-title">Module sets</h2><span className="subtle">{sets.length}</span></div>
        <ul className="hub-set-list" role="listbox" aria-labelledby="hub-sets-title">
          {sets.map((set, index) => { const isSelected = set.id === selected?.id, on = same(set)
            return <li key={set.id} ref={element => { options.current[index] = element }} role="option" aria-selected={isSelected} tabIndex={isSelected ? 0 : -1}
              className={'hub-set' + (isSelected ? ' is-selected' : '')} onClick={() => onSelect(set.id)} onKeyDown={event => move(event, index)}>
              <span className={'unit-led is-' + (on ? 'on' : 'off')} aria-hidden="true" />
              <strong>{set.name}</strong><b>{set.moduleIds.length}</b>
              <small>{set.moduleIds.map(moduleName).join(' · ') || 'No modules yet'}</small>
              {on && <em>On your Octatrack</em>}
            </li> })}
        </ul>
        <div className="hub-set-actions">
          <button type="button" className="text-button" onClick={onCreate}><Icon name="plus" size={14} />New module set</button>
          {selected && <span><button type="button" className="text-button" onClick={() => onEdit(selected.id)}>Edit</button><button type="button" className="text-button" onClick={() => onDialog('rename')}>Rename</button><button type="button" className="text-button" onClick={() => onDialog('duplicate')}>Duplicate</button><button type="button" className="text-button" onClick={() => onDialog('delete')}>Delete</button></span>}
        </div>
      </section>
      <section className="hub-unit" aria-labelledby="hub-unit-title">
        <div className="hub-unit-head">
          <DeviceImage device={DEVICES_BY_ID.octatrack} eager />
          <div><h2 id="hub-unit-title">{identity?.model ? identity.model.replace('OCTATRACK', 'Octatrack') : 'Octatrack'}</h2>
            <p role="status"><span className={'unit-led is-' + (connected ? 'on' : busy ? 'load' : 'off')} aria-hidden="true" />{line}</p></div>
          {action}
        </div>
        {connected && !inventory ? <p className="link-hint">Reading what’s on it…</p>
          : tiles.length ? <ul className="module-tiles hub-tiles">{tiles.map(({ id, state: tile }) => { const module = MODULES.find(item => item.id === id)
            return <li key={id} className={'module-tile' + (connected ? ' is-' + tile : ' is-last')}>
              <button type="button" className="module-tile-open" aria-haspopup="dialog" disabled={!module} onClick={() => onOpen(id)}><ModulePreview id={id} compact /><strong>{moduleName(id)}</strong><small>{module?.detail ?? 'Not in the library'}</small></button>
              <StateChip state={connected ? tile : 'off'}>{connected ? changes.length ? CHIP[tile] : 'On it' : 'Last seen'}</StateChip>
            </li> })}</ul>
          : unitIds ? <p className="link-hint">No modules on it.</p>
          : usb ? <p className="link-hint">Plug in your Octatrack to see what’s on it.</p> : null}
        {connected && <MissingNote needs={needs} />}
        {connected && inventory && inventory.moduleIds.length > 0 && !onUnit && <button type="button" className="text-button hub-save" onClick={onSaveUnit}>Save what’s on it as a module set <Icon name="plus" size={14} /></button>}
        {selected && usb && <div className="hub-footer">
          {connected && inventory && same(selected) ? <p className="hub-insync"><span className="unit-led is-on" aria-hidden="true" />Your Octatrack has exactly <b>{selected.name}</b>.</p>
            : <><p>{connected && inventory ? <>Loading <b>{selected.name}</b> {adds.length ? 'adds ' + names(adds) : ''}{adds.length && leaves.length ? ' and ' : ''}{leaves.length ? 'removes ' + names(leaves) : ''}.</>
                : busy ? <>A load is running.</> : status === 'stock' ? <>Install the base to load <b>{selected.name}</b>.</> : <>Connect your Octatrack to load <b>{selected.name}</b>.</>}</p>
              <button type="button" className="button button-primary" disabled={!connected || !inventory} onClick={() => onLoad(selected.id)}><Icon name="download" size={16} />Load {selected.name} onto Octatrack…</button></>}
        </div>}
        <details className="card-install" open={!usb}><summary>Install from the card instead</summary>
          <p className="link-hint">Build a .bin for {selected ? <b>{selected.name}</b> : 'your module set'} on its page, then install it like an OS update. <a href="#configuration">Open it <Icon name="arrow" size={14} /></a></p>
        </details>
      </section>
    </div>
  </div>
}
