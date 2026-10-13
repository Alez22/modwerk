import { useId } from 'react'
import type { OctatrackLink } from '../engine/elekloader/octatrack-link'
import type { LoadReading } from '../engine/elekloader/upload-wire'
import { useOctatrackLoad } from '../hooks/useOctatrackLoad'
import { loadPath } from '../config/octatrack-load'
import './octatrack-load.css'

const percent = (value: number | null | undefined) => value == null ? '—' : `${(value / 10).toFixed(1)}%`
function Meter({ title, value, peak }: { title: string; value?: number | null; peak?: number | null }) {
  return <div className="load-meter"><span>{title}</span><strong>{percent(value)}</strong>{value == null ? <div className="load-meter-unavailable" aria-hidden="true" /> : <meter min={0} max={1000} value={value} aria-label={`${title} load`} aria-valuetext={percent(value)} />}{peak != null && <small>Recent device peak {percent(peak)}</small>}</div>
}
export function OctatrackLoad({ link, active }: { link: OctatrackLink | null; active: boolean }) {
  const { points, notice, clear, now, ready, visible } = useOctatrackLoad(link, active), id = useId()
  const last = points.at(-1)
  const latest = active && ready && visible && last && now - last.at <= 6000 ? last.reading : null
  const observed = points.filter(point => point.reading)
  const series: { key: keyof Pick<LoadReading, 'cpu' | 'tracks1to4' | 'tracks5to8'>; title: string; className: string }[] = [
    { key: 'cpu', title: 'CPU', className: 'load-cpu' }, { key: 'tracks1to4', title: 'Tracks 1–4', className: 'load-core1' }, { key: 'tracks5to8', title: 'Tracks 5–8', className: 'load-core0' },
  ]
  return <section className="octatrack-load" aria-labelledby={`${id}-title`}>
    <div className="load-heading"><div><h2 id={`${id}-title`}>Load <span className="samples-wip">Beta</span></h2><p>Current hardware meter windows and the last five minutes.</p></div><button type="button" className="button button-quiet" disabled={!points.length} onClick={clear}>Clear history</button></div>
    <div className="load-meters"><Meter title="CPU" value={latest?.cpu} /><Meter title="Tracks 1–4 · DSP" value={latest?.tracks1to4} peak={latest?.peak1to4} /><Meter title="Tracks 5–8 · DSP" value={latest?.tracks5to8} peak={latest?.peak5to8} /></div>
    <figure className="load-chart"><figcaption>Load over time · 0–100%</figcaption><div className="load-plot"><div className="load-y-labels" aria-hidden="true"><span>100%</span><span>0%</span></div><svg viewBox="0 0 600 120" preserveAspectRatio="none" role="img" aria-label="CPU and DSP load over the last five minutes. Missing readings appear as gaps."><path className="load-grid" d="M0 0H600 M0 60H600 M0 120H600" />{series.map(item => <path key={item.key} className={item.className} d={loadPath(points, item.key, now)} fill="none" />)}</svg></div><div className="load-time-labels"><span>5 min ago</span><span>Now</span></div><div className="load-legend">{series.map(item => <span key={item.key} className={item.className}>{item.title}</span>)}</div>
      <details><summary>History readings ({observed.length})</summary><div className="load-table"><table><thead><tr><th>Time</th><th>CPU</th><th>Tracks 1–4</th><th>Tracks 5–8</th></tr></thead><tbody>{points.map(point => <tr key={point.at}><td>{new Date(point.at).toLocaleTimeString()}</td><td>{percent(point.reading?.cpu)}</td><td>{percent(point.reading?.tracks1to4)}</td><td>{percent(point.reading?.tracks5to8)}</td></tr>)}</tbody></table></div></details>
    </figure>
    <p className="subtle" role="status">{!link?.getState().identity?.canSubmit ? 'Connect your Octatrack over USB to see live load.' : notice || (latest ? 'Updates every two seconds while this tab is visible. History stays in this session.' : 'Waiting for live load. USB sync takes priority.')}</p>
  </section>
}
