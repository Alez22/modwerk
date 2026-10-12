import { useState } from 'react'
import type { LinkState, OctatrackLink } from '../engine/elekloader/octatrack-link'
import { useOctatrackLink } from '../hooks/useOctatrackLink'
import { Icon } from './Icon'
import './octatrack-link.css'

const ACTIVE: LinkState['status'][] = ['sending', 'testing', 'trial', 'finishing']
const activity = ({ status, progress = 0 }: LinkState) => status === 'sending' ? `Loading ${Math.round(progress * 100)}%`
  : status === 'testing' ? 'Self-test' : status === 'trial' ? 'Waiting for Keep or Undo' : 'Finishing'

/** The Octatrack's connection in the status bar; nothing while idle or without WebUSB. */
export function OctatrackStatus({ link }: { link: OctatrackLink }) {
  const state = useOctatrackLink(link), { status, identity } = state
  if (status === 'unsupported' || status === 'idle' || status === 'connecting') return null
  const busy = ACTIVE.includes(status)
  return <span className="octatrack-status-bar"><span className={'status-dot' + (busy ? ' is-live' : identity?.canSubmit ? ' verified' : '')} />{busy ? 'Loading onto Octatrack · ' + activity(state) : status === 'busy' ? 'Octatrack in use' : 'Octatrack connected'}</span>
}

/** A pill while an update runs or waits for Keep or Undo, and for its result, on every page but the configuration page. */
export function OctatrackActivity({ link }: { link: OctatrackLink }) {
  const state = useOctatrackLink(link), { status, module, notice } = state
  const [dismissed, setDismissed] = useState<LinkState['notice']>()
  const result = notice && notice !== dismissed && !ACTIVE.includes(status) ? notice : undefined
  if (!ACTIVE.includes(status) && !result) return null
  return <aside className={'octatrack-activity' + (result?.tone === 'error' ? ' is-error' : '')} aria-label="Octatrack update" role="status">
    {result ? <><span>{result.text}</span><button type="button" className="icon-button" aria-label="Dismiss" onClick={() => setDismissed(notice)}><Icon name="close" size={15} /></button></>
      : <><span className="status-dot is-live" /><span><strong>{module}</strong> · {activity(state)}</span>
        {(status === 'trial' || status === 'finishing') && <><button type="button" className="button button-primary" disabled={status === 'finishing'} onClick={() => void link.keep()}>Keep</button><button type="button" className="button button-quiet" disabled={status === 'finishing'} onClick={() => void link.undo()}>Undo</button></>}
        <a className="text-button" href="#configuration">Open</a></>}
  </aside>
}
