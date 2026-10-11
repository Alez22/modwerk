import { createContext, useContext, useEffect, useState, useSyncExternalStore } from 'react'
import type { Inventory } from '../config/inventory'
import type { OctatrackLink } from '../engine/elekloader/octatrack-link'

/** The site's one link to the Octatrack, or null where there is no USB workflow (phones, flag off). */
export const OctatrackLinkContext = createContext<OctatrackLink | null>(null)
const noSubscription = () => () => {}

/** The link's state for one view. The link listens for the unit while any view is mounted. */
export function useOctatrackLink(link: OctatrackLink) {
  useEffect(() => link.start(), [link])
  return useSyncExternalStore(link.subscribe, link.getState, link.getState)
}

/** Whether an Octatrack with the Modwerk base is connected; re-renders only when that changes. `given` is for the provider's own component. */
export function useOctatrackBase(given?: OctatrackLink | null) {
  const fromContext = useContext(OctatrackLinkContext), link = given === undefined ? fromContext : given
  const connected = () => !!link?.getState().identity?.canSubmit
  return useSyncExternalStore(link?.subscribe ?? noSubscription, connected, connected) // server renders (tests, prerender) need a snapshot too
}

/** What the connected unit has on it, read again whenever its module set changes; undefined while unknown,
 * loading or disconnected. Re-renders only when the unit or its set changes, so the whole app can use it. */
export function useInventory(link?: OctatrackLink | null, read?: () => Promise<Inventory>) {
  const unitKey = () => { const state = link?.getState(); return state?.status === 'ready' && state.identity?.canSubmit ? state.identity.base + '|' + (state.active ?? '') : '' }
  const key = useSyncExternalStore(link?.subscribe ?? noSubscription, unitKey, unitKey)
  const [inventory, setInventory] = useState<{ key: string; value: Inventory }>()
  useEffect(() => {
    if (!key || !read) return
    let live = true
    read().then(value => { if (live) setInventory({ key, value }) }, error => console.error(error))
    return () => { live = false }
  }, [key, read])
  return key && inventory?.key === key ? inventory.value : undefined
}
