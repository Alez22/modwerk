import type { ReactNode } from 'react'
import type { OctatrackLink } from '../engine/elekloader/octatrack-link'
import { useOctatrackLink } from '../hooks/useOctatrackLink'
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

/** The card-install part of the module set page, folded away while a unit with the base is connected. */
export function CardInstall({ folded, children }: { folded: boolean; children: ReactNode }) {
  return folded ? <details className="card-install"><summary>Install from the card instead</summary>{children}</details> : children
}
