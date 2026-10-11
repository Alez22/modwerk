import { describe, expect, it } from 'vitest'
import { runSelftest, SELFTEST_FAILURES } from './selftest'
import { parseSelftest, SELFTEST_BYTES, type SelftestRecord } from './upload-usb'

const record = (state: number, failed = 0, done = 0, total = 4): SelftestRecord =>
  ({ state, failed, modules: 2, dsp: 2, intact: 2, ran: 2, peaks: { cpu: 500, tracks1to4: 600, tracks5to8: 550 }, done, total })
/** A unit whose self-test answers `states` in turn, the first to the start request. */
function unit(states: (SelftestRecord | undefined)[]) {
  const calls: boolean[] = []
  return { calls, selftest: async (start: boolean) => { calls.push(start); return states[Math.min(calls.length - 1, states.length - 1)] } }
}

describe('the base self-test as the update stress test', () => {
  it('passes when the unit reports passed, after polling while it runs, with progress', async () => {
    const u = unit([record(1, 0, 0), record(1, 0, 2), record(2, 0, 4)]), seen: number[] = []
    expect(await runSelftest(u, { pollMs: 0, progress: done => seen.push(done) })).toBeNull()
    expect(u.calls).toEqual([true, false, false])
    expect(seen).toEqual([0, 2])
  })
  it('names the first failure, in the order of selftest.h', async () => {
    expect(await runSelftest(unit([record(1), record(3, 8 | 256)]), { pollMs: 0 })).toBe(SELFTEST_FAILURES[3]) /* the DSP before the CPU */
    expect(await runSelftest(unit([record(1), record(3, 128)]), { pollMs: 0 })).toBe('a module doesn’t fit on the DSP, even on its own')
  })
  it('says when it cannot start (playing, or the loader busy)', async () => {
    expect(await runSelftest(unit([record(0)]), { pollMs: 0 })).toMatch(/stop playback/)
  })
  it('lets a base without the self-test through untested, but not one that stops answering', async () => {
    expect(await runSelftest(unit([undefined]), { pollMs: 0 })).toBeNull()
    expect(await runSelftest(unit([record(1), undefined]), { pollMs: 0 })).toMatch(/stopped answering/)
  })
  it('gives up after its time limit', async () => {
    expect(await runSelftest(unit([record(1)]), { pollMs: 1, timeoutMs: 5 })).toBe('it took too long')
  })
  it('reads the base record, big-endian, 56 bytes', () => {
    const view = new DataView(new ArrayBuffer(SELFTEST_BYTES))
    ;[2, 3, 0, 6, 6, 6, 6, 669, 571, 536, 8, 8].forEach((v, i) => view.setUint32(4 * i, v))
    expect(parseSelftest(view)).toEqual({ state: 2, failed: 0, modules: 6, dsp: 6, intact: 6, ran: 6,
      peaks: { tracks1to4: 669, tracks5to8: 571, cpu: 536 }, done: 8, total: 8 })
    expect(() => parseSelftest(new DataView(new ArrayBuffer(60)))).toThrow()
  })
})
