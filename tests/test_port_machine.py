"""T78a: synthetic controls of the no-instruction port dispatcher; no game image needed."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from original_match.port import Registry,install
from original_match.port.mem import PortError
from original_match.port.guest import call


def machine():
    from original_match.port.engine import PortMachine
    from original_match.machine import MEM_SIZE
    return PortMachine(bytes(MEM_SIZE),0x1000)


def nested(stop=None):
    m=machine();r=Registry('synthetic','Synthetic argument/return controls')
    @r.port('0791:0100',ret='retf 2')
    def parent(mem,variant):
        result=yield call('0791:0200',mem.arg(0)+1,ret_to='0791:0110',far=False)
        return result+2
    @r.port('0791:0200',ret='ret 2')
    def child(mem,variant):
        mem.site('0791:0205')
        return mem.arg(0)*3
    ports=install(m,[(r,None)])
    end=m.far_call('0791:0100',[4],'000E:0100',0x3000,0x800)
    if stop:m.at(stop[0],stop[1](m))
    return m,end,ports


class PortableMachine(unittest.TestCase):
    def test_partial_registers_memory_bounds_and_snapshots(self):
        m=machine();m.set_reg('eax',0x12345678)
        self.assertEqual((m.reg('ax'),m.reg('ah'),m.reg('al')),(0x5678,0x56,0x78))
        m.set_reg('ah',0xAB);self.assertEqual(m.reg('eax'),0x1234AB78)
        m.set_reg('ax',-1);self.assertEqual(m.reg('eax'),0x1234FFFF)
        m.set_reg('esp',0xABCD0800);m.set_reg('sp',0x900)
        self.assertEqual(m.reg('esp'),0xABCD0900)
        m.set_reg('eflags',0);self.assertEqual(m.reg('eflags'),2)
        m.write(3,b'abc');snap=m.snapshot();m.write(3,b'xxx');m.restore(snap)
        self.assertEqual(m.read(3,3),b'abc');self.assertEqual(m.snapshot(),snap)
        for address,size in ((-1,1),(0,0x110001),(0x10FFFF,2)):
            with self.assertRaises(PortError):m.read(address,size)
        with self.assertRaises(PortError):m.set_reg('unknown',1)

    def test_nested_near_and_far_returns_use_existing_port_frames(self):
        m,end,ports=nested();self.assertIsNone(m.run(end,fresh=True))
        self.assertEqual(m.reg('ax'),17);self.assertEqual(m.reg('sp'),0x806)
        self.assertEqual(m.frames,[]);self.assertEqual(list(ports.calls.values()),[1,1])
        self.assertEqual(m.pc(),end)

    def test_hooks_writer_identity_and_prewrite_order_are_preserved(self):
        m=machine();r=Registry('synthetic','Writer controls');seen=[]
        @r.port('0791:0100',ret='retf')
        def body(mem,variant):
            mem.wds8(0x10,7,'0791:0105');mem.site('0791:0108')
        install(m,[(r,None)])
        m.at('0791:0100',lambda replay:seen.append(('entry',replay)))
        m.watch(m.DS*16+0x10,1,lambda old,new:seen.append(('write',old,new,m.pc())))
        m.at('0791:0108',lambda replay:seen.append(('site',replay)))
        end=m.far_call('0791:0100',[],'000E:0100',0x3000,0x800)
        m.run(end,fresh=True)
        self.assertEqual(seen,[('entry',False),('write',b'\0',b'\7',m.lin('0791:0105')),('site',False)])
        m.write(m.DS*16+0x10,b'\t');self.assertEqual(len(seen),3)

    def test_entry_decision_resumes_before_running_the_callee_once(self):
        seen=[]
        def callback(m):
            def call(replay):
                seen.append(replay)
                if not replay:m.stop('decision')
            return call
        m,end,ports=nested(('0791:0200',callback))
        self.assertEqual(m.run(end,fresh=True),'decision')
        self.assertEqual(ports.calls['0791:0200'],0)
        self.assertIsNone(m.run(end));self.assertEqual(seen,[False,True])
        self.assertEqual(ports.calls['0791:0200'],1);self.assertEqual(m.reg('ax'),17)

    def test_deferred_site_event_resumes_the_parent_without_replaying_site(self):
        seen=[]
        def callback(m):
            def call(replay):seen.append(replay);m.stop('events')
            return call
        m,end,ports=nested(('0791:0205',callback))
        self.assertEqual(m.run(end,fresh=True),'events')
        self.assertEqual(len(m.frames),1)
        self.assertIsNone(m.run(end));self.assertEqual(seen,[False])
        self.assertEqual(list(ports.calls.values()),[1,1]);self.assertEqual(m.reg('ax'),17)

    def test_unregistered_addresses_never_execute_poison_instruction_bytes(self):
        m=machine();m.write(m.lin('0791:0400'),b'\xcd\x20\xcc')
        end=m.far_call('0791:0400',[],'000E:0100',0x3000,0x800)
        with self.assertRaisesRegex(PortError,'0791:0400'):m.run(end,fresh=True)
        self.assertEqual(m.reg('ax'),0)

    def test_write_listener_failure_does_not_land_the_refused_write(self):
        m=machine();r=Registry('synthetic','Failure control')
        @r.port('0791:0100',ret='retf')
        def body(mem,variant):mem.wds8(0x10,7,'0791:0105')
        install(m,[(r,None)])
        def refuse(old,new):raise ValueError('consumer failure')
        m.watch(m.DS*16+0x10,1,refuse)
        end=m.far_call('0791:0100',[],'000E:0100',0x3000,0x800)
        with self.assertRaisesRegex(ValueError,'consumer failure'):m.run(end,fresh=True)
        self.assertEqual(m.rd(0x10,1),0)

    def test_far_nested_long_return_and_caller_popped_arguments(self):
        m=machine();r=Registry('synthetic','Far call controls')
        @r.port('0791:0100',ret='retf 4',long=True)
        def parent(mem,variant):
            value=yield call('0A00:0200',0x1234,ret_to='0791:0110',far=True,caller_pops=True)
            return (mem.reg('dx')<<16)|value
        @r.port('0A00:0200',ret='retf',long=True)
        def child(mem,variant):
            if mem.arg(0)!=0x1234:raise AssertionError('Far argument order differs')
            return 0x12345678
        install(m,[(r,None)])
        end=m.far_call('0791:0100',[1,2],'000E:0100',0x3000,0x800)
        m.run(end,fresh=True)
        self.assertEqual((m.reg('dx'),m.reg('ax'),m.reg('sp')),(0x1234,0x5678,0x808))
        self.assertEqual(m.frames,[])

    def test_overlapping_word_write_and_port_reads_keep_listener_domains(self):
        m=machine();seen=[];reads=[]
        m.watch(m.DS*16+0x12,1,lambda old,new:seen.append((old,new)))
        m.write_as(m.DS*16+0x10,4,0x78563412,m.lin('0791:0105'))
        self.assertEqual(seen,[(b'\0',b'V')])
        m.io_tap=lambda kind,a,b:reads.append((kind,a,b))
        self.assertEqual(m.port_memory().ds8(0x12),0x56)
        self.assertEqual(reads,[])
        self.assertEqual(m.rd(0x12,1),0x56)
        self.assertEqual(reads,[('r',m.DS*16+0x12,b'V')])

    def test_positive_import_denial_control_and_plain_execution(self):
        script=r'''import builtins,sys
real=builtins.__import__
def no_unicorn(name,*args,**kwargs):
 if name=='unicorn' or name.startswith('unicorn.'):raise ImportError('positive Unicorn denial')
 return real(name,*args,**kwargs)
builtins.__import__=no_unicorn
try:__import__('unicorn')
except ImportError:pass
else:raise AssertionError('denial control failed')
from original_match.port.engine import PortMachine
from original_match.port import Registry,install
from original_match.machine import MEM_SIZE
m=PortMachine(bytes(MEM_SIZE),0x1000)
r=Registry('synthetic','No Unicorn')
@r.port('0791:0100',ret='retf')
def body(mem,variant):return 42
install(m,[(r,None)])
end=m.far_call('0791:0100',[],'000E:0100',0x3000,0x800)
m.run(end,fresh=True)
assert m.reg('ax')==42
assert 'unicorn' not in sys.modules
assert not hasattr(m,'_uc')
print('PASS positive denial and plain port execution')
'''
        env=dict(os.environ,PYTHONPATH=str(ROOT/'runtime'))
        run=subprocess.run([sys.executable,'-B','-c',script],cwd=ROOT,env=env,capture_output=True,text=True)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertIn('PASS positive denial',run.stdout)

if __name__=='__main__':unittest.main()
