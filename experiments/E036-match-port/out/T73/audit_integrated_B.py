"""Complete B acceptance with integrated Actions evidence, preserving B2 unchanged."""
import argparse,datetime,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];E=ROOT/'experiments/E036-match-port';O=E/'out/T73'
sys.path[:0]=[str(ROOT/'runtime'),str(E)]
from original_match import port
import compare,family,families

def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True);a=parser.parse_args()
 old=load(O/'acceptance-audit-B2.json');base=load(O/'acceptance-audit-B3-base.json');assert base==old
 directory=O/'all-actions-b1-40024462186';candidate=directory/'all-actions-b1.jsonl'
 manifest=load(directory/'manifest.json');binding=load(directory/'source-binding-final-1.json');calls=load(directory/'calls-audit-final-1.json')
 jobs=load(directory/'jobs-final-1.json');timing=load(directory/'timing-final-1.json');cost=load(directory/'runner-minutes-final-1.json')
 dispatch='329e7be1d27dec238c0db1670a74c25aff2a7876';expected_sha='cd8e824f045b0ff1e75ed707ebfa0c9413f28396fe3fbd9209dc5e8bf711e268'
 assert manifest['sha']==dispatch and manifest['inputs']['ports']=='all' and manifest['inputs']['family']=='ALL'
 assert manifest['run_id']=='40024462186' and sha(candidate)==expected_sha==cost['candidate_sha256']
 own_launch=load(O/'own-display-desktop-20261023-v2/launch.json');mut_launch=load(O/'falsifiers-desktop-20261023-B1/launch.json')
 fingerprints=own_launch['source_sha256'];assert fingerprints==mut_launch['source_sha256']
 assert set(binding['files'])==set(fingerprints) and binding['source_files_checked']==36
 dispatch_hashes={}
 for name,value in fingerprints.items():
  actual=subprocess.check_output(['git','show',dispatch+':'+name],cwd=ROOT)
  dispatch_hashes[name]=hashlib.sha256(actual).hexdigest()
  assert dispatch_hashes[name]==value==sha(ROOT/name),name
 assert binding['runtime_sha256']==base['runtime_sha256']==fingerprints['runtime/original_match/port/display.py']
 profile=family.read_display_profile();assert profile['mask']==[]
 reference=compare.load(ROOT/profile['reference']);records=compare.load(candidate)
 expected={mid:value for fam in families.select('ALL',families.discover()) for mid,value in fam.expected().items()}
 output,ok=compare.check(reference,records,expected,no_screen=True,strict_display=True,image_sha256=families.image_sha256());assert ok,output
 registry=port._module_registry('display');routines=set(registry.entries)
 assert set(manifest['inputs']['count'].split(','))==routines and len(routines)==88
 assert compare.candidate_display_profile(records,True)
 checks=0;totals={r:0 for r in routines}
 for rec in records.values():
  assert rec['variant'] is None and 'display' in rec['ports'] and set(rec['counts'])==routines
  for routine in routines:
   assert rec['counts'][routine]==rec['port_calls'][routine]
   totals[routine]+=rec['counts'][routine];checks+=1
 assert len(records)==62 and checks==5456 and calls['entry_checks']==5456 and calls['mismatches']==0
 assert calls['total_calls_by_routine']==totals and calls['reference_sha256']==sha(ROOT/profile['reference'])
 assert calls['mask']==[] and calls['projector_sha256']=='696aef9a91950d895037d22876d18482c699a783455646c1aceee9c41e8971c8'
 assert jobs['total_count']==len(jobs['jobs'])==33 and len({j['id'] for j in jobs['jobs']})==33
 seconds=0
 for job in jobs['jobs']:
  assert job['status']=='completed' and job['conclusion']=='success' and job['head_sha']==dispatch
  seconds+=(datetime.datetime.fromisoformat(job['completed_at'])-datetime.datetime.fromisoformat(job['started_at'])).total_seconds()
 assert seconds==37488 and seconds/60==624.8==cost['runner_minutes'] and cost['jobs']==33
 billable_ms=sum(v['total_ms'] for v in timing['billable'].values());assert billable_ms==0
 paths=[O/'acceptance-audit-B2.json',O/'acceptance-audit-B3-base.json',candidate]+[directory/n for n in ('manifest.json','source-binding-final-1.json','calls-audit-final-1.json','jobs-final-1.json','timing-final-1.json','runner-minutes-final-1.json','compare-final-1.log')]
 report=dict(base);report['scope']='Frozen B complete own, falsifier, integrated, suite and documentation acceptance evidence'
 report['integrated_all']={'status':'verified','matches_strict_identical':62,'entry_call_checks':5456,'mismatches':0,
   'candidate':str(candidate.relative_to(ROOT)),'candidate_sha256':expected_sha,'dispatch_head':dispatch,'collector_commit':'3c7d7b50',
   'source_fingerprint_maps_own_mutant_dispatch_current_identical':True,'source_files_checked':36,
   'run_id':40024462186,'jobs':33,'runner_seconds':seconds,'runner_minutes':seconds/60,'billable_ms':billable_ms}
 report['input_hashes']={str(p.relative_to(ROOT)):sha(p) for p in paths};report['dispatch_source_sha256']=dispatch_hashes
 (ROOT/a.out).open('x').write(json.dumps(report,indent=2)+'\n')
 print('B complete: own62/62; integrated62/62;5456 integrated entry checks;60/60 falsifiers;36 matching source files;33 jobs;37488 runner seconds=624.8 runner minutes;billable0.',flush=True)
if __name__=='__main__':main()
