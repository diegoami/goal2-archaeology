"""R1 regression controls: same mutant against previous and new hand tests.

Only private scratch copies are edited. Historical tests come from the reviewed
head; the port source is byte-identical to that head. No original game bytes.
"""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
OLD = '321d8469c48c7598279230105558d7a493be479c'
TESTS = ('tests/test_port_runtime.py', 'tests/test_port_geometry.py')
CASES = [
    ('negative Copy count inside Insert/Delete', 'runtime', 'count = 0 if s16(count) < 0 else count', 'count = 1 if s16(count) < 0 else count', 0),
    ('side-one base address', 'geometry', 'R.al = mem.ds8(SIDE_BASES + R.di)', 'R.al = mem.ds8(SIDE_BASES - R.di)', 0),
    ('lower bound AH', 'geometry', '        R.ah = 0', '        R.ah = 1', 0),
    ('upper bound AH', 'geometry', '        R.ah = 0', '        R.ah = 1', 1),
    ('saturated insert length byte', 'runtime', 'return bytes([0xFF]) + a[1:] + b[1:1 + 0xFF - a[0]]', 'return bytes([0x100]) + a[1:] + b[1:1 + 0xFF - a[0]]', 0),
    ('character compare width', 'runtime', 'flags = sub_flags(a, b, 8)', 'flags = sub_flags(a, b, 9)', 0),
    ('length compare width', 'runtime', 'R.arith(sub_flags(la, lb, 8))', 'R.arith(sub_flags(la, lb, 9))', 0),
    ('negative remainder carry', 'runtime', 'bx = (bx + (cx >> 16)) & M16', 'bx = (bx - (cx >> 16)) & M16', 1),
    ('division high-word rotation', 'runtime', 'carry, bx = bx >> 15, ((bx << 1) | carry) & M16', 'carry, bx = bx >> 15, ((bx >> 1) | carry) & M16', 0),
]

def tests(tmp, texts):
    for path, text in texts.items():
        (tmp/path).write_text(text)
    env = os.environ.copy()
    env['T60_NO_FUZZ'] = '1'
    result = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'tests.test_port_runtime', 'tests.test_port_geometry'],
                            cwd=tmp, env=env, text=True, capture_output=True, timeout=60)
    assert 'Ran ' in result.stderr, result.stdout+result.stderr
    assert 'ModuleNotFoundError' not in result.stderr, result.stderr
    return result

def main():
    old = {p:subprocess.check_output(['git','show',OLD+':'+p],cwd=ROOT,text=True) for p in TESTS}
    new = {p:(ROOT/p).read_text() for p in TESTS}
    base = ROOT/'.cache/tmp'
    base.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=base) as directory:
        tmp = Path(directory)
        shutil.copytree(ROOT/'runtime/original_match',tmp/'runtime/original_match',ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy(ROOT/'runtime/fileopts.py',tmp/'runtime/fileopts.py')
        shutil.copytree(ROOT/'experiments/E036-match-port/out/T60',tmp/'experiments/E036-match-port/out/T60')
        (tmp/'tests').mkdir()
        assert tests(tmp,old).returncode == tests(tmp,new).returncode == 0, 'unmutated baseline must pass both suites'
        for name,module,before,after,occurrence in CASES:
            path = tmp/'runtime/original_match/port'/f'{module}.py'
            original = path.read_text()
            positions=[]
            start=original.index('def advance_unavailable_ball_slot(') if module == 'geometry' else 0
            while (pos:=original.find(before,start)) >= 0:
                positions.append(pos)
                start=pos+len(before)
            assert len(positions)>occurrence, name+' applies'
            pos=positions[occurrence]
            try:
                path.write_text(original[:pos]+after+original[pos+len(before):])
                previous=tests(tmp,old)
                corrected=tests(tmp,new)
                print(name,'previous_exit',previous.returncode,'corrected_exit',corrected.returncode,flush=True)
                assert corrected.returncode != 0, name+' escaped corrected tests'
            finally:
                path.write_text(original)
        # The runner regression fails against the actual historical classifier.
        path=tmp/'experiments/E036-match-port/out/T60/mutations.py'
        original=path.read_text()
        try:
            path.write_text(subprocess.check_output(['git','show',OLD+':experiments/E036-match-port/out/T60/mutations.py'],cwd=ROOT,text=True))
            result=tests(tmp,new)
            assert result.returncode != 0 and 'MutationEvidence' in result.stderr, result.stderr
            print('historical broken fuzz classifier: new regression fails as intended',flush=True)
        finally:
            path.write_text(original)
    print(f'all {len(CASES)} behavioral controls and broken-classifier control detected')

if __name__ == '__main__':
    main()
