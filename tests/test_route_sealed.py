"""T123 sealed public round API and literal outer frames.

Published reference executions and positive denied PyPy workers are retained
under out/T123. Small boundary fixtures below contain no original code bytes.
"""
import dataclasses,hashlib,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools')]
from original_match import route as R
from original_match.image import Image
from original_match.machine import MEM_SIZE
from original_match.port import route as P
from original_match.port.tables import load as load_tables
from tests.test_port_stages import _Calls,RET
RET.update({'000E:7072':'000E:70EE','000E:70B9':'000E:77C2'})


def terminal_state(stage):
    """Declared empty completed calendar; tests entry guard before any kit write."""
    tables=load_tables(ROOT/'static/goal-exe/tables')
    image=Image.__new__(Image);image.header=bytes(32);image.memory=bytearray(MEM_SIZE)
    image.load=0;image.DS=0x2581;image.tables=tables;tables.place(image.memory,0)
    ds=image.DS*16;image.memory[ds+0xA923:ds+0xA927]=(0x100).to_bytes(2,'little')+(0x5000).to_bytes(2,'little')
    game=0x50100
    for off,value in [(0x26,1),(0x28,1)]:image.memory[game+off:game+off+2]=value.to_bytes(2,'little')
    image.memory[game+0x3C]=stage;image.memory[game+0x3D]=1
    return image.state(tables),tables


class OuterFrames(_Calls):
    def test_shareware_leaf_preserves_AH_and_real_frame(self):
        self.assertEqual(P.PORTS.entries['000E:7072'].ret,'ret')
        m,p=self.call('000E:7072',specs=[(P.PORTS,None)],before=lambda m:m.set_reg('ax',0xABCD))
        self.proved(p,'000E:7072');self.assertEqual(m.reg('ax'),0xAB00)


class Boundary(unittest.TestCase):
    def test_terminal_entry_returns_immutable_step_without_starting_backend(self):
        from port_test_runtime import call_in_pypy
        from original_match.port.tables import to_record
        for stage in (4,8):
            with self.subTest(stage=stage):
                state,tables=terminal_state(stage)
                result=call_in_pypy('test_route_sealed','_boundary_report',args=(state,to_record(tables),False))
                self.assertTrue(result['pure']);self.assertTrue(result['immutable']);self.assertTrue(result['denials'])

    def test_repeated_terminal_request_preserves_every_state_byte(self):
        from port_test_runtime import call_in_pypy
        from original_match.port.tables import to_record
        state,tables=terminal_state(8)
        result=call_in_pypy('test_route_sealed','_boundary_report',args=(state,to_record(tables),True))
        self.assertTrue(result['pure']);self.assertTrue(result['repeated'])


def _denials():
    """Positive worker guards, active before any production API call."""
    import builtins,io,os
    original_import=builtins.__import__;original_open=builtins.open;original_os_open=os.open
    def importing(name,*args,**kwargs):
        if name=='unicorn' or name.startswith('unicorn.'):raise ImportError('T123 positive Unicorn import denial')
        return original_import(name,*args,**kwargs)
    def forbidden(path):
        try:return os.fspath(path).lower().endswith(('.exe','.sav','.dat'))
        except TypeError:return False
    def opening(path,*args,**kwargs):
        if forbidden(path):raise PermissionError('T123 positive original file denial')
        return original_open(path,*args,**kwargs)
    def os_open(path,*args,**kwargs):
        if forbidden(path):raise PermissionError('T123 positive original file denial')
        return original_os_open(path,*args,**kwargs)
    builtins.__import__=importing;builtins.open=io.open=opening;os.open=os_open
    for probe in (lambda:__import__('unicorn'),lambda:open('GOAL.EXE','rb'),lambda:open('probe.sav','rb'),lambda:os.open('probe.DAT',os.O_RDONLY)):
        try:probe()
        except (ImportError,PermissionError):pass
        else:raise AssertionError('denial control inactive')
    from original_match import machine
    def denied(*a,**k):raise RuntimeError('T123 positive Unicorn start denial')
    machine.Uc=denied
    # With imports denied, these constructor argument constants are absent.
    # Sentinels only let the positive tripwire be reached; no VM starts.
    machine.UC_ARCH_X86=0;machine.UC_MODE_16=0
    try:machine.Machine(bytearray(MEM_SIZE),0)
    except RuntimeError as exc:assert 'positive Unicorn start denial' in str(exc)
    else:raise AssertionError('backend-start denial inactive')
    return True


def _factory_report(state,table_record,fixture,context,bad=False):
    assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
    _denials()
    from original_match import Match,Fixture
    from original_match.port.tables import from_record
    tables=from_record(table_record);image=Image.from_state(state,tables);before=hashlib.sha256(image.memory[:MEM_SIZE]).hexdigest()
    if bad:
        context=dict(context);context['ESP']+=2
        try:Match.from_route_entry(image,Fixture(**fixture),context)
        except ValueError:return {'refused':True,'unchanged':hashlib.sha256(image.memory[:MEM_SIZE]).hexdigest()==before}
        raise AssertionError('invalid entry accepted')
    m=Match.from_route_entry(image,Fixture(**fixture),context)
    assert type(m) is Match and not m.inputs and not m.over and m.engine=='port' and m.opts['tail'] is False
    assert m.m.read(0,MEM_SIZE)==bytes(image.memory[:MEM_SIZE])
    assert all(m.m.reg(k)==v for k,v in context.items())
    return {'preserved':True,'backend':'pypy3.11','denials':True,'manager_tags':[m._manager_byte(c) for c in (fixture['first'],fixture['second'])]}


def _entry_report(state,table_record):
    assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
    _denials()
    from original_match import Match
    from original_match.port.tables import from_record
    step=R.play_round(state,from_record(table_record),R.DEFAULT_KEYS)
    assert step.status=='match' and type(step.match) is Match and not step.match.over and not step.match.inputs
    before=hashlib.sha256(step.continuation.m.read(0,MEM_SIZE)).hexdigest()
    for bad_cont,bad_match in [(object(),step.match),(step.continuation,object()),(step.continuation,step.match)]:
        try:R.resume_round(bad_cont,bad_match)
        except ValueError:pass
        else:raise AssertionError('foreign/incomplete resume accepted')
    assert hashlib.sha256(step.continuation.m.read(0,MEM_SIZE)).hexdigest()==before
    return {'status':step.status,'normal_match':True,'no_autopick':not hasattr(step.match,'team_choices'),'invalid_resume_pure':True,'denials':True}


def _fixtures():
    import importlib.util
    path=ROOT/'experiments/E040-route-fixture-writes/out/T123/fixtures.py'
    spec=importlib.util.spec_from_file_location('_t123_test_fixtures',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


class MatchEntry(unittest.TestCase):
    def test_factory_preserves_actual_context_and_existing_manager2(self):
        from port_test_runtime import call_in_pypy
        from original_match.port.tables import to_record
        for manager2 in (False,True):
            with self.subTest(manager2=manager2):
                image,context,fixture=_fixtures().entry(manager2=manager2)
                result=call_in_pypy('test_route_sealed','_factory_report',args=(image.state(image.tables),to_record(image.tables),fixture,context))
                self.assertTrue(result['preserved']);self.assertTrue(result['denials'])
                self.assertIn(130 if manager2 else 129,result['manager_tags'])

    def test_factory_refuses_invalid_frame_before_changes(self):
        from port_test_runtime import call_in_pypy
        from original_match.port.tables import to_record
        image,context,fixture=_fixtures().entry()
        result=call_in_pypy('test_route_sealed','_factory_report',args=(image.state(image.tables),to_record(image.tables),fixture,context,True))
        self.assertTrue(result['refused']);self.assertTrue(result['unchanged'])

    def test_real_pending_normal_match_and_invalid_resume_are_pure(self):
        from port_test_runtime import call_in_pypy
        from original_match.port.tables import to_record
        image=_fixtures().image()
        result=call_in_pypy('test_route_sealed','_entry_report',args=(image.state(image.tables),to_record(image.tables)))
        self.assertTrue(result['normal_match']);self.assertTrue(result['no_autopick']);self.assertTrue(result['invalid_resume_pure'])


def _boundary_report(state,table_record,repeat):
    assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
    _denials()
    from original_match.port.tables import from_record
    tables=from_record(table_record);before=json.dumps(state,sort_keys=True)
    step=R.play_round(state,tables,R.DEFAULT_KEYS)
    assert step.status=='deferred-rollover' and step.state==state and step.state is not state
    assert step.played_fixtures==() and step.news_pages==() and step.match is None and step.continuation is None
    try:step.status='complete'
    except dataclasses.FrozenInstanceError:immutable=True
    else:raise AssertionError('mutable RoundStep')
    if repeat:
        second=R.play_round(step.state,tables,None)
        assert second.status==step.status and second.state==step.state and not second.played_fixtures and not second.news_pages
    assert json.dumps(state,sort_keys=True)==before
    return {'pure':True,'immutable':immutable,'denials':True,'repeated':repeat}


class ReachedSetLeaves(unittest.TestCase):
    def test_expand_and_union_full_memory_registers_and_wrapped_overlap(self):
        """Declared synthetic Pascal frames, including hidden result pointers."""
        from tests.test_port_entrypoints import oracle
        from original_match.machine import Machine
        from original_match.port.engine import PortMachine
        from original_match import port
        image=_fixtures().image();baseline=bytes(image.memory[:MEM_SIZE])
        cases=[]
        for descriptor in (0,0x20,0x0103,0x1F01,0x2020,0xFFFF):
            for src,dst in ((0x100,0x200),(0x100,0x101),(0xFFFE,0xFFFC)):
                cases.append(('23E4:0831',[descriptor,src,0x9000,dst,0x9000]))
        for src,dst in ((0x100,0x200),(0x100,0x102),(0x102,0x100),(0xFFFF,0xFFF9)):
            cases.append(('23E4:0900',[src,0x9000,dst,0x9000]))
        for target,args in cases:
            for flags in (0x202,0xED7):
                with self.subTest(target=target,args=args,flags=flags):
                    machines=[Machine(baseline,image.load),PortMachine(baseline,image.load)]
                    port.install(machines[1],['entrypoints'])
                    for machine in machines:
                        machine.write(0x90000,bytes((i*37+11)&255 for i in range(0x10020)))
                        oracle.run_one(machine,True,target,args,dict(ax=0xABCD,bx=0xDEAD,cx=0x7654,dx=0x9876,si=0x4321,di=0x2468,bp=0x6789,eflags=flags))
                    self.assertEqual(oracle.final(machines[1]),oracle.final(machines[0]))
                    self.assertEqual(machines[1].read(0,MEM_SIZE),machines[0].read(0,MEM_SIZE))
                    # RETF consumes only explicit arguments, leaving hidden result pointer.
                    self.assertEqual(machines[1].reg('sp'),oracle.SP0-12)


RET.update({'0791:B15F':'0791:D4D1','1771:5BF6':'000E:6C4A','1771:7812':'1771:79CF'})


class ReachedRouteLeaves(_Calls):
    def test_decider_membership_and_score_equality_preserve_full_AH(self):
        from original_match.port import silent
        for kind in (0,1,4,8,203,204,255):
            for scores in (b'\x02\x02',b'\x02\x03'):
                with self.subTest(kind=kind,scores=list(scores)):
                    def prepare(m):
                        m.write(0x90100,bytes([0xFF,0,kind,0,3,0,4,0]));m.write(m.DS*16+0x9B3C,scores);m.set_reg('ax',0xABCD)
                    m,p=self.call('0791:B15F',args=(0x9000,0x100),specs=[(silent.PORTS,None)],before=prepare)
                    self.proved(p,'0791:B15F');self.assertEqual(m.reg('ax')>>8,0xAB)

    def test_silent_header_real_helper_frames(self):
        from original_match.port import display
        for stage in (2,5,8):
            with self.subTest(stage=stage):
                m,p=self.call('1771:5BF6',specs=[(display.PORTS,None)],game={0x3C:stage})
                self.proved(p,'1771:5BF6')

    def test_fixture_row_real_hidden_string_and_pending_marker(self):
        from original_match.port import display
        for kind in (0,1,2,4,8,203):
            for status in (0xFE,0xFF,2):
                with self.subTest(kind=kind,status=status):
                    def prepare(m):m.write(0x90100,bytes([status,1,kind,0,3,0,4,0]))
                    m,p=self.call('1771:7812',args=(0x9000,0x100,7,0x21),specs=[(display.PORTS,None)],before=prepare)
                    self.proved(p,'1771:7812')


def _pair_candidate(state,tables):
    import importlib.util
    path=ROOT/'experiments/E040-route-fixture-writes/out/T123/pairs.py'
    spec=importlib.util.spec_from_file_location('_t123_pairs',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.candidate(state,tables)


def _before_callback(sources,function,args,kwargs):
    import types,importlib
    import original_match
    for name,text in sources.items():
        parent,_,leaf=name.rpartition('.');module=types.ModuleType(name);module.__package__=parent;module.__file__=str(ROOT/'runtime'/Path(*name.split('.')).with_suffix('.py'))
        sys.modules[name]=module;exec(compile(text,module.__file__,'exec'),module.__dict__);setattr(importlib.import_module(parent),leaf,module)
    original_match.Match=sys.modules['original_match.match'].Match
    globals()['R']=sys.modules['original_match.route'];globals()['P']=sys.modules['original_match.port.route']
    return globals()[function](*args,**kwargs)


class ReachedFalsifiers(_Calls):
    def test_omitted_decider_header_and_row_are_detected_by_original(self):
        from original_match import port
        from original_match.port.prove import ProofError
        for owner,target,args in [('silent','0791:B15F',(0x9000,0x100)),('display','1771:5BF6',()),('display','1771:7812',(0x9000,0x100,7,0x21))]:
            with self.subTest(target=target):
                original=port._module_registry(owner).entries[target]
                mutant=port.Registry(owner,'test-only exact body omission, ABI preserved')
                mutant._add(port.Entry(target,original.ret,lambda mem,variant:None,'omitted-body'))
                def prepare(m):
                    m.write(0x90100,b'\xfe\x00\x04\x00\x03\x00\x04\x00')
                    m.write(m.DS*16+0x9B3C,b'\x02\x02');m.set_reg('ax',0xABCD)
                with self.assertRaises(ProofError):self.call(target,args=args,specs=[(mutant,None)],before=prepare)

    def test_omitted_expand_and_union_fail_complete_original_comparison(self):
        from tests.test_port_entrypoints import oracle
        from original_match import port
        from original_match.machine import Machine
        from original_match.port.engine import PortMachine
        baseline=bytes(self.image.memory[:MEM_SIZE])
        for target,args in [('23E4:0831',[0x0103,0x100,0x9000,0x200,0x9000]),('23E4:0900',[0x100,0x9000,0x200,0x9000])]:
            with self.subTest(target=target):
                entry=port._module_registry('entrypoints').entries[target]
                mutant=port.Registry('entrypoints','test-only body omission')
                mutant._add(port.Entry(target,entry.ret,lambda mem,variant:None,'omitted-body'))
                reference=Machine(baseline,self.image.load);candidate=PortMachine(baseline,self.image.load)
                port.install(candidate,[(mutant,None)])
                for machine in (reference,candidate):
                    machine.write(0x90100,bytes(range(64)));machine.write(0x90200,bytes([0xA5])*64)
                    oracle.run_one(machine,True,target,args,dict(ax=0xABCD,eflags=0xED7))
                self.assertNotEqual(candidate.read(0,MEM_SIZE),reference.read(0,MEM_SIZE))
