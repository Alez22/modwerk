// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { finishBaseInstall, lastSuccessfulSync, pendingBaseInstall, rememberSuccessfulSync, waitForBaseInstall } from './octatrack-progress'

const base = 'a'.repeat(64), image = 'b'.repeat(64)
beforeEach(() => { localStorage.clear(); sessionStorage.clear() })
afterEach(() => vi.unstubAllGlobals())

describe('remembering the Octatrack journey', () => {
  it('keeps a downloaded base pending until connection confirms the installation', () => {
    waitForBaseInstall(image, base, image, 'studio')
    expect(pendingBaseInstall()).toEqual({ sha256: image, expectedBase: base, previousBase: image, returnSetId: 'studio' })
    expect(lastSuccessfulSync()).toBeUndefined()
    finishBaseInstall()
    expect(pendingBaseInstall()).toBeUndefined()
  })
  it('does not resume legacy downloads without an exact expected identity', () => {
    sessionStorage.setItem('modwerk.octatrack.pending-base', JSON.stringify({ sha256: image, previousBase: base, returnSetId: 'studio' }))
    expect(pendingBaseInstall()).toBeUndefined()
    sessionStorage.setItem('modwerk.octatrack.pending-base', JSON.stringify({ sha256: image, expectedBase: base, returnSetId: 42 }))
    expect(pendingBaseInstall()).toBeUndefined()
  })
  it('keeps the successful set snapshot independently of later edits and filters other bases', () => {
    const set = { name: 'Studio set', moduleIds: ['everb'], base, active: image, at: '2026-10-12T19:00:00Z' }
    rememberSuccessfulSync(set)
    set.name = 'Edited set'; set.moduleIds.push('miniverb')
    expect(lastSuccessfulSync(base)).toMatchObject({ name: 'Studio set', moduleIds: ['everb'], at: set.at })
    expect(lastSuccessfulSync(image)).toBeUndefined()
  })
  it('ignores corrupt or incomplete records and works when storage is unavailable', () => {
    sessionStorage.setItem('modwerk.octatrack.pending-base', '{')
    localStorage.setItem('modwerk.octatrack.last-sync', JSON.stringify({ name: 'Broken', base, active: image, moduleIds: [], at: 'not a date' }))
    expect(pendingBaseInstall()).toBeUndefined(); expect(lastSuccessfulSync()).toBeUndefined()
    const blocked = { getItem() { throw new Error('blocked') }, setItem() { throw new Error('blocked') }, removeItem() { throw new Error('blocked') } }
    vi.stubGlobal('localStorage', blocked); vi.stubGlobal('sessionStorage', blocked)
    expect(() => { waitForBaseInstall(image, base); finishBaseInstall(); rememberSuccessfulSync({ name: 'Studio', moduleIds: [], base, active: image, at: '2026-10-12' }) }).not.toThrow()
    expect(pendingBaseInstall()).toBeUndefined(); expect(lastSuccessfulSync()).toBeUndefined()
  })
})
