// @vitest-environment jsdom
import { act, createElement, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { newConfiguration } from '../config/workspace'
import { moduleSetReview } from '../engine/elekloader/module-set'
import type { LinkState, OctatrackLink } from '../engine/elekloader/octatrack-link'
import { OctatrackHub } from './OctatrackHub'

vi.mock('../engine/elekloader/module-set', async original => ({ ...await original<typeof import('../engine/elekloader/module-set')>(), moduleSetReview: vi.fn() }))
afterEach(() => { vi.restoreAllMocks(); vi.unstubAllGlobals(); sessionStorage.clear(); localStorage.clear() })

describe('beta module set controls', () => {
  it('changes the editing set without sending anything, and sync reviews the newly selected set only on request', async () => {
    vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true)
    const first = newConfiguration('Live', ['miniverb']), second = newConfiguration('Studio', ['synth'])
    const inventory = { moduleIds: ['miniverb'], removedStockFx: [] }
    const state: LinkState = { status: 'ready', identity: { canSubmit: true, base: '5b'.repeat(32), model: 'OCTATRACK MKII' } }
    const update = vi.fn(), sync = vi.fn(), install = vi.fn()
    const link = { getState: () => state, subscribe: () => () => {}, start: () => () => {}, update } as unknown as OctatrackLink
    vi.mocked(moduleSetReview).mockReturnValue({ changes: { add: ['synth'], remove: ['miniverb'], stockOff: [], stockOn: [] }, updates: [], needsSync: true, problem: undefined })
    function Workspace() {
      const [selectedId, select] = useState(first.id)
      return createElement(OctatrackHub, { link, inventory, sets: [first, second], selectedId, onSelect: select, onSync: sync, onInstall: install, header: null, grid: null, card: null })
    }
    const container = document.createElement('div'); document.body.append(container)
    const root = createRoot(container)
    try {
      await act(() => root.render(createElement(Workspace)))
      const footer = container.querySelector('footer[aria-label="Module set sync"]')!
      expect(footer.parentElement?.classList.contains('octatrack-hub')).toBe(true)
      expect(footer.previousElementSibling?.classList.contains('hub-split')).toBe(true)
      expect(container.querySelector('.hub-split .hub-sync-bar')).toBeNull()
      const chooser = container.querySelector<HTMLSelectElement>('.hub-set-picker')!
      await act(() => { chooser.value = second.id; chooser.dispatchEvent(new Event('change', { bubbles: true })) })
      expect(chooser.value).toBe(second.id)
      expect(container.querySelector('.hub-sync-bar strong')?.textContent).toBe('Studio')
      expect(vi.mocked(moduleSetReview)).toHaveBeenLastCalledWith(second, inventory, undefined)
      expect(sync).not.toHaveBeenCalled()
      expect(install).not.toHaveBeenCalled()
      expect(update).not.toHaveBeenCalled()
      await act(() => container.querySelector<HTMLButtonElement>('.hub-sync-bar button')!.click())
      expect(sync).toHaveBeenCalledExactlyOnceWith(second.id)
      expect(update).not.toHaveBeenCalled()
    } finally { await act(() => root.unmount()); container.remove() }
  })
})
