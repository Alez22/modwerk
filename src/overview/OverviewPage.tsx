import { useState, type ReactNode } from 'react'
import { Icon } from '../components/Icon'
import { DeviceImage, MachinePhotoCredits } from '../devices/DeviceImage'
import { DEVICES, DEVICE_STEPS, STATUS_LABELS } from '../devices/registry'
import { issueRepository } from '../community/report-context'
import { DEVELOP_PITCH, type Overview, type OverviewKind, type OverviewLayout, type OverviewMachine } from './overview'
import './overview.css'

const plural = (count: number, word: string) => count + ' ' + word + (count === 1 ? '' : 's')
const names = (items: string[]) => items.length > 1 ? items.slice(0, -1).join(', ') + ' and ' + items[items.length - 1] : items[0] ?? ''
const variants = (machine: OverviewMachine) => machine.device.variants?.join(' · ')
const developLabel = (machine: OverviewMachine) => machine.coreReady ? 'Build the first mod' : 'Start developing'
function recentLabel(machine: OverviewMachine, shown = 3) { return machine.recent.slice(0, shown).join(' · ') + (machine.count > shown ? ' +' + (machine.count - shown) : '') }
function progressLabel(machine: OverviewMachine) { return machine.stepsDone + ' of ' + DEVICE_STEPS.length + ' steps' + (machine.coreReady ? ' · core ready' : '') }

// The landing page: every machine, how many modules it has, and an invitation to start one where there are none.
// Three layouts are under review (grid, spotlight, bento); the preview switch picks one.
export function OverviewPage({ overview, layout }: { overview: Overview; layout: OverviewLayout }) {
  return <div className={'overview-page is-' + layout}>
    {layout === 'spotlight' ? <SpotlightLayout overview={overview} /> : layout === 'bento' ? <BentoLayout overview={overview} /> : <GridLayout overview={overview} />}
    <MachinePhotoCredits />
  </div>
}

function Stats({ overview }: { overview: Overview }) {
  return <dl className="overview-stats">
    <div><dt>modules</dt><dd>{overview.modules}</dd></div>
    <div><dt>machines with mods</dt><dd>{overview.withMods}</dd></div>
    <div><dt>creators</dt><dd>{overview.creators}</dd></div>
    <div className="is-call"><dt>machines without mods</dt><dd>{overview.withoutMods}</dd></div>
  </dl>
}

function CategoryMix({ machine }: { machine: OverviewMachine }) {
  return <>
    <span className="overview-mix" aria-hidden="true">{machine.categories.map(item => <span key={item.category} className={'is-' + item.category} style={{ flexGrow: item.count }} />)}</span>
    <ul className="overview-legend" aria-label="Modules by category">{machine.categories.map(item => <li key={item.category}><i className={'is-' + item.category} aria-hidden="true" />{item.label} <b>{item.count}</b></li>)}</ul>
  </>
}

function Ladder({ machine }: { machine: OverviewMachine }) {
  return <span className="overview-ladder" aria-hidden="true">{DEVICE_STEPS.map(step => <i key={step.id} className={'is-' + machine.device.steps[step.id]} />)}</span>
}

function Progress({ machine }: { machine: OverviewMachine }) {
  return <div className="overview-progress"><Ladder machine={machine} /><span className="overview-progress-label"><b>{progressLabel(machine)}</b>{machine.next && <span>Next: {machine.next.title}{machine.next.started ? ' (started)' : ''}</span>}</span></div>
}

function Needs() {
  return <ul className="overview-needs" aria-label="What you need">
    <li><Icon name="check" size={14} />No coding experience needed</li>
    <li><Icon name="check" size={14} />A Claude or ChatGPT subscription</li>
    <li><Icon name="check" size={14} />A free GitHub account</li>
  </ul>
}

function DevelopActions({ guide = true }: { guide?: boolean }) {
  return <div className="overview-actions">
    <a className="button button-primary" href="#submit"><Icon name="plus" size={16} />Start developing</a>
    {guide && <a className="button button-quiet" href={issueRepository() + '/blob/main/docs/ADD_A_MACHINE.md'} target="_blank" rel="noreferrer">Read the machine guide<Icon name="external" size={14} /></a>}
    <a className="button button-quiet" href="#forum"><Icon name="message" size={16} />Ask in the forum</a>
  </div>
}

// A: every machine as an equal tile; machines without mods carry their own Start developing button.
function GridLayout({ overview }: { overview: Overview }) {
  const [filter, setFilter] = useState<OverviewKind | 'all'>('all')
  const filters: { id: OverviewKind | 'all'; label: string }[] = [{ id: 'all', label: 'All machines' }, { id: 'mods', label: 'Mods available' }, { id: 'research', label: 'Research started' }, { id: 'open', label: 'No research yet' }]
  const shown = overview.machines.filter(machine => filter === 'all' || machine.kind === filter)
  return <>
    <header className="page-heading overview-heading">
      <div><p className="page-kicker">MODWERK / OVERVIEW</p><h1>Choose your machine</h1><p>Custom firmware modules for Elektron instruments. Open a machine to browse its library and build firmware in your browser, or help bring the first mods to the next one.</p></div>
      <Stats overview={overview} />
    </header>
    <div className="overview-filters">
      <div className="overview-chips" role="group" aria-label="Show machines">{filters.map(item => <button key={item.id} type="button" className={'overview-chip is-' + item.id} aria-pressed={filter === item.id} onClick={() => setFilter(item.id)}><i aria-hidden="true" />{item.label}<small>{item.id === 'all' ? overview.machines.length : overview.machines.filter(machine => machine.kind === item.id).length}</small></button>)}</div>
      <span className="subtle">Machines with mods first, then by research progress</span>
    </div>
    <div className="overview-grid">{shown.map(machine => <MachineTile key={machine.device.id} machine={machine} />)}</div>
    <section className="overview-band" aria-labelledby="overview-band-title">
      <span className="overview-band-number" aria-hidden="true">{overview.withoutMods}</span>
      <div className="overview-band-copy">
        <p className="overview-kicker">OPEN FOR DEVELOPMENT</p>
        <h2 id="overview-band-title">{overview.withoutMods} machines are waiting for their first mod. Make it yours.</h2>
        <p>You don’t need to be a programmer. With a Claude or ChatGPT subscription, the starter prompt sets you up and guides you through every step, from describing your idea to a reviewed release. Start with a module for a machine that already has mods, or help open a new one.</p>
        <Needs />
        <DevelopActions />
      </div>
    </section>
  </>
}

function MachineTile({ machine }: { machine: OverviewMachine }) {
  const { device } = machine, mods = machine.count > 0, title = device.name + (variants(machine) ? ' ' + variants(machine) : '')
  return <article className={'overview-tile is-' + machine.kind}>
    <a className="overview-art" href={machine.href} aria-label={mods ? 'Open the ' + title + ' library, ' + plural(machine.count, 'module') : title + ': no mods yet, see how to start'}>
      <DeviceImage device={device} />
      <span className={'overview-status is-' + device.status}>{STATUS_LABELS[device.status]}</span>
      {mods ? <span className="overview-count"><strong>{machine.count}</strong><small>{machine.count === 1 ? 'module' : 'modules'}</small></span> : <span className="overview-wanted"><Icon name="plus" size={12} />First mod wanted</span>}
    </a>
    <div className="overview-tile-body">
      <h2 className="overview-tile-title"><a href={machine.href}>{device.name}</a>{variants(machine) && <small>{variants(machine)}</small>}</h2>
      <p className="overview-summary">{device.summary}</p>
      {mods ? <><CategoryMix machine={machine} /><div className="overview-tile-foot"><span className="overview-recent">{recentLabel(machine)}</span><a className="overview-open" href={machine.href}>Open library<Icon name="arrow" size={14} /></a></div></>
        : <><Progress machine={machine} /><a className="overview-develop" href={machine.developHref}><Icon name="plus" size={16} />{developLabel(machine)}</a></>}
    </div>
  </article>
}

// B: the machines with mods in the spotlight, a Start developing band in the middle, then the machines waiting for a first mod.
function SpotlightLayout({ overview }: { overview: Overview }) {
  const modded = overview.machines.filter(machine => machine.kind === 'mods'), research = overview.machines.filter(machine => machine.kind === 'research'), open = overview.machines.filter(machine => machine.kind === 'open')
  const coreReady = research.filter(machine => machine.coreReady)
  const most = Math.max(1, ...overview.reached.map(step => step.count))
  return <>
    <section className="overview-hero" aria-labelledby="overview-hero-title">
      <div className="overview-hero-copy">
        <p className="page-kicker">MODWERK / OVERVIEW</p>
        <h1 id="overview-hero-title">New tricks for your <span>Elektron</span> machine.</h1>
        <p>{overview.modules} modules for {names(modded.map(machine => machine.device.name))}, made by {plural(overview.creators, 'creator')}. Pick a machine, choose your modules and build the firmware in your browser. Your firmware stays on your device.</p>
        <div className="overview-actions">
          <a className="button button-primary" href="#all"><Icon name="grid" size={16} />Browse all {overview.modules} modules</a>
          <a className="button overview-button-develop" href="#submit"><Icon name="plus" size={16} />Start developing</a>
        </div>
        <p className="overview-hero-note"><Icon name="plus" size={14} />Want to build one? No coding needed: a Claude or ChatGPT subscription and the starter prompt are enough.</p>
      </div>
      <Stats overview={overview} />
    </section>

    <div className="overview-section-head"><h2>Mods available <small>{plural(modded.length, 'machine')} · {plural(overview.modules, 'module')}</small></h2><a href="#all">Browse every module<Icon name="arrow" size={14} /></a></div>
    <div className="overview-features">{modded.map((machine, index) => <FeatureCard key={machine.device.id} machine={machine} big={index === 0} />)}</div>

    <section className="overview-band is-warm" aria-labelledby="overview-band-title">
      <div className="overview-band-copy">
        <p className="overview-kicker">OPEN FOR DEVELOPMENT</p>
        <h2 id="overview-band-title">{overview.withoutMods} machines have no mods yet. Pick one and be first.</h2>
        <p>{DEVELOP_PITCH} Every machine follows the same road to its first mod{coreReady.length ? <>, and {names(coreReady.map(machine => machine.device.name + (variants(machine) ? ' ' + variants(machine) : '')))} already {coreReady.length === 1 ? 'has' : 'have'} a core with hooks</> : null}.</p>
        <Needs />
        <DevelopActions />
      </div>
      <div className="overview-funnel">
        <p className="overview-funnel-title">Road to the first mod <span>machines without mods, by step done</span></p>
        <ol>{overview.reached.map((step, index) => {
          const last = index === overview.reached.length - 1 && !step.count
          return <li key={step.title}><span className={'overview-funnel-bar' + (last ? ' is-you' : '')} aria-hidden="true">{last ? 'YOU?' : <span style={{ height: step.count / most * 100 + '%' }} />}</span><strong>{step.count}</strong><small>{step.title}</small></li>
        })}</ol>
      </div>
    </section>

    {!!research.length && <><div className="overview-section-head"><h2>Closest to a first mod <small>research started</small></h2></div>
      <div className="overview-close">{research.map(machine => <article key={machine.device.id} className="overview-close-card">
        <a className="overview-thumb" href={machine.href} aria-label={machine.device.name + (variants(machine) ? ' ' + variants(machine) : '') + ': ' + progressLabel(machine)}><DeviceImage device={machine.device} /></a>
        <div className="overview-close-body">
          <h3><a href={machine.href}>{machine.device.name}</a>{variants(machine) && <small>{variants(machine)}</small>}</h3>
          <Progress machine={machine} />
          <a className="overview-develop-link" href={machine.developHref}><Icon name="plus" size={14} />{developLabel(machine)}</a>
        </div>
      </article>)}</div></>}

    {!!open.length && <><div className="overview-section-head"><h2>Not explored yet <small>no public research</small></h2></div>
      <div className="overview-open-grid">{open.map(machine => <a key={machine.device.id} className="overview-open-card" href={machine.href}>
        <span className="overview-open-art"><DeviceImage device={machine.device} /></span>
        <span className="overview-open-body"><strong>{machine.device.name}{variants(machine) && <small>{variants(machine)}</small>}</strong><span className="overview-develop-link">Be the first<Icon name="arrow" size={13} /></span></span>
      </a>)}</div></>}
  </>
}

function FeatureCard({ machine, big }: { machine: OverviewMachine; big: boolean }) {
  const { device } = machine, shown = big ? 8 : 3
  return <article className={'overview-feature' + (big ? ' is-big' : ' is-row') + ' is-' + device.status}>
    <a className="overview-feature-art" href={machine.href} aria-label={'Open the ' + device.name + ' library, ' + plural(machine.count, 'module')}><DeviceImage device={device} /><span className={'overview-status is-' + device.status}>{STATUS_LABELS[device.status]}</span></a>
    <div className="overview-feature-body">
      <div className="overview-feature-title"><h3><a href={machine.href}>{device.name}</a><small>{[variants(machine), big && device.firmware ? 'OS ' + device.firmware.releases.join(' / ') : ''].filter(Boolean).join(' · ')}</small></h3><span className="overview-feature-count"><strong>{machine.count}</strong><small>{machine.count === 1 ? 'module' : 'modules'}</small></span></div>
      {big && <p className="overview-summary">{device.summary}</p>}
      <CategoryMix machine={machine} />
      <ul className="overview-names" aria-label={'Recently updated ' + device.name + ' modules'}>{machine.recent.slice(0, shown).map(name => <li key={name}>{name}</li>)}{machine.count > shown && <li className="is-more">+{machine.count - shown} more</li>}</ul>
      <div className="overview-feature-foot"><span className="overview-recent">{plural(machine.creators, 'creator')}</span><a className="overview-open" href={machine.href}>{big ? 'Open the ' + device.name + ' library' : 'Open library'}<Icon name="arrow" size={15} /></a></div>
    </div>
  </article>
}

// C: one grid of tiles in several sizes, with the Start developing tile in the middle of it.
function BentoLayout({ overview }: { overview: Overview }) {
  const modded = overview.machines.filter(machine => machine.kind === 'mods'), waiting = overview.machines.filter(machine => machine.kind !== 'mods')
  const totals = overview.machines.flatMap(machine => machine.categories).reduce<Record<string, number>>((sum, item) => ({ ...sum, [item.category]: (sum[item.category] ?? 0) + item.count }), {})
  return <>
    <header className="page-heading overview-heading">
      <div><p className="page-kicker">MODWERK / OVERVIEW</p><h1>{DEVICES.length} machines. {overview.modules} modules. <span>Room for yours.</span></h1><p>Open a machine to browse its mods and build its firmware in your browser. No mods for yours yet? Start the first one, no coding experience needed.</p></div>
      <ul className="overview-key" aria-label="Status key"><li className="is-available">Mods available</li><li className="is-preview">In preview</li><li className="is-research">Research started</li><li className="is-open">No research yet</li></ul>
    </header>
    <div className="overview-bento">
      {modded.map((machine, index) => <BentoTile key={machine.device.id} machine={machine} size={index === 0 ? 'is-big' : index === 1 ? 'is-wide' : 'is-single'}>
        <span className="overview-bento-number"><strong>{machine.count}</strong><small>{machine.count === 1 ? 'module' : 'modules'}{machine.creators ? ' · ' + plural(machine.creators, 'creator') : ''}</small></span>
        {index === 0 && <ul className="overview-bento-categories" aria-label="Modules by category">{machine.categories.map(item => <li key={item.category}>{item.label}<i className={'is-' + item.category} aria-hidden="true" /><b>{item.count}</b></li>)}</ul>}
      </BentoTile>)}
      <a className="overview-bento-tile is-all" href="#all">
        <span className="overview-bento-name"><strong>Every module</strong><span className="overview-dot is-available">{plural(overview.withMods, 'machine')}</span></span>
        <span>
          <span className="overview-bento-number"><strong>{overview.modules}</strong><small>modules · {plural(overview.creators, 'creator')}</small></span>
          <span className="overview-mix" aria-hidden="true">{Object.entries(totals).sort((a, b) => b[1] - a[1]).map(([category, count]) => <span key={category} className={'is-' + category} style={{ flexGrow: count }} />)}</span>
          <span className="overview-open">Browse the library<Icon name="arrow" size={14} /></span>
        </span>
      </a>
      <a className="overview-bento-tile is-develop" href="#submit">
        <span className="overview-bento-row"><span className="overview-kicker">OPEN FOR DEVELOPMENT</span><span className="overview-slots" aria-hidden="true">{waiting.map((machine, index) => <i key={machine.device.id} className={index ? undefined : 'is-you'} />)}</span></span>
        <span className="overview-bento-row">
          <span><strong className="overview-develop-title">{overview.withoutMods} machines. Zero mods. Be first.</strong><span className="overview-develop-copy">No coding needed: with a Claude or ChatGPT subscription, the starter prompt guides you through every step.</span></span>
          <span className="overview-develop-go"><Icon name="plus" size={16} />Start developing</span>
        </span>
      </a>
      {waiting.map(machine => <BentoTile key={machine.device.id} machine={machine} size="is-single">
        <span className="overview-bento-foot"><Ladder machine={machine} /><span><span>{machine.kind === 'research' ? progressLabel(machine) : 'No mods yet'}</span><b>{developLabel(machine)}<Icon name="arrow" size={12} /></b></span></span>
      </BentoTile>)}
    </div>
  </>
}

function BentoTile({ machine, size, children }: { machine: OverviewMachine; size: string; children: ReactNode }) {
  const { device } = machine, mods = machine.count > 0, title = device.name + (variants(machine) ? ' ' + variants(machine) : '')
  return <a className={'overview-bento-tile ' + size + ' is-' + machine.kind} href={machine.href} aria-label={mods ? title + ': ' + plural(machine.count, 'module') + ', open the library' : title + ': no mods yet, ' + (machine.kind === 'research' ? progressLabel(machine) : 'no research yet') + '. See how to start.'}>
    <span className="overview-bento-top"><span className="overview-bento-name"><strong>{device.name}{variants(machine) && <small>{variants(machine)}</small>}</strong><span className={'overview-dot is-' + device.status}>{STATUS_LABELS[device.status]}</span></span><span className={mods ? 'overview-go' : 'overview-plus'}><Icon name={mods ? 'arrow' : 'plus'} size={15} /></span></span>
    <span className="overview-bento-art"><DeviceImage device={device} /></span>
    {children}
  </a>
}
