"""Verify only the completed evidence prefix after the owner's stop-all instruction."""
from pathlib import Path
import ast,datetime,hashlib,json,sys
root=Path('/home/diego/projects/goal2-archaeology');task=sys.argv[1]
tree,module,own,variants,fuzz_family,fuzz_size={
'T64':('task-T64-port-ball','ball','own.jsonl',('launch-reverse-x','pass-always-replace','shot-skip-jitter'),'F40',40),
'T69':('agent-aca0f4fd155445184','frame','own-final-20261020.jsonl',('clock-reload','rating-sign','possession-swapped'),'O8',8)}[task]
work=root/'.claude/worktrees'/tree;out=work/'experiments/E036-match-port/out'/task
sys.path[:0]=[str(work/'runtime'),str(work/'experiments/E036-match-port')]
import compare,families,records
frozen=out/('own-falsifier-input-20261020T163810Z.json' if task=='T64' else 'own-falsifier-input-20261020T164316Z.json')
hashes=json.loads(frozen.read_text())['source_sha256'];assert all(hashlib.sha256((work/n).read_bytes()).hexdigest()==h for n,h in hashes.items())
addresses=sorted(ast.literal_eval(n.args[0]) for n in ast.walk(ast.parse((work/'runtime/original_match/port'/f'{module}.py').read_text())) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='port')
checks=[]
for label,family,expect,paths in [('own','ALL','identical',[out/own])]+[(v,fuzz_family,'differ',[out/('falsifier-'+v+('.jsonl' if task=='T64' else '-final-20261020.jsonl'))]) for v in variants]:
 if label!='own' and not paths[0].exists():
  stamp='20261020T163810Z' if task=='T64' else '20261020T192724Z';paths=[out/f'fz-{label}-{stamp}-{k}.jsonl' for k in (0,1)]
 rows={};source_hashes={}
 for p in paths:
  if p.exists():
   source_hashes[str(p.relative_to(work))]=hashlib.sha256(p.read_bytes()).hexdigest()
   for i,row in compare.load(p).items():assert i not in rows;rows[i]=row
 refs={};expected={}
 for f in families.select(family,families.discover()):refs.update(compare.load(work/f.reference));expected.update(f.expected())
 assert set(rows)<=set(expected)
 for row in rows.values():records.validate(row);assert records.is_completed(row)
 lines,ok=compare.check(refs,rows,{k:v for k,v in expected.items() if k in rows},image_sha256=families.image_sha256(),expect=expect) if rows else ([],True)
 equal=all(x['counts'].get(a,0)==x['port_calls'].get(a,0) for x in rows.values() for a in addresses)
 assert ok and equal
 checks.append({'label':label,'family':family,'expect':expect,'completed':len(rows),'required':len(expected),'complete':len(rows)==len(expected),'ok_for_completed_prefix':ok,'counts_equal':equal,'missing_ids':sorted(set(expected)-set(rows)),'source_sha256':source_hashes,'comparison':lines})
assert not (out/('all.jsonl' if task=='T64' else 'all-final-20261020.jsonl')).exists()
result={'task':task,'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owner_stop':True,'runtime_unchanged':True,'runtime_sha256':hashes,'checks':checks,'integrated_ALL':{'completed':0,'required':62,'complete':False},'policy':'Checks plus green CI; one milestone review for port stage. Cancelled per-PR reviews are not approvals. No automatic resumption.'}
p=root/'.cache/shutdown-20261021'/f'{task}-stopped-evidence-verification.json';assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'task':task,'checks':[{k:v for k,v in x.items() if k not in ('comparison','source_sha256','missing_ids')} for x in checks],'integrated_ALL':result['integrated_ALL']},indent=2))
