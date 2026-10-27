"""Shared provenance/CLI for lifecycle source projections, without importing the engine."""
import argparse
import json
from pathlib import Path
import re
from check import ROOT, BASE, ROUTINES, VERSIONS, pin, sha, write_new


def make_ledger(task, script, sections, rows, examples, calculations, modules, *, addresses=(), artifacts=(), sources=()):
    """Rows are authored interpretations; hashes/coverage do not establish their truth."""
    wanted = set(ROUTINES[task]) | set(addresses)
    listing_files = set()
    for path in (ROOT / 'static/goal-exe/code').glob('*.asm'):
        for address in re.findall(r'^; ---- routine (\S+)', path.read_text(), re.M):
            if address in wanted:
                listing_files.add(path.relative_to(ROOT).as_posix())
    paths = [f'runtime/original_match/port/{name}.py' for name in modules]
    paths.append('notes/engine-study/T98/tables.py')
    paths += sorted(listing_files) + list(sources)
    paths += [p.relative_to(ROOT).as_posix() for p in (ROOT / 'static/goal-exe/data').glob('ds_2581_*.hex')]
    data = dict(task=task, status='proposed; source-derived explanation',
                method='Original named/listing reading and source-derived projections; no original/port engine execution.',
                sections=sections,
                routines=[dict(address=a, mechanism=m, fields=f, visible_effect=e,
                               limits='Conditional source mechanism; natural reach/frequency not established by this calculation.')
                          for a,m,f,e in rows],
                examples=examples, calculations=calculations,
                supporting_artifacts={p:sha((ROOT/p).read_bytes()) for p in artifacts},
                analysis_sha256={str(Path(script).relative_to(ROOT)):sha(Path(script).read_bytes()),
                                 'notes/engine-study/T104/common.py':sha(Path(__file__).read_bytes())})
    return pin(data, sorted(wanted), sorted(set(paths)), source_commit=BASE)


def run(task, builder):
    ap = argparse.ArgumentParser(description=builder.__module__ + ': source-derived lifecycle explanation')
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    data = builder()
    path = ROOT / f'notes/engine-study/T104/{task}-v{VERSIONS[task]}.json'
    if args.check:
        assert json.loads(path.read_text()) == data, 'source/calculations differ from current ledger'
        print(f'PASS: {task}, {len(data["routines"])} routines, {len(data["examples"])} worked examples, '
              f'{len(data["calculations"].get("controls", {}))} altered-rule controls; source pins match')
    else:
        write_new(path, data)
        print(f'wrote {task} source ledger; no engine execution')
