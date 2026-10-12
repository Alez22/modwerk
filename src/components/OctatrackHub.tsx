import { MODULES } from '../catalog/modules'
import { lastInventory, sameModules, type Inventory } from '../config/inventory'
import type { Configuration } from '../config/workspace'
import type { OctatrackLink } from '../engine/elekloader/octatrack-link'
import { useOctatrackLink } from '../hooks/useOctatrackLink'
import { moduleHref } from '../routing'
import { Icon } from './Icon'
import { StateChip } from './ModuleGrid'
import { ModulePreview } from './ModulePreview'
import { MissingNote, type ProjectNeeds } from './OctatrackUpdate'
import './octatrack-link.css'

const moduleName = (id: string) => MODULES.find(module => module.id === id)?.name ?? id
const BUSY = ['sending', 'testing', 'trial', 'finishing']

/**
 * Your Octatrack: what is on it now (or when this browser last read it), your module sets against it, and the one
 * way to load one, through the guided dialog. Nothing loads from here without that dialog.
 */
export function OctatrackHub({ link, inventory, sets, needs, onLoad, onEdit, onCreate, onSaveUnit, onInstall }: {
  link: OctatrackLink | null; inventory?: Inventory; sets: Configuration[]; needs?: ProjectNeeds
  onLoad: (id: string) => void; onEdit: (id: string) => void; onCreate: () => void; onSaveUnit: () => void; onInstall: () => void
}) {
  const state = useOctatrackLink(link), { status, identity } = state
  const connected = !!identity?.canSubmit && status === 'ready', busy = BUSY.includes(status)
  const last = connected || busy ? undefined : lastInventory()
  const shown = connected ? inventory?.moduleIds : last?.moduleIds
  const match = shown && sets.find(set => sameModules(set.moduleIds, shown))
  const [line, action] = busy ? ['Loading onto your Octatrack…', null]
    : connected ? [`Connected · Modwerk base ${identity!.base.slice(0, 8)}`, null]
    : status === 'connecting' ? ['Looking for your Octatrack…', null]
    : status === 'unsupported' ? ['This browser can’t use USB. Open this page in Chrome or Edge on a computer.', null]
    : status === 'busy' ? ['Another tab or app is using your Octatrack.', <button key="retry" className="text-button" onClick={() => void link?.retry()}>Try again</button>]
    : status === 'stock' || status === 'ready' ? [status === 'stock' ? 'Connected · original OS' : 'Connected · a Modwerk base this site can’t talk to', <button key="install" className="button button-primary" onClick={onInstall}>Install the base</button>]
    : ['Not connected', <button key="connect" className="button button-quiet" onClick={() => void link?.connect()}>Connect</button>]
  const reason = connected ? '' : busy ? 'A load is running.' : status === 'stock' ? 'Install the base to load module sets.' : 'Connect your Octatrack to load a module set.'
  return <div className="configuration-page octatrack-hub">
    <header className="page-heading configuration-heading"><div>
      <h1>Your Octatrack <span className="module-beta-badge">Beta</span></h1>
      <p>What’s on it, and your module sets. Nothing goes onto it until you load a set and keep it.</p>
    </div></header>
    <section className="configuration-section hub-unit" aria-labelledby="hub-unit-title">
      <div className="section-title">
        <h2 id="hub-unit-title">{connected ? 'On it now' : last ? 'When last connected' : 'On it'} {shown && <span className="subtle">{shown.length}</span>}</h2>
        <span className={'unit-strip is-' + (connected ? 'connected' : busy ? 'busy' : 'off')} role="status"><span className={'status-dot' + (connected ? ' verified' : busy ? ' is-live' : '')} />{line}{action}</span>
      </div>
      {connected && !inventory ? <p className="link-hint">Reading what’s on it…</p>
        : shown ? shown.length ? <ul className="module-tiles">{shown.map(id => <li key={id} className="module-tile">
            <a className="module-tile-open" href={moduleHref(id)}><ModulePreview id={id} compact /><strong>{moduleName(id)}</strong><small>{MODULES.find(module => module.id === id)?.detail ?? 'Not in the library'}</small></a>
          </li>)}</ul> : <p className="link-hint">No modules on it.</p>
        : <p className="link-hint">Plug in your Octatrack to see what’s on it.</p>}
      {last && <p className="link-hint">Read {new Date(last.at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}. It may have changed since.</p>}
      {match && <p className="hub-match">Same modules as your set <b>{match.name}</b>.</p>}
      {connected && <MissingNote needs={needs} />}
      {connected && inventory && inventory.moduleIds.length > 0 && !match && <button type="button" className="text-button" onClick={onSaveUnit}>Save what’s on it as a module set <Icon name="plus" size={14} /></button>}
    </section>
    <section className="configuration-section hub-sets" aria-labelledby="hub-sets-title">
      <div className="section-title"><h2 id="hub-sets-title">Your module sets <span className="subtle">{sets.length}</span></h2>
        <button type="button" className="button button-quiet" onClick={onCreate}><Icon name="plus" size={16} />New module set</button></div>
      {reason && sets.length > 0 && <p className="link-hint">{reason}</p>}
      <ul className="hub-set-list">{sets.map(set => {
        const on = connected && !!inventory && sameModules(set.moduleIds, inventory.moduleIds)
        return <li key={set.id}>
          <span className="hub-set-name"><strong>{set.name}</strong><small>{set.moduleIds.map(moduleName).join(', ') || 'No modules yet'}</small></span>
          {on && <StateChip state="on" className="is-legend">On your Octatrack</StateChip>}
          <button type="button" className="button button-quiet" onClick={() => onEdit(set.id)}>Edit</button>
          {!on && <button type="button" className="button button-primary" disabled={!connected || !inventory} onClick={() => onLoad(set.id)}>Load onto Octatrack…</button>}
        </li>
      })}</ul>
      {!sets.length && <p className="link-hint">No module sets yet.</p>}
    </section>
    <details className="card-install"><summary>Install from the card instead</summary>
      <p className="link-hint">No USB here? Build a .bin for the card on your module set’s page, then install it like an OS update. <a href="#configuration">Open your module set <Icon name="arrow" size={14} /></a></p>
    </details>
  </div>
}
