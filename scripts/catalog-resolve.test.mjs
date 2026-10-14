import { describe, expect, it } from 'vitest'
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, resolve } from 'node:path'
import { merge3, resolveCatalogMerge } from './catalog-resolve.mjs'

const sha = text => createHash('sha256').update(text).digest('hex')
const row = id => ({ machine: 'digitakt', id, version: '1.0.0' })
const pin = id => ({ file: id + '.elemod', sha256: id, id })

// One repository state with these module ids in all four shared files.
function write(dir, ids, notes = {}) {
  const put = (path, value, indent) => { mkdirSync(dirname(resolve(dir, path)), { recursive: true }); writeFileSync(resolve(dir, path), JSON.stringify(value, null, indent) + '\n') }
  put('src/catalog/machine-modules.json', { schemaVersion: 3, modules: ids.map(row) }, 2)
  put('src/community/module-changelogs.json', { schemaVersion: 1, modules: Object.fromEntries(ids.map(id => [id, [{ version: '1.0.0', changes: [notes[id] ?? 'First release.'] }]])) }, 2)
  put('vendor/elekloader/catalog/catalog.json', { schema: 1, kind: 'elekloader-catalog', revision: ids.join(), cores: [], mods: ids.map(pin) }, 1)
  put('vendor/elekloader/elekloader.lock.json', { schema: 1, kind: 'elekloader-kit-lock', catalog: { revision: ids.join(), sha256: ids.join(), cores: 0, mods: ids.length } }, 1)
}
function conflictedRepo(main, pr, notes = {}) {
  const dir = mkdtempSync(resolve(tmpdir(), 'catalog-resolve-'))
  const git = (...args) => execFileSync('git', ['-c', 'user.name=t', '-c', 'user.email=t@t', ...args], { cwd: dir, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] })
  git('init', '-q', '-b', 'main'); write(dir, ['a']); git('add', '-A'); git('commit', '-qm', 'base')
  git('checkout', '-qb', 'pr'); write(dir, pr, notes.pr); git('commit', '-qam', 'pr')
  git('checkout', '-q', 'main'); write(dir, main, notes.main); git('commit', '-qam', 'main')
  git('checkout', '-q', 'pr')
  expect(() => git('merge', '-q', 'main')).toThrow()
  return { dir, git }
}

describe('catalog resolve', () => {
  it('keeps main’s order, appends the PR’s new entries and keeps one-sided changes', () => {
    const lists = { modules: entry => entry.id }
    expect(merge3({ v: 1, modules: [{ id: 'a' }] }, { v: 1, modules: [{ id: 'a' }, { id: 'c' }] }, { v: 2, modules: [{ id: 'a' }, { id: 'b' }] }, lists, 'file'))
      .toEqual({ v: 2, modules: [{ id: 'a' }, { id: 'b' }, { id: 'c' }] })
    expect(() => merge3({ modules: [{ id: 'a', v: 1 }] }, { modules: [{ id: 'a', v: 2 }] }, { modules: [{ id: 'a', v: 3 }] }, lists, 'file')).toThrow('file.modules[a] changed differently on both sides')
  })

  it('resolves two module additions and derives the catalogue revision and lock', () => {
    const { dir, git } = conflictedRepo(['a', 'b'], ['a', 'c'])
    try {
      resolveCatalogMerge(dir)
      const json = path => JSON.parse(readFileSync(resolve(dir, path), 'utf8'))
      expect(json('src/catalog/machine-modules.json').modules.map(entry => entry.id)).toEqual(['a', 'b', 'c'])
      expect(Object.keys(json('src/community/module-changelogs.json').modules)).toEqual(['a', 'b', 'c'])
      const text = readFileSync(resolve(dir, 'vendor/elekloader/catalog/catalog.json'), 'utf8'), catalog = JSON.parse(text)
      expect(catalog.mods.map(entry => entry.id)).toEqual(['a', 'b', 'c'])
      expect(catalog.revision).toBe(sha(JSON.stringify({ schema: 1, kind: 'elekloader-catalog', cores: [], mods: catalog.mods })))
      expect(json('vendor/elekloader/elekloader.lock.json').catalog).toEqual({ revision: catalog.revision, sha256: sha(text), cores: 0, mods: 3 })
      expect(git('diff', '--name-only', '--diff-filter=U')).toBe('')
    } finally { rmSync(dir, { recursive: true, force: true }) }
  })

  it('leaves a module’s notes changed on both sides to a person', () => {
    const { dir } = conflictedRepo(['a', 'b'], ['a', 'c'], { main: { a: 'Main note.' }, pr: { a: 'PR note.' } })
    try { expect(() => resolveCatalogMerge(dir)).toThrow('modules.a changed differently on both sides') }
    finally { rmSync(dir, { recursive: true, force: true }) }
  })
})
