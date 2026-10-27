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

class Transcendentals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image=Image.from_bytes(reference_image(ROOT/'.cache/dl'))
        cls.baseline=bytes(cls.image.memory[:MEM_SIZE]).ljust(MEM_SIZE,b'\0')

    def pair(self,address,registers,polynomial=None,coefficients=()):
        original=Machine(bytearray(self.baseline),self.image.load)
        candidate=PortMachine(self.baseline,self.image.load)
        port.install(candidate,['real'])
        if polynomial:
            from original_match.port import real as translated
            registry=port.Registry('synthetic_polynomial','Synthetic polynomial ABI controls')
            @registry.port(address,ret='ret')
            def body(mem,variant):
                R=translated.RealRegs(mem)
                getattr(translated,polynomial)(R)
                R.store()
            port.install(candidate,[(registry,None)])
        for machine in (original,candidate):
            if coefficients:
                data=b''.join(w.to_bytes(2,'little') for row in coefficients for w in row)
                machine.write(machine.seg(0x23E4)*16+0x2000,data)
        regs=dict(ax=0xABCD,bx=0x1234,cx=0x7654,dx=0x9876,si=0x4321,di=0x2468,bp=0x6789,eflags=0x202)
        regs.update(registers)
        original.at('23E4:00D1',lambda replay:original.stop('expected-real-error'))
        _,reason=oracle.run_one(original,not polynomial,address,[],regs)
        if reason=='expected-real-error':
            with self.assertRaisesRegex(PortError,f'real runtime error {original.reg("ax")}'):
                oracle.run_one(candidate,not polynomial,address,[],regs)
            expected=oracle.final(original);actual=oracle.final(candidate)
            for key in ('cs','eip'):expected.pop(key);actual.pop(key)
        else:
            self.assertIsNone(reason)
            oracle.run_one(candidate,not polynomial,address,[],regs)
            expected=oracle.final(original);actual=oracle.final(candidate)
        self.assertEqual(actual,expected)
        import hashlib
        self.assertEqual(hashlib.sha256(candidate.read(0,MEM_SIZE)).hexdigest(),hashlib.sha256(original.read(0,MEM_SIZE)).hexdigest())
        return original.reg('ax') if reason else None

    def test_original_ln_exp_register_flags_frames_and_errors(self):
        values=[real(e,m,n) for e in (0,1,100,127,128,129,130,133,134,135,136,137,254,255)
                for m in (0,(1<<39)-1) for n in (False,True)]
        for magnitude in (87,88,89):
            mantissa=(magnitude << (40-magnitude.bit_length()))-(1<<39)
            values += [real(128+magnitude.bit_length(),mantissa,negative) for negative in (False,True)]
        values += [real(129,m) for m in ((1<<13)-1,1<<13,(1<<13)+1)]
        values += [real(128,(1<<39)-(1<<14)+delta) for delta in (-1,0,1)]
        rnd=random.Random(7832)
        values += [real(rnd.randrange(1,256),rnd.getrandbits(39),bool(rnd.getrandbits(1))) for _ in range(20)]
        errors=set()
        for address in ('23E4:0E67','23E4:0F10'):
            for value in values:
                for flags in (0x202,0xED7):
                    with self.subTest(address=address,registers=value,flags=flags):
                        error=self.pair(address,dict(zip(('ax','bx','dx','eflags'),value+(flags,))))
                        if error is not None:errors.add(error)
        self.assertEqual(errors,{0xCD,0xCF})

    def test_original_shared_polynomials_on_authored_coefficients(self):
        for name,address in (('polynomial','23E4:1101'),('odd_polynomial','23E4:10E8')):
            for count in (1,2,6,8):
                coefficients=[real(129+i%2,1 if i%2 else 0,bool(i%3==0)) for i in range(count)]
                for value in (real(0),real(128),real(129),real(128,0,True)):
                    with self.subTest(polynomial=name,count=count,value=value):
                        self.pair(address,dict(zip(('ax','bx','dx'),value),cx=count,di=0x2000),name,coefficients)

    def test_positive_denial_ln_one_exp_zero(self):
        script='''import builtins
real_import=builtins.__import__
def deny(name,*a,**kw):
 if name=='unicorn' or name.startswith('unicorn.'):raise ImportError('denied')
 return real_import(name,*a,**kw)
builtins.__import__=deny
try:__import__('unicorn')
except ImportError:pass
else:raise AssertionError('guard failed')
from original_match import Image
from original_match.assets import reference_image
from original_match.port.engine import PortMachine
from original_match.port import install
from tests.test_port_real import oracle
image=Image.from_bytes(reference_image('.cache/dl'))
m=PortMachine(image.memory,image.load)
install(m,['real'])
oracle.run_one(m,True,'23E4:0E67',[],dict(ax=0x81,bx=0,dx=0))
assert (m.reg('ax'),m.reg('bx'),m.reg('dx'))==(0,0,0)
oracle.run_one(m,True,'23E4:0F10',[],dict(ax=0,bx=0,dx=0))
assert (m.reg('ax'),m.reg('bx'),m.reg('dx'))==(0x81,0,0)
from original_match.port import Registry
from original_match.port.real import RealRegs,polynomial
r=Registry('synthetic_polynomial','hand-derived polynomial')
@r.port('23E4:1101',ret='ret')
def evaluate(mem,variant):
 R=RealRegs(mem);polynomial(R);R.store()
install(m,[(r,None)])
m.write(m.seg(0x23E4)*16+0x2000,b'\\x81\\x00\\x00\\x00\\x00\\x00'*2)
oracle.run_one(m,False,'23E4:1101',[],dict(ax=0x82,bx=0,dx=0,cx=2,di=0x2000))
assert (m.reg('ax'),m.reg('bx'),m.reg('dx'))==(0x83,0,0x6000) # 1+2+2^2=7
assert not hasattr(m,'_uc')
'''
        result=subprocess.run([sys.executable,'-B','-c',script],cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/'runtime')),capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
