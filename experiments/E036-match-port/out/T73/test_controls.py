"""T73 fixed-baseline and one-line controls on the owned state/profile tests.

No worktree or branch switch: runtime and minimal experiment/test dependencies are
read from fixed pre-task255de405, then only the T73 files under test are overlaid.
Every measured verdict is written by the caller to an immutable output log.
"""
import io, hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
ROOT=Path(__file__).resolve().parents[4]
BASE='255de405b9c6a730960dcae23ed423ae433ad9f5'
D='runtime/original_match/port/display.py'
F='experiments/E036-match-port/family.py'
C='experiments/E036-match-port/compare.py'
CONTROLS=[
 ('fixed pre-task baseline',None,None,None),
 ('041A board key clear omitted',D,"mem.wds8(0xA976,0,'0791:041A')","mem.wds8(0xA976,1,'0791:041A')"),
 ('0691 last pitch slot omitted',D,'range(1, 23)','range(1, 22)'),
 ('0682 numbered glyph offset shifted',D,'r.ax = r.ax + 0x2F','r.ax = r.ax + 0x30'),
 ('0640 half glyph OR instead of XOR',D,'r.al = r.al ^ (r.dx & 255)','r.al = r.al | (r.dx & 255)'),
 ('8FAF erased old cell changed',D,"w16(mem, r, 0x90E, r.bx, '8FAF')","w16(mem, r, 0x90E, r.bx+1, '8FAF')"),
 ('8F66 erase membership ignored',D,'if member(mem):','if False:'),
 ('8FD7 high-ball boundary inclusive',D,'high = r.ax > 2','high = r.ax >= 2'),
 ('9045 occupied new cell overwritten',D,'if r.ax == r.bx:','if True:'),
 ('9085 quick reset branch inverted',D,'if mem.ds8(0x9A3E) == 0:','if mem.ds8(0x9A3E) != 0:'),
 ('A6AF pitch copy shorter',D,'r.ax = 0xFA0','r.ax = 0xF9F'),
 ('94CF wrong secondary seed',D,'r.di = 0x8336','r.di = 0x8338'),
 ('950B noise threshold equality changed',D,'larger = s16(r.dx) > s16(r.bx) or (r.dx == r.bx and r.ax > r.cx)',
  'larger = s16(r.dx) > s16(r.bx) or (r.dx == r.bx and r.ax >= r.cx)'),
 ('012B backward DF cleared',D,'if reverse:\n        r.std()','if reverse:\n        r.cld()'),
 ('0116 text attribute unswapped',D,'r.ax = ((r.ax & 255) << 8) | (r.ax >> 8)','r.ax = r.ax'),
 ('010C text nonempty loop skipped',D,'if r.cx:\n        r.di = ss16','if not r.cx:\n        r.di = ss16'),
 ('01DB text column offset changed',D,'r.di = r.di + r.ax + r.cx - 0xA2','r.di = r.di + r.ax + r.cx - 0xA0'),
 ('072B score sides swapped',D,"((0x9B3D, 2, '0739'","((0x9B3C, 2, '0739'"),
 ('0C6B pending flag not cleared',D,'mem.wds8(0x9B55,0,"0791:0C6B")','mem.wds8(0x9B55,1,"0791:0C6B")'),
 ('16B1 snapshot last squad slot omitted',D,'for slot in range(1, 21):','for slot in range(1, 20):'),
 ('17FE snapshot seed destination changed',D,"mem.wds16(0x9974, r.ax, '0791:17FE')","mem.wds16(0x9976, r.ax, '0791:17FE')"),
 ('screen projection applied to every event kind',F,'if kind == "full_time" and "screen_sha256" in data:','if "screen_sha256" in data:'),
 ('screen projection drops seed too',F,'if key != "screen_sha256"','if key not in ("screen_sha256", "seed")'),
 ('empty selected profile falls back',F,'return True\n\n\ndef display_profile_selected','return bool(mask)\n\n\ndef display_profile_selected'),
 ('raw runs accidentally projected',F,'if not selected:\n        return False','if not selected:\n        return True'),
 ('CLI declared mask not selected',F,'mask = profile["mask"]','mask = []'),
 ('profile checkpoint identity omitted',F,'if display_profile:\n        key["display_profile"] = 1','if False:\n        key["display_profile"] = 1'),
 ('strict profile inherits coarse block skip',C,'if no_screen and not strict_display else set()','if no_screen else set()'),
 ('mismatched display mask allowed',C,'if required and not all(matching):','if False:'),
 ('display profile reference override allowed',C,'if supplied.resolve() != bound.resolve():','if False:'),
 ('removed void routine returns a value',D,'value=None, why=','value=1, why='),
 ('0083 empty statistics bar executes writes',D,'r.ax=rw(mem,r,2)+rw(mem,r,0)\n    if r.ax:','r.ax=rw(mem,r,2)+rw(mem,r,0)\n    if True:'),
 ('2F58 empty player row executes name call',D,"if word:\n        r=yield from guest(mem,r,'1771:2EE5'","if True:\n        r=yield from guest(mem,r,'1771:2EE5'"),
 ('3916 live slot brightness includes bench12',D,'bright=r.ax<12','bright=r.ax<=12'),
 ('3B09 mark flag guard inverted',D,'if mem.ds8(0xC1E) and flag:','if not mem.ds8(0xC1E) and flag:'),
 ('3B80 zone branch excludes position2',D,'if rb(mem,r,6)>=2:','if rb(mem,r,6)>2:'),
 ('3D18 nonmatch branch inverted',D,"if not mem.ds8(0xC1E):\n        r=yield from guest(mem,r,'1771:3B3F'","if mem.ds8(0xC1E):\n        r=yield from guest(mem,r,'1771:3B3F'"),
 ('43D8 both-feet branch inverted',D,'if r.al:\n        r.di=0x425D;','if not r.al:\n        r.di=0x425D;'),
 ('044B special message colour changed',D,'r.al=0x82 if matched else mem.ds8(0x7922)','r.al=0x83 if matched else mem.ds8(0x7922)'),
 ('1E18 delay local count incremented',D,'r.ax=count;r.local16(-8,r.ax)','r.ax=count+1;r.local16(-8,r.ax)'),
 ('04BF second digit row shifted',D,"((0,0xDC,'049E'),(80,0xDB,'04BF'))","((0,0xDC,'049E'),(79,0xDB,'04BF'))"),
 ('0540 seventh segment omitted',D,'for index in range(1,8):','for index in range(1,7):'),
 ('05B8 last digit column shifted',D,'digit=r.ax;r.ax=0x4B','digit=r.ax;r.ax=0x4C'),
 ('19B2 top-row boundary excludes row4',D,'if pointer==0xA972 and ss16(mem,r,r.bp+6)>4:','if pointer==0xA972 and ss16(mem,r,r.bp+6)>=4:'),
 ('C553 outgoing notice column shifted',D,"(6,29,'0791:C540'","(6,30,'0791:C540'"),
 ('1EDE tone divisor argument changed',D,'r.local16(6,r.ax)\n        r.al=ss16(mem,r,r.bp+6)&255','r.local16(6,r.ax+1)\n        r.al=ss16(mem,r,r.bp+6)&255'),
 ('1EC4 sound enable guard inverted',D,"if not mem.ds8(0xA9FC):\n        r=yield from guest(mem,r,'214B:1E75',ret='214B:1ECA')","if mem.ds8(0xA9FC):\n        r=yield from guest(mem,r,'214B:1E75',ret='214B:1ECA')"),
]
paths=['runtime','tests/test_e036_compare.py',F,C,'experiments/E036-match-port/families.py',
       'experiments/E036-match-port/records.py','experiments/E036-match-port/families']
archive=subprocess.check_output(['git','archive',BASE,*paths],cwd=ROOT)
current={name:(ROOT/name).read_bytes() for name in (D,F,C)}
owned_test=(ROOT/'tests/test_port_display.py').read_bytes()
print('snapshot hashes', {name:hashlib.sha256(data).hexdigest() for name,data in current.items()},flush=True)
print('tests sha256',hashlib.sha256(owned_test).hexdigest(),flush=True)
all_ok=True
for name,target,old,new in CONTROLS:
 with tempfile.TemporaryDirectory() as temporary:
  into=Path(temporary)
  with tarfile.open(fileobj=io.BytesIO(archive)) as tf:tf.extractall(into,filter='data')
  (into/'tests/test_port_display.py').write_bytes(owned_test)
  inventory=into/'experiments/E036-match-port/out/T73';inventory.mkdir(parents=True)
  shutil.copy(ROOT/'experiments/E036-match-port/out/T73/static-inventory.json',inventory)
  if target is not None:
   for changed in (D,F,C):
    p=into/changed;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(current[changed])
   p=into/target;s=p.read_text();assert s.count(old)==1,(name,s.count(old));p.write_text(s.replace(old,new))
  result=subprocess.run([sys.executable,'-B','-m','unittest','tests.test_port_display'],cwd=into,
                        capture_output=True,text=True,timeout=180)
  caught=result.returncode!=0 and ('AssertionError' in result.stderr or
       (target is None and "no port module 'display'" in result.stderr))
  all_ok &= caught
  print(f'{name}: exit {result.returncode}, '+('caught' if caught else 'NOT CAUGHT'),flush=True)
  if not caught:print(result.stderr,flush=True)
print('all controls caught' if all_ok else 'a control was not caught',flush=True)
sys.exit(0 if all_ok else 1)
