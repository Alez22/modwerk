import { useSyncExternalStore } from 'react'
import type { Configuration } from '../config/workspace'
import { DeviceImage } from '../devices/DeviceImage'
import type { DeviceProfile } from '../devices/registry'
import type { LinkState, OctatrackLink } from '../engine/elekloader/octatrack-link'
import { Icon } from './Icon'

const noSubscription = () => () => {}
const LIVE: LinkState['status'][] = ['connecting', 'sending', 'testing', 'trial', 'finishing']

/**
 * The machine you work on, in the sidebar: its picture, its name and the module set you are editing,
 * leading to that set's page. With a USB link, a dot on the picture shows the connection
 * (connected, busy, not connected); without one (other machines, phones) there is no dot.
 */
export function InstrumentItem({ device, set, href, link, current }: { device: DeviceProfile; set?: Configuration; href: string; link?: OctatrackLink | null; current: boolean }) {
  const connection = useSyncExternalStore(link?.subscribe ?? noSubscription, () => {
    const state = link?.getState()
    return !state || state.status === 'unsupported' ? '' : LIVE.includes(state.status) ? 'busy' : state.identity?.canSubmit ? 'connected' : state.status === 'stock' ? 'stock' : 'off'
  }, () => '')
  const label = connection === 'connected' ? 'connected' : connection === 'busy' ? 'busy' : connection === 'stock' ? 'connected, original OS' : connection === 'off' ? 'not connected' : ''
  return <a className="sidebar-device instrument-item" href={href} aria-current={current ? 'page' : undefined} aria-label={device.name + (label ? ', ' + label : '') + (set ? ', ' + set.name : '')}>
    <span className="instrument-picture"><DeviceImage device={device} eager />{connection && <span className={'instrument-dot is-' + connection} title={device.name + ' ' + label} />}</span>
    <span><strong>{device.name}</strong><small>{set ? set.name : 'No module set yet'}</small></span>
    <Icon name="arrow" size={14} />
  </a>
}
