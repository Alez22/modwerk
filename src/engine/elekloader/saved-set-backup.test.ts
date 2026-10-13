import { createHash } from 'node:crypto'
import { describe, expect, it } from 'vitest'
import { parseSavedSetMetadata, parseSavedSetChunk, SAVED_SET_CAPACITY } from './upload-wire'
import { UsbVendorTransport, type ControlDevice } from './upload-usb'

const digest = (bytes: Uint8Array) => createHash('sha256').update(bytes).digest('hex')
const zero = '0'.repeat(64)
const file = (length = 951) => {
  const bytes = Uint8Array.from({ length }, (_, index) => (index * 17 + 3) & 255)
  bytes.set([0x4d, 0x57, 0x53, 0x54]); bytes.fill(0x19, 20, 52)
  return bytes
}
// Independent MWSE/MWSC fixtures, not the production encoder or device code.
const metadata = (state: number, token: number, slot: number, data?: Uint8Array) => {
  const bytes = new Uint8Array(80), view = new DataView(bytes.buffer)
  bytes.set([0x4d, 0x57, 0x53, 0x45, 1, state, slot, 0]); view.setUint32(8, token)
  if (data) { view.setUint32(12, data.length); bytes.set(Buffer.from(digest(data), 'hex'), 16); bytes.set(data.subarray(20, 52), 48) }
  return view
}
const chunk = (token: number, slot: number, index: number, data: Uint8Array) => {
  const bytes = new Uint8Array(480), view = new DataView(bytes.buffer), offset = index * 448, count = Math.min(448, data.length - offset)
  bytes.set([0x4d, 0x57, 0x53, 0x43, 1, 2, slot, 0]); view.setUint32(8, token); view.setUint32(12, offset)
  view.setUint32(16, data.length); view.setUint32(20, count); bytes.set(data.subarray(offset, offset + count), 32)
  return view
}

describe('immutable saved-file wire validation', () => {
  const data = file(), ready = () => metadata(2, 7, 1, data)
  it('reads exact bounded records and each chunk, including a DataView offset', () => {
    const padded = new Uint8Array(96); padded.set(new Uint8Array(ready().buffer), 9)
    const record = parseSavedSetMetadata(new DataView(padded.buffer, 9, 80))
    expect(record).toEqual({ status: 'ready', token: 7, slot: 1, length: 951, sha256: digest(data), fileBase: '19'.repeat(32) })
    for (let index = 0; index < 3; index++) expect(parseSavedSetChunk(chunk(7, 1, index, data), record, index)).toEqual(data.slice(index * 448, (index + 1) * 448))
    expect(parseSavedSetMetadata(metadata(5, 1, 0))).toMatchObject({ status: 'read-failed', length: 0, sha256: zero })
  })
  it('rejects framing, nonready bytes, zero/reused-range tokens, invalid status and oversized metadata', () => {
    for (const length of [0, 4, 79, 81]) expect(() => parseSavedSetMetadata(new DataView(new ArrayBuffer(length)))).toThrow()
    for (const [offset, value] of [[0, 0], [4, 2], [5, 7], [6, 2], [7, 1]]) {
      const view = ready(); view.setUint8(offset, value); expect(() => parseSavedSetMetadata(view)).toThrow()
    }
    for (const token of [0, 65536]) { const view = ready(); view.setUint32(8, token); expect(() => parseSavedSetMetadata(view)).toThrow() }
    for (const length of [0, SAVED_SET_CAPACITY + 1]) { const view = ready(); view.setUint32(12, length); expect(() => parseSavedSetMetadata(view)).toThrow() }
    for (const offset of [12, 16, 48]) { const view = metadata(1, 7, 1); view.setUint8(offset, 1); expect(() => parseSavedSetMetadata(view)).toThrow() }
  })
  it('rejects swapped ownership, offsets, totals, counts, padding and indices before exposing bytes', () => {
    const record = parseSavedSetMetadata(ready())
    for (const offset of [0, 4, 5, 6, 7, 11, 15, 19, 23, 24, 31, 479]) {
      const view = chunk(7, 1, 2, data); view.setUint8(offset, view.getUint8(offset) ^ 1)
      expect(() => parseSavedSetChunk(view, record, 2), String(offset)).toThrow()
    }
    for (const index of [-1, 0.5, 3, 65535]) expect(() => parseSavedSetChunk(chunk(7, 1, 0, data), record, index)).toThrow()
    expect(() => parseSavedSetChunk(chunk(7, 1, 0, data), { ...record, status: 'pending' }, 0)).toThrow()
  })
})

class ExportDevice implements ControlDevice {
  state = 0; token = 0; slot = 0; polls = 0; commands: { request: number; value: number }[] = []
  files = [file(), file(52)]
  mutate?: (request: number, value: number, reply: DataView) => DataView
  failBegin = false; lostRelease = false; unsupported = false; busy = false; slot0Failure = false
  controller?: AbortController
  async controlTransferOut(): Promise<never> { throw new Error('Backup must never submit data or upload frames') }
  async controlTransferIn(setup: Parameters<ControlDevice['controlTransferIn']>[0], length: number) {
    const { request, value } = setup; this.commands.push({ request, value })
    expect(setup).toMatchObject({ requestType: 'vendor', recipient: 'interface', index: 1 })
    expect(length).toBe(request === 32 ? 480 : 80)
    if (this.unsupported) return { status: 'stall' }
    if (request === 31 && value) {
      expect([1, 2]).toContain(value)
      if (this.busy) return { status: 'ok', data: metadata(3, this.token, this.slot) }
      this.slot = value - 1; this.token++; this.state = 1; this.polls = 0
      if (this.failBegin) throw new Error('Begin reply lost')
      this.controller?.abort(new Error('cancel after acknowledged Begin'))
    } else if (request === 31 && this.state === 1 && ++this.polls >= 2) this.state = this.slot0Failure && !this.slot ? 5 : 2
    else if (request === 33) {
      expect(value).toBe(this.token); this.state = 0
      if (this.lostRelease) throw new Error('Release reply lost')
    }
    let reply: DataView = request === 32 ? chunk(this.token, this.slot, value, this.files[this.slot])
      : metadata(this.state, this.token, this.slot, this.state === 2 ? this.files[this.slot] : undefined)
    reply = this.mutate?.(request, value, reply) ?? reply
    return { status: 'ok', data: reply }
  }
}

describe('saved-file transport lease lifecycle', () => {
  it('backs up both immutable files, verifies their complete hashes and releases each lease once', async () => {
    const device = new ExportDevice(), result = await new UsbVendorTransport(device, 1).savedBackup()
    expect(result?.map(record => record.status)).toEqual(['ready', 'ready'])
    for (const [slot, record] of result!.entries()) {
      expect(record).toMatchObject({ slot, token: slot + 1, sha256: digest(device.files[slot]) })
      expect(record.status === 'ready' && record.data).toEqual(device.files[slot])
    }
    expect(device.commands.filter(command => command.request === 33)).toEqual([{ request: 33, value: 1 }, { request: 33, value: 2 }])
    expect(device.state).toBe(0)
  })
  it('keeps a read-failed slot distinct from absence and still reads the other fixed slot', async () => {
    const device = new ExportDevice(); device.slot0Failure = true
    const result = await new UsbVendorTransport(device, 1).savedBackup()
    expect(result?.[0]).toMatchObject({ slot: 0, status: 'read-failed', length: 0 })
    expect(result?.[0]).not.toHaveProperty('data'); expect(result?.[1].status).toBe('ready')
    expect(device.commands.filter(command => command.request === 32)).toHaveLength(1)
  })
  it('reconstructs the maximum-size file without another chunk beyond its bounded end', async () => {
    const device = new ExportDevice(); device.files[0] = file(SAVED_SET_CAPACITY)
    const result = await new UsbVendorTransport(device, 1).savedBackup()
    expect(result?.[0].status === 'ready' && result[0].data).toEqual(device.files[0])
    expect(device.commands.filter(command => command.request === 32)).toHaveLength(Math.ceil(SAVED_SET_CAPACITY / 448) + 1)
  })
  it('stalls on old bases without Begin, chunks or release', async () => {
    const device = new ExportDevice(); device.unsupported = true
    expect(await new UsbVendorTransport(device, 1).savedBackup()).toBeUndefined()
    expect(device.commands).toEqual([{ request: 31, value: 0 }])
  })
  it('never adopts or releases an unacknowledged Begin, and never repeats it', async () => {
    const device = new ExportDevice(); device.failBegin = true
    await expect(new UsbVendorTransport(device, 1).savedBackup()).rejects.toThrow('Begin reply lost')
    expect(device.commands).toEqual([{ request: 31, value: 0 }, { request: 31, value: 1 }])
  })
  it('does not release another client’s refused snapshot', async () => {
    const device = new ExportDevice(); device.busy = true
    await expect(new UsbVendorTransport(device, 1).savedBackup()).rejects.toThrow('did not acknowledge')
    expect(device.commands.filter(command => command.request === 33)).toHaveLength(0)
  })
  it('releases an acknowledged Begin even if cancellation arrives with its reply', async () => {
    const device = new ExportDevice(); device.controller = new AbortController()
    await expect(new UsbVendorTransport(device, 1).savedBackup(device.controller.signal)).rejects.toThrow('cancel after')
    expect(device.commands).toEqual([{ request: 31, value: 0 }, { request: 31, value: 1 }, { request: 33, value: 1 }])
    expect(device.state).toBe(0)
  })
  it('reconciles a lost release only by reading status', async () => {
    const device = new ExportDevice(); device.lostRelease = true
    expect((await new UsbVendorTransport(device, 1).savedBackup())?.[1].status).toBe('ready')
    expect(device.commands.filter(command => command.request === 33)).toHaveLength(2)
    expect(device.state).toBe(0)
  })
  it.each(['token', 'payload', 'digest', 'fileBase'])('rejects altered %s and releases its own snapshot', async field => {
    const device = new ExportDevice()
    device.mutate = (request, _value, view) => {
      if (field === 'token' && request === 32) view.setUint32(8, 3)
      if (field === 'payload' && request === 32) view.setUint8(32, view.getUint8(32) ^ 1)
      if (field === 'digest' && request === 31 && view.getUint8(5) === 2) view.setUint8(16, view.getUint8(16) ^ 1)
      if (field === 'fileBase' && request === 31 && view.getUint8(5) === 2) view.setUint8(48, 0)
      return view
    }
    await expect(new UsbVendorTransport(device, 1).savedBackup()).rejects.toThrow()
    expect(device.commands.filter(command => command.request === 33)).toEqual([{ request: 33, value: 1 }])
    expect(device.state).toBe(0)
  })
})
