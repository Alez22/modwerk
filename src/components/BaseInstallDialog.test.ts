// @vitest-environment jsdom
import { act, createElement } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { fakeSession, fakeUnit, FAKE_BASE } from '../dev/octatrack-link-fake'
import { OctatrackLink } from '../engine/elekloader/octatrack-link'
import { pendingBaseInstall, waitForBaseInstall } from '../config/octatrack-progress'
import { BaseInstallDialog } from './BaseInstallDialog'

vi.mock('../config/firmware-filename', () => ({ saveFirmware: vi.fn() }))
let root: Root, container: HTMLDivElement
beforeEach(() => {
  vi.stubGlobal('IS_REACT_ACT_ENVIRONMENT', true)
  sessionStorage.clear()
  HTMLDialogElement.prototype.showModal = function () { this.open = true }
  HTMLDialogElement.prototype.close = function () { this.open = false }
  HTMLElement.prototype.scrollTo = () => {}
  container = document.createElement('div'); document.body.append(container); root = createRoot(container)
})
afterEach(async () => { await act(() => root.unmount()); container.remove(); vi.unstubAllGlobals() })

const button = (text: string) => [...container.querySelectorAll('button')].find(element => element.textContent === text)!
const ready = async (link: OctatrackLink, status: string) => act(async () => { await vi.waitFor(() => expect(link.getState().status).toBe(status)) })
async function mount(kind: 'stock' | 'base') {
  const unit = fakeUnit(kind), link = new OctatrackLink(unit.usb, fakeSession(unit)), onReady = vi.fn()
  await act(async () => root.render(createElement(BaseInstallDialog, { link, firmwareReady: true, onChooseFirmware() {},
    buildBase: async () => ({ buffer: new ArrayBuffer(0), sha256: 'b'.repeat(64) }), onClose() {}, onReady })))
  await ready(link, kind === 'base' ? 'ready' : 'stock')
  return { unit, link, onReady }
}

describe('resuming the first base installation', () => {
  it('waits through an original-OS connection and returns to the set when a base reconnects', async () => {
    waitForBaseInstall('b'.repeat(64))
    const { unit, link, onReady } = await mount('stock')
    expect(container.textContent).toContain('Waiting for your Octatrack')
    expect(onReady).not.toHaveBeenCalled()
    await act(async () => { unit.unplug(); unit.plug('base') })
    await ready(link, 'ready')
    expect(onReady).toHaveBeenCalledTimes(1)
    expect(pendingBaseInstall()).toBeUndefined()
  })
  it('does not treat a download while already connected as a completed installation', async () => {
    const { unit, link, onReady } = await mount('base')
    await act(() => container.querySelector<HTMLInputElement>('input[type=checkbox]')!.click())
    await act(async () => button('Download base .bin').click())
    expect(pendingBaseInstall()?.previousBase).toBe(FAKE_BASE)
    expect(onReady).not.toHaveBeenCalled()
    await act(async () => unit.unplug())
    await act(async () => unit.plug('base'))
    await ready(link, 'ready')
    expect(onReady).toHaveBeenCalledTimes(1)
  })
  it('resumes a pending first install when the page is reopened with the base already present', async () => {
    waitForBaseInstall('b'.repeat(64))
    const { onReady } = await mount('base')
    expect(onReady).toHaveBeenCalledTimes(1)
  })
})
