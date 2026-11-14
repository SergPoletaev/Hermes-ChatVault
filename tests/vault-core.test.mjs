import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import vm from 'node:vm'

const code = fs.readFileSync(new URL('../src/vault-extra.js', import.meta.url),'utf8')
const o={vaultRedact:false,vaultImagesPdf:true,vaultImagesHtml:true,vaultImagesPng:true}
const context = vm.createContext({
  TextEncoder, Blob, Uint8Array, Uint32Array, Map, Set, Array, Date,
  optAtom:{get:()=>o},
  chshEmbeddedMedia:new Map(),
  chshPrepareExportTurns:async t=>t,
  stateAtom:{get:()=>({title:'Private conversation'})},
  t:()=> 'Chat',
  selectedIds:()=>[], turnsAtom:{get:()=>[]},
  metaAtom:{get:()=>null},
  buildMetaLine:()=>'', host:{}, download:()=>{},
})
vm.runInContext(code, context, {filename:'vault-extra.js'})
const run=(code)=>vm.runInContext(code,context)

test('opt-in heuristic text redaction', ()=>{
  o.vaultRedact=true
  const s='contact foo@example.net; pwd password=abcd12345; Bearer secretToken987; C:\\Users\\somebody\\Documents\\photo.webp'
  const t=run('vaultRedactText('+JSON.stringify(s)+')')
  assert.ok(!t.includes('foo@example.net'))
  assert.ok(!t.includes('abcd12345'))
  assert.ok(!t.includes('secretToken987'))
  assert.ok(!t.includes('somebody'))
  o.vaultRedact=false
  assert.equal(run('vaultRedactText("hello")'),'hello')
})

test('media off strips local references',()=>{
  const sample='@image: C:\\Users\\x\\test.webp\n[Image attached at: E:\\path\\p.png]\n![alt](C:\\Temp\\a.webp)'
  const out=run('vaultStripMedia('+JSON.stringify(sample)+')')
  assert.ok(!out.includes('test.webp'))
  assert.ok(!out.includes('E:\\path'))
  assert.ok(!out.includes('Temp'))
})

test('ZIP32 store entries, CRC32 standard vector',async()=>{
  assert.equal(run('vaultCrc32(new TextEncoder().encode("123456789"))'),0xcbf43926)
  const zip=run('vaultZip([{name:"conversation.html",text:"<p>yes</p>"},{name:"聊天.md",text:"hello 世界"}])')
  const arr=new Uint8Array(await zip.arrayBuffer())
  assert.equal(arr[0],0x50);assert.equal(arr[1],0x4b)
  assert.equal(arr[arr.length-22],0x50);assert.equal(arr[arr.length-21],0x4b)
})

test('ZIP rejects unsafe names and memory runaway',()=>{
  assert.throws(()=>run('vaultZip([{name:"../secret",text:"a"}])'))
  assert.throws(()=>run('vaultZip([{name:"duplicate",text:"a"},{name:"duplicate",text:"b"}])'))
})

test('preparing redacted turns never mutates original',async()=>{
  o.vaultRedact=true; o.vaultImagesHtml=false
  const original={id:0,user:{text:'@image: C:\\Users\\x\\a.webp\nkey=abcdefgh12345'},asst:[{text:'test@example.com'}],tools:[]}
  context._fixture = [original]
  const out=await run('vaultPrepareExportTurns(_fixture,"html")')
  assert.ok(out[0].user.text.includes('[Image omitted]'))
  assert.ok(!out[0].user.text.includes('abcdefgh12345'))
  assert.ok(!out[0].asst[0].text.includes('test@example.com'))
  assert.ok(original.user.text.includes('abcdefgh12345'))
})
