#!/usr/bin/env python3
"""Read-only T92 full-byte receipt verification. No guest execution."""
import hashlib,json,subprocess,sys,zipfile,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_text())
def state(p):
 with zipfile.ZipFile(p) as z:return z.read('memory.bin'),json.loads(z.read('registers.json'))
def word(mem,addr,n=2):return int.from_bytes(mem[addr:addr+n],'little')
def main():
 count=0
 for case,attempt in [('role3','role3-r1'),('role3','role3-r2'),('role4','role4-r1'),('role4','role4-r2'),('E062','E062-r1'),('E062','E062-r2'),('EC60','EC60-r1')]:
  pub=ROOT/'notes/400-synthetic'/attempt;private=ROOT/'.cache/400-synthetic'/attempt;r=load(pub/'record.json');con=load(pub/'construction.json')
  assert r['synthetic'] and r['case']==case and r['bound_s']==60 and r['elapsed_s']<60
  assert r['status']==('failed' if attempt=='E062-r1' else 'passed')
  producer=subprocess.check_output(['git','show',r['head']+':notes/400-synthetic/produce.py'],cwd=ROOT);assert sha(producer)==r['producer_sha256']
  for p,h in r['runtime_files'].items():assert sha((ROOT/'.cache/400-nice-try/core-source'/p).read_bytes())==h,p
  reference=load(ROOT/'notes/400-last/uc-r2/source.json')['runtime_files'];assert r['runtime_files']==reference
  for p,h in r['source_files'].items():assert sha((ROOT/p).read_bytes())==h,p
  raw=(private/'base.g2core').read_bytes();assert sha(raw)==r['base_sha256']=='068a47729a3b1822ae6d3df7777eb99880bbcf74315e22098869ccaeac29ad28'
  n=int.from_bytes(raw[4:8],'little');meta=json.loads(raw[8:8+n]);base=zlib.decompress(raw[8+n:]);mem=bytearray(base[:0x110000]);regs=meta['regs'].copy()
  for e in r['edits']:
   if 'address' in e:
    addr=e['address'];old=bytes.fromhex(e['old']);new=bytes.fromhex(e['new']);assert mem[addr:addr+e['size']]==old
    mem[addr:addr+e['size']]=new
   else:
    name=e['register'].upper();assert regs[name]==e['old'];regs[name]=e['new']
  im,ir=state(private/'input.ucstate');assert im==mem and ir['regs']==regs and ir['load']==meta['load']
  assert sha((private/'input.ucstate').read_bytes())==r['constructed_sha256']==con['constructed_sha256']
  lo=meta['load']*16;hi=lo+0x25810;assert im[lo:hi]==base[lo:hi]
  ds=regs['DS']*16;ss=regs['SS']*16;rows=[json.loads(s) for s in (pub/'steps.jsonl').read_text().splitlines()];assert len(rows)==r['observations']
  for i,row in enumerate(rows,1):
   assert row['n']==i
   p=private/row['machine_file'];assert sha(p.read_bytes())==row['machine_sha256']
   m,st=state(p);assert st['regs']==row['regs'];assert m[lo:hi]==base[lo:hi]
   # All frame words are actual stopped-machine bytes, not reconstructed labels.
   for f in row['frames']:
    assert f['parent']==word(m,ss+f['bp'])
    assert f['words']==[word(m,ss+f['bp']+off) for off in range(-16,18,2)]
   count+=1
  if case in ['role3','role4']:
   role=3 if case=='role3' else 4;kind=10 if role==3 else 11
   assert r['keys']==[172 if attempt.endswith('r2') else 176,177,13,99,27,32,13,13]
   assert [x['label']['control'] for x in rows if isinstance(x['label'],dict) and x['label'].get('from_same_input')]==['navigation','computer','escape','default','pitch']
   assert len([x for x in rows if x['reason']=='continuation-boundary'])==5
   assert rows[12]['site']=='0791:CF3A' and rows[12]['reason']=='read'
   assert rows[13]['site']=='0791:CC54' and rows[13]['reason']=='poll'
   # Live CC7B parent is CC2E at poll; directly CC7B at CF3A blocking read.
   for row in rows:
    if row['reason'] not in ['read','poll']:continue
    m,st=state(private/row['machine_file']);bp=st['regs']['EBP']&65535
    if row['reason']=='poll':bp=word(m,ss+bp)
    assert word(m,ss+bp+2)==0x6D74
    assert word(m,ss+bp+4)&255==role and word(m,ss+bp+6)&255==1
    pick=word(m,ss+bp-7);highlight=word(m,ss+bp-5)
    if row['n']==2:initial_highlight=highlight;initial_pick=pick
    if row['n']==3 and attempt.endswith('r2'):assert highlight==(initial_highlight-2)%11+1
    if row['n']==4 and attempt.endswith('r2'):assert highlight==initial_highlight
   returns=[e['ax'] for e in r['events'] if e['site']=='0791:6D74'];assert len(returns)==5
   # Same available stored pick: Enter, C, Esc, default and pitch-return Enter all384.
   assert initial_pick==384
   if attempt.endswith('r2'):assert returns==[384]*5
   for row in rows:
    if row['reason']=='continuation-boundary' and attempt.endswith('r2'):assert row['stored_pick']==384
   for e in r['events']:
    if e['site']=='0791:CC7B':assert e['words'][2:]==[kind,role,1]
   if role==4:
    assert r['range_recipe']==dict(direction=-1,x=0,y=-18,product=18)
    assert [e['ax'] for e in r['events'] if e['site']=='0791:6F70']==[18]*5
    assert [e['ax'] for e in r['events'] if e['site']=='0791:6F7F']==[0]*5
  else:
   message=rows[1];assert message['site']=='214B:098A' and message['reason']=='read'
   assert ('There is no player here' if case=='E062' else 'has a vacancy in the first team') in message['text']
   assert r['keys']==[13,13] if case=='E062' else r['keys']==[13]
   m,st=state(private/message['machine_file'])
   target=0xE062 if case=='E062' else 0xEC60
   assert any(word(m,ss+f['bp']+2)==target and word(m,ss+f['bp']+4)==meta['load']+0x791 for f in message['frames'])
   ev={e['site']:e for e in r['events']}
   if case=='E062':
    assert ev['0791:E062']['ax']&255==1
    assert rows[2]['site']=='0791:E61F' and rows[2]['reason']=='read'
   else:
    assert all(ev[s]['ax']&255==0 for s in ['0791:EB82','0791:EBD7','0791:EC22'])
    assert ev['0791:EC60']['ax']&255==1
    assert rows[-1]['reason']=='continuation-boundary' and rows[-1]['regs']['EAX']&255==0
    # Actual counter1 and single available keeper at message wait (EA09 frame).
    frame=message['frames'][-1]['bp'];assert m[ss+frame-2]==1 and m[ss+frame-16]==1
 for p in [ROOT/'.cache/400-synthetic/t92-fixtures-v2-private.zip',ROOT/'.cache/400-synthetic/readback/t92-fixtures-v2-private.zip']:
  assert sha(p.read_bytes())=='ab1864e3449a643bdc6119650e09b9d29e90ab01476aa9eace468d6834f9eeae'
 print(f'PASS: four synthetic fixtures / {count} immutable stopped machines, all edits and original code bytes verified; independent selector controls + actual CF3A; both original message waits/dismissals; E062-r1 failed assertion preserved; private package/readback hashes match')
if __name__=='__main__':main()
