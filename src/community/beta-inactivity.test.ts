import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { testServer } from './test-server'
import { betaIdleEmail, remindInactiveBetaTesters } from '../../server/beta-inactivity'
import worker from '../../worker'

const DAY = 86400, databases: Array<{ close(): void }> = [], mail: { to: string[]; subject: string }[] = []
let provider: () => Promise<Response>
beforeEach(() => {
  mail.length = 0; provider = async () => Response.json({ id: 'test-email' })
  vi.stubGlobal('fetch', vi.fn(async (url: string, options: RequestInit) => { if (url !== 'https://api.resend.com/emails') return new Response(null, { status: 404 }); mail.push(JSON.parse(String(options.body))); return provider() }))
  vi.stubGlobal('setTimeout', (callback: () => void) => { callback(); return 0 })
})
afterEach(() => { vi.unstubAllGlobals(); for (const db of databases.splice(0)) db.close() })

async function fixture() {
  const server = await testServer(); databases.push(server.db)
  const start = Math.floor(Date.now() / 1000)
  const sql = (seconds: number) => new Date(seconds * 1000).toISOString().slice(0, 19).replace('T', ' ')
  function tester(name: string, { joined = start - 30 * DAY, seen = null as number | null, admin = false } = {}) {
    server.db.prepare('INSERT INTO auth_users(id,name,email,emailVerified,createdAt,updatedAt) VALUES(?,?,?,1,0,0)').run(name, name, name + '@example.test')
    server.db.prepare('INSERT INTO users(id,username,display_name,email_verified,beta_tester,is_admin) VALUES(?,?,?,1,1,?)').run(name, name, name, Number(admin))
    server.db.prepare("INSERT INTO forum_moderation(id,actor_id,target,action,reason,created_at) VALUES(?,?,?,'beta-tester:accept','test',?)").run(crypto.randomUUID(), name, name, sql(joined))
    if (seen !== null) visit(name, seen)
  }
  const visit = (name: string, seen: number) => server.db.prepare('INSERT INTO member_presence(user_id,seen_at) VALUES(?,?) ON CONFLICT(user_id) DO UPDATE SET seen_at=excluded.seen_at').run(name, seen)
  const run = (at: number) => remindInactiveBetaTesters(server.env, server.env.DB!, at * 1000)
  const state = (name: string) => server.db.prepare('SELECT beta_tester AS tester,beta_reminded_at AS reminded FROM users WHERE id=?').get(name)
  return { ...server, start, tester, visit, run, state }
}

it('reminds a quiet tester once, frees the place five days later, and leaves visitors, newcomers and admins alone', async () => {
  const { db, start, tester, visit, run, state } = await fixture()
  tester('quiet', { seen: start - 6 * DAY })
  tester('returning', { seen: start - 6 * DAY })
  tester('active', { seen: start - DAY })
  tester('newcomer', { joined: start - DAY })
  tester('owner', { seen: start - 20 * DAY, admin: true })

  expect(await run(start)).toEqual({ reminded: 2, removed: 0 })
  expect(mail.map(message => message.to[0]).sort()).toEqual(['quiet@example.test', 'returning@example.test'])
  expect(mail[0]).toMatchObject(betaIdleEmail)
  expect(state('quiet')).toEqual({ tester: 1, reminded: start })
  expect(db.prepare("SELECT accepted FROM account_mail_daily WHERE purpose='beta'").get()).toEqual({ accepted: 2 })

  // Only one reminder per quiet spell.
  expect(await run(start + 3 * DAY)).toEqual({ reminded: 0, removed: 0 })
  visit('returning', start + 3 * DAY)
  // Five days on, the active tester and the never-seen newcomer have gone quiet too.
  expect(await run(start + 5 * DAY)).toEqual({ reminded: 2, removed: 1 })
  expect(state('quiet')).toEqual({ tester: 0, reminded: start })
  expect(state('returning')).toEqual({ tester: 1, reminded: start })
  expect(state('newcomer')).toEqual({ tester: 1, reminded: start + 5 * DAY })
  expect(db.prepare("SELECT target,reason FROM forum_moderation WHERE action='beta-tester:inactive'").all()).toEqual([{ target: 'quiet', reason: 'no visit for 5 days after the reminder' }])
  expect(mail).toHaveLength(4)

  // The visit started a new spell: five more quiet days bring a new reminder, not a removal.
  expect(await run(start + 8 * DAY)).toEqual({ reminded: 1, removed: 0 })
  expect(mail.at(-1)!.to).toEqual(['returning@example.test'])
  expect(state('returning')).toEqual({ tester: 1, reminded: start + 8 * DAY })
  expect(state('owner')).toEqual({ tester: 1, reminded: null })
})

it('keeps the place when the reminder was not accepted, and runs from the hourly cron', async () => {
  const { start, tester, run, state, env } = await fixture()
  tester('quiet', { seen: start - 6 * DAY })
  provider = async () => new Response('down', { status: 500 })
  expect(await run(start)).toEqual({ reminded: 0, removed: 0 })
  expect(state('quiet')).toEqual({ tester: 1, reminded: null })
  expect(await run(start + 6 * DAY)).toEqual({ reminded: 0, removed: 0 })
  expect(state('quiet')).toEqual({ tester: 1, reminded: null })

  provider = async () => Response.json({ id: 'test-email' })
  const jobs: Promise<unknown>[] = []
  worker.scheduled({ cron: '17 * * * *' }, env, { waitUntil: job => { jobs.push(job) } })
  await Promise.all(jobs)
  expect(mail.at(-1)!.to).toEqual(['quiet@example.test'])
  expect((state('quiet') as { reminded: number }).reminded).toBeGreaterThanOrEqual(start)
})
