import { afterEach, describe, expect, it, vi } from 'vitest'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { DEVELOPMENT_DISCORD_URL } from '../config/development-discord'
import { SUPPORT_URL } from '../config/support'

afterEach(() => { vi.unstubAllGlobals(); vi.resetModules() })

describe('owner note', () => {
  it('links the Discord and Ko-fi pages and warns against live use', async () => {
    const { OwnerNote } = await import('./OwnerNote')
    const html = renderToStaticMarkup(createElement(OwnerNote, { onClose() {} }))
    expect(html).toContain(`href="${DEVELOPMENT_DISCORD_URL}"`)
    expect(html).toContain(`href="${SUPPORT_URL}"`)
    expect(html).toContain('safe to use in a live setting')
  })

  it('shows once per browser, and once per visit when storage is blocked', async () => {
    const storage = new Map<string, string>()
    vi.stubGlobal('localStorage', { getItem: (key: string) => storage.get(key) ?? null, setItem: (key: string, value: string) => storage.set(key, value) })
    let note = await import('./OwnerNote')
    expect(note.ownerNoteSeen()).toBe(false)
    note.closeOwnerNote()
    vi.resetModules(); note = await import('./OwnerNote')
    expect(note.ownerNoteSeen()).toBe(true)

    vi.stubGlobal('localStorage', { getItem() { throw new Error('blocked') }, setItem() { throw new Error('blocked') } })
    vi.resetModules(); note = await import('./OwnerNote')
    expect(note.ownerNoteSeen()).toBe(false)
    note.closeOwnerNote()
    expect(note.ownerNoteSeen()).toBe(true)
  })
})
