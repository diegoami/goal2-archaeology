"""Reproduce the bounded literal/wrapper target inventory; dynamic calls remain explicit.
Only source text and registered address identifiers are inspected; no original image.
"""
import ast
import json
from pathlib import Path
import re
import sys
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'runtime'))
from original_match.port import load
known = {address for registry, _ in load(['all']) for address in registry.entries}
absent, dynamic = {}, []
for path in sorted((ROOT / 'runtime/original_match/port').glob('*.py')):
    for node in ast.walk(ast.parse(path.read_text())):
        if not isinstance(node, ast.Call): continue
        name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ''
        index = {'call': 0, '_call': 2, 'guest': 1 if path.stem == 'positioning' else 2}.get(name)
        if index is None or len(node.args) <= index: continue
        target = node.args[index]
        location = f'{path.name}:{node.lineno}'
        if not isinstance(target, ast.Constant) or not isinstance(target.value, str):
            dynamic.append(location)
            continue
        address = target.value
        if re.fullmatch('[0-9A-F]{4}', address): address = '0791:' + address
        if re.fullmatch('[0-9A-F]{4}:[0-9A-F]{4}', address) and address not in known:
            absent.setdefault(address, []).append(location)
print(json.dumps(dict(registered=len(known), absent=absent, nonliteral_calls=dynamic,
    limitation='Literal/wrapper inventory only; dynamic targets and admitted paths still require source/runtime coverage.'), indent=2))
