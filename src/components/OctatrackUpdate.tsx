import { useState, type ReactNode } from 'react'
import { changeCount, inventoryChanges, type Inventory, type InventoryTarget } from '../config/inventory'
import type { OctatrackLink, SetChange } from '../engine/elekloader/octatrack-link'
import { useInventory, useOctatrackLink } from '../hooks/useOctatrackLink'
import { ChangeSummary } from './InventoryChanges'
import { Icon } from './Icon'
import './octatrack-link.css'

/** The builder: the target set as what the base loads, change by change. */
export type PrepareUpdate = (target: InventoryTarget) => Promise<{ name: string; changes: SetChange[] }>
/** The base: what is on the unit. */
export type ReadInventory = () => Promise<Inventory>
export type StressTest = () => Promise<string | null>
const STEPS = ['Load', 'Self-test', 'Keep']
/** What the unit's project names that the unit lacks: library names, names the library does not know, and how to add
 * the ones this set does not have yet (absent when it has them all). */
export interface ProjectNeeds { names: string[]; unknown: string[]; add?: () => void }
const list = (items: string[]) => new Intl.ListFormat('en', { type: 'conjunction' }).format(items)
export function MissingNote({ needs }: { needs?: ProjectNeeds }) {
  if (!needs || !needs.names.length && !needs.unknown.length) return null
  const { names, unknown, add } = needs, verb = (n: number) => n === 1 ? 'isn’t' : 'aren’t'
  return <p className="usb-missing" role="status">
    {names.length > 0 && <>Your project uses {list(names)}, which {verb(names.length)} on your Octatrack. {add
      ? <button className="text-button" onClick={add}>Add to set</button> : `Load onto Octatrack to bring ${names.length === 1 ? 'it' : 'them'} back.`}</>}
    {unknown.length > 0 && <>{names.length ? ' It also uses ' : 'Your project uses '}{list(unknown)}, which {verb(unknown.length)} in the library.</>}
  </p>
}

/**
 * The checkout card's flow once an Octatrack with the Modwerk base is connected: update it over USB
 * (stop playback, load, stress test, keep or undo) instead of building a .bin for the card, which stays
 * one click away. Without such a unit, `children` (the .bin flow) shows with a hint about USB.
 * `prepareUpdate` (the builder) and `stressTest` (the test runner) are absent until they exist.
 */
export function OctatrackUpdate({ link, set, prepareUpdate, readInventory, stressTest, needs, onInstall, children, bar = false }: {
  link: OctatrackLink
  /** The sticky sync bar of the full-width page, shown only while a unit with the base is connected. */
  bar?: boolean
  /** The module set on this page; loading makes the unit match it. */
  set: InventoryTarget
  readInventory?: ReadInventory
  prepareUpdate?: PrepareUpdate
  stressTest?: StressTest
  /** Modules the unit's project names that the unit lacks (its MISSING list). */
  needs?: ProjectNeeds
  onInstall: () => void
  children: ReactNode
}) {
  const state = useOctatrackLink(link), inventory = useInventory(link, readInventory)
  const moduleCount = set.moduleIds.length, changes = inventory && inventoryChanges(inventory, set)
  const [download, setDownload] = useState(false)
  const [preparing, setPreparing] = useState<'idle' | 'busy' | 'failed'>('idle')
  const { status, identity, active, module, progress = 0, tested, notice } = state
  const base = !!identity?.canSubmit && ['ready', 'sending', 'testing', 'trial', 'finishing'].includes(status)

  if (!base || download) return <>
    {children}
    {status === 'idle' && <p className="usb-hint">Got the Modwerk base? Plug in your Octatrack to update it over USB. <button className="text-button" onClick={() => void link.connect()}>Connect</button></p>}
    {(status === 'stock' || status === 'ready' && !identity?.canSubmit) && <p className="usb-hint">Your Octatrack is connected. Install the Modwerk base once to update it over USB. <button className="text-button" onClick={onInstall}>Install the base</button></p>}
    {status === 'busy' && <p className="usb-hint">Another tab or app is using your Octatrack. <button className="text-button" onClick={() => void link.retry()}>Try again</button></p>}
    {base && <p className="usb-hint"><button className="text-button" onClick={() => setDownload(false)}>Update over USB instead</button></p>}
  </>

  async function update() {
    setPreparing('busy')
    try { const prepared = await prepareUpdate!(set); setPreparing('idle'); await link.update(prepared.name, prepared.changes, stressTest) }
    catch (error) { console.error(error); setPreparing('failed') }
  }
  const step = status === 'sending' ? 0 : status === 'testing' ? 1 : 2
  const busy = status !== 'ready'
  const text = status === 'sending' ? (progress < 1 ? `Loading… ${Math.round(progress * 100)}%` : 'Starting…')
    : status === 'testing' ? 'Running the Octatrack’s self-test…'
    : status === 'trial' || status === 'finishing' ? `${tested ? 'Passed. ' : ''}${module} is running. Try it, then keep it or undo.`
    : preparing === 'busy' ? 'Preparing your modules…'
    : changes && !changeCount(changes) ? 'Your Octatrack already matches this module set.'
    : 'Your Octatrack will match this module set. Stop playback first; after its self-test you keep it or undo.'
  if (bar) return <section className="sync-bar" aria-label="Load onto your Octatrack" aria-busy={status === 'sending' || status === 'testing' || status === 'finishing'}>
    <div className="sync-bar-status" role="status">
      {status === 'ready' && changes && changeCount(changes) > 0 && preparing !== 'busy' ? <><strong>Next load</strong><ChangeSummary changes={changes} inline /></>
        : <p>{status === 'ready' && changes && !changeCount(changes) ? <><span className="status-dot verified" /> Your Octatrack matches this module set.</> : text}</p>}
      {status === 'ready' && <MissingNote needs={needs} />}
      {status === 'sending' && <progress className="link-progress" max={1} value={progress} aria-label="Loading" />}
      {preparing === 'failed' && <p className="file-error" role="alert">This module set could not be prepared for USB.</p>}
      {notice && <p className={notice.tone === 'success' ? 'success-note' : 'file-error'} role={notice.tone === 'success' ? 'status' : 'alert'}>{notice.text}</p>}
    </div>
    <div className="sync-bar-actions">
      {status === 'ready' && !prepareUpdate && <span className="subtle">The browser can’t build updates yet.</span>}
      {status === 'ready' && <button className="button button-primary" disabled={!prepareUpdate || (!moduleCount && !inventory?.moduleIds.length) || (!!changes && !changeCount(changes)) || preparing === 'busy'} onClick={() => void update()}><Icon name="download" size={16} />Load onto Octatrack</button>}
      {status === 'sending' && progress < 1 && <button className="button button-quiet" onClick={() => link.cancel()}>Cancel</button>}
      {(status === 'trial' || status === 'finishing') && <><button className="button button-quiet" disabled={status === 'finishing'} onClick={() => void link.undo()}>Undo</button><button className="button button-primary" disabled={status === 'finishing'} onClick={() => void link.keep()}><Icon name="check" size={16} />Keep</button></>}
    </div>
  </section>
  return <section className="build-section usb-update" aria-labelledby="usb-update-title" aria-busy={status === 'sending' || status === 'testing' || status === 'finishing'}>
    <div>
      <h2 id="usb-update-title">Load onto your Octatrack <span className="module-beta-badge">Beta</span></h2>
      <p className="usb-identity"><span className="status-dot verified" />{identity!.model} · base {identity!.base.slice(0, 8)}{inventory ? ` · ${inventory.moduleIds.length} ${inventory.moduleIds.length === 1 ? 'module' : 'modules'} installed` : active && (active === identity!.base ? ' · no modules' : ' · last module ' + active.slice(0, 8))}</p>
      <p role="status">{text}</p>
      {busy && <div className="build-progress" role="progressbar" aria-label="Update progress" aria-valuemin={0} aria-valuemax={STEPS.length} aria-valuenow={step}>
        <ol className="build-progress-steps" aria-hidden="true">{STEPS.map((label, i) => <li key={label} className={i < step ? 'is-complete' : i === step ? 'is-active' : undefined}>
          <span className="build-progress-track" /><span className="build-progress-label"><span className="build-progress-marker">{i < step ? <Icon name="check" size={14} /> : i + 1}</span><span>{label}</span></span>
        </li>)}</ol>
      </div>}
      {status === 'ready' && <MissingNote needs={needs} />}
      {status === 'ready' && changes && changeCount(changes) > 0 && <ChangeSummary changes={changes} />}
      {status === 'trial' && <p className="subtle">Unplugging or closing the site also undoes it.</p>}
      {preparing === 'failed' && <p className="file-error" role="alert">This module set could not be prepared for USB.</p>}
      {notice && <p className={notice.tone === 'success' ? 'success-note' : 'file-error'} role={notice.tone === 'success' ? 'status' : 'alert'}>{notice.text}</p>}
    </div>
    <div className="build-actions">
      {status === 'ready' && <button className="button button-primary" disabled={!prepareUpdate || (!moduleCount && !inventory?.moduleIds.length) || (!!changes && !changeCount(changes)) || preparing === 'busy'} onClick={() => void update()}><Icon name="download" size={16} />Load onto Octatrack</button>}
      {status === 'ready' && (!moduleCount && !inventory?.moduleIds.length ? <p className="export-note">Add at least one module from the library.</p> : !prepareUpdate && <p className="export-note">The browser can’t build updates yet.</p>)}
      {status === 'sending' && progress < 1 && <button className="button button-quiet" onClick={() => link.cancel()}>Cancel</button>}
      {(status === 'trial' || status === 'finishing') && <><button className="button button-primary" disabled={status === 'finishing'} onClick={() => void link.keep()}><Icon name="check" size={16} />Keep</button><button className="button button-quiet" disabled={status === 'finishing'} onClick={() => void link.undo()}>Undo</button></>}
      {status === 'ready' && <button className="text-button" onClick={() => setDownload(true)}>Download .bin instead</button>}
    </div>
  </section>
}
