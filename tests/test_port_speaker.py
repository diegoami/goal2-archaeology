"""T123a: speaker-on return ABI against the unmodified original, including flags."""
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from original_match import Image, port
from original_match.assets import reference_image
from original_match.machine import Machine, MEM_SIZE, REGS
from original_match.port.engine import PortMachine

ADDRESS = '214B:1E75'
SS, ENTRY_SP, BP = 0xA000, 0xEFF4, 0x6789
FLAGS = (0x202, 0x203, 0x206, 0x242, 0x282, 0xA02, 0xED7)


def run(m, mute, ax, flags, same_segment=False):
    m.write(m.DS * 16 + 0xA9FC, bytes([mute]))
    cs = m.seg(0x214B)
    ret_cs, ret_ip = (cs if same_segment else 0x9F00), 0x10
    m.write(SS * 16 + ENTRY_SP - 4, bytes([0xA5]) * 16)
    m.write(SS * 16 + ENTRY_SP, ret_ip.to_bytes(2, 'little') + ret_cs.to_bytes(2, 'little'))
    registers = dict(eax=0xCAFE0000 | ax, ebx=0x1234DEAD, ecx=0x34567654,
                     edx=0x45679876, esi=0x56784321, edi=0x67892468,
                     ebp=0x789A0000 | BP, esp=ENTRY_SP, eflags=flags,
                     cs=cs, eip=0x1E75, ds=m.DS, es=0x9000, ss=SS, fs=0x8000, gs=0x7000)
    for name, value in registers.items():
        m.set_reg(name, value)
    reason = m.run(ret_cs * 16 + ret_ip, timeout_s=10, fresh=True)
    assert reason is None, reason
    return {name: m.reg(name) for name in REGS}


def digest(m):
    return hashlib.sha256(m.read(0, MEM_SIZE)).hexdigest()


def check_plain():
    entry = port._module_registry('display').entries[ADDRESS]
    assert entry.stub is None and entry.far and entry.pop == 0
    for mute in (0, 1, 3, 255):
        for flags in FLAGS:
            m = PortMachine(bytes(MEM_SIZE), 0x1000)
            port.install(m, ['display'])
            run(m, mute, 0x1234, flags)
            assert m.reg('ax') == (0x1234 if mute else 0x1203)
            assert m.reg('ah') == 0x12
            expected = (flags & ~0x8D5) | (4 if mute in (0, 3, 255) else 0) | (128 if mute == 255 else 0)
            assert m.reg('eflags') == expected, (mute, flags, m.reg('eflags'), expected)
            assert m.reg('sp') == ENTRY_SP + 4 and m.reg('bp') == BP
            assert m.read(SS * 16 + ENTRY_SP - 2, 2) == BP.to_bytes(2, 'little')
            assert not hasattr(m, '_uc')


class SpeakerABI(unittest.TestCase):
    def test_original_all_registers_flags_complete_memory_and_frames(self):
        image = Image.from_bytes(reference_image(ROOT / '.cache/dl'))
        baseline = bytes(image.memory[:MEM_SIZE]).ljust(MEM_SIZE, b'\0')
        count = 0
        for mute in (0, 1, 3, 255):
            for ax in (0x1234, 0xAB00, 0x00FF):
                for flags in FLAGS:
                    for same_segment in (False, True):
                        with self.subTest(mute=mute, ax=ax, flags=flags, same_segment=same_segment):
                            original = Machine(bytearray(baseline), image.load)
                            candidate = PortMachine(baseline, image.load)
                            port.install(candidate, ['display'])
                            expected = run(original, mute, ax, flags, same_segment)
                            actual = run(candidate, mute, ax, flags, same_segment)
                            self.assertEqual(actual, expected)
                            self.assertEqual(digest(candidate), digest(original), 'complete memory, including dead frame')
                            self.assertEqual(candidate.reg('ax'), ax if mute else (ax & 0xFF00) | 3)
                            self.assertEqual(candidate.reg('ah'), ax >> 8)
                            self.assertEqual(candidate.reg('sp'), ENTRY_SP + 4)
                            self.assertEqual(candidate.reg('bp'), BP)
                            self.assertEqual(candidate.read(SS * 16 + ENTRY_SP - 2, 2), BP.to_bytes(2, 'little'))
                            count += 1
        print(f'T123a original controls: {count}; full REGS/FLAGS and complete memory matched', flush=True)

    def test_plain_positive_unicorn_and_executable_denial(self):
        script = r'''import builtins
from pathlib import Path
real_import, real_open, real_path_open = builtins.__import__, builtins.open, Path.open
seen = set()
def deny_import(name, *args, **kwargs):
 if name == 'unicorn' or name.startswith('unicorn.'):
  seen.add('unicorn'); raise ImportError('T123a denied Unicorn')
 return real_import(name, *args, **kwargs)
def deny_open(path, *args, **kwargs):
 if str(path).lower().endswith('.exe'):
  seen.add('exe'); raise PermissionError('T123a denied EXE')
 return real_open(path, *args, **kwargs)
def deny_path_open(path, *args, **kwargs):
 if str(path).lower().endswith('.exe'):
  seen.add('exe'); raise PermissionError('T123a denied EXE')
 return real_path_open(path, *args, **kwargs)
builtins.__import__, builtins.open, Path.open = deny_import, deny_open, deny_path_open
try: __import__('unicorn')
except ImportError: pass
else: raise AssertionError('import guard did not fire')
try: Path('GOAL.EXE').read_bytes()
except PermissionError: pass
else: raise AssertionError('EXE guard did not fire')
from tests.test_port_speaker import check_plain
check_plain()
assert seen == {'unicorn', 'exe'}
print('T123a positive Unicorn/EXE denial: 28 real PortMachine calls passed')
'''
        result = subprocess.run([sys.executable, '-B', '-c', script], cwd=ROOT,
                                env=dict(os.environ, PYTHONPATH=str(ROOT / 'runtime')),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        print(result.stdout.strip(), flush=True)
