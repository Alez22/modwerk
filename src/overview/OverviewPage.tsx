import { useState } from 'react'
import { Icon } from '../components/Icon'
import { DeviceImage, MachinePhotoCredits } from '../devices/DeviceImage'
import { DEVICE_STEPS, STATUS_LABELS } from '../devices/registry'
import { issueRepository } from '../community/report-context'
import { DEVELOP_PITCH, type Overview, type OverviewKind, type OverviewMachine } from './overview'
import './overview.css'

const plural = (count: number, word: string) => count + ' ' + word + (count === 1 ? '' : 's')
const variants = (machine: OverviewMachine) => machine.device.variants?.join(' · ')
const developLabel = (machine: OverviewMachine) => machine.coreReady ? 'Build the first mod' : 'Start developing'
function recentLabel(machine: OverviewMachine, shown = 3) { return machine.recent.slice(0, shown).join(' · ') + (machine.count > shown ? ' +' + (machine.count - shown) : '') }

const FILTERS: { id: OverviewKind | 'all'; label: string }[] = [{ id: 'all', label: 'All' }, { id: 'mods', label: 'Mods available' }, { id: 'research', label: 'Research started' }, { id: 'open', label: 'No research yet' }]

// The landing page: every machine, how many modules it has, and an invitation to start one where there are none.
export function OverviewPage({ overview }: { overview: Overview }) {
  const [filter, setFilter] = useState<OverviewKind | 'all'>('all')
  const count = (id: OverviewKind | 'all') => id === 'all' ? overview.machines.length : overview.machines.filter(machine => machine.kind === id).length
  const shown = overview.machines.filter(machine => filter === 'all' || machine.kind === filter)
  return <div className="overview-page">
    <header className="overview-heading">
      <div>
        <h1>Choose your machine</h1>
        <p><b>{overview.modules}</b> modules by <b>{overview.creators}</b> creators for Elektron instruments</p>
      </div>
      <div className="overview-chips" role="group" aria-label="Show machines">{FILTERS.map(item => <button key={item.id} type="button" className={'overview-chip is-' + item.id} aria-pressed={filter === item.id} onClick={() => setFilter(item.id)}>{item.id !== 'all' && <i aria-hidden="true" />}{item.label}<small>{count(item.id)}</small></button>)}</div>
    </header>
    <div className="overview-grid">{shown.map(machine => <MachineTile key={machine.device.id} machine={machine} />)}</div>
    <section className="overview-band" aria-labelledby="overview-band-title">
      <div className="overview-band-copy">
        <h2 id="overview-band-title">{plural(overview.withoutMods, 'machine')} {overview.withoutMods === 1 ? 'is' : 'are'} waiting for a first mod</h2>
        <p>{DEVELOP_PITCH}</p>
      </div>
      <div className="overview-actions">
        <a className="button button-primary" href="#submit"><Icon name="plus" size={16} />Start developing</a>
        <a className="button button-quiet" href={issueRepository() + '/blob/main/docs/ADD_A_MACHINE.md'} target="_blank" rel="noreferrer">Machine guide<Icon name="external" size={14} /></a>
        <a className="button button-quiet" href="#forum"><Icon name="message" size={16} />Ask in the forum</a>
      </div>
    </section>
    <MachinePhotoCredits />
  </div>
}

function MachineTile({ machine }: { machine: OverviewMachine }) {
  const { device } = machine, mods = machine.count > 0, title = device.name + (variants(machine) ? ' ' + variants(machine) : '')
  return <article className={'overview-tile is-' + machine.kind}>
    <a className="overview-art" href={machine.href} aria-label={mods ? 'Open the ' + title + ' library, ' + plural(machine.count, 'module') : title + ': no mods yet, see how to start'}>
      <DeviceImage device={device} />
      <span className={'overview-status is-' + device.status}>{STATUS_LABELS[device.status]}</span>
      {mods && <span className="overview-count"><strong>{machine.count}</strong><small>{machine.count === 1 ? 'module' : 'modules'}</small></span>}
    </a>
    <div className="overview-tile-body">
      <h2 className="overview-tile-title"><a href={machine.href}>{device.name}</a>{variants(machine) && <small>{variants(machine)}</small>}</h2>
      <p className="overview-summary">{device.summary}</p>
      {mods ? <>
        <span className="overview-mix" aria-hidden="true">{machine.categories.map(item => <span key={item.category} className={'is-' + item.category} style={{ flexGrow: item.count }} />)}</span>
        <ul className="overview-legend" aria-label="Modules by category">{machine.categories.map(item => <li key={item.category}><i className={'is-' + item.category} aria-hidden="true" />{item.label} <b>{item.count}</b></li>)}</ul>
        <div className="overview-tile-foot"><span className="overview-meta">{recentLabel(machine)}</span><a className="overview-open" href={machine.href}>Open library<Icon name="arrow" size={14} /></a></div>
      </> : <>
        <span className="overview-ladder" aria-hidden="true">{DEVICE_STEPS.map(step => <i key={step.id} className={'is-' + device.steps[step.id]} />)}</span>
        <p className="overview-progress"><b>{machine.stepsDone} of {DEVICE_STEPS.length} steps</b>{machine.next && <span>Next: {machine.next.title}{machine.next.started ? ' (started)' : ''}</span>}</p>
        <div className="overview-tile-foot"><a className="overview-develop" href={machine.developHref}><Icon name="plus" size={14} />{developLabel(machine)}</a></div>
      </>}
    </div>
  </article>
}
