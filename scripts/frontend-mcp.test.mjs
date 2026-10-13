import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { mkdtemp, rm, readFile, writeFile, chmod, symlink, mkdir } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createFrontendTools, createProtocol, validateApiPath } from './frontend-mcp.mjs'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { fileURLToPath } from 'node:url'

let folder, service
beforeAll(async () => { folder = await mkdtemp(join(tmpdir(), 'modwerk-mcp-test-')); await chmod(folder, 0o700); service = await createFrontendTools({ dataDir: folder }) }, 30000)
afterAll(async () => { await service?.close(); await rm(folder, { recursive: true, force: true }) })

describe('frontend MCP protocol and isolated site workflows', () => {
  it('initializes, discovers tools, and returns structured results and bounded errors', async () => {
    const protocol = createProtocol(service)
    expect((await protocol({ jsonrpc: '2.0', id: 1, method: 'tools/list' })).error.code).toBe(-32002)
    expect((await protocol({ jsonrpc: '2.0', id: 2, method: 'initialize' })).result.capabilities.tools).toBeDefined()
    expect((await protocol({ jsonrpc: '2.0', id: 3, method: 'tools/list' })).result.tools.some(item => item.name === 'device_undo')).toBe(true)
    expect((await protocol({ jsonrpc: '2.0', id: 4, method: 'tools/call', params: { name: 'site_features', arguments: {} } })).result.structuredContent.beta).toBe(true)
    expect((await protocol({ jsonrpc: '2.0', id: 5, method: 'tools/call', params: { name: 'shell', arguments: {} } })).result.isError).toBe(true)
    expect(await protocol({ jsonrpc: '2.0', method: 'notifications/initialized' })).toBeUndefined()
    expect((await protocol([])).error.code).toBe(-32600)
  })
  it('uses real catalogue, module guides, card conflicts and all published USB combinations', async () => {
    const catalogue = await service.call('site_catalogue', { machine: 'octatrack', beta: true })
    expect(catalogue.machines.some(item => item.id === 'octatrack')).toBe(true)
    expect((await service.call('site_module', { id: 'everb' })).controls.length).toBeGreaterThan(0)
    expect((await service.call('site_selection', { moduleIds: ['vector', 'analog-bassdrum'] })).conflicts.length).toBeGreaterThan(0)
    const usb = catalogue.modules.filter(module => module.usb).map(module => module.id)
    expect(usb.length).toBeGreaterThanOrEqual(4)
    for (let mask = 1; mask < 1 << usb.length; mask++) {
      const moduleIds = usb.filter((_, index) => mask & 1 << index)
      const prepared = await service.call('site_selection', { moduleIds, usb: true, capabilities: { abi: 8, features: 7, maxSites: 128, maxCopies: 128 } })
      expect(prepared.changes).toHaveLength(moduleIds.length)
      expect(prepared.changes.every(change => /^[a-f0-9]{64}$/.test(change.sha256) && change.undoSha256)).toBe(true)
    }
    await expect(service.call('site_selection', { moduleIds: ['analog-bassdrum'], usb: true })).rejects.toThrow('USB')
  })
  it('round trips sets through frontend validation without including private firmware', async () => {
    const created = await service.call('set_save', { name: 'MCP test', moduleIds: ['miniverb'] })
    const updated = await service.call('set_save', { id: created.id, name: 'Edited', moduleIds: ['everb', 'miniverb'] })
    expect(updated.id).toBe(created.id)
    expect(updated.createdAt).toBe(created.createdAt)
    const backup = await service.call('set_export')
    expect(backup.firmwareIncluded).toBe(false)
    expect(backup.configurations).toHaveLength(1)
    const old = { ...updated, id: 'imported', moduleVersions: { everb: '0.0.1', miniverb: '0.0.1' } }
    await service.call('set_import', { configurations: [old] })
    expect((await service.call('set_list')).configurations.find(item => item.id === 'imported').moduleVersions).toEqual(updated.moduleVersions)
    expect(JSON.parse(await readFile(join(folder, 'sets.json'), 'utf8'))).toHaveLength(2)
    await expect(service.call('set_save', { name: 'Invalid', moduleIds: ['not-a-module'] })).rejects.toThrow('Unknown module')
    await expect(service.call('set_import', { configurations: [{ ...updated, id: 'invalid', keepStockFx2: 'no' }] })).rejects.toThrow('unreadable')
    expect((await service.call('set_list')).configurations).toHaveLength(2)
    await service.call('set_delete', { id: created.id })
    expect((await service.call('set_list')).configurations).toHaveLength(1)
  })
  it('requires explicit API/device write opt-ins and rejects caller-selected file paths', async () => {
    await expect(service.call('api_request', { path: '/forum/threads', method: 'POST', body: {}, confirm: true })).rejects.toThrow('--allow-api-writes')
    await expect(service.call('device_status')).rejects.toThrow('--device-socket')
    await expect(service.call('device_trial', { review: 'anything' })).rejects.toThrow('--allow-device-writes')
    await expect(service.call('firmware_download', { request: {} })).rejects.toThrow('--stock')
    await expect(service.call('firmware_download', { request: {}, stock: '/etc/passwd' })).rejects.toThrow('Unexpected')
    await expect(service.call('set_save', { name: 'Duplicate', moduleIds: ['everb', 'everb'] })).rejects.toThrow('unique')
  })
  it('allows only frontend API routes on the startup-selected origin', () => {
    expect(validateApiPath('/forum/threads?q=echo+delay')).toBe('/forum/threads?q=echo+delay')
    expect(validateApiPath('/auth/session')).toBe('/auth/session')
    expect(validateApiPath('/auth/build-access')).toBe('/auth/build-access')
    expect(validateApiPath('/auth/base-install-prompt')).toBe('/auth/base-install-prompt')
    for (const path of ['https://evil.test/api', '//evil.test/api', '/forum/../auth/login', '/forum/%2e%2e', '/forum\\evil', '/auth/login', '/developer/auth/token', '/admin/keys', '/raw-memory']) expect(() => validateApiPath(path)).toThrow()
  })
  it('refuses unsafe API origins and non-private/symlinked credential files', async () => {
    await expect(createFrontendTools({ dataDir: folder, apiBase: 'http://example.test/api' })).rejects.toThrow('HTTPS')
    const credentials = join(folder, 'credentials.json'), alias = join(folder, 'alias.json')
    await writeFile(credentials, JSON.stringify({ session: 'not a secret for tests' }), { mode: 0o644 })
    await expect(createFrontendTools({ dataDir: folder, sessionFile: credentials })).rejects.toThrow('private')
    await chmod(credentials, 0o600); await symlink(credentials, alias)
    await expect(createFrontendTools({ dataDir: folder, sessionFile: alias })).rejects.toThrow('private')
  }, 30000)
  it('isolates workspace ownership and emits only JSON-RPC to stdout in a real stdio client', async () => {
    const other = await mkdtemp(join(tmpdir(), 'modwerk-mcp-cli-test-'))
    const script = fileURLToPath(new URL('./frontend-mcp.mjs', import.meta.url))
    try {
      await expect(createFrontendTools({ dataDir: other })).rejects.toThrow('separate MCP process')
      await expect(promisify(execFile)(process.execPath, [script, '--data-dir', folder])).rejects.toThrow('already locked')
      const candidate = join(other, 'candidate'), workspace = join(other, 'state')
      await mkdir(candidate)
      // Candidate checkouts may predate the MCP itself. Read their real source,
      // without requiring a copy of the bridge/server in the selected root.
      const sourceRoot = fileURLToPath(new URL('../', import.meta.url))
      for (const directory of ['src', 'public', 'vendor']) await symlink(join(sourceRoot, directory), join(candidate, directory), 'dir')
      const input = [
        { jsonrpc: '2.0', id: 1, method: 'initialize' },
        { jsonrpc: '2.0', id: 2, method: 'tools/list' },
        { jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: 'site_features', arguments: {} } },
      ].map(value => JSON.stringify(value)).join('\n') + '\n'
      const result = await new Promise((resolve, reject) => {
        const child = execFile(process.execPath, [script, '--data-dir', workspace, '--frontend-root', candidate], { timeout: 20000 }, (error, stdout, stderr) => error ? reject(error) : resolve({ stdout, stderr }))
        child.stdin.end(input)
      })
      const replies = result.stdout.trim().split('\n').map(line => JSON.parse(line))
      expect(replies.map(reply => reply.id)).toEqual([1, 2, 3])
      expect(replies.every(reply => reply.jsonrpc === '2.0' && reply.result)).toBe(true)
      expect(replies[2].result.structuredContent.beta).toBe(true)
      await expect(readFile(join(workspace, '.mcp-lock/owner.json'))).rejects.toMatchObject({ code: 'ENOENT' })
    } finally { await rm(other, { recursive: true, force: true }) }
  }, 30000)
})
