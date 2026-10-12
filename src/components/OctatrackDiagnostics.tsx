import { useEffect, useRef, useState, useSyncExternalStore } from 'react'
import type { OctatrackLink } from '../engine/elekloader/octatrack-link'
import type { Inventory } from '../config/inventory'
import { changeDiagnosticSharing, collectOctatrackDiagnostics, diagnosticPreference, subscribeDiagnosticPreference } from '../community/octatrack-diagnostics'
import { api } from '../community/api'
import { browserRequestsPrivacy } from '../community/usage'
import type { DiagnosticEntry } from '../community/octatrack-diagnostics-contract'

export function OctatrackDiagnosticsCollector({memberId,link,inventory}: {memberId:string;link:OctatrackLink|null;inventory?:Inventory}) {
  const latest = useRef(inventory)
  useEffect(()=>{latest.current=inventory},[inventory])
  useEffect(()=>collectOctatrackDiagnostics(memberId,link,()=>latest.current),[memberId,link])
  return null
}
export function OctatrackDiagnosticsSettings() {
  const state = useSyncExternalStore(subscribeDiagnosticPreference,diagnosticPreference,diagnosticPreference)
  const privacy = browserRequestsPrivacy()
  return <section className="octatrack-diagnostics" aria-label="Beta diagnostics">
    <h3>Help me find beta bugs</h3>
    <p>Please keep this page open and your Octatrack connected while you try the beta.</p>
    <label className="load-check"><input type="checkbox" checked={state.enabled} disabled={!state.ready || state.busy || privacy} onChange={event=>void changeDiagnosticSharing(event.target.checked)}/>Automatically share technical diagnostics</label>
    <p className="link-hint">Optional. I use base and module identities, sync stages, failure codes and numeric performance readings to investigate bugs. They’re linked to your account, private to site administrators and kept for up to 30 days. This choice applies to your signed-in beta sessions for 90 days.</p>
    <details><summary>What is shared</summary>
      <p>Base and running-set hashes, package hashes and sizes, installed module IDs with this site’s catalogue versions, connection and sync events, self-test results, load peaks and loader refusal codes. Status is read at most every 30 seconds while the connection is idle. The catalogue version is not a claim about an older installed package.</p>
      <p>No firmware, samples, audio, project contents, set names, device serial numbers, raw memory or crash dumps. Diagnostics use the site’s Cloudflare service and aren’t posted to GitHub or shared with module authors. <a href="#privacy" target="_blank" rel="noreferrer">Privacy and your rights</a>.</p>
      <p>Consent is optional under GDPR Article 6(1)(a). You can stop sharing and delete these diagnostics below; it won’t affect beta access or syncing. Access and export are also available through your account data download. Older entries are hidden after 30 days and deleted by hourly cleanup; storage is capped at the latest 1,000 entries per account.</p>
      <p>Separate daily counts of sync starts, successful Keeps, Undos and failures carry no account, device, module or session identifier. These counts last 30 days and follow your <a href="#privacy" target="_blank" rel="noreferrer">usage-count preference</a> and your browser’s privacy signals.</p>
    </details>
    {state.ready && (state.hasChoice || state.error) && <button className="text-button" disabled={state.busy} onClick={()=>void changeDiagnosticSharing(false)}>Stop sharing and delete</button>}
    {state.notice && <p className="link-hint" role="status">{state.notice}</p>}
    {state.lastSent && <p className="link-hint" role="status">Last diagnostic received: {new Date(state.lastSent).toLocaleTimeString()}</p>}
    {privacy && <p className="link-hint">Your browser requests privacy, so automatic diagnostics stay off here.</p>}
    {state.error && <p className="file-error" role="alert">{state.error}</p>}
  </section>
}
export function OctatrackDiagnosticsAdmin() {
  const [data,setData] = useState<{events:DiagnosticEntry[];counts:{day:string;event:string;count:number}[]}>(),[error,setError]=useState('')
  async function load() { try {setData(await api('/admin/octatrack/diagnostics'));setError('')} catch(error) {setError(error instanceof Error?error.message:'Couldn’t read diagnostics.')} }
  useEffect(()=>{let cancelled=false;void api<{events:DiagnosticEntry[];counts:{day:string;event:string;count:number}[]}>('/admin/octatrack/diagnostics').then(value=>{if(!cancelled)setData(value)}).catch(error=>{if(!cancelled)setError(error instanceof Error?error.message:'Couldn’t read diagnostics.')});return()=>{cancelled=true}},[])
  return <section className="configuration-section"><div className="section-title"><h2>Octatrack beta diagnostics</h2><button className="button button-quiet" onClick={()=>void load()}>Refresh</button></div>
    <p className="service-note">Private opt-in records from the last 30 days; newest 100 shown. A record is an observation, not a confirmed bug. Daily action counts include testers who leave technical sharing off.</p>
    {data && <><details><summary>Daily sync counts</summary>{data.counts.map(row=><p key={row.day+row.event}>{row.day} · {row.event}: {row.count}</p>)}</details>{data.events.length ? data.events.map(entry=><details key={entry.eventId+entry.username}><summary>{entry.createdAt} · @{entry.username} · {entry.data.event}</summary><pre className="diagnostic-json">{JSON.stringify(entry.data,null,2)}</pre></details>) : <p>No shared diagnostics yet.</p>}</>}
    {error && <p className="file-error" role="alert">{error}</p>}
  </section>
}
