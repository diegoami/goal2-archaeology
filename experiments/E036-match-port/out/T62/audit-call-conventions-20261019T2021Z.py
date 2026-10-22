"""Read-only T62 call-arity audit against the static listing, no runtime proof."""
import ast
import hashlib
import json
import pathlib
import re

root = pathlib.Path('/home/diego/projects/goal2-archaeology')
work = root / '.claude/worktrees/agent-a55a365b32cd67a36'
source = work / 'runtime/original_match/port/motion.py'
returns = {}
for listing in (work / 'static/goal-exe/code').glob('*.asm'):
    target = None
    for line in listing.read_text().splitlines():
        header = re.match(r'; ---- routine ([0-9A-F]{4}:[0-9A-F]{4})\b', line)
        if header:
            target = header[1]
            returns.setdefault(target, set())
        ret = re.search(r'\s(retf?)\s*(0x[0-9a-f]+|[0-9]+)?\s*$', line)
        if target and ret:
            returns[target].add((ret[1], int(ret[2], 0) if ret[2] else 0))
tree = ast.parse(source.read_text())
handlers = next(ast.literal_eval(n.value) for n in tree.body
                if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'HANDLERS' for t in n.targets))
rows = []
for node in ast.walk(tree):
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != 'call':
        continue
    target = node.args[0]
    targets = [target.value] if isinstance(target, ast.Constant) else [v[0] for v in handlers.values()]
    assert isinstance(target, ast.Constant) or isinstance(target, ast.Name) and target.id == 'target'
    kw = {k.arg: ast.literal_eval(k.value) for k in node.keywords if k.arg in ('far', 'caller_pops')}
    far = kw.get('far', True)
    pop = 0 if kw.get('caller_pops', False) else 2 * (len(node.args) - 1)
    expected = ('retf' if far else 'ret', pop)
    for address in targets:
        actual = sorted(returns.get(address, set()))
        rows.append({'line': node.lineno, 'target': address, 'expected_return': expected,
                     'listing_returns': actual, 'matches': bool(actual) and all(r == expected for r in actual)})
result = {'scope': 'Static call argument bytes and near/far convention only; no stack-resumption or match-equivalence proof.',
          'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'calls': rows, 'mismatches': [r for r in rows if not r['matches']]}
path = root / '.cache/t62-static-call-conventions.json'
path.write_text(json.dumps(result, indent=2) + '\n')
print(f'{len(rows)} resolved call alternatives; {len(result["mismatches"])} mismatches')
for row in result['mismatches']:
    print(row)
