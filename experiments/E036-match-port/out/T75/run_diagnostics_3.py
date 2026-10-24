"""Normal/native and all three early mutant probes before broad acceptance."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
PY='/home/diego/.local/bin/python3.12'
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'experiments/E036-match-port')]
import compare,families
from original_match.port import selection
folder=OUT/'diagnostics-3';folder.mkdir(exist_ok=False)
(folder/'source.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'runtime/original_match').rglob('*.py'))}},indent=2)+'\n')
entries=','.join(sorted(selection.PORTS.entries)+['0791:E6A9','0791:E20B','0791:EB89','0791:DAF8','0791:DB38','0791:DBFA','0791:DC7E','0791:DDCB','0791:DEA6','0791:E2E6','1771:4FAA','1771:55FC'])
jobs=[]
for label,ports,variant in [('native','',None),('normal','menus,selection',None)]+[(v,'menus,selection','selection.'+v) for v in selection.PORTS.variants]:
 command=[PY,'-B','experiments/E036-match-port/family.py','--family','ALL','--only','S/decisions-70','--time-limit','1800','--stretch-limit','300','--count',entries,'--out',str(folder/(label+'.jsonl'))]
 if ports:command+=['--ports',ports]
 if variant:command+=['--variant',variant]
 (folder/(label+'-command.json')).write_text(json.dumps(command,indent=2)+'\n')
 log=(folder/(label+'.log')).open('x');p=subprocess.Popen(command,cwd=ROOT,env={**os.environ,'HARNESS_HEAVY_SLOTS':'4'},stdout=log,stderr=subprocess.STDOUT);jobs.append((label,p,log))
(folder/'pids.json').write_text(json.dumps({label:p.pid for label,p,_ in jobs},indent=2)+'\n')
exits={}
for label,p,log in jobs:exits[label]=p.wait();log.close()
(folder/'exits.json').write_text(json.dumps(exits,indent=2)+'\n')
ref=compare.load(ROOT/'experiments/E036-match-port/families/S-no-managed-side-reference-20261024-v1.jsonl')
sp={s.id:s.sha256 for f in families.discover().values() for s in f.matches};native=compare.load(folder/'native.jsonl')
branches={'request-not-set':'0791:E6A9','form-not-swapped':'0791:E20B','keeper-check-inverted':'0791:EB89'}
proof=[]
for label,_,_ in jobs:
 c=compare.load(folder/(label+'.jsonl'));expected={mid:sp[mid] for mid in c}
 lines,ok=compare.check(ref,c,expected,expect='differ' if label in branches else 'identical',image_sha256=families.image_sha256())
 (folder/(label+'-compare.log')).write_text('\n'.join(lines)+'\n')
 proof.append({'name':label,'ok':ok,'branch_reached':native['S/decisions-70']['counts'].get(branches.get(label,''))})
(folder/'comparisons.json').write_text(json.dumps(proof,indent=2)+'\n')
