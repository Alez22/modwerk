import { useEffect, useRef, useState } from 'react'
import { changeCount, inventoryChanges, loadStep, type Inventory, type InventoryTarget } from '../config/inventory'
import { LinkBusyError, type OctatrackLink } from '../engine/elekloader/octatrack-link'
import { ModuleSetError, USB_MODULE_IDS } from '../engine/elekloader/module-set'
import { useOctatrackLink } from '../hooks/useOctatrackLink'
import { MODULES } from '../catalog/modules'
import { StateChip } from './ModuleGrid'
import { ModulePreview } from './ModulePreview'
import { Icon } from './Icon'
import type { PrepareUpdate, StressTest } from './OctatrackUpdate'
import './octatrack-link.css'

const STEPS = ['Sync', 'Self-test', 'Try it']

const list = (ids: string[]) => new Intl.ListFormat('en', { type: 'conjunction' }).format(ids.map(id => MODULES.find(item => item.id === id)?.name ?? id))

/**
 * The one way to sync a module set to the Octatrack: review what changes, confirm playback is stopped, sync,
 * self-test, then try it and keep it or undo. While the trial runs it can't be dismissed; closing would undo it.
 * A module with no package for USB shows as Card only in the review: Sync waits, and `onEdit` (take it out of the
 * set) or `onCard` (install the set from the card) lead on. A failed sync offers `onReport` (the set's problem report).
 */
export function LoadDialog({ link, set, inventory, prepareUpdate, stressTest, onClose, onEdit, onCard, onReport }: {
  link: OctatrackLink; set: InventoryTarget; inventory?: Inventory; prepareUpdate?: PrepareUpdate; stressTest?: StressTest; onClose: () => void
  onEdit: () => void; onCard: () => void; onReport: () => void
}) {
  const dialog = useRef<HTMLDialogElement>(null), title = useRef<HTMLHeadingElement>(null)
  const state = useOctatrackLink(link), { status, progress = 0, tested, notice } = state
  const [stopped, setStopped] = useState(false), [started, setStarted] = useState(false), [preparing, setPreparing] = useState(false)
  const [error, setError] = useState(''), [leaving, setLeaving] = useState(false)
  const step = loadStep(status, started, preparing)
  const connected = !!state.identity?.canSubmit && status === 'ready'
  const changes = inventory && inventoryChanges(inventory, set), stays = inventory ? set.moduleIds.filter(id => inventory.moduleIds.includes(id)) : []
  const cardOnly = changes ? changes.add.filter(id => !USB_MODULE_IDS.includes(id)) : []
  useEffect(() => {
    const element = dialog.current, previousFocus = document.activeElement
    element?.showModal()
    return () => { element?.close(); if (previousFocus instanceof HTMLElement) previousFocus.focus() }
  }, [])
  // The heading takes focus on open and at each step, since the button that moved the step on is gone.
  useEffect(() => { title.current?.focus() }, [step])

  async function load() {
    setStarted(true); setPreparing(true); setError('')
    try { const prepared = await prepareUpdate!(set); setPreparing(false); await link.update(prepared.name, prepared.changes, stressTest) }
    catch (failure) { console.error(failure); setPreparing(false); setError(failure instanceof ModuleSetError || failure instanceof LinkBusyError ? failure.message : 'This module set couldn’t be prepared, so nothing was sent.') }
  }
  const index = step === 'loading' ? 0 : step === 'testing' ? 1 : 2
  const closable = step === 'review' || step === 'done'

  return <dialog ref={dialog} className="base-install-dialog load-dialog" aria-labelledby="load-title" onCancel={event => { event.preventDefault(); if (closable) onClose(); else if (step === 'trial') setLeaving(true) }}>
    {closable && <button type="button" className="icon-button base-install-close" aria-label="Close" onClick={onClose}><Icon name="close" size={18} /></button>}
    <header className="base-install-header"><div><span className="guide-eyebrow">Sync to your Octatrack</span><h2 id="load-title" ref={title} tabIndex={-1}>{set.name}</h2></div></header>
    {step === 'review' ? <>
      {!connected ? <p className="base-install-intro">Connect your Octatrack with the Modwerk base first.</p>
        : !changes ? <p className="base-install-intro">Reading what’s on it…</p>
        : !changeCount(changes) ? <p className="base-install-intro">Your Octatrack already has exactly these modules.</p>
        : <>
          <p className="base-install-intro">After syncing, the Octatrack tests itself, then you keep it or undo. Your project isn’t changed.</p>
          <ul className="load-changes">{([['card', 'Card only', cardOnly], ['load', 'Adds', changes.add.filter(id => !cardOnly.includes(id))], ['leaving', 'Removes', changes.remove], ['on', 'Stays', stays]] as const).flatMap(([state, label, ids]) => ids.map(id => {
            const module = MODULES.find(item => item.id === id)
            return <li key={id} className={'load-change is-' + state}>
              {module ? <ModulePreview id={id} compact /> : <span className="compact-preview" />}
              <span className="load-change-name"><strong>{module?.name ?? id}</strong>{state === 'leaving' ? <small>Tracks that use it play dry until you sync it again.</small> : state === 'card' && <small>Can’t be loaded over USB yet.</small>}</span>
              <StateChip state={state}>{label}</StateChip>
            </li>
          }))}</ul>
          {cardOnly.length > 0 && <div className="load-blocked" role="note">
            <p>{list(cardOnly)} still {cardOnly.length === 1 ? 'needs' : 'need'} the card. Take {cardOnly.length === 1 ? 'it' : 'them'} out of {set.name} to sync the rest now, or install {set.name} from the card.</p>
            <p><button type="button" className="text-button" onClick={onEdit}>Edit {set.name}</button><button type="button" className="text-button" onClick={onCard}>Install from the card</button></p>
          </div>}
        </>}
    </> : step === 'done' ? <p className={'base-install-intro ' + (error || notice?.tone === 'error' ? 'file-error' : 'success-note')} role={error || notice?.tone === 'error' ? 'alert' : 'status'}>{error || notice?.text || (status === 'busy' ? 'Another tab or app is using your Octatrack, so nothing was sent.' : 'Done.')}</p>
    : <>
      <ol className="load-steps" aria-label="Steps">{STEPS.map((label, i) => <li key={label} className={i < index ? 'is-complete' : i === index ? 'is-active' : undefined} aria-current={i === index ? 'step' : undefined}>{label}</li>)}</ol>
      {/* Sending and the self-test report how far they are; the trial waits on you. */}
      {(step === 'loading' && !preparing || step === 'testing') && <progress className="load-progress" max={1} value={progress} aria-label={step === 'loading' ? 'Syncing' : 'Self-test'} />}
      <p className="base-install-intro" role="status">{step === 'loading' ? (preparing ? 'Preparing your modules…' : progress < 1 ? `Syncing… ${Math.round(progress * 100)}%` : 'Starting…')
        : step === 'testing' ? `Running the Octatrack’s self-test… ${Math.round(progress * 100)}%`
        : `${tested ? 'The self-test passed. ' : ''}“${set.name}” is running on your Octatrack. Try it, then keep it or undo.`}</p>
      {step === 'trial' && notice?.tone === 'error' && <p className="file-error" role="alert">{notice.text}</p>}
      {step === 'trial' && (leaving && status === 'trial' ? <p className="file-error" role="alert">Closing now undoes it. Keep it or undo it first.</p> : <p className="link-hint">Unplugging or closing the site also undoes it.</p>)}
    </>}
    <footer className="base-install-footer">
      {step === 'review' && connected && changes && changeCount(changes) > 0 && !cardOnly.length
        ? <label className="load-check"><input type="checkbox" checked={stopped} onChange={event => setStopped(event.target.checked)} />Playback is stopped</label> : <span />}
      <div className="base-install-actions">
        {step === 'review' && <><button type="button" className="button button-quiet" onClick={onClose}>Cancel</button>
          <button type="button" className="button button-primary" disabled={!connected || !changes || !changeCount(changes) || cardOnly.length > 0 || !stopped || !prepareUpdate} onClick={() => void load()}><Icon name="download" size={16} />Sync</button></>}
        {step === 'loading' && !preparing && progress < 1 && <button type="button" className="button button-quiet" onClick={() => link.cancel()}>Cancel</button>}
        {step === 'trial' && <><button type="button" className="button button-quiet" disabled={status === 'finishing'} onClick={() => void link.undo()}>Undo</button>
          <button type="button" className="button button-primary" disabled={status === 'finishing'} onClick={() => void link.keep()}><Icon name="check" size={16} />Keep</button></>}
        {step === 'done' && (error || notice?.tone === 'error') && <button type="button" className="button button-quiet" aria-haspopup="dialog" onClick={onReport}><Icon name="message" size={16} />Report a problem</button>}
        {step === 'done' && <button type="button" className="button button-primary" onClick={onClose}>Done</button>}
      </div>
    </footer>
  </dialog>
}
