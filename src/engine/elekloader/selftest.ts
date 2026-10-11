// The Octatrack base's self-test (SYSTEM > MODWERK TEST; sdk/machines/octatrack/elekloader/dsp.c), run by the site
// on a trial before it is kept: the modules intact, the DSP ones together while the pattern plays with their knobs
// moving (no core and not the CPU past 90 %), and a stress round. About 3 s for every eight DSP modules.
import type { SelftestRecord } from './upload-usb.ts'

/** What each failed bit means, as the end of "The stress test failed: …". The order of selftest.h's bits. */
export const SELFTEST_FAILURES = [
  'a module didn’t install cleanly',
  'the modules couldn’t be loaded again while playing',
  'the Octatrack’s DSP stopped',
  'together these modules overload the DSP',
  'the module loader reported errors',
  'the test couldn’t put your tracks back as they were',
  'the test was stopped on the Octatrack',
  'a module doesn’t fit on the DSP, even on its own',
  'together these modules overload the CPU',
] as const

export interface SelftestTransport { selftest(start: boolean, signal?: AbortSignal): Promise<SelftestRecord | undefined> }

const wait = (ms: number, signal?: AbortSignal) => new Promise<void>((resolve, reject) => {
  const timer = setTimeout(resolve, ms)
  signal?.addEventListener('abort', () => { clearTimeout(timer); reject(signal.reason) }, { once: true })
})

/** Starts the test and waits for it: null when it passed, else why it failed (the first reason, in bit order).
 * shortcut: a base without the self-test (it stalls the request) passes untested, as updates were before; refuse
 * those once every published base has it. */
export async function runSelftest(transport: SelftestTransport, options: { signal?: AbortSignal; pollMs?: number; timeoutMs?: number;
  progress?: (done: number, total: number) => void } = {}): Promise<string | null> {
  const { signal, pollMs = 500, timeoutMs = 180_000, progress } = options
  let record = await transport.selftest(true, signal)
  if (!record) return null
  if (record.state !== 1) return 'the Octatrack couldn’t start it; stop playback and try again'
  for (const start = Date.now(); record.state === 1; ) {
    progress?.(record.done, record.total)
    if (Date.now() - start > timeoutMs) return 'it took too long'
    await wait(pollMs, signal)
    const next = await transport.selftest(false, signal)
    if (!next) return 'the Octatrack stopped answering it'
    record = next
  }
  if (record.state === 2) return null
  const failed = record.failed
  const bit = SELFTEST_FAILURES.findIndex((_, i) => failed >> i & 1)
  return bit < 0 ? 'the Octatrack reported a failure' : SELFTEST_FAILURES[bit]
}
