import { useEffect, useRef, useState } from 'react'
import { changeCount, inventoryChanges, loadStep, type Inventory, type InventoryTarget } from '../config/inventory'
import { LinkBusyError, type OctatrackLink } from '../engine/elekloader/octatrack-link'
import { ModuleSetError } from '../engine/elekloader/module-set'
import { useOctatrackLink } from '../hooks/useOctatrackLink'
import { ChangeSummary } from './InventoryChanges'
import { Icon } from './Icon'
import type { PrepareUpdate, StressTest } from './OctatrackUpdate'
import './octatrack-link.css'

const STEPS = ['Load', 'Self-test', 'Try it']

/**
 * The one way to load a module set onto the Octatrack: review what changes, confirm playback is stopped, load,
 * self-test, then try it and keep it or undo. While the trial runs it can't be dismissed; closing would undo it.
 */
export function LoadDialog({ link, set, inventory, prepareUpdate, stressTest, onClose }: {
  link: OctatrackLink; set: InventoryTarget; inventory?: Inventory; prepareUpdate?: PrepareUpdate; stressTest?: StressTest; onClose: () => void
}) {
  const dialog = useRef<HTMLDialogElement>(null)
  const state = useOctatrackLink(link), { status, progress = 0, tested, notice } = state
  const [stopped, setStopped] = useState(false), [started, setStarted] = useState(false), [preparing, setPreparing] = useState(false)
  const [error, setError] = useState(''), [leaving, setLeaving] = useState(false)
  const step = loadStep(status, started, preparing)
  const connected = !!state.identity?.canSubmit && status === 'ready'
  const changes = inventory && inventoryChanges(inventory, set), stays = inventory ? set.moduleIds.filter(id => inventory.moduleIds.includes(id)) : []
  useEffect(() => {
    const element = dialog.current, previousFocus = document.activeElement
    element?.showModal()
    return () => { element?.close(); if (previousFocus instanceof HTMLElement) previousFocus.focus() }
  }, [])

  async function load() {
    setStarted(true); setPreparing(true); setError('')
    try { const prepared = await prepareUpdate!(set); setPreparing(false); await link.update(prepared.name, prepared.changes, stressTest) }
    catch (failure) { console.error(failure); setPreparing(false); setError(failure instanceof ModuleSetError || failure instanceof LinkBusyError ? failure.message : 'This module set couldn’t be prepared, so nothing was sent.') }
  }
  const index = step === 'loading' ? 0 : step === 'testing' ? 1 : 2
  const closable = step === 'review' || step === 'done'

  return <dialog ref={dialog} className="base-install-dialog load-dialog" aria-labelledby="load-title" onCancel={event => { event.preventDefault(); if (closable) onClose(); else if (step === 'trial') setLeaving(true) }}>
    {closable && <button type="button" className="icon-button base-install-close" aria-label="Close" onClick={onClose}><Icon name="close" size={18} /></button>}
    <header className="base-install-header"><h2 id="load-title">Load “{set.name}” onto your Octatrack</h2></header>
    {step === 'review' ? <>
      {!connected ? <p className="base-install-intro">Connect your Octatrack with the Modwerk base first.</p>
        : !changes ? <p className="base-install-intro">Reading what’s on it…</p>
        : !changeCount(changes) ? <p className="base-install-intro">Your Octatrack already has exactly these modules.</p>
        : <>
          <ChangeSummary changes={changes} stays={stays} />
          {changes.remove.length > 0 && <p className="link-hint">Tracks that use a module it removes play dry until you load it again.</p>}
          <label className="load-check"><input type="checkbox" checked={stopped} onChange={event => setStopped(event.target.checked)} />Playback is stopped</label>
          <p className="link-hint">Your project isn’t changed.</p>
        </>}
    </> : step === 'done' ? <p className={'base-install-intro ' + (error || notice?.tone === 'error' ? 'file-error' : 'success-note')} role={error || notice?.tone === 'error' ? 'alert' : 'status'}>{error || notice?.text || (status === 'busy' ? 'Another tab or app is using your Octatrack, so nothing was sent.' : 'Done.')}</p>
    : <>
      <div className="build-progress" role="progressbar" aria-label="Load progress" aria-valuemin={0} aria-valuemax={STEPS.length} aria-valuenow={index}>
        <ol className="build-progress-steps" aria-hidden="true">{STEPS.map((label, i) => <li key={label} className={i < index ? 'is-complete' : i === index ? 'is-active' : undefined}>
          <span className="build-progress-track" /><span className="build-progress-label"><span className="build-progress-marker">{i < index ? <Icon name="check" size={14} /> : i + 1}</span><span>{label}</span></span>
        </li>)}</ol>
      </div>
      <p className="base-install-intro" role="status">{step === 'loading' ? (preparing ? 'Preparing your modules…' : progress < 1 ? `Loading… ${Math.round(progress * 100)}%` : 'Starting…')
        : step === 'testing' ? 'Running the Octatrack’s self-test…'
        : `${tested ? 'The self-test passed. ' : ''}“${set.name}” is running on your Octatrack. Try it, then keep it or undo.`}</p>
      {step === 'trial' && notice?.tone === 'error' && <p className="file-error" role="alert">{notice.text}</p>}
      {step === 'trial' && (leaving && status === 'trial' ? <p className="file-error" role="alert">Closing now undoes it. Keep it or undo it first.</p> : <p className="link-hint">Unplugging or closing the site also undoes it.</p>)}
    </>}
    <footer className="base-install-footer">
      <span />
      <div className="base-install-actions">
        {step === 'review' && <><button type="button" className="button button-quiet" onClick={onClose}>Cancel</button>
          <button type="button" className="button button-primary" disabled={!connected || !changes || !changeCount(changes) || !stopped || !prepareUpdate} onClick={() => void load()}><Icon name="download" size={16} />Load</button></>}
        {step === 'loading' && !preparing && progress < 1 && <button type="button" className="button button-quiet" onClick={() => link.cancel()}>Cancel</button>}
        {step === 'trial' && <><button type="button" className="button button-quiet" disabled={status === 'finishing'} onClick={() => void link.undo()}>Undo</button>
          <button type="button" className="button button-primary" disabled={status === 'finishing'} onClick={() => void link.keep()}><Icon name="check" size={16} />Keep</button></>}
        {step === 'done' && <button type="button" className="button button-primary" onClick={onClose}>Done</button>}
      </div>
    </footer>
  </dialog>
}
