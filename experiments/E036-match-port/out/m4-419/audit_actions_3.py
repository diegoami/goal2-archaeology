"""Accept only a complete strict ALL75 run bound to the frozen delivered core."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import compare,families,records
from original_match import port
run=OUT/'all-actions-2-40126565563';candidate_path=run/'all-actions-2.jsonl'
manifest=json.loads((run/'manifest.json').read_text());assert manifest['sha']=='158790a0620c486a5c8dad0e0670cc6064151e8d'
logs=sorted(run.glob('shard-*-run.txt'));assert len(logs)==38
for log in logs:
 text=log.read_text();heads=re.findall(r'^HEAD: ([0-9a-f]{40}) ',text,re.M)
 assert heads==[manifest['sha']],(log.name,heads)
 assert re.search(r'^exit 0 finished ',text,re.M),log.name
assert (run/'collect.txt').read_text().rstrip().endswith('exit 0')
candidate=compare.load(candidate_path);definitions=families.discover();specs={m.id:m for f in definitions.values() for m in f.matches}
assert len(candidate)==len(specs)==75
profile=compare.candidate_display_profile(candidate,True);assert profile and profile['mask']==[]
reference=compare.load(ROOT/profile['reference'])
lines,passed=compare.check(reference,candidate,{mid:s.sha256 for mid,s in specs.items()},no_screen=True,strict_display=True,image_sha256={mid:s.image_sha256 for mid,s in specs.items()})
with (OUT/'all-actions-2-compare.log').open('x') as f:f.write('\n'.join(lines)+'\n')
assert passed,lines
addresses=['1771:'+a for a in ('883F','89C1','89FE','8A5D','8CCF','8D84','9028','91CE','937C','9509','5C94','5CCB')]
modules=port.available();checks=0
for row in candidate.values():
 assert row['mask']==[] and len(row['after']['ds'])==64 and row['ports']==modules and row['variant'] is None
 for a in addresses:assert row['counts'][a]==row['port_calls'][a],(row['id'],a);checks+=1
fs=candidate['FS/public-stage8-holland-belgium']
assert fs['port_calls']['1771:9509']==fs['port_calls']['1771:883F']==fs['port_calls']['1771:937C']==1 and fs['port_calls']['1771:8CCF']==8
assert len(fs['after']['ranges']['records'])==105
paths=sorted(list((ROOT/'runtime/original_match').rglob('*.py'))+[p for p in (ROOT/'experiments/E036-match-port').glob('*.py') if p.name!='locate.py'])
# locate.py is a separate replay diagnostic, never imported by the family runner.
# Its source-selection fix has a dedicated test and a later frozen full-suite run.
hashes={}
for p in paths:
 rel=str(p.relative_to(ROOT));current=hashlib.sha256(p.read_bytes()).hexdigest();dispatched=hashlib.sha256(subprocess.check_output(['git','show',manifest['sha']+':'+rel],cwd=ROOT)).hexdigest();assert current==dispatched,rel;hashes[rel]=current
old=ROOT/'experiments/E036-match-port/families/display/reference-all-rare-20261024-v1.jsonl'
assert (ROOT/profile['reference']).read_bytes().startswith(old.read_bytes())
receipt={'strict_identical':75,'mask':[],'all_DS_blocks_compared':True,'entry_call_checks':checks,'all_38_shard_heads_match_dispatch':True,'all_38_family_processes_exit_zero':True,'original_entry_totals':{a:sum(row['counts'][a] for row in candidate.values()) for a in addresses},'source_sha':manifest['sha'],'match_runtime_and_producer_sources_match_dispatched':True,'separately_tested_diagnostic_change':'experiments/E036-match-port/locate.py source selection, outside the family runner','source_sha256':hashes,'candidate_sha256':hashlib.sha256(candidate_path.read_bytes()).hexdigest(),'old74_reference_bytes_preserved':True,'finals':{'score':fs['score'],'source_sha256':fs['image_sha256'],'records_blocks':105,'9509':1,'883F':1,'937C':1,'8CCF':8}}
with (OUT/'all-actions-2-audit.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print('PASS: ALL75 strict;900 entry/call checks; every DS block; full finals calendar; source hashes match dispatch')
