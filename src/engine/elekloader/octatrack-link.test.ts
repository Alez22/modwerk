import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { sha } from '../../../vendor/elekloader/kit/src/bytes.ts'
import { FAKE_BASE, fakeSession, fakeUnit } from '../../dev/octatrack-link-fake'
import { removalPackage } from './module-set'
import { LinkBusyError, OctatrackLink, tabLocks } from './octatrack-link'
import { UploadUnconfirmedError } from './upload-session'
import { UsbVendorTransport } from './upload-usb'

const settle = () => new Promise(resolve => setTimeout(resolve, 0))
async function linked(kind: 'base' | 'stock' | 'none' = 'base') {
  const unit = fakeUnit(kind), link = new OctatrackLink(unit.usb, fakeSession(unit), 300)
  link.start(); await settle(); await settle()
  return { unit, link }
}
// Each link gets its own in-tab lock; Node's own navigator.locks would be shared by every test.
beforeEach(() => { vi.stubGlobal('navigator', {}) })
afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals() })

describe('finding the unit', () => {
  it('holds one cross-tab lock for the complete two-file backup and releases the interface before another read', async () => {
    const unit = fakeUnit(), locks = tabLocks()
    const a = new OctatrackLink(unit.usb, fakeSession(unit), 300, locks), b = new OctatrackLink(unit.usb, fakeSession(unit), 300, locks)
    const stopA = a.start(), stopB = b.start()
    await vi.waitFor(() => expect([a.getState().status, b.getState().status]).toEqual(['ready', 'ready']))
    await settle()
    const device = (await unit.usb.getDevices())[0], claim = vi.spyOn(device, 'claimInterface'), release = vi.spyOn(device, 'releaseInterface')
    let complete: () => void = () => {}, finished = false
    let backup: Promise<unknown> | undefined, reading: Promise<unknown> | undefined
    const snapshot = vi.spyOn(UsbVendorTransport.prototype, 'savedBackup').mockImplementationOnce(() => new Promise(resolve => { complete = () => resolve([]) }))
    try {
      backup = a.savedBackup(); await settle()
      reading = b.inventory().then(() => { finished = true }); await settle()
      expect(finished).toBe(false); expect(claim).toHaveBeenCalledTimes(1); expect(release).not.toHaveBeenCalled()
      complete(); await backup; await reading
      expect(finished).toBe(true); expect(claim).toHaveBeenCalledTimes(2); expect(release).toHaveBeenCalledTimes(2)
      expect(a.getState().status).toBe('ready'); expect(b.getState().status).toBe('ready')
    } finally { complete(); await Promise.allSettled([backup, reading]); snapshot.mockRestore(); stopA(); stopB() }
  })
  it('does not read diagnostic status if consent is withdrawn while claiming the interface', async () => {
    const {unit,link}=await linked(),device=(await unit.usb.getDevices())[0]
    const transfer=vi.spyOn(device,'controlTransferIn'),release=vi.spyOn(device,'releaseInterface')
    let complete:()=>void=()=>{},allowed=true
    vi.spyOn(device,'claimInterface').mockImplementationOnce(()=>new Promise<void>(resolve=>{complete=resolve}))
    const controller=new AbortController(),reading=link.health(controller.signal,()=>allowed)
    const cancelled=expect(reading).rejects.toBeInstanceOf(LinkBusyError)
    await settle();allowed=false;controller.abort();complete();await cancelled
    expect(transfer).not.toHaveBeenCalled();expect(release).toHaveBeenCalledTimes(1)
  })
  it('reports a browser without WebUSB instead of offering a dead button', () => {
    expect(new OctatrackLink(undefined).getState().status).toBe('unsupported')
  })
  it('reopens an allowed unit and reads its base without the picker', async () => {
    const { link } = await linked()
    expect(link.getState()).toMatchObject({ status: 'ready', identity: { base: FAKE_BASE, model: 'OCTATRACK MKII', canSubmit: true }, active: FAKE_BASE })
  })
  it('tells a stock unit apart, then finds the base when the unit restarts after its OS upgrade', async () => {
    const { unit, link } = await linked('stock')
    expect(link.getState().status).toBe('stock')
    unit.unplug(); expect(link.getState().status).toBe('idle')
    unit.plug('base'); await settle(); await settle()
    expect(link.getState().status).toBe('ready')
  })
  it('says when another tab or app holds the unit, and retries', async () => {
    const unit = fakeUnit(), link = new OctatrackLink(unit.usb, fakeSession(unit))
    unit.taken = true; link.start(); await settle(); await settle()
    expect(link.getState().status).toBe('busy')
    unit.taken = false; await link.retry()
    expect(link.getState().status).toBe('ready')
  })
  it('stays connected while any view still uses it', async () => {
    const unit = fakeUnit(), link = new OctatrackLink(unit.usb, fakeSession(unit))
    const card = link.start(), dialog = link.start(); await settle(); await settle()
    card(); card()
    expect(link.getState().status).toBe('ready')
    unit.unplug(); expect(link.getState().status).toBe('idle') // still listening
    dialog(); unit.plug('base'); await settle(); await settle()
    expect(link.getState().status).toBe('idle') // nobody listens any more
  })
})

describe('sending a module', () => {
  const data = new Uint8Array(10000), one = [{ module: 'PREVIEW VOL', data }]
  it('runs a trial, then keeps it', async () => {
    const { link } = await linked()
    const progress: number[] = []
    link.subscribe(() => { if (link.getState().status === 'sending') progress.push(link.getState().progress!) })
    await link.update('PREVIEW VOL', one)
    expect(link.getState()).toMatchObject({ status: 'trial', module: 'PREVIEW VOL', active: sha(data) })
    expect(progress.at(-1)).toBe(1)
    await link.keep()
    expect(link.getState()).toMatchObject({ status: 'ready', notice: { tone: 'success' }, active: sha(data) })
    expect(link.getState().notice!.text).toMatch(/Kept\. PREVIEW VOL stays on your Octatrack, also after a restart/)
  })
  it('keeps the trial running when playback blocks keep, and finishes once stopped', async () => {
    const { unit, link } = await linked()
    await link.update('PREVIEW VOL', one)
    unit.playing = true; await link.undo()
    expect(link.getState()).toMatchObject({ status: 'trial', notice: { tone: 'error', text: expect.stringMatching(/Stop playback/) } })
    unit.playing = false; await link.undo()
    expect(link.getState()).toMatchObject({ active: FAKE_BASE, notice: { text: expect.stringMatching(/^Undone/) } })
  })
  it('goes ahead as soon as playback stops within the wait', async () => {
    const { unit, link } = await linked()
    unit.playing = true; setTimeout(() => { unit.playing = false }, 100) // the base pressing STOP, or the user
    await link.update('PREVIEW VOL', one)
    expect(link.getState().status).toBe('trial')
  })
  it('refuses to start while playing, without asking the user to unplug', async () => {
    const { unit, link } = await linked()
    unit.playing = true; await link.update('PREVIEW VOL', one)
    expect(link.getState()).toMatchObject({ status: 'ready', notice: { tone: 'error', text: 'Stop playback or finish recording on the Octatrack to continue.' } })
  })
  it('stress-tests an update before it can be kept, and undoes it when the test fails', async () => {
    const { link } = await linked(), seen: string[] = []
    link.subscribe(() => { seen.push(link.getState().status) })
    await link.update('My set', one, async () => null)
    expect(seen).toContain('testing')
    expect(link.getState()).toMatchObject({ status: 'trial', tested: true })
    await link.keep()
    await link.update('My set', one, async () => 'CPU over budget on track 3')
    expect(link.getState()).toMatchObject({ status: 'ready', notice: { tone: 'error', text: 'The self-test failed: CPU over budget on track 3. Nothing was kept.' } })
  })
  it('refuses a module bigger than the base can stage', async () => {
    const { link } = await linked()
    await link.update('HUGE', [{ module: 'HUGE', data: new Uint8Array(262145) }])
    expect(link.getState().notice?.text).toMatch(/too big/)
  })
  it('cancels a transfer cleanly', async () => {
    const { link } = await linked()
    link.subscribe(() => { if (link.getState().progress) link.cancel() }) // the button shows once sending has started
    await link.update('PREVIEW VOL', one)
    expect(link.getState().notice?.text).toBe('Cancelled. Nothing changed on the Octatrack.')
  })
  it('says why the Octatrack rejected a module, from the base’s record', async () => {
    const { unit, link } = await linked()
    unit.refusal = 7 // a track plays the effect it would replace
    await link.update('PREVIEW VOL', one)
    expect(link.getState().notice?.text).toMatch(/A track is playing this module’s effect/)
    unit.refusal = 1 // malformed: the plain text
    await link.update('PREVIEW VOL', one)
    expect(link.getState().notice?.text).toBe('The Octatrack can’t run this module file.')
  })
  it('stages again when the loader was busy for a moment', async () => {
    const { unit, link } = await linked()
    unit.refusal = 5 // DSP code moving: busy now, free a moment later
    setTimeout(() => { unit.refusal = undefined }, 50)
    await link.update('PREVIEW VOL', one)
    expect(link.getState().status).toBe('trial')
  })
  it('recovers from a missing reply without asking to unplug', async () => {
    const unit = fakeUnit(), base = fakeSession(unit)
    let calls = 0
    const connect: typeof base = async (...args) => {
      const session = await base(...args)
      if (++calls !== 2) return session
      let trusted = true // the update's session: a chunk's reply goes missing mid-transfer
      return Object.create(session, {
        connectionTrusted: { get: () => trusted },
        stage: { value: async () => { trusted = false; unit.staged = true; throw new UploadUnconfirmedError('chunk was not confirmed', session.status) } },
      })
    }
    const link = new OctatrackLink(unit.usb, connect, 300)
    link.start(); await settle(); await settle()
    await link.update('PREVIEW VOL', one)
    expect(calls).toBe(3)
    expect(link.getState()).toMatchObject({ status: 'ready', notice: { text: 'The Octatrack missed a reply, so nothing changed. Try again.' } })
  })
  it('keeps the trial alive with a request every second, and explains an unplug mid-trial', async () => {
    vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] })
    const { unit, link } = await linked()
    await link.update('PREVIEW VOL', one)
    const device = (await unit.usb.getDevices())[0], identify = vi.spyOn(device, 'controlTransferIn')
    vi.advanceTimersByTime(3000)
    expect(identify).toHaveBeenCalledTimes(3)
    unit.unplug()
    expect(link.getState()).toMatchObject({ status: 'idle', notice: { text: expect.stringMatching(/undoes PREVIEW VOL by itself/) } })
    vi.advanceTimersByTime(3000)
    expect(identify).toHaveBeenCalledTimes(3)
  })
})

describe('loading a module set', () => {
  // Runtime packages as the builder makes them: an install has an image, a removal none (sdk/runtime/loader/README.md).
  const install = (id: string) => { const data = new Uint8Array(36); data.set([0x4d, 0x57, 0x52, 0x4d, 0, 4]); const view = new DataView(data.buffer); view.setUint32(8, 4); view.setUint32(28, Number.parseInt(id, 16)); return data }
  const change = (id: string, removes = false) => ({ module: 'M' + id.slice(-1), data: removes ? removalPackage(id) : install(id), undo: removes ? install(id) : removalPackage(id) })
  const set = [change('0000000a', true), change('0000000b'), change('0000000c')]
  async function loaded(stressTest?: () => Promise<string | null>) {
    const result = await linked(); result.unit.modules = ['0000000a']
    await result.link.update('Live', set, stressTest)
    return result
  }
  it('keeps each change before the last at once, runs the last as the trial, and keeps it', async () => {
    const { unit, link } = await loaded(async () => null)
    expect(link.getState()).toMatchObject({ status: 'trial', module: 'Live', tested: true })
    expect(unit.kept).toEqual(['-0000000a', '+0000000b'])
    await link.keep()
    expect(unit.kept).toEqual(['-0000000a', '+0000000b', '+0000000c'])
    expect(link.getState().notice).toMatchObject({ tone: 'success', text: 'Kept. Live stays on your Octatrack, also after a restart.' })
    expect((await link.inventory())!.map(item => item.module)).toEqual(['0000000b', '0000000c'])
  })
  it('undoes the whole set: the trial rolled back, then the kept changes put back newest first', async () => {
    const { unit, link } = await loaded()
    await link.undo()
    expect(unit.kept).toEqual(['-0000000a', '+0000000b', '-0000000b', '+0000000a'])
    expect(unit.modules).toEqual(['0000000a'])
    expect(link.getState()).toMatchObject({ status: 'ready', notice: { tone: 'success', text: 'Undone. Your Octatrack is back to how it was.' } })
  })
  it('rolls back again while the loader cannot switch yet', async () => {
    const { unit, link } = await loaded()
    unit.stuck = 2; await link.undo()
    expect(link.getState()).toMatchObject({ status: 'ready', notice: { tone: 'success', text: 'Undone. Your Octatrack is back to how it was.' } })
  })
  it('undoes the set when the self-test fails', async () => {
    const { unit, link } = await loaded(async () => 'the Octatrack’s DSP stopped')
    expect(unit.kept).toEqual(['-0000000a', '+0000000b', '-0000000b', '+0000000a'])
    expect(link.getState().notice?.text).toBe('The self-test failed: the Octatrack’s DSP stopped. Nothing was kept.')
  })
  it('puts back what it kept when the base refuses a change part way, and names the module', async () => {
    const unit = fakeUnit(), base = fakeSession(unit)
    let stages = 0
    const connect: typeof base = async (...args) => {
      const session = await base(...args)
      return Object.create(session, { stage: { value: (...stage: Parameters<typeof session.stage>) => { unit.refusal = ++stages === 2 ? 2 : undefined; return session.stage(...stage) } } })
    }
    const link = new OctatrackLink(unit.usb, connect, 300)
    link.start(); await settle(); await settle(); unit.modules = ['0000000a']
    await link.update('Live', set)
    expect(unit.kept).toEqual(['-0000000a', '+0000000a'])
    expect(link.getState()).toMatchObject({ status: 'ready', notice: { tone: 'error', text: 'Mb: There isn’t enough module memory left on the Octatrack. Remove a module, then try again.' } })
  })
  it('says which modules it could not put back', async () => {
    const { unit, link } = await linked(); unit.modules = ['0000000a']
    await link.update('Live', [{ ...set[0], undo: undefined }, set[1]])
    await link.undo()
    expect(link.getState().notice?.text).toBe('Undone, except: Ma couldn’t be put back: the site has no package for it.')
  })
  it('explains an unplug part way through a set', async () => {
    const { unit, link } = await loaded()
    unit.unplug()
    expect(link.getState()).toMatchObject({ status: 'idle', notice: { text: 'USB disconnected. Your Octatrack is between the two module sets: sync one of them again.' } })
  })
})

describe('several tabs of the site', () => {
  const data = (n: number) => new Uint8Array(4000).fill(n)
  async function tabs() {
    const unit = fakeUnit(), locks = tabLocks() // one lock for both, as navigator.locks is across tabs
    const a = new OctatrackLink(unit.usb, fakeSession(unit), 300, locks), b = new OctatrackLink(unit.usb, fakeSession(unit), 300, locks)
    a.start(); b.start()
    for (let i = 0; i < 6; i++) await settle()
    return { unit, a, b }
  }
  it('take turns: the other tab skips its reads during a load, and its own load waits instead of failing', async () => {
    const { unit, a, b } = await tabs()
    expect([a.getState().status, b.getState().status]).toEqual(['ready', 'ready'])
    await a.update('Set A', [{ module: 'A', data: data(1) }])
    expect(a.getState().status).toBe('trial')
    await expect(b.inventory()).rejects.toBeInstanceOf(LinkBusyError) // skipped this round, not "can't list"
    expect(await b.missing()).toBeUndefined() // a poll keeps what it had
    const waiting = b.update('Set B', [{ module: 'B', data: data(2) }])
    await settle()
    expect(b.getState().status).toBe('ready') // waiting for the unit, not failed
    await a.keep()
    await waiting
    // Tab B planned its load against the unit before A's: it refuses to send it.
    expect(b.getState().notice?.text).toBe('Another tab changed your Octatrack meanwhile, so nothing was synced. Review the sync again.')
    expect(unit.active).toBe(sha(data(1)))
  })
  it('lets the waiting tab load once the other tab undid its load', async () => {
    const { a, b } = await tabs()
    await a.update('Set A', [{ module: 'A', data: data(1) }])
    const waiting = b.update('Set B', [{ module: 'B', data: data(2) }])
    await a.undo()
    await waiting
    expect(b.getState()).toMatchObject({ status: 'trial', module: 'Set B' })
    await b.keep()
  })
})
