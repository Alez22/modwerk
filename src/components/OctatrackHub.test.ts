// @vitest-environment jsdom
import { act, createElement, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { newConfiguration } from '../config/workspace'
import { moduleSetReview } from '../engine/elekloader/module-set'
import type { LinkState, OctatrackLink } from '../engine/elekloader/octatrack-link'
import { OctatrackHub } from './OctatrackHub'

vi.mock('./OctatrackDiagnostics', () => ({ OctatrackDiagnosticsSettings: () => null }))
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
      expect(footer.parentElement?.getAttribute('role')).toBe('tabpanel')
      expect(footer.parentElement?.parentElement?.classList.contains('octatrack-hub')).toBe(true)
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


it('keeps local samples across keyboard tab switches and pauses preview without sending module changes', async () => {
  vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true)
  const createURL = vi.fn(() => 'blob:hub-sample'), revokeURL = vi.fn(), pause = vi.spyOn(HTMLMediaElement.prototype, 'pause').mockImplementation(() => {})
  vi.stubGlobal('URL', class extends URL { static createObjectURL = createURL; static revokeObjectURL = revokeURL })
  vi.stubGlobal('fetch', vi.fn(() => { throw new Error('Local sample selection must not use the API') }))
  const config = newConfiguration('Live', ['miniverb']), select = vi.fn(), sync = vi.fn(), install = vi.fn(), update = vi.fn()
  const state: LinkState = { status: 'ready', identity: { canSubmit: true, base: '5b'.repeat(32), model: 'OCTATRACK MKII' } }
  const link = { getState: () => state, subscribe: () => () => {}, start: () => () => {}, update } as unknown as OctatrackLink
  vi.mocked(moduleSetReview).mockReturnValue({ changes: { add: ['miniverb'], remove: [], stockOff: [], stockOn: [] }, updates: [], needsSync: true, problem: undefined })
  const container = document.createElement('div'); document.body.append(container); const root = createRoot(container)
  try {
    await act(() => root.render(createElement(OctatrackHub, { link, inventory: { moduleIds: [], removedStockFx: [] }, sets: [config], selectedId: config.id, onSelect: select, onSync: sync, onInstall: install, header: null, grid: createElement('p', null, 'Module grid'), card: null })))
    const tabs = container.querySelectorAll<HTMLButtonElement>('[role="tab"]'), panels = container.querySelectorAll<HTMLElement>('[role="tabpanel"]')
    expect(tabs[0].getAttribute('aria-selected')).toBe('true'); expect(panels[0].hidden).toBe(false); expect(panels[1].hidden).toBe(true)
    expect(tabs[1].getAttribute('aria-controls')).toBe(panels[1].id)
    await act(() => tabs[0].dispatchEvent(new KeyboardEvent('keydown', { key: 'ArrowRight', bubbles: true })))
    expect(document.activeElement).toBe(tabs[1]); expect(tabs[1].tabIndex).toBe(0); expect(tabs[0].tabIndex).toBe(-1)
    expect(panels[0].hidden).toBe(true); expect(panels[1].hidden).toBe(false)
    expect(container.querySelector('footer')?.closest('[hidden]')).toBe(panels[0])
    const input = container.querySelector<HTMLInputElement>('input[aria-label="Choose sample files"]')!
    Object.defineProperty(input, 'files', { value: [new File(['local'], 'kick.wav', { type: 'audio/wav' })], configurable: true })
    await act(() => input.dispatchEvent(new Event('change', { bubbles: true })))
    expect(createURL).not.toHaveBeenCalled()
    await act(() => container.querySelector<HTMLButtonElement>('.samples-tree button')!.click())
    expect(createURL).toHaveBeenCalledTimes(1); expect(container.querySelector('audio')?.autoplay).toBe(false)
    pause.mockClear()
    await act(() => tabs[1].dispatchEvent(new KeyboardEvent('keydown', { key: 'Home', bubbles: true })))
    expect(document.activeElement).toBe(tabs[0]); expect(panels[0].hidden).toBe(false); expect(pause).toHaveBeenCalledTimes(1)
    expect(revokeURL).not.toHaveBeenCalled()
    await act(() => tabs[0].dispatchEvent(new KeyboardEvent('keydown', { key: 'End', bubbles: true })))
    expect(panels[1].textContent).toContain('kick.wav'); expect(createURL).toHaveBeenCalledTimes(1)
    expect(select).not.toHaveBeenCalled(); expect(sync).not.toHaveBeenCalled(); expect(install).not.toHaveBeenCalled(); expect(update).not.toHaveBeenCalled()
    expect(fetch).not.toHaveBeenCalled()
  } finally { await act(() => root.unmount()); container.remove() }
  expect(revokeURL).toHaveBeenCalledWith('blob:hub-sample')
})

it('opens the Samples WIP without USB support or a module set', async () => {
  vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true)
  const sync = vi.fn(), install = vi.fn(), select = vi.fn(), container = document.createElement('div'); document.body.append(container); const root = createRoot(container)
  try {
    await act(() => root.render(createElement(OctatrackHub, { link: null, sets: [], onSelect: select, onSync: sync, onInstall: install, header: null, grid: null, card: null })))
    await act(() => container.querySelectorAll<HTMLButtonElement>('[role="tab"]')[1].click())
    expect(container.querySelectorAll<HTMLElement>('[role="tabpanel"]')[1].hidden).toBe(false)
    expect(container.textContent).toContain('No USB connection is needed')
    expect(container.querySelector<HTMLButtonElement>('.samples-actions button')?.disabled).toBe(false)
    expect(sync).not.toHaveBeenCalled(); expect(install).not.toHaveBeenCalled(); expect(select).not.toHaveBeenCalled()
  } finally { await act(() => root.unmount()); container.remove() }
})
