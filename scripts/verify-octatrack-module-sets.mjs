// SPDX-License-Identifier: GPL-3.0-or-later
// The site's module set flow (OctatrackLink with module-set.ts's packages) against a base, through the USB bench:
// load a set and keep it, load another and undo it, then load it and keep it, then load an empty set. After each
// step the unit's INVENTORY must list exactly the set (or the one before, after an undo). Leaves no module installed.
//
//   node scripts/verify-octatrack-module-sets.mjs SOCKET [--hardware] [--selftest]
//
// SOCKET is ot_emu's --usb-host socket, or with --hardware sdk/machines/octatrack/elekloader/usb_bridge.py's for a
// real unit (stop `npm run device -- serve` first; the transport must be stopped). --selftest runs the base's
// self-test on the first load, as the site does. Node 24.
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import path from 'node:path'
import { registerHooks } from 'node:module'
import { Bench, device, enumerate } from './usb-bench.mjs'
// The app uses bundler resolution and Vite's import.meta.env; neither exists in Node (as scripts/octatrack-module-page.mjs).
registerHooks({
  resolve(specifier, context, next) {
    const local = specifier.startsWith('./') || specifier.startsWith('../')
    const resolved = local && !path.extname(specifier) ? specifier + '.ts' : specifier
    const attributes = local && resolved.endsWith('.json') ? { type: 'json' } : context.importAttributes
    return { ...next(resolved, { ...context, importAttributes: attributes }), importAttributes: attributes }
  },
  load(url, context, next) {
    const result = next(url, context)
    return url.endsWith('.ts') ? { ...result, source: String(result.source).replaceAll('import.meta.env.DEV', 'false') } : result
  },
})
const { OctatrackLink } = await import('../src/engine/elekloader/octatrack-link.ts')
const { inventoryFrom, prepareModuleSet } = await import('../src/engine/elekloader/module-set.ts')
const { UploadSession } = await import('../src/engine/elekloader/upload-session.ts')
const { findVendorInterface } = await import('../src/engine/elekloader/upload-usb.ts')
const { diagnostics } = await import('../src/dev/octatrack-usb-lifecycle.ts')

const [socket] = process.argv.slice(2).filter(arg => !arg.startsWith('--')), hardware = process.argv.includes('--hardware')
if (!socket) throw new Error('Usage: verify-octatrack-module-sets.mjs SOCKET [--hardware] [--selftest]')
const wait = ms => new Promise(resolve => setTimeout(resolve, ms))
const bench = new Bench(socket, { timeoutMs: 600000 }); await bench.ready()
const configuration = await enumerate(bench, hardware), index = findVendorInterface(configuration), control = device(bench)
// The base holds host frames until its boot restore is over (ep0.c): let the unit's own time pass first.
while ((await diagnostics(control, index)).ticks < 900) await wait(500)

// The bench as WebUSB: one device, already open and configured; claiming is the bridge's. WebUSB runs a device's control
// transfers one at a time, the bench does not: the link's keepalive must not cut into another request's stages.
let queue = Promise.resolve()
const serial = transfer => (...args) => { const run = queue.then(() => transfer(...args)); queue = run.catch(() => {}); return run }
const unit = { controlTransferIn: serial(control.controlTransferIn), controlTransferOut: serial(control.controlTransferOut), opened: true, configuration, async open() {}, async close() {}, async selectConfiguration() {}, async claimInterface() {}, async releaseInterface() {} }
const usb = { async requestDevice() { return unit }, async getDevices() { return [unit] }, addEventListener() {}, removeEventListener() {} }
const link = new OctatrackLink(usb, (transport, base) => UploadSession.connect(transport, base, { timeoutMs: 60000 }), 60000)
link.start()
while (link.getState().status !== 'ready') await wait(200)
console.log(`${link.getState().identity.model}, base ${link.getState().identity.base.slice(0, 16)}…`)

const file = entry => new Uint8Array(readFileSync(new URL('../public/' + entry.path, import.meta.url)))
const ids = async () => inventoryFrom(await link.inventory()).moduleIds
async function load(moduleIds, finish, stressTest) {
  const before = await ids(), { name, changes } = await prepareModuleSet({ name: moduleIds.join(' + ') || 'nothing', moduleIds }, inventoryFrom(await link.inventory()), file)
  const started = Date.now()
  await link.update(name, changes, stressTest)
  if (stressTest && link.getState().status === 'ready') { // the emulator's load meters are not the chip's: its self-test may fail
    const notice = link.getState().notice?.text ?? '', after = await ids()
    console.log(`self-test failed, ${name} undone: ${notice}; on the unit: ${after.join(', ') || 'nothing'}`)
    assert.match(notice, /Nothing was kept\.$/); assert.deepEqual([...after].sort(), [...before].sort())
    return load(moduleIds, finish)
  }
  assert.equal(link.getState().status, 'trial', link.getState().notice?.text)
  await (finish === 'keep' ? link.keep() : link.undo())
  const after = await ids(), want = finish === 'keep' ? moduleIds : before
  console.log(`${finish} ${name}: ${changes.length} changes in ${((Date.now() - started) / 1000).toFixed(1)} s; ${link.getState().notice?.text}; on the unit: ${after.join(', ') || 'nothing'}`)
  assert.deepEqual([...after].sort(), [...want].sort())
}
const start = await ids()
console.log('on the unit at the start:', start.join(', ') || 'nothing')
await load(['everb', 'miniverb'], 'keep', process.argv.includes('--selftest') ? () => link.selftest() : undefined)
await load(['miniverb', 'tapehead', 'airwindows-chorus'], 'undo')
await load(['miniverb', 'tapehead', 'airwindows-chorus'], 'keep')
await load([], 'keep')
console.log('Module sets: load, keep, undo and remove passed; INVENTORY matched after every step.')
process.exit(0)
