"""T78b3a: synthetic six-byte-real arithmetic against unmodified original code."""
import importlib.util
import os
from pathlib import Path
import random
import subprocess
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import Image,port
from original_match.assets import reference_image
from original_match.machine import Machine,MEM_SIZE
from original_match.port.engine import PortMachine
from original_match.port.mem import PortError
spec=importlib.util.spec_from_file_location('real_oracle',ROOT/'experiments/E036-match-port/out/T60/fuzz.py')
oracle=importlib.util.module_from_spec(spec);spec.loader.exec_module(oracle)

def real(exponent,mantissa=0,negative=False):
    return ((mantissa&255)<<8)|exponent,(mantissa>>8)&65535,((mantissa>>24)&32767)|(32768 if negative else 0)

def cases():
    for value in (0,1,-1,2,-2,255,256,32767,32768,-32768,0x7FFFFFFF,-0x80000000):
        yield '23E4:0CB9',dict(ax=value&65535,dx=(value>>16)&65535)
    values=[real(0),real(0,(1<<39)-1,True),real(129),real(128),real(130),real(129,0,True),real(129,(1<<39)-1),
            real(1),real(255),real(128,(1<<39)-1,True),real(159),real(160),real(127),real(160,0,True),
            real(159,(1<<39)-(1<<9)),real(159,(1<<39)-(1<<8)),
            real(168),real(169),real(129,1),real(128,1)]
    rnd=random.Random(783)
    values += [real(rnd.randrange(1,256),rnd.getrandbits(39),bool(rnd.getrandbits(1))) for _ in range(12)]
    for a in values:
        yield '23E4:0CC5',dict(zip(('ax','bx','dx'),a))
        for b in values:
            regs=dict(zip(('ax','bx','dx','cx','si','di'),a+b))
            for address in ('23E4:0C93','23E4:0CA5','23E4:0CAB'):
                yield address,regs

class Arithmetic(unittest.TestCase):
    def test_synthetic_arithmetic_register_flags_frames_and_errors(self):
        image=Image.from_bytes(reference_image(ROOT/'.cache/dl'))
        baseline=bytes(image.memory[:MEM_SIZE]).ljust(MEM_SIZE,b'\0')
        error_codes=set()
        controls=0
        for address,overrides,flags in ((a,b,f) for a,b in cases() for f in (0x202,0xED7)):
            with self.subTest(address=address,registers=overrides,flags=flags):
                original=Machine(bytearray(baseline),image.load)
                candidate=PortMachine(baseline,image.load)
                port.install(candidate,['real'])
                regs=dict(ax=0xABCD,bx=0x1234,cx=0x7654,dx=0x9876,si=0x4321,di=0x2468,bp=0x6789,eflags=flags)
                regs.update(overrides)
                original.at('23E4:00D1',lambda replay:original.stop('expected-real-error'))
                _,reason=oracle.run_one(original,True,address,[],regs)
                controls+=1
                if reason=='expected-real-error':
                    error_codes.add(original.reg('ax'))
                    with self.assertRaisesRegex(PortError,f'real runtime error {original.reg("ax")}'):
                        oracle.run_one(candidate,True,address,[],regs)
                    expected=oracle.final(original);actual=oracle.final(candidate)
                    for key in ('cs','eip'):expected.pop(key);actual.pop(key)
                else:
                    self.assertIsNone(reason)
                    oracle.run_one(candidate,True,address,[],regs)
                    expected=oracle.final(original);actual=oracle.final(candidate)
                self.assertEqual(actual,expected)
                # Hashes keep an assertion failure from printing any reference image bytes.
                import hashlib
                self.assertEqual(hashlib.sha256(candidate.read(0,MEM_SIZE)).hexdigest(),hashlib.sha256(original.read(0,MEM_SIZE)).hexdigest())

        self.assertEqual(error_codes,{0xC8,0xCD,0xCF})
        print(f'original differential controls: {controls}; error codes: {sorted(error_codes)}',flush=True)

    def test_positive_import_denial_and_hand_derived_integer_round_trip(self):
        script='''import builtins
real_import=builtins.__import__
def deny(name,*a,**kw):
 if name=='unicorn' or name.startswith('unicorn.'):raise ImportError('denied')
 return real_import(name,*a,**kw)
builtins.__import__=deny
try:__import__('unicorn')
except ImportError:pass
else:raise AssertionError('guard failed')
from tests.test_port_real import oracle
from original_match.port.engine import PortMachine
from original_match.port import install
from original_match.machine import MEM_SIZE
m=PortMachine(bytes(MEM_SIZE),0x1000)
install(m,['real'])
oracle.run_one(m,True,'23E4:0CB9',[],dict(ax=1,dx=0))
assert (m.reg('ax'),m.reg('bx'),m.reg('dx'))==(0x81,0,0)
oracle.run_one(m,True,'23E4:0CC5',[],dict(ax=0x81,bx=0,dx=0))
assert (m.reg('dx'),m.reg('ax'))==(0,1)
for address,rhs,expected in (('23E4:0C93',0x81,0x82),('23E4:0CA5',0x82,0x82),('23E4:0CAB',0x82,0x80)):
 oracle.run_one(m,True,address,[],dict(ax=0x81,bx=0,dx=0,cx=rhs,si=0,di=0))
 assert (m.reg('ax'),m.reg('bx'),m.reg('dx'))==(expected,0,0),address
oracle.run_one(m,True,'23E4:0CC5',[],dict(ax=0x80,bx=0,dx=0x8000))
assert (m.reg('dx'),m.reg('ax'))==(0xFFFF,0xFFFF)
assert not hasattr(m,'_uc')
'''
        result=subprocess.run([sys.executable,'-B','-c',script],cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/'runtime')),capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
