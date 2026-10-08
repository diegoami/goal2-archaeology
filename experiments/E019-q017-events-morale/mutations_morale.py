#!/usr/bin/env python3
"""Round-1 mutation sweep for `runtime/model/morale.py`.

For every numeric constant in the module and for every behavior mutant
(named helpers deleted), shift / delete the named token, restore the
original, and re-run the unit tests. Each mutant must break at least one
test (T32's discipline, F019 review R2).

Run after the unit tests are green. Records each mutant to stdout.
"""
import importlib
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MORALE_PATH = ROOT / 'runtime/model/morale.py'


CONSTANTS = [
    ('BYTE_BITS', 8),
    ('WORD_BITS', 16),
    ('LIVE_LOWER', 1),
    ('LIVE_UPPER', 255),
    ('SAVED_UPPER', 32),
    ('PANEL_MIN', 0),
    ('PANEL_MAX', 32),
    ('PANEL_SEED', 6),
    ('PANEL_DIVISOR', 11),
    ('PANEL_FLOOR', 1),
]


def restore():
    """Re-read the model file from disk, in case a previous mutation left
    it modified."""
    sys.path.insert(0, str(ROOT))
    importlib.reload(__import__('runtime.model.morale', fromlist=['morale']))


def mutate_constant(name, value, delta):
    original = MORALE_PATH.read_text()
    mutated = re.sub(
        rf"^({name}\s*=\s*){value}\b",
        rf"\g<1>{value + delta}",
        original, flags=re.MULTILINE,
    )
    if mutated == original:
        return False, None
    return True, original, mutated


def write_and_sync(path, content):
    """Write the file and fsync so the subprocess sees the mutation.

    Without an explicit flush, Python's buffered writer can hold the new
    content in process memory while the subprocess reads stale bytes
    from the kernel's page cache.
    """
    with open(path, 'w') as f:
        f.write(content)
        f.flush()
        import os
        os.fsync(f.fileno())


def delete_helper(name):
    """Delete the named function from the module by removing its def line."""
    original = MORALE_PATH.read_text()
    mutated = re.sub(
        rf"^def {name}\([^)]*\):.*?(?=\n(?:def |class |if __name__|\Z))",
        '', original, flags=re.MULTILINE | re.DOTALL,
    )
    if mutated == original:
        return False, None
    return True, original, mutated


def run_unit_tests():
    """Run `tests/test_model_morale.py` in a child Python interpreter to
    avoid stale-module cache."""
    import os
    cwd = os.getcwd()
    file_content = MORALE_PATH.read_text()
    has_panel_max_33 = 'PANEL_MAX = 33' in file_content
    proc = subprocess.run(
        [sys.executable, '-m', 'unittest', '-v', 'tests.test_model_morale'],
        cwd=ROOT, capture_output=True, text=True, timeout=60,
    )
    summary = f"\n[cwd={cwd}, returncode={proc.returncode}, has_PANEL_MAX_33={has_panel_max_33}]"
    return proc.returncode == 0, summary + proc.stdout[-2000:]


def _run_iteration_for_debug(name, value, delta):
    """Run a single iteration as the main loop would."""
    ok, original, mutated = mutate_constant(name, value, delta)
    if not ok:
        return None
    MORALE_PATH.write_text(mutated)
    try:
        return run_unit_tests()
    finally:
        MORALE_PATH.write_text(original)
        restore()


def main():
    import os
    killed = 0
    survived = []
    for name, value in CONSTANTS:
        for delta in (1, -1):
            ok, original, mutated = mutate_constant(name, value, delta)
            if not ok:
                survived.append(f'{name}={value + delta} (mutation did not apply)')
                continue
            write_and_sync(MORALE_PATH, mutated)
            try:
                green, log = run_unit_tests()
            finally:
                write_and_sync(MORALE_PATH, original)
                # restore() reloads the parent-process module cache after the
                # file has been restored; without it the parent's module
                # still holds the mutated constant, which can confuse the
                # NEXT mutation's captured `original`. We pass on reload
                # (the subprocess is a fresh Python interpreter and the
                # file on disk is the canonical source).
            if green:
                survived.append(f'{name}={value + delta} (unit suite still green)')
            else:
                killed += 1
                print(f'killed: {name}={value + delta}')
    # Behaviour mutants: delete each named helper and confirm a test fails.
    for helper in ('injure', 'send_off', 'scorer', 'team_reaction', 'event_clamp'):
        ok, original, mutated = delete_helper(helper)
        if not ok:
            survived.append(f'delete {helper} (mutation did not apply)')
            continue
        write_and_sync(MORALE_PATH, mutated)
        try:
            green, log = run_unit_tests()
        finally:
            write_and_sync(MORALE_PATH, original)
        if green:
            survived.append(f'delete {helper} (unit suite still green)')
        else:
            killed += 1
            print(f'killed: delete {helper}')
    # Sanity: re-run after restore.
    green, _ = run_unit_tests()
    if not green:
        survived.append('post-restore run failed')
    print(f'\nkilled: {killed}, survived: {len(survived)}')
    if survived:
        for s in survived:
            print(f'  SURVIVED: {s}')
        sys.exit(1)


if __name__ == '__main__':
    main()