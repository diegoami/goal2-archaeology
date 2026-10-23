"""T71: remap named-view finding citations within the same routine, verifying identical line text."""
import csv
import difflib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[4]
OLD = Path('/tmp/t71-before-named')
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

pattern = re.compile(r'((?:static:)?(?:static/goal-exe/)?named/)(seg_[0-9A-Za-z_]+\.c):(\d+)')
changes, unresolved = [], []
for path in sorted((ROOT/'findings').glob('F*.md')):
    text = path.read_text()
    def replace(match):
        before = match.group(2),int(match.group(3))
        after = mapping.get(before)
        if after is None:
            unresolved.append(dict(finding=str(path.relative_to(ROOT)), citation=match.group(0), text=(OLD/before[0]).read_text().splitlines()[before[1]-1]))
            return match.group(0)
        if before != after[:2]:
            changes.append(dict(finding=str(path.relative_to(ROOT)), before=f'{before[0]}:{before[1]}',after=f'{after[0]}:{after[1]}',same_text=after[2]))
        return f'{match.group(1)}{after[0]}:{after[1]}'
    result = pattern.sub(replace,text)
    if '--write' in sys.argv and result != text:
        path.write_text(result)
print(json.dumps(dict(changes=changes,unresolved=unresolved),indent=2))
sys.exit(bool(unresolved))
