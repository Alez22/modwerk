// SPDX-License-Identifier: GPL-3.0-or-later
// Every Digitakt/Digitone module PR appends to the same shared catalogue files, so after one merges the others
// conflict with main. After `git merge main` stops on those conflicts, this resolves them entry by entry:
//   npm run catalog:resolve        then review, `git commit` and `npm run pr:ready`
// It reads the merge's three sides as Git objects and runs no module code.
import { execFileSync } from 'node:child_process'
import { createHash } from 'node:crypto'
import { writeFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const CATALOG = 'vendor/elekloader/catalog/catalog.json', LOCK = 'vendor/elekloader/elekloader.lock.json'
// Each file's JSON indent and its lists merged per entry. Each entry depends only on its own module, so merging
// entries gives what the generators would write. The Octatrack catalogue is left out on purpose: its source revision
// binds every compiled package, so two Octatrack PRs need a rebuild, not a merge.
const FILES = {
  'src/catalog/machine-modules.json': { indent: 2, lists: { modules: row => row.machine + '/' + row.id } },
  'src/community/module-changelogs.json': { indent: 2, lists: {} },
  [CATALOG]: { indent: 1, lists: { cores: pin => pin.file, mods: pin => pin.file } },
  [LOCK]: { indent: 1, lists: {} },
}
const sha = text => createHash('sha256').update(text).digest('hex')
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b)
const plain = value => value !== null && typeof value === 'object' && !Array.isArray(value)

/** Three-way JSON merge: a change on one side wins; objects merge by key and `lists` by entry id; any other value
 * changed differently on both sides throws. Order: theirs (main), then what only ours (the PR) adds. */
export function merge3(base, ours, theirs, lists, path) {
  if (same(ours, theirs) || same(ours, base)) return theirs
  if (same(theirs, base)) return ours
  const id = lists?.[path.split('.').pop()]
  if (id && [base ?? [], ours, theirs].every(Array.isArray)) {
    const index = list => new Map(list.map(row => [id(row), row]))
    const b = index(base ?? []), o = index(ours), t = index(theirs)
    return [...new Set([...t.keys(), ...o.keys()])].map(key => merge3(b.get(key), o.get(key), t.get(key), null, path + '[' + key + ']')).filter(row => row !== undefined)
  }
  if (lists && [base, ours, theirs].every(plain)) {
    const out = {}
    for (const key of new Set([...Object.keys(theirs), ...Object.keys(ours)])) {
      const value = merge3(base[key], ours[key], theirs[key], lists, path + '.' + key)
      if (value !== undefined) out[key] = value
    }
    return out
  }
  throw new Error(path + ' changed differently on both sides')
}

// Whole-catalogue hashes and counts always differ between two PRs; blank them and derive them after the merge.
function blank(path, value) {
  if (value === undefined) return value
  if (path === CATALOG) value.revision = ''
  if (path === LOCK) Object.assign(value.catalog, { revision: '', sha256: '', cores: 0, mods: 0 })
  return value
}

/** Resolves an in-progress `git merge` in `cwd` whose only conflicts are in the shared catalogue files. */
export function resolveCatalogMerge(cwd) {
  const git = (...args) => execFileSync('git', args, { cwd, encoding: 'utf8', maxBuffer: 256 * 1024 * 1024 })
  const conflicted = git('diff', '--name-only', '--diff-filter=U', '-z').split('\0').filter(Boolean)
  const other = conflicted.filter(path => !(path in FILES))
  if (other.length) throw new Error('Conflicts outside the shared catalogue need a person: ' + other.join(', '))
  const refs = [git('merge-base', 'HEAD', 'MERGE_HEAD').trim(), 'HEAD', 'MERGE_HEAD']
  const read = (ref, path) => git('ls-tree', '--name-only', ref, '--', path).trim() === path ? git('show', ref + ':' + path) : undefined
  const merged = {}
  for (const [path, { indent, lists }] of Object.entries(FILES)) {
    const [base, ours, theirs] = refs.map(ref => read(ref, path))
    if (ours === undefined && theirs === undefined) continue
    // Refuse rather than silently reformat a file whose layout changed on main.
    if (theirs !== undefined && JSON.stringify(JSON.parse(theirs), null, indent) + '\n' !== theirs) throw new Error(path + ' on main is not in the layout this resolver writes')
    const value = merge3(...[base, ours, theirs].map(text => blank(path, text === undefined ? undefined : JSON.parse(text))), lists, path)
    if (value === undefined) throw new Error(path + ' was deleted on one side')
    merged[path] = value
  }
  merged['src/catalog/machine-modules.json']?.modules.sort((a, b) => a.machine.localeCompare(b.machine) || a.id.localeCompare(b.id))
  const text = path => JSON.stringify(merged[path], null, FILES[path].indent) + '\n'
  const catalog = merged[CATALOG]
  if (catalog) {
    catalog.revision = sha(JSON.stringify({ schema: catalog.schema, kind: catalog.kind, cores: catalog.cores, mods: catalog.mods }))
    if (merged[LOCK]) Object.assign(merged[LOCK].catalog, { revision: catalog.revision, sha256: sha(text(CATALOG)), cores: catalog.cores.length, mods: catalog.mods.length })
  }
  for (const path of Object.keys(merged)) { writeFileSync(resolve(cwd, path), text(path)); git('add', '--', path) }
  if (git('diff', '--name-only', '--diff-filter=U').trim()) throw new Error('Unresolved conflicts remain')
  return Object.keys(merged)
}

if (process.argv[1] === fileURLToPath(import.meta.url)) console.log('Resolved ' + resolveCatalogMerge(process.cwd()).join(', ') + '. Review them, git commit, then npm run pr:ready.')
