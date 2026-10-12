import { useSyncExternalStore } from 'react'
import { lastInventory, type Inventory } from '../config/inventory'
import type { Configuration } from '../config/workspace'
import { DeviceImage } from '../devices/DeviceImage'
import type { DeviceProfile } from '../devices/registry'
import type { LinkState, OctatrackLink } from '../engine/elekloader/octatrack-link'
import { Icon } from './Icon'

const noSubscription = () => () => {}
const LIVE: LinkState['status'][] = ['connecting', 'sending', 'testing', 'trial', 'finishing']
const modules = (n: number) => n + (n === 1 ? ' module' : ' modules')

/**
 * The machine you work on, in the sidebar. With a USB link (the Octatrack) it shows the unit, not a set: what is on
 * it, or what this browser read when it was last connected, with a dot for the connection, and leads to the hub.
 * Without one (other machines, phones) it shows the module set you are editing and leads to its page.
 */
export function InstrumentItem({ device, set, href, link, current, inventory }: { device: DeviceProfile; set?: Configuration; href: string; link?: OctatrackLink | null; current: boolean; inventory?: Inventory }) {
  const status = useSyncExternalStore(link?.subscribe ?? noSubscription, () => {
    const state = link?.getState()
    return !state ? '' : state.identity?.canSubmit && state.status === 'ready' ? 'connected' : state.status
  }, () => '')
  const connection = !status || status === 'unsupported' ? '' : LIVE.includes(status as LinkState['status']) ? 'busy' : status === 'connected' || status === 'stock' ? status : 'off'
  const last = connection === 'off' || status === 'unsupported' ? lastInventory() : undefined
  const unit = status === 'connecting' ? 'Connecting…' : connection === 'busy' ? 'Loading…'
    : status === 'connected' ? inventory ? inventory.moduleIds.length ? modules(inventory.moduleIds.length) + ' on it' : 'No modules on it' : 'Connected'
    : status === 'stock' ? 'Original OS: install the base' : status === 'busy' ? 'In use by another tab or app' : last ? 'Last seen: ' + modules(last.moduleIds.length) : 'Not connected'
  const detail = link ? unit : set ? set.name : 'No module set yet'
  return <a className="sidebar-device instrument-item" href={href} aria-current={current ? 'page' : undefined} aria-label={device.name + ', ' + detail}>
    <span className="instrument-picture"><DeviceImage device={device} eager />{connection && <span className={'instrument-dot is-' + connection} title={device.name + ': ' + unit} />}</span>
    <span><strong>{device.name}</strong><small>{detail}</small></span>
    <Icon name="arrow" size={14} />
  </a>
}
