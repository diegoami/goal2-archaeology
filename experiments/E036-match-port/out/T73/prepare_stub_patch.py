"""Prepare (never apply) six possible ALL-proven stub classifications.

Precondition for applying the emitted patch: full ALL ablation proof for every
routine and main-session review. A temporary git-archive test bundle is not a
worktree and writes no Git metadata. No active source/profile/reference changes.
"""
import argparse,ast,difflib,hashlib,io,json,subprocess,sys,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
D='runtime/original_match/port/display.py';T='tests/test_port_display.py';C='experiments/E036-match-port/out/T73/test_controls.py'
REMOVED={'0791:006C','1771:0AF8','1771:1527','1771:3947','214B:1E8D','214B:1EBC'}

def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def replace_methods(source,replacements):
 lines=source.splitlines(True);changes=[];found=set()
 for cls in ast.parse(source).body:
  if not isinstance(cls,ast.ClassDef):continue
  for fn in cls.body:
   key=(cls.name,getattr(fn,'name',None))
   if key in replacements:
    changes.append((fn.lineno-1,fn.end_lineno,replacements[key]));found.add(key)
 assert found==set(replacements),set(replacements)-found
 for lo,hi,text in sorted(changes,reverse=True):lines[lo:hi]=[text+'\n']
 return ''.join(lines)

def build_display(source):
 tree=ast.parse(source);lines=source.splitlines(True);cuts=[];removed_names=set();found=set()
 for fn in tree.body:
  if not isinstance(fn,ast.FunctionDef):continue
  for dec in fn.decorator_list:
   if isinstance(dec,ast.Call) and isinstance(dec.func,ast.Attribute) and isinstance(dec.func.value,ast.Name) and dec.func.value.id=='PORTS' and dec.func.attr=='port':
    address=ast.literal_eval(dec.args[0])
    if address in REMOVED:cuts.append((min(d.lineno for d in fn.decorator_list)-1,fn.end_lineno));found.add(address);removed_names.add(fn.name)
 assert found==REMOVED
 assert not any(isinstance(n,ast.Name) and n.id in removed_names for n in ast.walk(tree))
 for lo,hi in sorted(cuts,reverse=True):del lines[lo:hi]
 result=''.join(lines);tree=ast.parse(result)
 sets=[n.comparators[0] for n in ast.walk(tree) if isinstance(n,ast.Compare) and isinstance(n.left,ast.Name) and n.left.id=='address' and len(n.ops)==1 and isinstance(n.ops[0],ast.NotIn) and isinstance(n.comparators[0],ast.Set)]
 assert len(sets)==1
 node=sets[0];old=ast.get_source_segment(result,node);values=[ast.literal_eval(e) for e in node.elts]
 assert REMOVED<=set(values)
 new='{'+', '.join(repr(v) for v in values if v not in REMOVED)+'}'
 result=result.replace(old,new,1);ast.parse(result)
 return result

def build_tests(source):
 helper='''def assert_explicit_void_removal(case, rig, address, words):
    """Checks the declared Python stub, never original branch-PC execution."""
    case.assertIsNotNone(port._module_registry('display').entries[address].stub)
    rig.mem.regs.update(ax=0xA55A,dx=0x5AA5,eflags=0x602)
    initial_registers=dict(rig.mem.regs)
    case.assertIsNone(rig.run(address,words))
    case.assertEqual(rig.mem.regs,initial_registers)
    before=bytes(rig.mem.memory);registers=initial_registers
    case.assertIsNone(rig.run(address,words))
    case.assertEqual(bytes(rig.mem.memory),before)
    case.assertEqual(rig.mem.regs,registers)
    case.assertEqual(rig.calls,[])
    case.assertEqual(rig.writes,[])


'''
 replacements={
 ('Display','test_skill_bars_keep_all_twelve_unclamped_unsigned_products'):'''    def test_skill_bar_removal_preserves_even_nonzero_skill_inputs(self):
        r=Rig();r.player(1,4,255);r.player(1,5,0);r.player(1,7,0)
        for k in range(1,13):r.ds8(0x6D25+k,k-1);r.ds8(0x6DCD+k-1,k+1)
        r.ds16(0xA96E,GOFF);r.ds16(0xA970,GSEG)
        assert_explicit_void_removal(self,r,'1771:3947',(10,4,1))
''',
 ('UnreachedStateBranchTests','test_empty_statistics_bar_and_nonempty_reached_twin'):'''    def test_removed_statistics_bar_preserves_zero_and_nonzero_inputs(self):
        for first,second in ((0,0),(1,65535),(1,3)):
            r=Rig();r.lin16(0x40100,first);r.lin16(0x40102,second)
            r.ds16(0xA96E,0x200);r.ds16(0xA970,0x500)
            assert_explicit_void_removal(self,r,'0791:006C',(0,4,0x100,0x4000))
''',
 ('TeamPanelHelperTests','test_manager_status_zero_guard_and_status_band_boundaries'):'''    def test_removed_manager_status_preserves_all_argument_bands(self):
        for manager,status in ((0,0),(1,0),(130,0),(1,1),(1,9),(1,255)):
            r=Rig();r.ds16(0xA91F,0x100);r.ds16(0xA921,0x5400)
            r.lin8(0x54100+manager*3+1,status)
            assert_explicit_void_removal(self,r,'1771:0AF8',(24,10,manager))
''',
 ('TeamPanelHelperTests','test_country_rating_signed_zero_and_eight_point_boundaries'):'''    def test_removed_rating_label_calls_no_rating_or_text_helpers(self):
        for country in (0,3,128):
            r=Rig();r.ds8(0x7884,1);r.ds8(0x7885,2)
            assert_explicit_void_removal(self,r,'1771:1527',(25,8,country))
''',
 ('SoundChainMemoryTests','test_speaker_off_keeps_kit_return_byte_and_saved_frame'):'''    def test_removed_speaker_off_keeps_incoming_result_and_creates_no_frame(self):
        for disabled in (0,1):
            r=Rig();r.ds8(0xA9FC,disabled);r.lin16(BP0,0xCAFE)
            assert_explicit_void_removal(self,r,'214B:1E8D',())
            self.assertEqual(r.u16(BP0),0xCAFE)
''',
 ('ToneMemoryTests','test_tone_divisor_argument_and_return_high_byte_are_preserved'):'''    def test_removed_tone_frequency_preserves_enabled_and_disabled_inputs(self):
        for disabled in (0,1):
            for frequency in (1,440,32768,65535):
                r=Rig();r.ds8(0xA9FC,disabled)
                assert_explicit_void_removal(self,r,'214B:1EBC',(frequency,))
''',
 ('ToneMemoryTests','test_disabled_sound_skips_division_even_for_zero_frequency'):'''    def test_removed_tone_preserves_zero_frequency_and_creates_no_frame(self):
        r=Rig();r.ds8(0xA9FC,1);r.lin16(BP0,0xCAFE)
        assert_explicit_void_removal(self,r,'214B:1EBC',(0,))
        self.assertEqual(r.u16(BP0+6),0)
        self.assertEqual(r.u16(BP0),0xCAFE)
'''}
 result=replace_methods(source,replacements)
 original='''                    r.run(address,words)
                    before=bytes(r.mem.memory);registers=dict(r.mem.regs)'''
 fixed='''                    initial_registers=dict(r.mem.regs)
                    self.assertIsNone(r.run(address,words))
                    self.assertEqual(r.mem.regs,initial_registers)
                    before=bytes(r.mem.memory);registers=initial_registers'''
 assert result.count(original)==1
 result=result.replace(original,fixed,1)
 assert result.count('class Case(unittest.TestCase):')==1
 result=result.replace('class Case(unittest.TestCase):',helper+'class Case(unittest.TestCase):',1)
 ast.parse(result);return result

def build_controls(source):
 changes={
 '0083 empty statistics bar executes writes':('006C removed-body return cleanup shortened','"0791:006C": "ret 8"','"0791:006C": "ret 6"'),
 '1EDE tone divisor argument changed':('1EBC removed-body return cleanup widened','"214B:1EBC": "retf 2"','"214B:1EBC": "retf 4"'),
 '1EC4 sound enable guard inverted':('1E8D removed-body far return changed to near','"214B:1E8D": "retf"','"214B:1E8D": "ret"')}
 tree=ast.parse(source);assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CONTROLS' for t in n.targets))
 lines=source.splitlines(True);replacements=[];found=set()
 for item in assignment.value.elts:
  name=ast.literal_eval(item.elts[0])
  if name in changes:
   title,old,new=changes[name]
   replacements.append((item.lineno-1,item.end_lineno,' ('+repr(title)+',D,'+repr(old)+','+repr(new)+'),\n'));found.add(name)
 assert found==set(changes)
 for lo,hi,text in sorted(replacements,reverse=True):lines[lo:hi]=[text]
 result=''.join(lines);ast.parse(result);return result

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',required=True);a=ap.parse_args()
 out=(ROOT/a.out).resolve();out.relative_to((ROOT/'experiments/E036-match-port/out/T73').resolve());out.mkdir(exist_ok=False)
 before={name:(ROOT/name).read_text() for name in (D,T,C)}
 assert sha(before[D])=='81a8fe8613aaaa1062f6e468f92989b683dfde52c2c0b12d11b56ed2cdab42fe'
 after={D:build_display(before[D]),T:build_tests(before[T]),C:build_controls(before[C])}
 patch=''.join(''.join(difflib.unified_diff(before[n].splitlines(True),after[n].splitlines(True),fromfile='a/'+n,tofile='b/'+n)) for n in (D,T,C))
 (out/'proposal.patch').write_text(patch)
 # Check all prospective control replacements still address exactly one operation.
 namespace={'__file__':str(ROOT/C)};exec(after[C].split('paths=')[0],namespace)
 for name,target,old,new in namespace['CONTROLS']:
  if target:
   body=after.get(target,(ROOT/target).read_text())
   assert body.count(old)==1,(name,body.count(old))
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 paths=['runtime','tests/test_e036_compare.py','experiments/E036-match-port/family.py','experiments/E036-match-port/compare.py','experiments/E036-match-port/families.py','experiments/E036-match-port/records.py','experiments/E036-match-port/families']
 archive=subprocess.check_output(['git','archive',head,*paths],cwd=ROOT)
 with tempfile.TemporaryDirectory(prefix='t73-prospective-') as temporary:
  into=Path(temporary)
  with tarfile.open(fileobj=io.BytesIO(archive)) as tf:tf.extractall(into,filter='data')
  for name,text in after.items():p=into/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
  p=into/'experiments/E036-match-port/out/T73/static-inventory.json';p.write_bytes((ROOT/'experiments/E036-match-port/out/T73/static-inventory.json').read_bytes())
  result=subprocess.run([sys.executable,'-B','-m','unittest','tests.test_port_display'],cwd=into,capture_output=True,text=True,timeout=180)
  (out/'unit.log').write_text(result.stdout+result.stderr+'exit '+str(result.returncode)+'\n')
  probe='''import unittest
from tests.test_port_display import port, Rig, assert_explicit_void_removal
entry=port._module_registry('display').entries['0791:006C']
def bad(mem,variant):mem.regs['ax']=1
entry.fn=bad
try:assert_explicit_void_removal(unittest.TestCase(),Rig(),'0791:006C',(0,4,0x100,0x4000))
except AssertionError:print('idempotent first-call AX clobber: caught')
else:raise AssertionError('idempotent first-call AX clobber escaped')
'''
  negative=subprocess.run([sys.executable,'-B','-c',probe],cwd=into,capture_output=True,text=True,timeout=30)
  (out/'first-call-register-control.log').write_text(negative.stdout+negative.stderr+'exit '+str(negative.returncode)+'\n')
 assert all((ROOT/n).read_text()==text for n,text in before.items()),'active source changed'
 receipt={'purpose':'prospective only; no active changes; requires full ALL ablation proof and main review before apply','head':head,'source_sha256':{n:sha(v) for n,v in before.items()},'proposed_sha256':{n:sha(v) for n,v in after.items()},'removed_routines':sorted(REMOVED),'unit_exit':result.returncode,'first_call_register_control_exit':negative.returncode,'active_sources_unchanged':True,'all_50_instruction_controls_have_unique_targets':True,'baseline':'255de405b9c6a730960dcae23ed423ae433ad9f5'}
 (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2),flush=True);return result.returncode or negative.returncode
if __name__=='__main__':sys.exit(main())
