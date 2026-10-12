import { useRef, type KeyboardEvent, type ReactNode } from 'react'
import { MODULES } from '../catalog/modules'
import { changeCount, inventoryChanges, lastInventory, listboxMove, sameModules, type Inventory } from '../config/inventory'
import { lastSuccessfulSync } from '../config/octatrack-progress'
import type { Configuration } from '../config/workspace'
import { DeviceImage } from '../devices/DeviceImage'
import { DEVICES_BY_ID } from '../devices/registry'
import type { OctatrackLink } from '../engine/elekloader/octatrack-link'
import { useOctatrackLink } from '../hooks/useOctatrackLink'
import { Icon } from './Icon'
import { OctatrackDiagnosticsSettings } from './OctatrackDiagnostics'
import { MissingNote, type ProjectNeeds } from './OctatrackUpdate'
import './octatrack-link.css'

const moduleName = (id: string) => MODULES.find(module => module.id === id)?.name ?? id
const modules = (n: number) => n + (n === 1 ? ' module' : ' modules')
const BUSY = ['sending', 'testing', 'trial', 'finishing']

/**
 * Your Octatrack: the configuration page of the beta. A split view with your module sets on the leading side
 * (selecting one makes it the set you edit, the one the library adds to and the one Sync sends) and, on the trailing
 * side, the unit and the selected set's modules (`grid`, App's ModuleGrid, with the unit's LED states). The page's
 * header (`header`) and the card route (`card`: base OS file, checks, build) are App's own parts, so nothing the
 * configuration page had is lost. Nothing goes onto the unit without the guided sync.
 */
export function OctatrackHub({ link, inventory, sets, selectedId, needs, onSelect, onSync, onInstall, header, grid, card }: {
  link: OctatrackLink | null; inventory?: Inventory; sets: Configuration[]; selectedId?: string; needs?: ProjectNeeds
  onSelect: (id: string) => void; onSync: (id: string) => void; onInstall: () => void
  header: ReactNode; grid: ReactNode; card: ReactNode
}) {
  const state = useOctatrackLink(link), { status, identity } = state
  const connected = !!identity?.canSubmit && status === 'ready', busy = BUSY.includes(status), usb = !!link && status !== 'unsupported'
  const last = connected || busy ? undefined : lastInventory()
  const unitIds = connected ? inventory?.moduleIds : last?.moduleIds
  const selected = sets.find(set => set.id === selectedId) ?? sets[0]
  const same = (set: Configuration) => set.moduleIds.length > 0 && !!unitIds && sameModules(set.moduleIds, unitIds)
  const onUnit = sets.find(same)
  const lastSync = lastSuccessfulSync(identity?.base ?? last?.base)
  const lastName = onUnit?.name ?? (last && lastSync && sameModules(last.moduleIds, lastSync.moduleIds) ? lastSync.name : undefined)
  const options = useRef<(HTMLLIElement | null)[]>([])
  function move(event: KeyboardEvent, index: number) {
    const next = listboxMove(event.key, index, sets.length)
    if (next === undefined) return
    event.preventDefault(); onSelect(sets[next].id); options.current[next]?.focus()
  }
  const changes = connected && inventory && selected ? inventoryChanges(inventory, selected) : undefined
  const when = last && new Date(last.at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })
  const [line, action]: [ReactNode, ReactNode] = !usb ? ['This browser can’t use USB. Install from the card below, or open this page in Chrome or Edge on a computer.', null]
    : busy ? ['Syncing…', null]
    : connected ? [<>Connected · {inventory ? modules(inventory.moduleIds.length) + ' on it' : 'reading what’s on it…'}{onUnit && <> · same as <b>{onUnit.name}</b></>}</>, null]
    : status === 'connecting' ? ['Looking for your Octatrack…', null]
    : status === 'busy' ? ['Another tab or app is using your Octatrack.', <button key="retry" className="button button-quiet" onClick={() => void link?.retry()}>Try again</button>]
    : status === 'stock' || status === 'ready' ? [status === 'stock' ? 'Connected · original OS' : 'Connected · a Modwerk base this site can’t talk to', <button key="install" className="button button-primary" onClick={onInstall}>Install the base</button>]
    : [<>Not connected{last ? <> · Last seen: {lastName ? <b>{lastName}</b> : modules(last.moduleIds.length)} · {when}</> : null}</>, <button key="connect" className="button button-quiet" onClick={() => void link?.connect()}>Connect</button>]
  return <div className="configuration-page octatrack-hub">
    {header}
    <div className="hub-split">
      <section className="hub-sets" aria-labelledby="hub-sets-title">
        <div className="hub-pane-label"><h2 id="hub-sets-title">Module sets</h2><span className="subtle">{sets.length}</span></div>
        <ul className="hub-set-list" role="listbox" aria-labelledby="hub-sets-title">
          {sets.map((set, index) => { const isSelected = set.id === selected?.id, on = same(set)
            return <li key={set.id} ref={element => { options.current[index] = element }} role="option" aria-selected={isSelected} tabIndex={isSelected ? 0 : -1}
              className={'hub-set' + (isSelected ? ' is-selected' : '')} onClick={() => onSelect(set.id)} onKeyDown={event => move(event, index)}>
              <span className={'unit-led is-' + (on && connected ? 'on' : 'off')} aria-hidden="true" />
              <strong>{set.name}</strong><b>{set.moduleIds.length}</b>
              <small>{set.moduleIds.map(moduleName).join(' · ') || 'No modules yet'}</small>
              {on && (connected ? <em>On your Octatrack</em> : <small>Last seen on your Octatrack</small>)}
            </li> })}
        </ul>
      </section>
      <section className="hub-unit" aria-labelledby="hub-unit-title">
        <div className="hub-unit-head">
          <DeviceImage device={DEVICES_BY_ID.octatrack} eager />
          <div><h2 id="hub-unit-title">{identity?.model ? identity.model.replace('OCTATRACK', 'Octatrack') : 'Octatrack'}</h2>
            <p role="status"><span className={'unit-led is-' + (connected ? 'on' : busy ? 'load' : 'off')} aria-hidden="true" />{line}</p></div>
          {action}
        </div>
        {lastSync && <p className="hub-last-sync">Last sync from this browser: <b>{lastSync.name}</b> · <time dateTime={lastSync.at}>{new Date(lastSync.at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}</time></p>}
        {selected && usb && <div className="hub-sync-bar" aria-label="Module set sync">
          <div><strong>{selected.name}</strong>
            <p>{changes ? changeCount(changes) ? <>Adds {changes.add.length} · Removes {changes.remove.length}{!!(changes.stockOff.length + changes.stockOn.length) && <> · Stock effects change</>}</>
                : selected.moduleIds.length ? <span className="hub-insync"><span className="unit-led is-on" aria-hidden="true" />Already on your Octatrack</span> : 'No modules in this set.'
              : busy ? 'A sync is running.' : status === 'stock' ? 'Install the base to sync this set.' : connected ? 'Reading what’s on your Octatrack…' : 'Connect your Octatrack to sync this set.'}</p>
          </div>
          <button type="button" className="button button-primary" disabled={!changes || !changeCount(changes)} onClick={() => onSync(selected.id)}><Icon name="download" size={16} />Sync to Octatrack</button>
        </div>}
        {connected && <MissingNote needs={needs} onSync={selected ? () => onSync(selected.id) : undefined} />}
        {grid}
        {card}
        <details className="hub-diagnostics"><summary>Beta diagnostics</summary><OctatrackDiagnosticsSettings/></details>
      </section>
    </div>
  </div>
}
