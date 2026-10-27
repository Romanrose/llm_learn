import test from 'node:test'
import assert from 'node:assert/strict'
import { bundleSessions, literal, mergeOfficial, dateKey, semesterMatches, text, run } from './update-courses.mjs'

import fs from 'node:fs'
import os from 'node:os'
import { join } from 'node:path'
import { parse, stringify } from 'yaml'

const config = { adapter:'jhu',url:'https://example.edu/fall26/' }
const original = () => ({ id:'sample',publishOutputs:true,paths:{root:'courses/robotics-hardware/sample'},schedule:{source:config.url},items:[1,2,3].map(n=>({id:`lecture-0${n}`,order:n,date:`2026-10-${String(n).padStart(2,'0')}`,title:`Session ${n}`,status:n===1?'published':'scheduled',resources:[],readings:[],outputs:n===1?[{id:'lecture-note',source:'reviewed.md'}]:[],generation:{state:n===1?'reviewed':'pending'}})),practice:[] })
const parsed = () => ({units:[1,2,3].map(n=>({title:`Session ${n}`,date:`Oct ${n}`,resources:n===1?[{label:'New slides',url:'https://example.edu/slides.pdf'}]:[],readings:[]})),practices:[]})

test('merges links while preserving reviewed outputs, state and stable IDs',()=>{
 const before=original();const {course,changes}=mergeOfficial(before,parsed(),config,'2026-10-16')
 assert.equal(changes.length,1);assert.equal(before.items[0].resources.length,0)
 assert.deepEqual(course.items.map(i=>i.id),before.items.map(i=>i.id))
 assert.deepEqual(course.items[0].outputs,before.items[0].outputs)
 assert.deepEqual(course.items[0].generation,before.items[0].generation)
 assert.equal(course.items[0].status,'published');assert.equal(course.publishOutputs,true)
})
test('repeat checks produce no writes, timestamps, duplicate links or new units',()=>{
 const once=mergeOfficial(original(),parsed(),config,'2026-10-16').course
 const again=mergeOfficial(once,parsed(),config,'2026-10-17')
 assert.deepEqual(again.changes,[]);assert.deepEqual(again.course,once)
})
test('broken layout cannot replace a catalog with an empty schedule',()=>{
 assert.throws(()=>mergeOfficial(original(),{units:[],practices:[]},config),/Too few matched/)
})
test('new dated sessions append an ID and never renumber existing sessions',()=>{
 const p=parsed();p.units.push({title:'New session',date:'Oct 20',resources:[{label:'Slides',url:'https://example.edu/new.pdf'}],readings:[]})
 const {course}=mergeOfficial(original(),p,config,'2026-10-16')
 assert.equal(course.items.at(-1).id,'lecture-04');assert.equal(course.items.at(-1).status,'scheduled');assert.deepEqual(course.items.at(-1).outputs,[])
})
test('curated assignment GitHub is preferred to a newly listed handout',()=>{
 const c=original();c.practice=[{id:'assignment-2',title:'Starter',url:'https://github.com/official/starter'}]
 const p=parsed();p.practices=[{label:'Assignment 2',url:'https://example.edu/assignment2.html'}]
 assert.deepEqual(mergeOfficial(c,p,config).course.practice,c.practice)
})
test('official JS data is read without executing remote expressions',()=>{
 assert.deepEqual(bundleSessions('const data=[{code:"1a",date:"Oct 1",title:"One"},{code:"1b",date:"Oct 2",title:"Two"}]').map(s=>s.title),['One','Two'])
 assert.throws(()=>bundleSessions('const data=[{code:"1a",date:"Oct 1",title:process.exit()},{code:"1b",date:"Oct 2",title:"Two"}]'),/Executable/)
 assert.throws(()=>literal({type:'CallExpression'}),/Executable/)
})
test('dates normalize across official course formats',()=>{
 assert.equal(dateKey('Wed Sep 23, 2026'),'2026-09-23');assert.equal(dateKey('2026-10-15'),'2026-10-15');assert.equal(dateKey('TBA'),'')
})
test('a new semester cannot pass by containing an old-offering link',()=>{
 assert.equal(semesterMatches('<h1>Spring 2027</h1><a>Fall 2026 archive</a>','https://example.edu/','Fall\\s*2026'),false)
 assert.equal(semesterMatches('<h1>Fall 2026</h1>','https://example.edu/','Fall\\s*2026'),true)
 assert.equal(semesterMatches('<h1>Fall 2027</h1>','https://example.edu/fa26/','fa26'),false)
})
test('a renamed lecture with an existing PDF adds PPT without duplicating the lecture',()=>{
 const c=original();c.items[0].readings=[{label:'Introduction & Overview',url:'https://example.edu/intro.pdf'}]
 const p=parsed();p.units[0]={title:'Introduction',date:'',resources:[{label:'Intro',url:'https://example.edu/intro.pdf'},{label:'PPT',url:'https://example.edu/intro.pptx'}],readings:[]}
 const {course}=mergeOfficial(c,p,config)
 assert.equal(course.items.length,3);assert.equal(course.items[0].resources.length,1)
 assert.equal(course.items[0].resources[0].url,'https://example.edu/intro.pptx')
})

const response = (url, overrides = {}) => ({ ok:true, url, headers:new Headers({'content-type':'text/html'}), text:async()=>'<h1>Fall 2026</h1>', ...overrides })
test('temporary network errors retry with backoff and preserve underlying diagnostics',async()=>{
 const waits=[];let calls=0
 const fetchImpl=async()=>{calls++;throw new TypeError('fetch failed',{cause:Object.assign(new Error('TLS connection reset'),{code:'ECONNRESET'})})}
 await assert.rejects(text(config.url,{fetchImpl,sleep:async n=>waits.push(n)}),/after 3 attempt.*ECONNRESET: TLS connection reset/)
 assert.equal(calls,3);assert.deepEqual(waits,[1000,2000])
 calls=0
 assert.equal(await text(config.url,{fetchImpl:async()=>{if (++calls<3) return response(config.url,{ok:false,status:503});return response(config.url)},sleep:async()=>{}}),'<h1>Fall 2026</h1>')
 assert.equal(calls,3)
})
test('document and permanent HTTP failures are not retried or accepted',async()=>{
 for (const overrides of [{url:'https://other.edu/fall26/'},{url:config.url+'spring27/'},{headers:new Headers({'content-type':'application/pdf'})},{ok:false,status:404}]) {
  let calls=0
  await assert.rejects(text(config.url,{fetchImpl:async()=>{calls++;return response(config.url,overrides)},sleep:async()=>assert.fail('unexpected retry')}))
  assert.equal(calls,1)
 }
})
function fixture(t, ids) {
 const workspace=fs.mkdtempSync(join(os.tmpdir(),'course-updates-'));t.after(()=>fs.rmSync(workspace,{recursive:true,force:true}))
 fs.mkdirSync(join(workspace,'website/catalog-data/courses'),{recursive:true})
 const configs=ids.map(id=>({id,adapter:'jhu',url:`https://example.edu/${id}/`,semester:'Fall\\s*2026',until:'2099-01-31'}))
 const paths=Object.fromEntries(ids.map(id=>[id,join(workspace,`website/catalog-data/courses/${id}.yaml`)]))
 for(const id of ids) fs.writeFileSync(paths[id],stringify({...original(),id,paths:{resources:`courses/${id}/resources`}}))
 const output=join(workspace,'output');const summary=join(workspace,'summary')
 const options={workspace,configs,only:undefined,apply:true,env:{GITHUB_OUTPUT:output,GITHUB_STEP_SUMMARY:summary},fetchText:async()=>'<h1>Fall 2026</h1>',parsePage:async()=>({rows:[1,2,3].map(n=>[{text:`Oct ${n}`},{text:`Session ${n}`},{text:''},{links:n===1?[{label:'New slides',url:'https://example.edu/slides.pdf'}]:[]},{links:[]}])})}
 return {workspace,paths,output,summary,options}
}
test('a failed middle source leaves its files untouched while both healthy courses write and report',async t=>{
 const f=fixture(t,['before','broken','after']);const before=fs.readFileSync(f.paths.broken,'utf8')
 const result=await run({...f.options,fetchText:async url=>{if(url.includes('/broken/'))throw new TypeError('fetch failed',{cause:Object.assign(new Error('reset'),{code:'ECONNRESET'})});return '<h1>Fall 2026</h1>'}})
 assert.equal(result.hadErrors,true);assert.equal(result.changed,true)
 assert.deepEqual(result.results.map(r=>r.status),['updated','error','updated'])
 assert.equal(fs.readFileSync(f.paths.broken,'utf8'),before)
 assert.equal(fs.existsSync(join(f.workspace,'courses/broken/resources/manifest.yaml')),false)
 for (const id of ['before','after']) {
  assert.equal(parse(fs.readFileSync(f.paths[id],'utf8')).items[0].resources.length,1)
  assert.equal(parse(fs.readFileSync(join(f.workspace,`courses/${id}/resources/manifest.yaml`),'utf8')).resources.length,1)
 }
 assert.match(fs.readFileSync(f.output,'utf8'),/changed=true\nhad_errors=true/)
 assert.match(fs.readFileSync(f.summary,'utf8'),/ECONNRESET/)
 assert.equal(JSON.parse(fs.readFileSync(join(f.workspace,'workflow/.runtime/course-updates/results.json')))[1].status,'error')
})
test('preview and all-source failures produce reports without writing course data',async t=>{
 const f=fixture(t,['one']);const before=fs.readFileSync(f.paths.one,'utf8')
 const preview=await run({...f.options,apply:false});assert.equal(preview.changed,false)
 assert.equal(fs.readFileSync(f.paths.one,'utf8'),before)
 const failed=await run({...f.options,fetchText:async()=>'<h1>Spring 2027</h1>'})
 assert.equal(failed.hadErrors,true);assert.equal(failed.changed,false)
 assert.equal(fs.readFileSync(f.paths.one,'utf8'),before)
})
test('broken layouts and invalid manifests cannot write their course while healthy sources progress',async t=>{
 const f=fixture(t,['layout','manifest','healthy']);const before=fs.readFileSync(f.paths.manifest,'utf8')
 const manifestPath=join(f.workspace,'courses/manifest/resources/manifest.yaml');fs.mkdirSync(join(f.workspace,'courses/manifest/resources'),{recursive:true});fs.writeFileSync(manifestPath,'resources: [broken')
 const result=await run({...f.options,parsePage:async(html,url)=>url.includes('/layout/')?{rows:[]}:f.options.parsePage()})
 assert.deepEqual(result.results.map(r=>r.status),['error','error','updated'])
 assert.equal(fs.readFileSync(f.paths.manifest,'utf8'),before)
 assert.equal(fs.readFileSync(manifestPath,'utf8'),'resources: [broken')
})

test('Actions publishes validated sources before its separate failure-report job',()=>{
 const workflow=parse(fs.readFileSync(new URL('../../.github/workflows/update-courses.yml',import.meta.url),'utf8'))
 const update=workflow.jobs.update;const sync=update.steps.find(s=>s.id==='sync')
 assert.equal(sync['continue-on-error'],true)
 assert.equal(update.outputs.had_errors,'${{ steps.sync.outputs.had_errors }}')
 assert.equal(workflow.jobs.deploy.needs,'update')
 const report=workflow.jobs['report-source-failures']
 assert.deepEqual(report.needs,['update','deploy'])
 assert.match(report.if,/always\(\).*had_errors == 'true'/)
 assert.match(report.steps[0].run,/exit 1/)
 assert.ok(update.steps.some(s=>s.if?.includes("had_errors != 'true'") && s.run==='exit 1'))
 const artifact=update.steps.find(s=>s.with?.name==='course-update-report')
 assert.equal(artifact.if,'always()');assert.equal(artifact.with['include-hidden-files'],true)
 for(const name of ['Build the complete site before publishing any changes','Commit the official resource update']) assert.equal(update.steps.find(s=>s.name===name).if,"steps.sync.outputs.changed == 'true'")
})
