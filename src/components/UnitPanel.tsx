import { MODULES } from '../catalog/modules'
import type { OctatrackLink } from '../engine/elekloader/octatrack-link'
import { useOctatrackLink } from '../hooks/useOctatrackLink'
import { Icon } from './Icon'
import { ModulePreview } from './ModulePreview'
import './octatrack-link.css'

/** Under the module set's title: is the Octatrack there, and what to do if not. Nothing without WebUSB. */
export function UnitStrip({ link, onInstall }: { link: OctatrackLink; onInstall: () => void }) {
  const { status, identity } = useOctatrackLink(link)
  if (status === 'unsupported') return null
  const busy = ['sending', 'testing', 'trial', 'finishing'].includes(status), base = !!identity?.canSubmit
  const [tone, text, action] = busy ? ['busy', 'Loading onto your Octatrack…', null]
    : base ? ['connected', `Octatrack connected · Modwerk base ${identity!.base.slice(0, 8)}`, null]
    : status === 'connecting' ? ['off', 'Looking for your Octatrack…', null]
    : status === 'busy' ? ['off', 'Another tab or app is using your Octatrack.', <button key="retry" className="text-button" onClick={() => void link.retry()}>Try again</button>]
    : status === 'stock' || status === 'ready' ? ['stock', status === 'stock' ? 'Your Octatrack runs the original OS.' : 'Your Octatrack runs a Modwerk base this site can’t talk to.', <button key="install" className="text-button" onClick={onInstall}>Install the base</button>]
    : ['off', 'Octatrack not connected. Plug it in to load modules over USB.', <button key="connect" className="text-button" onClick={() => void link.connect()}>Connect</button>]
  return <p className={'unit-strip is-' + tone} role="status"><span className={'status-dot' + (tone === 'connected' ? ' verified' : tone === 'busy' ? ' is-live' : '')} />{text}{action}</p>
}

/** Modules on the Octatrack that this set leaves out: loading the set removes them, unless they are added back. */
export function AlsoOnUnit({ ids, onAdd, onSaveSet }: { ids: string[]; onAdd: (id: string) => void; onSaveSet: () => void }) {
  return <section className="configuration-section also-on-unit" aria-labelledby="also-on-unit-title">
    <div className="section-title"><h2 id="also-on-unit-title">Also on your Octatrack <span className="subtle">{ids.length}</span></h2><button className="text-button" onClick={onSaveSet}>Save what’s on it as a module set <Icon name="plus" size={14} /></button></div>
    <p className="service-note">Not in this set, so loading it removes them.</p>
    <ul className="selected-list">{ids.map(id => { const module = MODULES.find(item => item.id === id)
      return <li key={id}><span className="selected-module-link"><ModulePreview id={id} compact /><span><strong>{module?.name ?? id}</strong><small>{module ? module.detail + ' · ' + module.authorName : 'Not in the library'}</small></span></span>
        {module && <button className="button button-quiet" onClick={() => onAdd(id)}><Icon name="plus" size={15} />Add to set</button>}</li> })}</ul>
  </section>
}
