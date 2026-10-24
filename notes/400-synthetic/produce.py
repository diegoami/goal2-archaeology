#!/usr/bin/env python3
"""T92 SYNTHETIC construction and raw-machine original-code replay (no game ports)."""
import argparse, hashlib, json, os, signal, subprocess, sys, time, zipfile, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PIN='5061474420b842ee98a4a1e4c9c2673c0764b1f2'
BASE_SHA='068a47729a3b1822ae6d3df7777eb99880bbcf74315e22098869ccaeac29ad28'
def sha(b): return hashlib.sha256(b).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2)+'\n')
def snapshot(m,p):
 s=m.snapshot()
 # Deterministic raw snapshot, including unsupported reads, without Core.save/rewind.
 with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
  for name,data in [('memory.bin',s['memory']),('registers.json',json.dumps(dict(load=s['load'],regs=s['regs']),sort_keys=True).encode())]:
   i=zipfile.ZipInfo(name,date_time=(2026,10,24,0,0,0));i.compress_type=zipfile.ZIP_DEFLATED;z.writestr(i,data)
 return sha(p.read_bytes())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('case',choices=['role3','role4','E062','EC60']);ap.add_argument('attempt');ap.add_argument('--code',type=Path,default=ROOT/'.cache/400-nice-try/core-source');ap.add_argument('--base',type=Path,default=ROOT/'.cache/400-last/uc-r1/0046.g2core');ap.add_argument('--replay',type=Path);a=ap.parse_args()
 pub=ROOT/'notes/400-synthetic'/a.attempt;private=ROOT/'.cache/400-synthetic'/a.attempt
 pub.mkdir(parents=True,exist_ok=False);private.mkdir(parents=True,exist_ok=False)
 sys.dont_write_bytecode=True;sys.path.insert(0,str(a.code))
 from goal2.core.runner import Core,decode_text
 from goal2.engine.original_match.machine import Machine,MEM_SIZE
 from goal2.engine.original_match.image import Image
 import unicorn
 raw=a.base.read_bytes();assert sha(raw)==BASE_SHA
 n=int.from_bytes(raw[4:8],'little');meta=json.loads(raw[8:8+n]);memory=zlib.decompress(raw[8+n:]);m=Machine(memory,meta['load']);m.restore(dict(memory=memory[:MEM_SIZE],regs=meta['regs']))
 assert not Image(bytes.fromhex(meta['header'])+memory).build_problems()
 rec=dict(synthetic=True,case=a.case,attempt=a.attempt,base_sha256=sha(raw),producer_sha256=sha(Path(__file__).read_bytes()),head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),core_pin=PIN,unicorn=unicorn.__version__,bound_s=60,edits=[],keys=[],status='failed',classification='integrated-synthetic' if a.case=='E062' else 'isolated-synthetic',runtime_files={str(p.relative_to(a.code)):sha(p.read_bytes()) for folder in ['goal2/core','goal2/engine/original_match'] for p in sorted((a.code/folder).rglob('*.py'))},source_files={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in sorted((ROOT/'static/goal-exe').glob('*/*')) if p.name in ['seg_0791_06.c','seg_0791_11.c','seg_0791_12.c','seg_0791_13.c','seg_0791_12.asm','seg_0791_13.asm','seg_0791_20.asm','seg_0791_22.asm','seg_0791_23.asm','seg_214B_01.asm','seg_214B_02.asm','seg_214B_03.asm','seg_1771_05.asm']})
 def edit(addr,value,size,why):
  old=m.read(addr,size);new=value.to_bytes(size,'little')
  if old!=new:
   rec['edits'].append(dict(address=addr,size=size,old=old.hex(),new=new.hex(),source=why));m.write(addr,new)
 def ds(off,v,size,why):edit(m.DS*16+off,v,size,why)
 def reg(name,v,why):
  old=m.reg(name)
  if old!=v:rec['edits'].append(dict(register=name,old=old,new=v,source=why));m.set_reg(name,v)
 countries=m.far(0xA917);players=m.far(0xA91B)
 side=next(s for s in range(2) if m.read(countries+191*m.rd(0x9B34+2*s)+46,1)[0]>128)
 country=m.rd(0x9B34+2*side);squad=countries+191*country
 rec.update(side=side,country=country,squad=[m.word_at(squad+2*i) for i in range(20)])
 end=None
 if a.replay:
  with zipfile.ZipFile(a.replay) as z:
   state=json.loads(z.read('registers.json'));m.restore(dict(memory=z.read('memory.bin'),regs=state['regs']))
  rec['replay_input_sha256']=sha(a.replay.read_bytes())
 else:
  if a.case in ('role3','role4','EC60'):
   # Source-derived near-call frame. Existing code at the return is NEVER executed.
   sp=0x3800;ss=m.reg('ss')
   ret={'role3':0x82E0,'role4':0x6FEA,'EC60':0xF067}[a.case]
   entry={'role3':0x6ECF,'role4':0x6F3E,'EC60':0xEA09}[a.case]
   edit(ss*16+sp,ret,2,'0791:82DD/6FE7/F064 original near-call return; stop before continuation')
   if a.case!='role3':edit(ss*16+sp+2,side if a.case=='role4' else 0x3C00,2,'6F3E [bp+4] side; EA09 [bp+4] parent static link')
   if a.case=='EC60':
    edit(ss*16+0x3C00-5,country,2,'EA09 parent [static-link-5] country; F063 push bp')
   reg('esp',(m.reg('esp')&~65535)|sp,'source-derived near-call stack in existing SS; room for EA09 0x418 locals')
   reg('ebp',0,'synthetic root frame sentinel, not a naturally reached caller')
   reg('cs',m.seg(0x0791),'source-derived original routine segment')
   reg('eip',entry,'isolated original routine entry, no instruction patch')
  if a.case=='role4':
   slot=m.rd(0x668+side,1)+1
   # 2BE5: ((minute > signed half length) XOR (pitch slot+6 <12)) indexes DS:7920.
   b=int(m.rd(0x831B)>int.from_bytes(m.read(m.DS*16+0x8319,1),'little',signed=True))
   d=m.rd(0x7920+(b ^ int(m.rd(0x80E8+22*slot+6,1)<12)),1)
   direction=int.from_bytes(bytes([d]),'little',signed=True);assert direction in [-1,1]
   ds(0x82F6,0,1,'6F75 ball signed x; abs(x)<=4')
   ds(0x82F7,(18*direction)&255,1,'6F6A signed ball y * 2BE5 direction =18 (inclusive range boundary)')
   rec['range_recipe']=dict(direction=direction,x=0,y=18*direction,product=18)
  if a.case in ('E062','EC60'):
   index=m.rd(0x0C1B) if a.case=='E062' else 10
   assert m.read(players+20*m.word_at(squad+2*(index-1))+6,1)[0]!=0
   edit(squad+2*(index-1),0,2,'E04B/EA CA: selected outfield squad word zero; preserve keeper')
   if a.case=='E062':
    ds(0x9B41,1,1,'E67B original substitution-mode gate before E690 call E022')
    edit(m.reg('ss')*16+(m.reg('bp')-1),0,1,'E02C first-selection parent local; must be unmarked')
   rec['vacancy_slot']=index
 # Continuation boundaries are part of the declared fixture, including replay.
 if a.case!='E062':end={'role3':'0791:82E0','role4':'0791:6FEA','EC60':'0791:F067'}[a.case]
 initial=m.snapshot();rec['constructed_sha256']=snapshot(m,private/'input.ucstate')
 # Ensure no executable byte differs from the untouched base.
 lo=m.load*16;hi=lo+0x25810;assert initial['memory'][lo:hi]==memory[lo:hi]
 (private/'base.g2core').write_bytes(raw)
 dump(pub/'construction.json',rec)
 start=time.monotonic();seq=0;events=[]
 class RawIO(Core):
  def _on_keypressed(self,replay):
   site=m.where(m.stack_word(2),m.stack_word(0))
   if site=='0791:CC54' and self.pending is None and not self.default:
    m.stop('poll');return
   m.set_reg('ax',(m.reg('ax')&0xFF00)|int(self.pending is not None));m.return_from(True,0)
  def _on_readkey(self,replay):
   if m.rd(0x79AE,1):return
   if self.pending is not None:
    k=self.pending;self.pending=None;self._answer(k);return
   m.stop('read')
 c=RawIO(m,bytes.fromhex(meta['header']),memory[MEM_SIZE:],10_000_000_000,[],BASE_SHA,dos_time=(12,0,0,0));c.default=False
 def frames():
  bp=m.reg('bp');result=[]
  for _ in range(12):
   if not 0<bp<65500:break
   result.append(dict(bp=bp,parent=m.frame_word(bp,0),words=[m.frame_word(bp,i) for i in range(-16,18,2)]))
   nb=m.frame_word(bp,0)
   if nb<=bp:break
   bp=nb
  return result
 def observe(label):
  nonlocal seq
  seq+=1;p=private/f'{seq:03}.ucstate';h=snapshot(m,p)
  row=dict(label=label,n=seq,reason=m.stop_reason,site=m.where(m.stack_word(2),m.stack_word(0)),pc=m.where(m.reg('cs'),m.reg('ip')),regs=m.snapshot()['regs'],machine_sha256=h,machine_file=p.name,frames=frames(),text=c._text(),stored_pick=m.rd(0x9976+10*side+2*(3 if a.case=='role3' else 4)),cursor=m.rd(0xC1B))
  with (pub/'steps.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
  print(json.dumps({k:row[k] for k in ['n','label','reason','site','pc']}),flush=True);return row
 def run(label):
  m.run(m.lin(end) if end else (1<<21),timeout_s=max(.001,60-(time.monotonic()-start)),fresh=True)
  if m.stop_reason is None:m.stop_reason='continuation-boundary'
  return observe(label)
 def key(k):
  rec['keys'].append(k)
  assert m.stop_reason in ['read','poll']
  if m.stop_reason=='read':c._answer(k)
  else:c.pending=k
  return run({'key':k})
 # Record source gates and real return values without changing them.
 def trace(site):
  def h(replay):
   events.append(dict(site=site,ax=m.reg('ax'),bp=m.reg('bp'),sp=m.reg('sp'),words=[m.frame_word(m.reg('bp'),i) for i in [-16,-2,4,6,8]]))
  m.at(site,h)
 for site in ['0791:6F70','0791:6F7F','0791:6D4E','0791:CC7B','0791:D00D','0791:6D74','0791:E022','0791:E062','0791:EB82','0791:EBD7','0791:EC22','0791:EC60'] :trace(site)
 signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('60-second attempt bound')));signal.alarm(60)
 try:
  observe('SYNTHETIC pre-input exact machine')
  if a.case in ['role3','role4']:
   # Every independent control replay begins from the identical constructed machine.
   for control,keys in [('navigation',[0xAC,0xB1,13]),('computer',[ord('c')]),('escape',[27]),('default',[]),('pitch',[32,13,13])]:
    m.restore(initial);c.pending=None;c.default=False
    row=run({'control':control,'from_same_input':True})
    assert row['reason']=='poll' and row['site']=='0791:CC54'
    assert ('PENALTY' if a.case=='role3' else 'FREE KICK') in row['text']
    if not keys:c.default=True;row=run({'control':control,'no_key':True})
    for k in keys:
     row=key(k)
     if k==32:assert row['reason']=='read' and row['site']=='0791:CF3A'
    assert row['reason']=='continuation-boundary'
  elif a.case=='E062':
   # Already at the retained E44F actual read. Original Enter triggers E690→E022.
   m.stop_reason='read';row=key(13)
   assert 'There is no player here' in row['text']
   assert row['reason']=='read'
   row=key(13);assert row['reason']=='read' and row['site']=='0791:E61F'
  else:
   row=run('EA09 from synthetic call frame; original ordered checks')
   assert 'has a vacancy in the first team' in row['text'] and row['reason']=='read'
   row=key(13);assert row['reason']=='continuation-boundary' and m.reg('al')==0
  rec['status']='passed'
 except BaseException as e:
  rec['error']=repr(e);observe('failed stopped machine');print(repr(e),flush=True)
 finally:
  signal.alarm(0);rec.update(elapsed_s=time.monotonic()-start,observations=seq,events=events)
  dump(pub/'record.json',rec)
 if rec['status']!='passed':sys.exit(1)
if __name__=='__main__':main()
