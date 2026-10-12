import type { InventoryTarget } from './inventory'

const INSTALL = 'modwerk.octatrack.pending-base', SYNC = 'modwerk.octatrack.last-sync'
export interface PendingBase { sha256: string; previousBase?: string }
export interface SuccessfulSync extends InventoryTarget { base: string; active: string; at: string }
const hash = (value: unknown): value is string => typeof value === 'string' && /^[a-f0-9]{64}$/.test(value)

/** Keep the installer resumable within this tab without treating a download as an installation. */
export function pendingBaseInstall(): PendingBase | undefined {
  try {
    const value = JSON.parse(sessionStorage.getItem(INSTALL) ?? 'null')
    return value && hash(value.sha256) && (value.previousBase === undefined || hash(value.previousBase)) ? value : undefined
  } catch { return undefined }
}
export function waitForBaseInstall(sha256: string, previousBase?: string) {
  try { sessionStorage.setItem(INSTALL, JSON.stringify({ sha256, previousBase })) } catch { /* this visit still waits */ }
}
export function finishBaseInstall() {
  try { sessionStorage.removeItem(INSTALL) } catch { /* storage is optional */ }
}

/** Record only an acknowledged Keep with a successful save, never a download, trial or Undo. */
export function rememberSuccessfulSync(value: SuccessfulSync) {
  try { localStorage.setItem(SYNC, JSON.stringify(value)) } catch { /* storage is optional */ }
}
export function lastSuccessfulSync(base?: string): SuccessfulSync | undefined {
  try {
    const value = JSON.parse(localStorage.getItem(SYNC) ?? 'null')
    return value && hash(value.base) && hash(value.active) && (!base || value.base === base) && typeof value.name === 'string'
      && Array.isArray(value.moduleIds) && value.moduleIds.every((id: unknown) => typeof id === 'string')
      && typeof value.at === 'string' && Number.isFinite(Date.parse(value.at)) ? value : undefined
  } catch { return undefined }
}
