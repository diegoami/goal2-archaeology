#!/usr/bin/env python3
"""What a goal2 consumer sees: the pinned, unchanged Core loads none of the role-3 waits (its catalogue has no CC7B role 3),
and loads each of them as the penalty-taker decision once only the screen label of roles 3 and 4 is widened (collect.adapt).
Needs the pinned Core source and the readback states (docs/requests/400-roles34.md). Loads, executes no further guest step."""
import json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import collect as c
c.load_core()
d=json.loads((HERE/'delivery.json').read_text());ROOT=HERE.parents[1]
items=[i for i in d['roles']['3']['inputs'] if i['label']!='preceding-wait' and not i['label'].endswith('return-accept')]
out={'unchanged':{},'label_widened':{}}
for i in items:
    raw=(ROOT/i['readback']).read_bytes()
    try:c.Core.load(raw,goal_dat=c.GOAL_DAT);out['unchanged'][i['label']]='loaded'
    except c.UnknownScreen as e:out['unchanged'][i['label']]='UnknownScreen at '+e.site
c.adapt()
for i in items:
    k=c.Core.load((ROOT/i['readback']).read_bytes(),goal_dat=c.GOAL_DAT)
    out['label_widened'][i['label']]=dict(kind=k.wait.kind,site=k.wait.site,poll=k.wait.poll,view=k.wait.view)
print(json.dumps(out,indent=1))
