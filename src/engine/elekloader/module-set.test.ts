import { readFileSync } from 'node:fs'
import { describe, expect, it, vi } from 'vitest'
import { sha } from '../../../vendor/elekloader/kit/src/bytes.ts'
import manifest from '../assets/octatrack-module-packages.json' with { type: 'json' }
import { removal } from '../../dev/octatrack-usb-lifecycle'
import { fetchPackage, inventoryFrom, ModuleSetError, prepareModuleSet, removalPackage, runtimeId, USB_MODULE_IDS } from './module-set'

const file = (path: string) => new Uint8Array(readFileSync(new URL('../../../public/' + path, import.meta.url)))
const load = async (entry: { path: string }) => file(entry.path)
const empty = { moduleIds: [], removedStockFx: [] }

describe('the site’s runtime packages', () => {
  it('publishes each listed module as its manifest says: DSP effects with no stock-code sites', () => {
    expect(USB_MODULE_IDS).toEqual(['everb', 'miniverb', 'tapehead', 'airwindows-chorus'])
    for (const entry of manifest.packages) {
      const data = file(entry.path), view = new DataView(data.buffer)
      expect(entry.path).toBe(`octatrack-modules/${entry.id}/${entry.version}.mwrm`)
      expect([data.length, sha(data), view.getUint32(28).toString(16).padStart(8, '0')]).toEqual([entry.bytes, entry.sha256, runtimeId(entry.id)])
      expect([String.fromCharCode(...data.subarray(0, 4)), view.getUint16(4), view.getUint32(20), view.getUint32(24)]).toEqual(['MWRM', 6, 0, 0]) // no hooks, no sites
    }
  })
  it('names a module by the first four bytes of the SHA-256 of its catalogue id, and removes it with an empty package', () => {
    expect(runtimeId('everb')).toBe('873d83cc')
    expect(runtimeId('0000002a')).toBe('0000002a') // a module the catalogue does not know keeps its runtime id
    expect(removalPackage('everb')).toEqual(removal('', 0x873d83cc).data) // scripts/device.mjs's removal
  })
})

describe('preparing a module set', () => {
  it('removes first, then installs, each with the package that undoes it', async () => {
    const current = inventoryFrom([{ handle: 27, layout: 1, module: '873d83cc', name: 'E-Verb' }, { handle: 0xff, layout: 0, module: '0000002a', name: '' }])
    expect(current).toEqual({ moduleIds: ['everb', '0000002a'], removedStockFx: [] })
    const { name, changes } = await prepareModuleSet({ name: 'Live', moduleIds: ['tapehead', 'miniverb'] }, current, load)
    expect(name).toBe('Live')
    expect(changes.map(change => change.module)).toEqual(['E-Verb', '0000002a', 'TapeHead', 'Mini Verb'])
    expect(changes[0]).toEqual({ module: 'E-Verb', data: removalPackage('everb'), undo: file(manifest.packages[0].path) })
    expect(changes[1]).toEqual({ module: '0000002a', data: removalPackage('0000002a'), undo: undefined }) // nothing to put back
    expect(changes[2]).toEqual({ module: 'TapeHead', data: file(manifest.packages[2].path), undo: removalPackage('tapehead') })
  })
  it('refuses what the base cannot do yet, before anything is sent', async () => {
    await expect(prepareModuleSet({ name: 'Set', moduleIds: ['everb', 'tapeecho'] }, empty, load)).rejects.toThrow(ModuleSetError)
    await expect(prepareModuleSet({ name: 'Set', moduleIds: [], removedStockFx: ['DARK REV'] }, empty, load)).rejects.toThrow(/stock effects/)
  })
  it('fetches the site’s copy and refuses one that did not arrive intact', async () => {
    const entry = manifest.packages[0], data = file(entry.path)
    vi.stubGlobal('fetch', async (url: string) => { expect(url).toBe('/' + entry.path); return new Response(data) })
    expect(await fetchPackage(entry)).toEqual(data)
    vi.stubGlobal('fetch', async () => new Response(data.subarray(1)))
    await expect(fetchPackage(entry)).rejects.toThrow(/couldn’t fetch E-Verb intact/)
    vi.unstubAllGlobals()
  })
})
