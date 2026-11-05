"""T123a falsifiers: execute actual leaf source with one expression changed, no file edits."""
import contextlib
import inspect
import io
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'runtime'))
from original_match.port import display
from tests.test_port_speaker import SpeakerABI

entry = display.PORTS.entries['214B:1E75']
original = entry.fn
source = inspect.getsource(original)
source = source[source.index('def '):]
mutations = {
    'enabled-al-loss': ('r.al=3 ', 'r.al=r.al '),
    'mute-condition-inverted': ('if not disabled:', 'if disabled:'),
}
for name, (before, after) in mutations.items():
    assert source.count(before) == 1
    namespace = dict(display.__dict__)
    exec(compile(source.replace(before, after), f'<T123a {name}>', 'exec'), namespace)
    entry.fn = namespace[original.__name__]
    output = io.StringIO()
    suite = unittest.TestSuite([SpeakerABI('test_original_all_registers_flags_complete_memory_and_frames')])
    with contextlib.redirect_stdout(output):
        result = unittest.TextTestRunner(stream=output).run(suite)
    entry.fn = original
    assert not result.wasSuccessful() and result.failures and not result.errors, output.getvalue()
    print(f'{name}: caught by original all-REGS/FLAGS/memory test; {len(result.failures)} failing controls')
