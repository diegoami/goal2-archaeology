"""T78b1: synthetic helper arguments, compared with unmodified original code.
Reference bytes are loaded by hash at runtime and are never committed here.
"""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from original_match import Image, port
from original_match.assets import reference_image
from original_match.machine import Machine, MEM_SIZE
from original_match.port.engine import PortMachine

spec = importlib.util.spec_from_file_location('helper_oracle', ROOT / 'experiments/E036-match-port/out/T60/fuzz.py')
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)

CASES = []
for slot in (0, 1, 11, 12, 13, 0x8001, 0xFFFF):
    CASES.append(('0791:045D', [slot], []))
for slot in (0, 11, 12, 255):
    CASES.append(('0791:2974', [0x100, 0x9000], [(0x90106, bytes([slot]))]))
    for half, left in ((0, 0), (0, 1), (1, 1), (1, 2), (127, 0xFFFF), (128, 0), (255, 0)):
        CASES.append(('0791:2BE5', [0x100, 0x9000], [(0x90106, bytes([slot])),
            ('ds', 0x8319, bytes([half])), ('ds', 0x831B, left.to_bytes(2, 'little')),
            ('ds', 0x7920, b'\xff\x01')]))
for x, y in ((0, 0), (8, 37), (-8, -37), (9, 0), (0, 38), (-128, 0), (0, -128), (127, 127)):
    CASES.append(('0791:2DCA', [(x & 255) | ((y & 255) << 8)], []))
for element in (0, 7, 8, 127, 128, 255, 0xFF80):
    for present in (False, True):
        data = bytearray(32)
        if present: data[(element & 255) >> 3] = 1 << (element & 7)
        CASES.append(('23E4:08DF', [0x100, 0x9000, element], [(0x90100, bytes(data))]))
for seed in (0, 1, 0x1234, 0x8000, 0xFFFF):
    for n in (0, 1, 2, 256, 0xFFFF):
        CASES.append(('214B:06B1', [n], [('ds', 0xA978, b'\x00\x01\x00\x90'), (0x90100, seed.to_bytes(2, 'little'))]))
    CASES.append(('214B:06FA', [], [('ds', 0xA978, b'\x00\x01\x00\x90'), (0x90100, seed.to_bytes(2, 'little'))]))

# T78b2: wrapped calls omitted by the original direct-call audit.
for position, destination in ((0, 0), (0xABCD, 0xABCD), (0xABCD, 0xABCE), (0xFF80, 0x0080)):
    record = position.to_bytes(2, 'little') + bytes(5) + destination.to_bytes(2, 'little')
    CASES.append(('0791:2CC5', [0x100, 0x9000], [(0x90100, record)]))
for target in (0xABCD, 0xABCE):
    CASES.append(('0791:2CC5', [0xFFFA, 0x9000], [
        (0x9FFFA, b'\xcd\xab'), (0x90001, target.to_bytes(2, 'little')),
        (0xA0001, b'\x00\x00')]))
for seed in (0, 1, 0x8000, 0xFFFF):
    for n in (0, 1, 2, 0xFFFF):
        for off in (0x100, 0x200):
            CASES.append(('214B:0688', [n, off, 0x9000], [
                ('ds', 0xA978, b'\x00\x01\x00\x90'),
                (0x90100, b'\x34\x12'), (0x90200, b'\x78\x56'),
                (0x90000 + off, seed.to_bytes(2, 'little'))]))

class Helpers(unittest.TestCase):
    def test_synthetic_helpers_against_original_including_dead_frames(self):
        image = Image.from_bytes(reference_image(ROOT / '.cache/dl'))
        baseline = bytes(image.memory[:MEM_SIZE]).ljust(MEM_SIZE, b'\0')
        registry = port._module_registry('entrypoints')
        for address, args, writes, flags in ((a, b, c, f) for a, b, c in CASES for f in (0x202, 0xED7)):
            with self.subTest(address=address, args=args, writes=writes, flags=flags):
                machines = [Machine(bytearray(baseline), image.load), PortMachine(baseline, image.load)]
                port.install(machines[1], ['entrypoints'])
                seen = [[], []]
                for m, log in zip(machines, seen):
                    for write in writes:
                        linear, data = (m.DS * 16 + write[1], write[2]) if write[0] == 'ds' else write
                        m.write(linear, data)
                    if address.startswith('214B'):
                        m.watch((args[2] * 16 + args[1]) if address == '214B:0688' else 0x90100, 2, lambda old, new, m=m, log=log: log.append((new, m.pc())))
                    oracle.run_one(m, registry.entries[address].far, address, args,
                        dict(ax=0xABCD, bx=0xDEAD, cx=0x7654, dx=0x9876, si=0x4321,
                             di=0x2468, bp=0x6789, eflags=flags))
                self.assertEqual(oracle.final(machines[1]), oracle.final(machines[0]))
                self.assertEqual(machines[1].read(0, MEM_SIZE), machines[0].read(0, MEM_SIZE))
                self.assertEqual(seen[1], seen[0])
                if address == '214B:0688':
                    other, expected = (0x90200, b'\x78\x56') if args[1] == 0x100 else (0x90100, b'\x34\x12')
                    for m in machines:
                        self.assertEqual(m.read(other, 2), expected, 'unrelated seed changed')
                self.assertFalse(hasattr(machines[1], '_uc'))

    def test_plain_helpers_with_unicorn_import_denied(self):
        script = '''import builtins
real = builtins.__import__
def deny(name,*a,**kw):
 if name == 'unicorn' or name.startswith('unicorn.'): raise ImportError('denied')
 return real(name,*a,**kw)
builtins.__import__=deny
try: __import__('unicorn')
except ImportError: pass
else: raise AssertionError('guard failed')
from original_match.port.engine import PortMachine
from original_match.port import install
from original_match.machine import MEM_SIZE
from tests.test_port_entrypoints import CASES, oracle
from original_match import port
registry=port._module_registry('entrypoints')
visited=set()
for address,args,writes in CASES:
 m=PortMachine(bytes(MEM_SIZE),0x1000)
 install(m,['entrypoints'])
 for write in writes:
  linear,data=(m.DS*16+write[1],write[2]) if write[0]=='ds' else write
  m.write(linear,data)
 oracle.run_one(m,registry.entries[address].far,address,args,{})
 assert not hasattr(m,'_uc')
 visited.add(address)
assert len(visited)==9
'''
        import os
        env = dict(os.environ, PYTHONPATH=str(ROOT / 'runtime'))
        result = subprocess.run([sys.executable, '-B', '-c', script], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
