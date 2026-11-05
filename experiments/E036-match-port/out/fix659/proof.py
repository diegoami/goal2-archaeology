"""#659: existing admitted E006 input, explicit captain130 withdrawn at half-time.

Uses the accepted family display projection: empty memory mask; only the documented
screen fields are projected. No new original state is captured or printed.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / 'runtime'), str(ROOT / 'experiments/E036-match-port')]
import family
import records
from original_match import Image
from original_match import match as current
from original_match import screens as S

parser = argparse.ArgumentParser()
parser.add_argument('--engine', choices=('original', 'port'), required=True)
parser.add_argument('--before', action='store_true')
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
module = current
if args.before:
    source = subprocess.check_output(['git', 'show', '174dfe4b151f3de08847315fab7653771d6c24f4:runtime/original_match/match.py'])
    path = ROOT / '.cache/before_match_659.py'
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(source)
    spec = importlib.util.spec_from_file_location('original_match.before_659', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

image_path = ROOT / '.cache/dl/e0afff6751747233-e006-1000-r0001.sav'
raw = image_path.read_bytes()
image_hash = hashlib.sha256(raw).hexdigest()
assert image_hash == 'e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d'
match = module.Match(Image.from_savestate(raw), module.Fixture(7, 19, index=21), managed=7,
                     captain=130, seed=0x1234, delay_byte=0, record_draws=True,
                     engine=args.engine, ports=['all'] if args.engine == 'port' else [], timeout_s=600)
prompts = []
prompt_objects = []
declarations = []
real_key = match._captain_key
real_declare = match._declare


def key():
    p = match.st['prompt']
    if p is not None and p.get('role') == 1:
        if not any(p is q for q in prompt_objects):
            prompt_objects.append(p)
        number = next(i + 1 for i, q in enumerate(prompt_objects) if p is q)
        here = match.m.frame_word(match.m.reg('bp'), S.PROMPT_SLOT_BP)
        value = real_key()
        prompts.append(dict(prompt=number, slot=here, key=value))
        if number > 1 and not args.before:
            assert value == S.ENTER, 'later prompt must accept the original highlight'
            assert 1 <= here <= 11
        return value
    return real_key()


def declare(*values):
    if values[0].startswith(('main seed ', 'delay byte ')):
        declarations.append(values[0])
    return real_declare(*values)


match._captain_key = key
match._declare = declare
events = []
withdrawn = False
started = time.monotonic()
error = None
try:
    for event in match.events():
        events.append((event.kind, event.minute, event.score, copy.deepcopy(event.data)))
        if event.kind == 'decision':
            if event.data['context'] == 'half_time' and not withdrawn:
                assert 130 in event.data['eleven'] and 134 in event.data['bench']
                withdrawn = True
                match.answer(substitutions=[(130, 134)])
            else:
                match.answer()
except Exception as exc:
    error = type(exc).__name__ + ': ' + str(exc)

receipt = dict(engine=args.engine, before=args.before, source_sha256=hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),
               image_sha256=image_hash, elapsed_s=time.monotonic()-started, error=error,
               withdrawn=withdrawn, captain_slot_after=match._squad(7).index(130)+1,
               prompt_keys=prompts, startup_declarations=declarations, memory_mask=[])
if args.before:
    assert withdrawn and error is not None and 'captain prompt' in error, receipt
    receipt['expected_failure_caught'] = True
else:
    assert error is None, receipt
    assert withdrawn and match.st['over']
    assert len(prompt_objects) >= 2, 'replacement captain prompt not reached'
    assert len(declarations) == 2, declarations
    result = match.result()
    assert result['kickoff_seed'] == 0x1234
    assert any(e['off'] == 130 and e['on'] == 134 for e in result['substitutions'])
    receipt.update(result_sha256=records.result_digest(result),
                   events_sha256=family.display_events_digest(events),
                   after=family.digest_memory(match, [], image_hash),
                   kickoff_seed=result['kickoff_seed'], draws=result['draws'],
                   draws_digest=result['draws_digest'], score=result['score'],
                   substitutions=result['substitutions'], completed=True)
args.out.write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({k:receipt[k] for k in ('engine','before','elapsed_s','error','withdrawn','captain_slot_after')}), flush=True)
