"""Actual original/ported Up/Down poll prefixes; input queue only, no guest edits."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import Image,Match,Fixture
from original_match.assets import reference_image
label=sys.argv[1];expect_pass=sys.argv[2]=='pass';results=[]
for ports in (None,['menus','display']):
 for key in (0xAC,0xB1):
  match=Match(Image.from_bytes(reference_image(ROOT/'.cache/dl')),Fixture(7,19,index=40),managed=7,seed=1,ports=ports,timeout_s=30)
  initial=None;wanted=None;observed_minute=None;error=None
  try:
   for event in match.events():
    if event.kind=='decision':match.answer()
    if event.kind=='minute':
     if event.minute==1 and initial is None:
      initial=match.m.rd(0x66A,1);delta=match.m.rd(0x7920+int(key==0xB1),1);delta=delta-256 if delta&128 else delta
      assert initial in range(5) and abs(delta)==1
      wanted=initial+delta;wanted=4 if wanted<0 else 0 if wanted>4 else wanted
      match.st['poll_keys'].append(key)
     elif event.minute>=2 and initial is not None:observed_minute=event.minute;break
  except Exception as exc:error=type(exc).__name__+': '+str(exc).splitlines()[0]
  pending=[f.entry.address for f in match.m.frames if f.entry.address=='0791:9372']
  final=match.m.rd(0x66A,1)
  passed=error is None and observed_minute==2 and final==wanted and not pending and not match.st['poll_keys']
  results.append({'ports':ports or [],'key':key,'before_mode':initial,'expected_mode':wanted,'after_mode':final,'observed_minute':observed_minute,'pending_poll_frames':pending,'error':error,'passed':passed,'complete_match':False,'intervention':'queued original key at minute1; no guest memory or CPU edits'})
with (OUT/f'arrow-prefix-{label}.json').open('x') as f:json.dump({'menus_sha256':hashlib.sha256((ROOT/'runtime/original_match/port/menus.py').read_bytes()).hexdigest(),'results':results},f,indent=2);f.write('\n')
assert all(r['passed'] for r in results if not r['ports']),results
ported=[r for r in results if r['ports']]
assert all(r['passed'] for r in ported) if expect_pass else all(not r['passed'] for r in ported),results
print('PASS: original arrow prefixes pass; ported prefixes', 'pass without orphan poll frames' if expect_pass else 'reproduce the pre-fix near/far defect')
