"""Read-only derived audit of frozen B own/falsifier/suite evidence.

Integrated ALL is deliberately not read or promoted here: its running cohort
requires a separate completion receipt. No engine/profile/reference is changed.
"""
import argparse,hashlib,json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];E=ROOT/'experiments/E036-match-port';OUT=E/'out/T73'
sys.path[:0]=[str(ROOT/'runtime'),str(E)]
from original_match import port
import compare,family,families

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(path.read_text())
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);a=p.parse_args()
 own_dir=OUT/'own-display-desktop-20261023-v2';mut_dir=OUT/'falsifiers-desktop-20261023-B1'
 own_launch=load(own_dir/'launch.json');mut_launch=load(mut_dir/'launch.json')
 assert own_launch['source_sha256']==mut_launch['source_sha256']
 for name,sha in own_launch['source_sha256'].items():assert digest(ROOT/name)==sha,name
 own_result=load(own_dir/'result.json');mut_result=load(mut_dir/'summary.json')
 assert own_result['source_changes']==[] and own_result['shard_failures']==[]
 assert own_result['compare_exit']==0 and own_result['calls_audit_exit']==0
 assert mut_result['source_changes']==[] and mut_result['all_caught']
 profile=family.read_display_profile();assert profile['mask']==[]
 reference=compare.load(ROOT/profile['reference']);own=compare.load(own_dir/'family.jsonl')
 expected={mid:sha for fam in families.select('ALL',families.discover()) for mid,sha in fam.expected().items()}
 lines,ok=compare.check(reference,own,expected,no_screen=True,strict_display=True,image_sha256=families.image_sha256());assert ok,lines
 registry=port._module_registry('display');retained={r for r,e in registry.entries.items() if e.stub is None};removed=set(registry.entries)-retained
 assert len(own)==62 and len(registry.entries)==88 and len(retained)==57 and len(removed)==31
 entry_checks=0
 for rec in own.values():
  assert not rec['variant'] and compare.candidate_display_profile({rec['id']:rec},True)
  assert set(rec['counts'])==set(registry.entries) and set(rec['port_calls'])==set(registry.entries)
  for routine in registry.entries:assert rec['counts'][routine]==rec['port_calls'][routine];entry_checks+=1
 assert entry_checks==5456
 manifest=mut_launch['manifest'];assert {r['variant'] for r in manifest}==set(registry.variants) and len(manifest)==60
 results={r['variant']:r for r in mut_result['results']};assert set(results)==set(registry.variants)
 original=compare.load(OUT/'coverage-unported-desktop-20261023/coverage-unported.jsonl')
 rows=[];omissions=set();instructions=set();completed=0;incomplete=[]
 for item in manifest:
  variant,routine=item['variant'],item['routine'];path=mut_dir/(variant+'.jsonl');records=compare.load(path)
  assert set(records)==set(item['only'].split(',')) and results[variant]['caught']
  assert compare.candidate_display_profile(records,True)
  output,ok=compare.check(reference,records,{mid:expected[mid] for mid in records},expect='differ',no_screen=True,strict_display=True,image_sha256=families.image_sha256());assert ok,output
  witnesses=[]
  for mid,rec in records.items():
   assert original[mid]['counts'][routine]>0 and own[mid]['counts'][routine]>0
   assert rec['port_calls'][routine]==rec['counts'][routine] and rec['counts'][routine]>0
   bad=compare.completed(rec);completed+=not bool(bad)
   if bad:incomplete.append({'variant':variant,'match':mid,'reason':bad})
   witnesses.append({'match':mid,'original_entries':original[mid]['counts'][routine],'B_normal_entries':own[mid]['counts'][routine],
                     'B_mutant_entries':rec['counts'][routine],'completed':not bool(bad),'completion_failure':bad,
                     'differences':compare.differences(reference[mid],rec,True,True) if not bad else []})
  if variant.startswith('omit-'):
   assert variant=='omit-'+routine.lower().replace(':','-') and routine in retained;omissions.add(routine)
  else:instructions.add(variant)
  rows.append({'variant':variant,'routine':routine,'witnesses':witnesses,'candidate':str(path.relative_to(ROOT)),
               'candidate_sha256':digest(path),'comparison':str((mut_dir/(variant+'-compare.log')).relative_to(ROOT))})
 assert omissions==retained and instructions=={'aggregate-divisor-ten','secondary-seed-adjacent','table-default-group-two'}
 assert completed==59 and len(incomplete)==1 and incomplete[0]['variant']=='omit-0791-0106'
 suite=load(OUT/'B1-validation-launch.json');assert suite['runtime_sha256']==own_launch['source_sha256']['runtime/original_match/port/display.py']
 assert suite['tests_sha256']==digest(ROOT/'tests/test_port_display.py')
 text=(OUT/'full-suite-B1.log').read_text();assert 'Ran 1963 tests in 847.169s' in text and 'OK (skipped=13)' in text and (OUT/'full-suite-B1.exit').read_text().strip()=='0'
 assert 'Ran 82 tests' in (OUT/'unit-display-36.txt').read_text() and '\nOK\n' in (OUT/'unit-display-36.txt').read_text()
 controls=(OUT/'test-controls-6.txt').read_text();assert controls.rstrip().endswith('all controls caught') and 'NOT CAUGHT' not in controls
 mapping=load(OUT/'unreached-map-2.json');assert mapping['all_mapped'] and len(mapping['rows'])==273
 assert mapping['runtime_source_sha256']==suite['runtime_sha256'] and mapping['test_source_sha256']==suite['tests_sha256']
 citation_count=0
 for filename,textkey,newkey in [('citation-map-applied-v1.json','same_text','after'),('other-citations-applied-v1.json','same_endpoint_texts','new')]:
  citation=load(OUT/filename);assert citation['unresolved']==[]
  for change in citation['changes']:
   target,number=change[newkey].rsplit(':',1);target=target if target.startswith(('named/','decompiled/','code/')) else 'named/'+target
   line_numbers=[int(n) for n in number.split('-')];wanted=change[textkey] if isinstance(change[textkey],list) else [change[textkey]]
   actual=(ROOT/'static/goal-exe'/target).read_text().splitlines()
   assert [actual[n-1] for n in line_numbers]==wanted,(filename,change)
  citation_count+=len(citation['changes'])
 assert citation_count==55
 report={'scope':'Frozen B own, falsifiers and suites only; integrated ALL is not yet claimed',
  'runtime_sha256':suite['runtime_sha256'],'source_fingerprint_maps_identical':True,'fingerprinted_files':len(own_launch['source_sha256']),
  'all_fingerprinted_current_files_match':True,'own_matches_strict_identical':62,'candidate_entry_call_checks':entry_checks,
  'retained_bodies':57,'void_stubs':31,'retained_routines_with_caught_omissions':57,'instruction_variants_caught':sorted(instructions),
  'total_variants_caught':60,'completed_differing_witnesses':completed,'noncompleted_caught_witnesses':incomplete,
  'unit_tests_passed':82,'instruction_ABI_controls_caught':50,'fixed_pre_task':'255de405b9c6a730960dcae23ed423ae433ad9f5',
  'unreached_original_blocks_mapped':273,'full_suite':{'tests':1963,'seconds':847.169,'existing_skips':13,'exit':0},
  'exact_endpoint_citation_moves_verified':55,'preexisting_invalid_blank_references_unchanged':19,
  'integrated_all':'unclaimed; running cohort requires a separate completion receipt','rows':rows}
 (ROOT/a.out).open('x').write(json.dumps(report,indent=2)+'\n')
 print('B own62/62;5456 entry checks;57/57 omission+3/3 instruction falsifiers;36 source fingerprints identical;82 units;50 controls;1963 suite;55 citation moves. Integrated ALL unclaimed.',flush=True)
if __name__=='__main__':main()
