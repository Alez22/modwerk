import { useEffect, useRef, useState } from 'react'
import { Icon } from './Icon'
import { assetUrl } from '../hosting'
import { DEVELOPMENT_DISCORD_URL } from '../config/development-discord'
import { SUPPORT_URL } from '../config/support'
import { pageBusy } from '../community/public-announcement'
import { trackUsage } from '../community/usage'

// A new note needs a new key, so everyone sees it once.
const KEY = 'modwerk.owner-note:2026-10-14'
let closedThisVisit = false
export function ownerNoteSeen() {
  if (closedThisVisit) return true
  try { return localStorage.getItem(KEY) === 'seen' } catch { return false }
}
export function closeOwnerNote() {
  closedThisVisit = true
  try { localStorage.setItem(KEY, 'seen') } catch { /* Stays closed for this visit when storage is blocked. */ }
}

export function OwnerNote({ onClose }: { onClose: () => void }) {
  const dialog = useRef<HTMLDialogElement>(null)
  useEffect(() => {
    const element = dialog.current, previousFocus = document.activeElement
    element?.showModal()
    return () => { element?.close(); if (previousFocus instanceof HTMLElement && previousFocus.isConnected) previousFocus.focus() }
  }, [])
  return <dialog ref={dialog} className="app-dialog support-dialog owner-note" aria-labelledby="owner-note-title" aria-describedby="owner-note-message" onCancel={event => { event.preventDefault(); onClose() }}>
    <h2 id="owner-note-title">Hey guys,</h2>
    <div id="owner-note-message">
      <p>the response to this project has been immense, and I'm super grateful for everything that has happened over the past weeks.</p>
      <p>But I really need to slow down. Honestly, I'm feeling burnt out. I can't keep up with the demand and all the new issue reports coming in. Many module maintainers aren't fixing the bugs in their modules, so I've ended up fixing most of them myself, while also working on a big Octatrack update that changes how FX get loaded onto the DSP chip.</p>
      <p>A big thank you to the developers who have been helping so far! It's just not enough to cover the demand. At this rate I simply <strong>CANNOT</strong> continue without more active helpers on the Discord server. This is a community project and I'd like it to stay that way.</p>
      <p>Also important: the modules are <strong>NOT</strong> safe to use in a live setting (yet). Flashing itself is known to be quite safe with the instrument's own bootloader, but the modules can still crash or misbehave.</p>
      <p>And to be clear: I'm not integrating any mods that clone products other companies still sell, or mods that would hurt Elektron's sales. These mods are mostly meant to be additive and to integrate well into the instruments' existing UI.</p>
      <p>If you like my work over the last weeks, I'd be grateful for a small donation. I've been covering all the hosting costs myself.</p>
      <p>Thank you,<br />Jannik</p>
    </div>
    <div className="dialog-actions">
      <button type="button" className="button button-quiet" autoFocus onClick={onClose}>Close</button>
      <a className="button button-quiet" href={DEVELOPMENT_DISCORD_URL} target="_blank" rel="noopener noreferrer" onClick={onClose} aria-label="Join Discord (opens in a new tab)"><img src={assetUrl('auth/discord.svg')} width={20} height={15} alt="" />Join Discord</a>
      <a className="button button-primary" href={SUPPORT_URL} target="_blank" rel="noopener noreferrer" onClick={() => { trackUsage('support_link_opened'); onClose() }} aria-label="Support on Ko-fi (opens in a new tab)"><Icon name="heart" size={15} />Support on Ko-fi</a>
    </div>
  </dialog>
}

/** Opens once per browser, when no other dialog, menu or text field is in use. */
export function OwnerNoteGate({ enabled }: { enabled: boolean }) {
  const [open, setOpen] = useState(false)
  useEffect(() => {
    if (!enabled || open || ownerNoteSeen()) return
    const timer = window.setInterval(() => { if (!pageBusy()) setOpen(true) }, 3000)
    return () => window.clearInterval(timer)
  }, [enabled, open])
  return open ? <OwnerNote onClose={() => { closeOwnerNote(); setOpen(false) }} /> : null
}
