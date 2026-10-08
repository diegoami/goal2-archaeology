#!/usr/bin/env python3
"""Register existing immutable routine traces as run/1 extraction records.

The timestamps are the registration/extraction times, not retroactively
invented guest execution times. No original routine is run by this script.
"""
import datetime
import hashlib
import json
import platform
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# The project's machine id, as every other run record writes it (runs/E014, runs/E015); the run
# schema wants a lowercase identifier, and platform.node() gave the Windows host name.
MACHINE = 'ubuntu-24-04-wsl2'
HERE = Path(__file__).resolve().parent


def main():
    commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip()
    script = Path(__file__)
    for rep, source in enumerate(('fixture-probe-002.json', 'fixture-probe-003.json'), 1):
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        raw = (HERE / source).read_bytes()
        trace = json.loads(raw)
        observations = [{'step': 0, 'source': 'file', 'field': f'immutable original-routine trace {source}',
                         'value': hashlib.sha256(raw).hexdigest()}]
        for step, case in enumerate(trace['cases'], 1):
            observations.append({'step': step, 'source': 'memory',
                                 'field': f"case {case['case']}: complete input, RNG, call and player-word byte trace",
                                 'value': json.dumps(case, sort_keys=True)})
        run_id = f'E018-r{rep:04d}'
        record = {
            'schema': 'run/1', 'run_id': run_id, 'experiment': 'E018',
            'arm': 'original-fixture-routine-trace-extraction', 'rep': rep,
            'code_commit': commit, 'machine': MACHINE,
            'artifact': {'set': 'goal2-67cf27d6', 'variant': None},
            'runtime': {'driver': f'experiments/E018-q016-confidence/register_probes.py@{commit}',
                        'platform': f'python-{platform.python_version()}/linux',
                        'fingerprint': {'unicorn': '2.1.4', 'source_trace_sha256': hashlib.sha256(raw).hexdigest()}},
            'interventions': [
                {'level': 'I1', 'what': 'Read and register existing original-routine trace; registration executes no guest code.'},
                {'level': 'I2', 'what': 'Source trace ran original 0791:B7FA in Unicorn from E011 half-time memory, with declared fixture, rank, squad and player-record inputs. Original RNG results and guest code unchanged; BIOS interrupts swallowed, no keys. Logged wait-family skips empty. First batch injection offsets were defective and its complete trace is retained.'}
            ],
            'start_state': {'id': 'E011-r0002-halftime', 'sha256': trace['cases'][0]['source_sha256'],
                            'restore': 'Source probe copied E011-r0002 half-time guest memory into Unicorn, with DS and relocated code segments from the savestate; stack setup follows runtime/emul/watched.py. Each case began from a fresh copy. Registration reads that trace, does not restore or rerun it.'},
            'seed': None,
            'actions': {'script': str(script.relative_to(ROOT)), 'sha256': hashlib.sha256(script.read_bytes()).hexdigest(), 'args': [source]},
            'observations': observations, 'outputs': [],
            'started': started, 'ended': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'status': 'completed'
        }
        destination = ROOT / 'runs/E018' / f'{run_id}.json'
        with destination.open('x') as handle:
            json.dump(record, handle, indent=2)
            handle.write('\n')
        print(run_id, 'registered', source, '(incomplete)' if rep == 1 else '(replacement)')


if __name__ == '__main__':
    main()
