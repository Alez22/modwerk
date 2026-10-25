import { Icon } from '../components/Icon'
import { DeviceArt } from '../devices/DeviceArt'
import { DeviceImage, PhotoCredit } from '../devices/DeviceImage'
import { deviceSteps, stepsDone, type DeviceArt as Art, type DeviceProfile, type StepState } from '../devices/registry'

// A device Modwerk has no profile for yet: a schematic box, and the road most firmware takes.
const GENERIC_ART: Art = { body: 'wide', encoders: 8, trigs: 16 }
const NEW_DEVICE_ROAD: ReturnType<typeof deviceSteps> = [
  { id: 'format', title: 'Firmware understood', description: 'How its update file is packed and checked.' },
  { id: 'boot', title: 'Changed build boots', description: 'A marked build starts, and the official update restores stock.' },
  { id: 'core', title: 'Base with hooks', description: 'Shared events, so several mods run together.' },
  { id: 'mods', title: 'First mods', description: 'Reviewed mods, sent over the same USB cable.' },
]
const STATE_LABELS: Record<StepState, string> = { done: 'Done', started: 'Started', open: 'Open' }

// Unlocking a machine, before its prompt: plug it in (read-only), the road from there to mods, and what it takes.
export function UnlockIntro({ device, name }: { device?: DeviceProfile; name: string }) {
  const road = device ? deviceSteps(device) : NEW_DEVICE_ROAD
  const reads = [['device', device ? name : 'maker · model'], ['os', device?.firmware?.releases.at(-1) ?? 'from its menu'], ['update', device?.firmware?.file ?? 'the maker’s file'], ['written', 'nothing']]
  return <section className="develop-intro unlock-intro" aria-label="How unlocking starts">
    <figure className="unlock-hero">
      <div className="unlock-hero-device">{device ? <DeviceImage device={device} eager /> : <DeviceArt art={GENERIC_ART} />}<span className="unlock-hero-label">{device ? name : 'Your device'}</span></div>
      <svg className="unlock-hero-cable" viewBox="0 0 120 24" fill="none" aria-hidden="true"><path d="M4 12H116" /><path className="is-flow" d="M4 12H116" /><circle cx="4" cy="12" r="3" /><circle cx="116" cy="12" r="3" /></svg>
      <div className="unlock-hero-agent">
        <span className="unlock-hero-command">› reading over USB</span>
        {reads.map(([key, value], i) => <span key={key} className={key === 'written' ? 'is-safe' : undefined} style={{ animationDelay: 0.5 + i * 0.45 + 's' }}><b>{key}</b>{value}</span>)}
        <span className="unlock-hero-label">Your coding agent</span>
      </div>
      <figcaption>Reading is safe. Nothing is written to the device until there is a tested way back to stock and your projects are backed up.</figcaption>
      {device && <PhotoCredit device={device} />}
    </figure>

    <div><h2>The road to mods <span className="subtle">{device ? stepsDone(device) + ' of ' + road.length + ' steps done' : 'The steps most firmware takes'}</span></h2>
      <ol className="unlock-road">
        <li className="is-now"><strong>Connect it over USB</strong><small>Your agent reads what the device reports. Everyone starts here.</small><span>Start</span></li>
        {road.map(step => { const state = device?.steps[step.id] ?? 'open'; return <li key={step.id} className={'is-' + state}><strong>{step.title}</strong><small>{step.description}</small><span>{STATE_LABELS[state]}</span></li> })}
      </ol>
    </div>

    <div><h2>What you need</h2>
      <ul className="develop-needs">
        <li><span className="develop-need-icon"><Icon name="sliders" /></span><strong>{device ? 'Your ' + device.name : 'The device'} and a cable</strong><small>USB, or a USB MIDI interface if it only has MIDI ports.</small></li>
        <li><span className="develop-need-icon"><Icon name="message" /></span><strong>A coding agent on your computer</strong><small>Claude Code or Codex. A chat assistant in the browser can help you set one up, but cannot do this work.</small></li>
        <li><span className="develop-need-icon"><Icon name="search" /></span><strong>Some programming experience</strong><small>The agent digs and explains each finding. You read what it found and decide when a test on the device is safe.</small></li>
      </ul>
      <p className="unlock-ask">Someone may already be on it: ask in the <a href="#forum?category=requests">forum</a> or on Discord first.</p>
    </div>
  </section>
}
