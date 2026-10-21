import { useState } from 'react'
import { Icon } from '../components/Icon'
import { DeviceImage, MachinePhotoCredits } from '../devices/DeviceImage'
import { DEVICE_STEPS } from '../devices/registry'
import type { Overview, OverviewKind, OverviewMachine } from './overview'
import './overview.css'

const FILTERS: { id: OverviewKind | 'all'; label: string }[] = [{ id: 'all', label: 'All' }, { id: 'mods', label: 'Mods available' }, { id: 'research', label: 'Research started' }, { id: 'open', label: 'No research yet' }]

// One short phrase per machine: its modules, or how far the research has come.
function stateLabel(machine: OverviewMachine) {
  if (machine.count) return machine.count + (machine.count === 1 ? ' module' : ' modules') + (machine.device.status === 'preview' ? ' in preview' : '')
  return machine.kind === 'research' ? machine.stepsDone + ' of ' + DEVICE_STEPS.length + ' steps' : 'No research yet'
}

// The landing page: every machine as one tile, and where the machines without mods begin, an invitation to build the first one.
export function OverviewPage({ overview }: { overview: Overview }) {
  const [filter, setFilter] = useState<OverviewKind | 'all'>('all')
  const count = (id: OverviewKind | 'all') => id === 'all' ? overview.machines.length : overview.machines.filter(machine => machine.kind === id).length
  const shown = overview.machines.filter(machine => filter === 'all' || machine.kind === filter)
  return <div className="overview-page">
    <header className="overview-heading">
      <div>
        <h1>Choose your machine</h1>
        <p><b>{overview.modules}</b> modules by <b>{overview.creators}</b> creators</p>
      </div>
      <div className="overview-chips" role="group" aria-label="Show machines">{FILTERS.map(item => <button key={item.id} type="button" className={'overview-chip is-' + item.id} aria-pressed={filter === item.id} onClick={() => setFilter(item.id)}>{item.id !== 'all' && <i aria-hidden="true" />}{item.label}<small>{count(item.id)}</small></button>)}</div>
    </header>
    <div className="machine-grid">
      {shown.filter(machine => machine.kind === 'mods').map(machine => <MachineTile key={machine.device.id} machine={machine} />)}
      {filter !== 'mods' && !!overview.withoutMods && <DevelopTile waiting={overview.withoutMods} />}
      {shown.filter(machine => machine.kind !== 'mods').map(machine => <MachineTile key={machine.device.id} machine={machine} />)}
    </div>
    <MachinePhotoCredits />
  </div>
}

function DevelopTile({ waiting }: { waiting: number }) {
  return <a className="overview-tile is-develop" href="#submit">
    <span className="overview-art">
      <span className="overview-waiting"><strong>{waiting}</strong><small>{waiting === 1 ? 'machine waits' : 'machines wait'} for a first mod</small></span>
      <span className="overview-pitch">No coding needed: a Claude or ChatGPT subscription and the starter prompt get you there.</span>
    </span>
    <div className="overview-tile-body">
      <div className="overview-tile-line"><h2 className="overview-tile-name">Start developing</h2><Icon name="plus" size={16} /></div>
    </div>
  </a>
}

function MachineTile({ machine }: { machine: OverviewMachine }) {
  const { device } = machine, variants = device.variants?.join(' · ')
  // Without mods the machine is locked: its picture starts the first mod, its name opens the research page.
  if (!machine.count) return <article className={'overview-tile is-locked is-' + machine.kind}>
    <a className="overview-art" href={machine.developHref} aria-label={'Start developing for the ' + device.name + (variants ? ' ' + variants : '')}>
      <DeviceImage device={device} />
      <span className="overview-lock" aria-hidden="true"><Icon name="lock" size={14} /></span>
      <span className="overview-cta" aria-hidden="true"><span><Icon name="plus" size={15} />Start developing</span></span>
    </a>
    <div className="overview-tile-body">
      <div className="overview-tile-line">
        <h2 className="overview-tile-name"><a href={machine.href}>{device.name}</a>{variants && <small>{variants}</small>}</h2>
        <span className="overview-state">{stateLabel(machine)}</span>
      </div>
      <span className="overview-ladder" aria-hidden="true">{DEVICE_STEPS.map(step => <i key={step.id} className={'is-' + device.steps[step.id]} />)}</span>
    </div>
  </article>
  return <a className={'overview-tile is-' + machine.kind + ' is-' + device.status} href={machine.href}>
    <span className="overview-art"><DeviceImage device={device} /></span>
    <div className="overview-tile-body">
      <div className="overview-tile-line">
        <h2 className="overview-tile-name">{device.name}{variants && <small>{variants}</small>}</h2>
        <span className="overview-state">{stateLabel(machine)}</span>
      </div>
      <span className="overview-mix" aria-hidden="true">{machine.categories.map(item => <span key={item.category} className={'is-' + item.category} style={{ flexGrow: item.count }} />)}</span>
    </div>
  </a>
}
