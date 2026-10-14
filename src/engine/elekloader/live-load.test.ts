import { describe, expect, it } from 'vitest'
import { LOAD_BYTES, LOAD_SLOTS_BYTES, parseLoadReading } from './upload-wire'
import { UsbVendorTransport, type ControlDevice } from './upload-usb'

function wire() {
  const view = new DataView(new ArrayBuffer(LOAD_BYTES))
  view.setUint32(0, 0x4d574c44); view.setUint8(4, 1); view.setUint8(5, 7); view.setUint16(6, LOAD_BYTES)
  for (const [offset, value] of [[8, 1000], [12, 1200], [16, 998], [20, 950], [24, 999], [28, 123], [32, 234], [36, 345], [40, 456], [44, 567]]) view.setUint32(offset, value)
  return view
}
describe('read-only hardware load wire', () => {
  it('maps the actual core order to tracks, keeps device peaks separate and handles tick wrap', () => {
    const view = wire()
    expect(parseLoadReading(view)).toEqual({ ticks: 1000, frames: 1200, cpu: 123, tracks5to8: 234, peak5to8: 345, tracks1to4: 456, peak1to4: 567 })
    view.setUint32(8, 10); for (const offset of [16, 20, 24]) view.setUint32(offset, 0xfffffff0)
    expect(parseLoadReading(view).cpu).toBe(123)
  })
  it('uses gaps for uninitialized and stale windows, preserving an actual measured zero', () => {
    const view = wire(); view.setUint8(5, 1); view.setUint32(28, 0)
    expect(parseLoadReading(view)).toMatchObject({ cpu: 0, tracks5to8: null, tracks1to4: null })
    view.setUint32(16, 399); expect(parseLoadReading(view).cpu).toBeNull()
    view.setUint32(16, 1001); expect(parseLoadReading(view).cpu).toBeNull()
  })
  it('refuses truncation, wrong framing, unknown flags and impossible readings', () => {
    for (let n = 0; n < LOAD_BYTES; n++) expect(() => parseLoadReading(new DataView(wire().buffer, 0, n))).toThrow()
    for (const [offset, value] of [[0, 0], [4, 2], [5, 8], [7, 49]]) {
      const view = wire(); view.setUint8(offset, value); expect(() => parseLoadReading(view)).toThrow()
    }
    const view = wire(); view.setUint32(40, 1001); expect(() => parseLoadReading(view)).toThrow('range')
  })
  it('sends only readonly requests and distinguishes an old base from broken transport', async () => {
    let reply: Awaited<ReturnType<ControlDevice['controlTransferIn']>> = { status: 'stall' }
    const asked: number[] = []
    const transport = new UsbVendorTransport({ async controlTransferOut() { throw new Error('Load must never write') }, async controlTransferIn(setup, length) {
      expect(setup).toMatchObject({ requestType: 'vendor', recipient: 'interface', request: 30, index: 1 })
      expect(length).toBe(setup.value ? LOAD_SLOTS_BYTES : LOAD_BYTES); asked.push(setup.value)
      return setup.value ? { status: 'stall' } : reply
    } }, 1)
    expect(await transport.load()).toBeUndefined()
    expect(asked).toEqual([1, 0]) // v2 first; a base without the slot meter stalls it, and is not asked again
    reply = { status: 'ok', data: wire() }; expect((await transport.load())?.cpu).toBe(123)
    expect(asked).toEqual([1, 0, 0])
    reply = { status: 'ok' }; await expect(transport.load()).rejects.toThrow('answer')
  })
})

/** MWLD v2: v1's fields, then the frame's cycles and 16 slots of id, state, age and mean/peak counts. */
function wire2(slots: [index: number, id: number, state: number, age: number, mean: number, peak: number][]) {
  const view = new DataView(new ArrayBuffer(LOAD_SLOTS_BYTES)), v1 = wire()
  for (let i = 0; i < LOAD_BYTES; i++) view.setUint8(i, v1.getUint8(i))
  view.setUint8(4, 2); view.setUint16(6, LOAD_SLOTS_BYTES); view.setUint32(48, 72520); view.setUint8(52, 16); view.setUint8(53, 2)
  for (const [i, id, state, age, mean, peak] of slots) {
    view.setUint8(56 + 8 * i, id); view.setUint8(57 + 8 * i, state); view.setUint16(58 + 8 * i, age)
    view.setUint16(60 + 8 * i, mean); view.setUint16(62 + 8 * i, peak)
  }
  return view
}
describe('per-slot DSP load (MWLD v2)', () => {
  it('lists the running slots with their core, share of it and cycles a sample', () => {
    const reading = parseLoadReading(wire2([[0, 20, 1, 120, 3626, 5439], [13, 23, 2, 0xffff, 0, 0], [14, 9, 3, 0xffff, 0, 0]]))
    expect(reading.cpu).toBe(123)
    expect(reading.slots).toEqual([
      { track: 1, fx: 1, core: 1, id: 20, state: 'measured', mean: 100, peak: 150, meanCycles: 453.3, peakCycles: 679.9, age: 2 },
      { track: 6, fx: 2, core: 0, id: 23, state: 'waiting', mean: null, peak: null, meanCycles: null, peakCycles: null, age: null },
      { track: 7, fx: 2, core: 0, id: 9, state: 'unmeasurable', mean: null, peak: null, meanCycles: null, peakCycles: null, age: null },
    ])
    expect(parseLoadReading(wire()).slots).toBeUndefined()
  })
  it('refuses a malformed slot section', () => {
    for (const change of [(v: DataView) => v.setUint8(52, 8), (v: DataView) => v.setUint8(57, 4), (v: DataView) => v.setUint32(48, 0),
      (v: DataView) => v.setUint16(6, LOAD_BYTES)]) {
      const view = wire2([[0, 20, 1, 0, 1, 2]]); change(view); expect(() => parseLoadReading(view)).toThrow()
    }
    const empty = wire2([]); empty.setUint8(56, 20); expect(() => parseLoadReading(empty)).toThrow() // an id on an empty slot
    expect(() => parseLoadReading(new DataView(wire2([]).buffer, 0, LOAD_SLOTS_BYTES - 1))).toThrow()
  })
  it('asks a base with the slot meter for v2 every time', async () => {
    const asked: number[] = []
    const transport = new UsbVendorTransport({ async controlTransferOut() { throw new Error('Load must never write') }, async controlTransferIn(setup) {
      asked.push(setup.value); return { status: 'ok', data: wire2([[4, 22, 1, 30, 1813, 1813]]) }
    } }, 1)
    expect((await transport.load())?.slots?.[0]).toMatchObject({ track: 5, fx: 1, core: 0, mean: 50 })
    await transport.load(); expect(asked).toEqual([1, 1])
  })
})
