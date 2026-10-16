import test from 'node:test'
import assert from 'node:assert/strict'
import { bundleSessions, literal, mergeOfficial, dateKey } from './update-courses.mjs'

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
test('a renamed lecture with an existing PDF adds PPT without duplicating the lecture',()=>{
 const c=original();c.items[0].readings=[{label:'Introduction & Overview',url:'https://example.edu/intro.pdf'}]
 const p=parsed();p.units[0]={title:'Introduction',date:'',resources:[{label:'Intro',url:'https://example.edu/intro.pdf'},{label:'PPT',url:'https://example.edu/intro.pptx'}],readings:[]}
 const {course}=mergeOfficial(c,p,config)
 assert.equal(course.items.length,3);assert.equal(course.items[0].resources.length,1)
 assert.equal(course.items[0].resources[0].url,'https://example.edu/intro.pptx')
})
