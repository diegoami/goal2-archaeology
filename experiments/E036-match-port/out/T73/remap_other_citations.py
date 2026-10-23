"""T73: one-shot pre-T73 document migration with identical endpoint text.

Run only on pre-migration documents against the saved pre-T73 named view;
receipts, not another --write invocation, verify the already applied migration."""
import csv
import difflib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
OLD = Path('/tmp/T73-named-before-regeneration-20261023')
NEW = ROOT/'static/goal-exe/named'
def index(base):
    rows = list(csv.DictReader((base/'index.tsv').open(), delimiter='\t'))
    return {r['address']:r for r in rows if r['file']}
old, new = index(OLD), index(NEW)
mapping = {}
for address, row in old.items():
    other = new[address]
    first = int(row['line'])-1
    last = min([int(r['line'])-1 for r in old.values() if r['file']==row['file'] and int(r['line'])>first+1] or [len((OLD/row['file']).read_text().splitlines())])
    next_first = int(other['line'])-1
    next_last = min([int(r['line'])-1 for r in new.values() if r['file']==other['file'] and int(r['line'])>next_first+1] or [len((NEW/other['file']).read_text().splitlines())])
    a = (OLD/row['file']).read_text().splitlines()[first:last]
    b = (NEW/other['file']).read_text().splitlines()[next_first:next_last]
    for match in difflib.SequenceMatcher(None,a,b,autojunk=False).get_matching_blocks():
        for k in range(match.size):
            assert a[match.a+k] == b[match.b+k]
            mapping[(row['file'],first+match.a+k+1)] = (other['file'], next_first+match.b+k+1, a[match.a+k])


import subprocess
RAW=ROOT/'static/goal-exe/decompiled'
raw_index=index(RAW)
pattern=re.compile(r'((?:static:)?(?:static/goal-exe/)?)(named/)(seg_[0-9A-Za-z_]+\.c):(\d+)(?:-(\d+))?')
changes,inherited,unresolved,pending=[],[],[],[]

def endpoint(file,line,force_raw=False):
    if not force_raw:
        target=mapping.get((file,line))
        if target:return ('named',*target)
        old_lines=(OLD/file).read_text().splitlines()
        if not old_lines[line-1].strip():
            for distance in range(1,5):
                for neighbour in (line-distance,line+distance):
                    anchor=mapping.get((file,neighbour))
                    if anchor:
                        candidate=anchor[1]+line-neighbour
                        new_lines=(NEW/anchor[0]).read_text().splitlines()
                        if 0<candidate<=len(new_lines) and new_lines[candidate-1]==old_lines[line-1]:
                            return ('named',anchor[0],candidate,old_lines[line-1])
    owners=[(addr,row) for addr,row in old.items() if row['file']==file and int(row['line'])<=line]
    if not owners:return None
    addr,row=max(owners,key=lambda pair:int(pair[1]['line']))
    raw=raw_index.get(addr)
    if not raw:return None
    original=(OLD/file).read_text().splitlines()
    first=int(row['line'])-1
    last=min([int(r['line'])-1 for r in old.values() if r['file']==file and int(r['line'])>first+1] or [len(original)])
    raw_lines=(RAW/raw['file']).read_text().splitlines()
    raw_first=int(raw['line'])-1
    raw_last=min([int(r['line'])-1 for r in raw_index.values() if r['file']==raw['file'] and int(r['line'])>raw_first+1] or [len(raw_lines)])
    relative=line-first-1
    for block in difflib.SequenceMatcher(None,original[first:last],raw_lines[raw_first:raw_last],autojunk=False).get_matching_blocks():
        if block.a<=relative<block.a+block.size:
            candidate=raw_first+block.b+relative-block.a+1
            assert raw_lines[candidate-1]==original[line-1]
            return ('decompiled',raw['file'],candidate,original[line-1])
    return None

for raw in subprocess.check_output(['git','ls-files','*.md'],cwd=ROOT,text=True).splitlines():
    rel=Path(raw)
    if rel.parts[0]=='findings' or 'out' in rel.parts or raw.startswith('static/goal-exe/named/'):
        continue
    path=ROOT/rel;text=path.read_text()
    def replace(match):
        prefix,view,file,start,end=match.groups();start=int(start);end=int(end) if end else None
        lines=(OLD/file).read_text().splitlines() if (OLD/file).exists() else []
        endpoints=[start]+([end] if end is not None else [])
        if any(n<1 or n>len(lines) for n in endpoints):
            inherited.append({'document':raw,'citation':match.group(0),'reason':'An endpoint was already out of range in the pre-T73 view; left unchanged for #307.'})
            return match.group(0)
        if end is None and not lines[start-1].strip():
            inherited.append({'document':raw,'citation':match.group(0),'reason':'The pre-T73 single-line citation already points to a blank line; left unchanged for #307.'})
            return match.group(0)
        targets=[endpoint(file,n) for n in endpoints]
        if len(targets)==2 and all(targets) and targets[0][:2]!=targets[1][:2]:
            targets=[endpoint(file,n,force_raw=True) for n in endpoints]
        if any(t is None for t in targets) or (len(targets)==2 and targets[0][:2]!=targets[1][:2]):
            unresolved.append({'document':raw,'citation':match.group(0),'old_texts':[lines[n-1] for n in endpoints]})
            return match.group(0)
        first=targets[0];new=f'{prefix}{first[0]}/{first[1]}:{first[2]}'
        if end is not None:new+=f'-{targets[1][2]}'
        if new!=match.group(0):
            changes.append({'document':raw,'old':match.group(0),'new':new,'same_endpoint_texts':[t[3] for t in targets]})
        return new
    result=pattern.sub(replace,text)
    if result!=text:pending.append((path,result))
if '--write' in sys.argv and not unresolved:
    for path,result in pending:path.write_text(result)
print(json.dumps({'changes':changes,'inherited_invalid_endpoints_unchanged':inherited,'unresolved':unresolved},indent=2))
sys.exit(bool(unresolved))
