import { afterEach, describe, expect, it, vi } from 'vitest'
import type { DatabaseSync } from 'node:sqlite'
import { testServer } from './test-server'
import { digest } from '../../server/security'
import { cleanupOctatrackDiagnostics, octatrackDiagnosticRoutes } from '../../server/octatrack-diagnostics'
import type { User } from '../../server/platform'
import { OCTATRACK_DIAGNOSTICS_VERSION as version } from './octatrack-diagnostics-contract'
import { handleCommunity } from '../../server/transport'
const databases: DatabaseSync[] = []
afterEach(()=>{vi.unstubAllGlobals();databases.splice(0).forEach(db=>db.close())})
async function fixture() {
  const server=await testServer();databases.push(server.db)
  for(const [id,token,beta] of [['tester','a'.repeat(64),1],['another','b'.repeat(64),1],['member','c'.repeat(64),0]] as const) {
    server.db.prepare('INSERT INTO users(id,display_name,username,email_verified,beta_tester) VALUES(?,?,?,1,?)').run(id,id,id,beta)
    server.db.prepare('INSERT INTO sessions(token_hash,user_id,expires) VALUES(?,?,?)').run(await digest(token),id,Math.floor(Date.now()/1000)+3600)
  }
  const admin=(await(await server.call('/auth/admin','POST',{key:'e'.repeat(64)})).json()).token as string
  const data=()=>({id:crypto.randomUUID(),event:'sync_failed',phase:'sending',base:'a'.repeat(64),error:'device',refusal:3,modules:[{id:'everb',catalogVersion:'0.1.1'}]})
  const consent=(enabled=true)=>server.call('/octatrack/diagnostics/consent','PUT',{enabled,version},'a'.repeat(64))
  const send=(body:unknown=data(),token='a'.repeat(64))=>server.call('/octatrack/diagnostics','POST',{version,data:body},token)
  return {...server,admin,data,consent,send}
}
describe('private Octatrack beta diagnostics',()=>{
  it('requires current explicit consent and verified beta access; never publishes reports',async()=>{
    const {call,db,consent,send}=await fixture()
    expect((await send(undefined,'')).status).toBe(401)
    expect((await send()).status).toBe(403)
    expect((await call('/octatrack/diagnostics/consent','PUT',{enabled:true,version},'c'.repeat(64))).status).toBe(403)
    expect((await call('/octatrack/diagnostics/consent','PUT',{enabled:true,version:'old'},'a'.repeat(64))).status).toBe(400)
    expect((await consent()).status).toBe(200)
    expect((await send()).status).toBe(200)
    expect(db.prepare('SELECT count(*) AS n FROM octatrack_diagnostic_events').get()).toEqual({n:1})
    for(const table of ['issues','issue_logs','notifications'])expect(db.prepare(`SELECT count(*) AS n FROM ${table}`).get()).toEqual({n:0})
    db.prepare("UPDATE users SET beta_tester=0 WHERE id='tester'").run()
    expect((await send()).status).toBe(403)
    expect((await consent(false)).status).toBe(200)
  })
  it('deduplicates retries, isolates accounts, permits admin review and deletes on withdrawal',async()=>{
    const {call,db,admin,consent,send,data}=await fixture(),payload=data()
    await consent();await send(payload);await send(payload)
    expect(db.prepare('SELECT count(*) AS n FROM octatrack_diagnostic_events').get()).toEqual({n:1})
    expect((await call('/admin/octatrack/diagnostics','GET',undefined,'a'.repeat(64))).status).toBe(403)
    expect(await(await call('/octatrack/diagnostics','GET',undefined,'b'.repeat(64))).json()).toEqual({events:[]})
    const review=await(await call('/admin/octatrack/diagnostics','GET',undefined,'',admin)).json()
    expect(review.events).toHaveLength(1);expect(review.events[0]).toMatchObject({username:'tester',data:payload})
    await consent(false)
    expect((await send(payload)).status).toBe(403)
    expect(db.prepare('SELECT count(*) AS n FROM octatrack_diagnostic_events').get()).toEqual({n:0})
  })
  it('rejects arbitrary text, raw logs, unknown modules, invalid readings and extra consent fields',async()=>{
    const {call,consent,send,data}=await fixture();await consent()
    for(const extra of [{log:'private raw log'},{project:'My private project'},{serial:'private'},{error:'free-form error'},{refusal:-1},{base:'not-a-hash'},{modules:[{id:'unknown',catalogVersion:'1'}]},{reading:{state:2}},{packages:[{sha256:'a'.repeat(64),bytes:1,data:'raw'}]}])expect((await send({...data(),...extra})).status).toBe(400)
    expect((await call('/octatrack/diagnostics/consent','PUT',{enabled:true,version,logs:true},'a'.repeat(64))).status).toBe(400)
    expect((await call('/octatrack/diagnostics','POST',{version,data:data()},'a'.repeat(64),'','https://evil.test')).status).toBe(403)
  })
  it('expires consent and records, and cascades account deletion',async()=>{
    const {call,db,env,consent,send}=await fixture();await consent();await send()
    db.prepare("UPDATE octatrack_diagnostic_events SET created_at='2020-01-01T00:00:00.000Z'").run()
    expect(await(await call('/octatrack/diagnostics','GET',undefined,'a'.repeat(64))).json()).toEqual({events:[]})
    await cleanupOctatrackDiagnostics(env.DB!)
    expect(db.prepare('SELECT count(*) AS n FROM octatrack_diagnostic_events').get()).toEqual({n:0})
    db.prepare("UPDATE octatrack_diagnostic_consent SET changed_at='2020-01-01T00:00:00.000Z'").run()
    expect((await send()).status).toBe(403)
    await consent();await send();db.prepare("DELETE FROM users WHERE id='tester'").run()
    expect(db.prepare('SELECT count(*) AS n FROM octatrack_diagnostic_events').get()).toEqual({n:0})
    expect(db.prepare('SELECT count(*) AS n FROM octatrack_diagnostic_consent').get()).toEqual({n:0})
  })
  it('rechecks account and beta eligibility after an in-flight request body completes',async()=>{
    const {db,env,consent,data,call,admin}=await fixture();await consent()
    const member=db.prepare("SELECT * FROM users WHERE id='tester'").get() as unknown as User
    async function pending(path:string,method:string,body:unknown,mutate:()=>void) {
      let complete:()=>void=()=>{}
      const stream=new ReadableStream({start(controller){complete=()=>{controller.enqueue(new TextEncoder().encode(JSON.stringify(body)));controller.close()}}})
      const request=new Request('https://api.example.test/api'+path,{method,headers:{'Content-Type':'application/json'},body:stream,duplex:'half'} as RequestInit)
      const response=octatrackDiagnosticRoutes(request,env.DB!,member,false)
      await new Promise(resolve=>setTimeout(resolve,0));mutate();complete();return response
    }
    await pending('/octatrack/diagnostics','POST',{version,data:data()},()=>db.prepare("UPDATE users SET beta_tester=0 WHERE id='tester'").run())
    expect(db.prepare('SELECT count(*) AS n FROM octatrack_diagnostic_events').get()).toEqual({n:0})
    db.prepare("UPDATE users SET beta_tester=1 WHERE id='tester'").run()
    await pending('/octatrack/diagnostics/consent','PUT',{enabled:true,version},()=>{db.prepare("UPDATE users SET suspended=1,email_verified=0 WHERE id='tester'").run();db.prepare("DELETE FROM octatrack_diagnostic_consent WHERE user_id='tester'").run()})
    expect(db.prepare('SELECT count(*) AS n FROM octatrack_diagnostic_consent').get()).toEqual({n:0})
    expect((await(await call('/admin/octatrack/diagnostics','GET',undefined,'',admin)).json()).events).toEqual([])
  })
  it('deletes private records and disables consent when beta access is removed',async()=>{
    const {db,call,admin,consent,send}=await fixture();await consent();await send()
    expect((await call('/admin/forum/beta-testers/tester','PUT',{betaTester:false,reason:'Beta complete'},'',admin)).status).toBe(200)
    expect(db.prepare('SELECT count(*) AS n FROM octatrack_diagnostic_events').get()).toEqual({n:0})
    expect(db.prepare("SELECT enabled FROM octatrack_diagnostic_consent WHERE user_id='tester'").get()).toEqual({enabled:0})
  })
  it('does not let a delayed enable from another tab supersede a later withdrawal',async()=>{
    const {db,env,consent,send}=await fixture();await consent();await send()
    const member=db.prepare("SELECT * FROM users WHERE id='tester'").get() as unknown as User
    let complete:()=>void=()=>{}
    const stream=new ReadableStream({start(controller){complete=()=>{controller.enqueue(new TextEncoder().encode(JSON.stringify({enabled:true,version})));controller.close()}}})
    const request=new Request('https://api.example.test/api/octatrack/diagnostics/consent',{method:'PUT',headers:{'Content-Type':'application/json'},body:stream,duplex:'half'} as RequestInit)
    const pending=octatrackDiagnosticRoutes(request,env.DB!,member,false)
    await new Promise(resolve=>setTimeout(resolve,5));await consent(false);complete();await pending
    expect(db.prepare("SELECT enabled FROM octatrack_diagnostic_consent WHERE user_id='tester'").get()).toEqual({enabled:0})
    expect(db.prepare('SELECT count(*) AS n FROM octatrack_diagnostic_events').get()).toEqual({n:0})
    expect((await send()).status).toBe(403)
  })
  it('counts only fixed actions without identities and honors browser privacy signals',async()=>{
    const {call,db,env,consent,data}=await fixture()
    expect((await call('/usage/count','POST',{event:'usb_sync_started'})).status).toBe(200)
    expect((await call('/usage/count','POST',{event:'usb_sync_started',moduleId:'everb'})).status).toBe(400)
    expect(db.prepare('SELECT day,event,count FROM octatrack_beta_daily').all()).toHaveLength(1)
    expect(db.prepare('SELECT count(*) AS n FROM usage_visitors').get()).toEqual({n:0})
    await consent()
    const response=await handleCommunity(new Request('https://api.example.test/api/octatrack/diagnostics',{method:'POST',headers:{Origin:'https://octamod.test',Authorization:'Bearer '+'a'.repeat(64),'Content-Type':'application/json',DNT:'1'},body:JSON.stringify({version,data:data()})}),env)
    expect(response.status).toBe(200);expect(await response.json()).toEqual({ok:true,stored:false})
    expect(db.prepare('SELECT count(*) AS n FROM octatrack_diagnostic_events').get()).toEqual({n:0})
  })
})
