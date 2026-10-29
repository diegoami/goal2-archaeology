"""T78b: the actual Match facade on Python ports with no instruction backend.

The reference fixture and policies are existing admitted kit inputs. Dispatcher
assembly is compared with the same proved ports under the reference machine;
the unhooked strict family acceptance remains T78d/T79.
"""
import dataclasses
import json
import hashlib
import tempfile
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import Image,Match,Fixture
from original_match.assets import reference_image
from original_match.port.engine import PortMachine


def play(image,engine,kind=1,seed=0x1234,interactive=False):
    m=Match(image,Fixture(7,19,index=21,kind=kind),managed=7,seed=seed,
            record_draws=True,delay_byte=0,ports=['all'],engine=engine)
    events=[];paused=False
    for event in m.events():
        events.append(dataclasses.asdict(event))
        if interactive and event.kind=='minute' and event.minute>=20 and not paused:
            paused=True;m.pause()
        if event.kind=='decision':
            if interactive and event.data['context']=='pause':
                m.answer(tactics={4:not bool(event.data['tactics']&8)})
            else:m.answer()
    return m,events


def memory_digest(match):
    # Preserve a complete-memory comparison without printing original image bytes on failure.
    return hashlib.sha256(match.m.read(0,0x110000)).hexdigest()


def play_knockout(image,engine):
    from original_match import example
    m=Match(image,Fixture(7,19,index=example.KNOCKOUT_INDEX,kind=example.KNOCKOUT),
            managed=7,substitutions=example.BUDGET,record_draws=True,ports=['all'],engine=engine,
            # Full Python-port stretches exceed the public API's 60s default on CI (#605).
            timeout_s=600)
    events=[]
    for event in m.events():
        events.append(dataclasses.asdict(event))
        if event.kind=='decision':example.knockout_answer(m,event.data,lambda *args:None)
    return m,events


class Engine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image=Image.from_savestate(reference_image(ROOT/'.cache/dl'))

    def test_port_constructor_uses_the_plain_backend_and_preserves_original_default(self):
        m=Match(self.image,Fixture(7,19,index=21),managed=7,engine='port')
        self.assertIsInstance(m.m,PortMachine);self.assertFalse(hasattr(m.m,'_uc'))
        self.assertEqual(m.opts['engine'],'port')
        self.assertGreater(len(m.ports.names),10)
        original=Match(self.image,Fixture(7,19,index=21),managed=7)
        self.assertNotIsInstance(original.m,PortMachine);self.assertNotIn('engine',original.opts)

    def test_unknown_engine_and_inline_original_proof_are_refused(self):
        for kwargs in (dict(engine='unknown'),dict(engine='port',prove=0)):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):Match(self.image,Fixture(7,19,index=21),managed=7,**kwargs)

    def test_complete_reference_fixture_events_results_and_memory_equal(self):
        original,events=play(self.image,'original')
        candidate,actual=play(self.image,'port')
        self.assertEqual(actual,events)
        self.assertEqual(candidate.result(),original.result())
        self.assertEqual(memory_digest(candidate),memory_digest(original))

    def test_interactive_pause_tactics_and_halftime_equal(self):
        original,events=play(self.image,'original',interactive=True)
        candidate,actual=play(self.image,'port',interactive=True)
        self.assertTrue(any(e['kind']=='decision' and e['data']['context']=='pause' for e in actual))
        self.assertEqual(actual,events);self.assertEqual(candidate.result(),original.result())
        self.assertEqual(memory_digest(candidate),memory_digest(original))

    def test_knockout_match_result_and_events_equal(self):
        original,events=play_knockout(self.image,'original')
        candidate,actual=play_knockout(self.image,'port')
        self.assertTrue(candidate.result()['extra_time'])
        self.assertIsNotNone(candidate.result()['shootout'])
        self.assertEqual(actual,events);self.assertEqual(candidate.result(),original.result())
        self.assertEqual(memory_digest(candidate),memory_digest(original))

    def test_no_unicorn_positive_denial_runs_a_complete_match(self):
        script=r'''import builtins,sys,json
real=builtins.__import__
def deny(name,*args,**kwargs):
 if name=='unicorn' or name.startswith('unicorn.'):raise ImportError('positive Unicorn denial')
 return real(name,*args,**kwargs)
builtins.__import__=deny
try:__import__('unicorn')
except ImportError:pass
else:raise AssertionError('denial is not installed')
from original_match import Image,Match,Fixture
from original_match.assets import reference_image
m=Match(Image.from_savestate(reference_image('.cache/dl')),Fixture(7,19,index=21),managed=7,seed=0x1234,record_draws=True,delay_byte=0,engine='port')
for event in m.events():pass
r=m.result()
assert r['score']==[1,1],r['score']
assert r['ticks']==4146,r['ticks']
assert r['draws']==184109,r['draws']
assert r['draws_digest']=='74b8eb805a4e391f2a0e4e213830b5c734d1b5086c75c682c5978b6403f9563e'
assert 'unicorn' not in sys.modules
assert not hasattr(m.m,'_uc')
print(json.dumps(dict(positive_denial=True,completed=True,score=r['score'],ticks=r['ticks'],draws=r['draws'])))
'''
        # This is a complete match, not one event stretch; CI exceeded 600s (#605).
        run=subprocess.run([sys.executable,'-B','-c',script],cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/'runtime')),capture_output=True,text=True,timeout=1800)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertIn('"completed": true',run.stdout)



class Checkpoints(unittest.TestCase):
    """T78c: real image checkpoints; no original bytes enter the receipts."""
    @classmethod
    def setUpClass(cls):
        cls.image=Image.from_savestate(reference_image(ROOT/'.cache/dl'))

    def new(self,engine='port'):
        return Match(self.image,Fixture(7,19,index=21),managed=7,engine=engine,record_draws=True)

    @staticmethod
    def unpack(blob):
        import zlib
        n=int.from_bytes(blob[4:8],'little')
        return json.loads(blob[8:8+n]),zlib.decompress(blob[8+n:])

    def test_plain_checkpoint_keeps_backend_and_legacy_saves_keep_original(self):
        m=self.new();blob=m.save();r=Match.load(blob)
        self.assertIsInstance(r.m,PortMachine);self.assertFalse(hasattr(r.m,'_uc'))
        self.assertEqual(r.engine,'port');self.assertEqual(hashlib.sha256(r.save()).digest(),hashlib.sha256(blob).digest())
        legacy=self.new('original');state,memory=self.unpack(legacy.save())
        for version in ('2','3','4'):
            with self.subTest(version=version):
                state['version']=version
                r=Match.load(Match._encode_save(state,memory))
                self.assertEqual(r.engine,'original');self.assertNotIsInstance(r.m,PortMachine)

    def test_unknown_corrupt_stale_backend_refuses_before_machine_construction(self):
        from original_match.match import MatchError
        state,memory=self.unpack(self.new('original').save())
        mutations=[dict(engine='future'),dict(engine=None),dict(engine=[]),dict(engine=True),
                   dict(engine='port',version='3'),dict(engine='port',ports=[])]
        before=hashlib.sha256(memory).hexdigest()
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                broken=json.loads(json.dumps(state))
                if 'version' in mutation:broken['version']=mutation['version']
                broken['opts'].update({k:v for k,v in mutation.items() if k!='version'})
                with patch('original_match.match.Machine',side_effect=AssertionError('constructed original')),patch(
                        'original_match.port.engine.PortMachine',side_effect=AssertionError('constructed port')):
                    with self.assertRaises((ValueError,MatchError)):
                        Match.load(Match._encode_save(broken,memory))
        self.assertEqual(hashlib.sha256(memory).hexdigest(),before)

    def test_replay_origin_must_be_plain_and_have_the_same_backend_before_construction(self):
        from original_match.match import MatchError
        state,memory=self.unpack(self.new('original').save())
        for outer_engine,inner_engine in (('original','port'),('port','original'),('port','unknown')):
            with self.subTest(outer=outer_engine,inner=inner_engine):
                outer=json.loads(json.dumps(state));inner=json.loads(json.dumps(state))
                for item,engine in ((outer,outer_engine),(inner,inner_engine)):
                    item['opts']['engine']=engine
                    if engine=='port':item['opts']['ports']=['all']
                outer['replay']={'origin':Match._encode_save(inner,memory).hex(),
                                 'events':0,'actions':[],'frames':[]}
                with patch('original_match.match.Machine',side_effect=AssertionError('constructed original')),patch(
                        'original_match.port.engine.PortMachine',side_effect=AssertionError('constructed port')):
                    with self.assertRaises((ValueError,MatchError)):
                        Match.load(Match._encode_save(outer,memory))

    def test_frame_free_answer_records_keep_pair_types_after_loading(self):
        # [designed: T78c] Authored pause state isolates the public answer record
        # schema without replaying a match; no fabricated game result is used.
        m=self.new()
        squad=m._squad(7);other=m._squad(19)
        m.st["waiting"]={"context":"pause"}
        m.answer(tactics={4:True},positions={squad[5]:7},
                 marking={squad[3]:other[9]},own_tactics={squad[7]:{1:True,2:None}},
                 substitutions=[(squad[10],squad[18])])
        before=m.st["decisions"]
        self.assertTrue(before[-1]["answer"]["own_tactics"])
        loaded=Match.load(m.save())
        self.assertEqual(loaded.st["decisions"],before)
        self.assertEqual(memory_digest(loaded),memory_digest(m))
        self.assertEqual(loaded.save(),m.save())

    def test_completed_quick_match_answer_records_and_memory_survive_loading(self):
        # [derived: E033] Actual play through a pause and post-match tail,
        # including nested answer records; the end checkpoint has no live frame.
        m=self.new();paused=False
        for event in m.events():
            if event.kind=='minute' and not paused:
                paused=True;m.pause()
            if event.kind=='decision':
                if event.data['context']=='pause':
                    d=event.data;player=d['eleven'][5]
                    m.answer(quick=True,tactics={4:True},
                             positions={player:dict(d['positions'])[player]},
                             marking={d['eleven'][3]:m._squad(19)[9]},
                             own_tactics={player:{1:True,2:None}})
                else:m.answer()
        self.assertTrue(paused)
        self.assertFalse(m.m.frames)
        before=m.result();loaded=Match.load(m.save())
        self.assertEqual(loaded.result(),before)
        self.assertEqual(loaded.st['decisions'],m.st['decisions'])
        self.assertEqual(memory_digest(loaded),memory_digest(m))
        self.assertEqual(loaded.save(),m.save())

    def test_live_decisions_and_completed_tail_with_positive_unicorn_denial(self):
        script=r'''import builtins,sys
real=builtins.__import__
def deny(name,*args,**kwargs):
 if name=='unicorn' or name.startswith('unicorn.'):raise ImportError('positive Unicorn denial')
 return real(name,*args,**kwargs)
builtins.__import__=deny
try:__import__('unicorn')
except ImportError:pass
else:raise AssertionError('denial not installed')
from tests.test_port_engine import Checkpoints,Match,Fixture
Checkpoints.setUpClass();case=Checkpoints('runTest')
def make():return Match(case.image,Fixture(7,19,index=21),managed=7,engine='port',record_draws=True)
def quick(m,d):m.answer(quick=True) if d['context']=='pause' else m.answer()
case.boundary_case('guarded live pause to quick result',make,quick,(1,))
assert 'unicorn' not in sys.modules
print('positive denial checkpoint PASS')
'''
        run=subprocess.run([sys.executable,'-B','-c',script],cwd=ROOT,
            env=dict(os.environ,PYTHONPATH=str(ROOT/'runtime')),capture_output=True,text=True,timeout=300)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertIn('positive denial checkpoint PASS',run.stdout)

    def boundary_case(self,name,make,policy,pause_at):
        # [derived] E033/E034's exact policies/boundaries, strengthened with complete
        # result (records + RNG transcript) and full-memory comparisons.
        import importlib.util
        spec=importlib.util.spec_from_file_location('t78c_e033',ROOT/'experiments/E033-original-match-kit/save_boundaries.py')
        harness=importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
        m=make();saves=[];kinds=set()
        def capture(i,event,phase):
            if phase=='answered' or event.kind not in kinds or event.kind in ('decision','end'):
                if event is not None:kinds.add(event.kind)
                saves.append((i,phase,m.save()))
        straight=harness.drive(m,policy,pause_at,capture)
        wanted=m.result();memory=memory_digest(m)
        self.assertTrue(saves,name)
        for index,phase,blob in saves:
            with self.subTest(scenario=name,index=index,phase=phase):
                r=Match.load(blob)
                self.assertIsInstance(r.m,PortMachine)
                self.assertEqual(r.engine,'port')
                actual_state,actual_memory=self.unpack(r.save());saved_state,saved_memory=self.unpack(blob)
                for actual,saved in ((json.dumps(actual_state,sort_keys=True).encode(),json.dumps(saved_state,sort_keys=True).encode()),
                                     (actual_memory,saved_memory)):
                    self.assertEqual(hashlib.sha256(actual).hexdigest(),hashlib.sha256(saved).hexdigest())
                rest=harness.drive(r,policy,pause_at,start=index+1)
                self.assertEqual(rest,straight[index+1:])
                self.assertEqual(r.result(),wanted)
                self.assertEqual(memory_digest(r),memory)
                print(f'checkpoint PASS {name} boundary={index} phase={phase}',flush=True)


def _checkpoint_scenarios():
    import importlib.util
    spec=importlib.util.spec_from_file_location('t78c_policies',ROOT/'experiments/E033-original-match-kit/save_boundaries.py')
    harness=importlib.util.module_from_spec(spec);spec.loader.exec_module(harness)
    import original_match as kit
    for number,(name,kwargs,pauses,policy) in enumerate(harness.SCENARIOS,1):
        def case(self,name=name,kwargs=kwargs,pauses=pauses,policy=policy):
            self.boundary_case(name,lambda:harness.make(kit,self.image,kwargs|{'engine':'port','record_draws':True}),policy,pauses)
        setattr(Checkpoints,f'test_e033_{number:02d}',case)
    from original_match import example
    policies=(lambda m,d:example.knockout_answer(m,d,lambda *a:None),harness.play_on,
              lambda m,d:m.answer(quick=True) if d['context']=='half_time' else m.answer())
    for number,(index,budget,policy) in enumerate(zip((39,42,9),(5,None,None),policies),1):
        def case(self,index=index,budget=budget,policy=policy):
            self.boundary_case(f'E034 index {index}',lambda:Match(self.image,Fixture(7,19,index=index,kind=200),
                managed=7,substitutions=budget,engine='port',record_draws=True),policy,())
        setattr(Checkpoints,f'test_e034_{number:02d}',case)
_checkpoint_scenarios()


class CLI(unittest.TestCase):
    def test_no_unicorn_requires_explicit_port_backend(self):
        commands = ([sys.executable, '-B', str(ROOT/'experiments/E036-match-port/family.py'),
                     '--family', 'S', '--out', str(ROOT/'.cache/unused-engine-refusal.jsonl')],
                    [sys.executable, '-B', '-m', 'original_match.check'])
        for command in commands:
            with self.subTest(command=command):
                run = subprocess.run([*command, '--no-unicorn'], cwd=ROOT,
                    env=dict(os.environ, PYTHONPATH=str(ROOT/'runtime')), capture_output=True, text=True, timeout=30)
                self.assertEqual(run.returncode, 2, run.stdout+run.stderr)
                self.assertIn('--no-unicorn requires --engine port', run.stdout+run.stderr)

    def test_abbreviated_engine_and_guard_options_do_not_relaunch_recursively(self):
        # Bound the old recursive relaunch in the test child, so failure cannot leak a process chain.
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            (folder/'sitecustomize.py').write_text(
                "import os\n"
                "depth=int(os.environ.get('GOAL2_TEST_CLI_DEPTH','0'))+1\n"
                "os.environ['GOAL2_TEST_CLI_DEPTH']=str(depth)\n"
                "if depth>2: os._exit(97)\n")
            for number,flags in enumerate((('--engine','port','--no-un'),('--eng','port','--no-unicorn'))):
                with self.subTest(flags=flags):
                    path=folder/f'case-{number}.jsonl'
                    command=[sys.executable,'-B',str(ROOT/'experiments/E036-match-port/family.py'),
                             '--family','S','--only','S/quick-1','--cache',str(ROOT/'.cache/dl'),
                             '--out',str(path),*flags]
                    env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(folder),str(ROOT/'runtime'))),GOAL2_TEST_CLI_DEPTH='0')
                    run=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=90)
                    self.assertEqual(run.returncode,0,run.stdout+run.stderr)
                    rows=[json.loads(line) for line in path.read_text().splitlines()]
                    self.assertEqual(rows[0]['engine'],'port')
                    self.assertIsNone(rows[0]['error'])

    @unittest.skipUnless(os.name=='posix','POSIX process replacement retains its PID')
    def test_checker_import_guard_replaces_the_process_without_a_child(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);trace=folder/'pids';bad=folder/'authored-invalid-image'
            bad.write_bytes(b'authored invalid image control')
            (folder/'sitecustomize.py').write_text(
                "import os\n"
                "with open(os.environ['GOAL2_TEST_PID_TRACE'],'a') as output: output.write(str(os.getpid())+'\\n')\n")
            command=[sys.executable,'-B','-m','original_match.check','--engine','port','--no-unicorn','--image',str(bad)]
            env=dict(os.environ,PYTHONPATH=os.pathsep.join((str(folder),str(ROOT/'runtime'))),GOAL2_TEST_PID_TRACE=str(trace))
            run=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=30)
            # The authored image is refused after guard startup; identity across that startup is the control.
            self.assertNotEqual(run.returncode,0)
            pids=trace.read_text().splitlines()
            self.assertEqual(len(pids),2,run.stdout+run.stderr)
            self.assertEqual(pids[0],pids[1],'checker guard created a child instead of replacing its process')

    def test_family_cli_guarded_quick_result_records_backend_identity(self):
        for workers in (1,2):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory)/f'quick-{workers}.jsonl'
                command = [sys.executable, '-B', str(ROOT/'experiments/E036-match-port/family.py'),
                           '--family', 'S', '--only', 'S/quick-1', '--engine', 'port', '--no-unicorn',
                           '--cache', str(ROOT/'.cache/dl'), '--out', str(path), '--workers',str(workers)]
                run = subprocess.run(command, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT/'runtime')),
                                     capture_output=True, text=True, timeout=600)
                self.assertEqual(run.returncode, 0, run.stdout+run.stderr)
                rows = [json.loads(line) for line in path.read_text().splitlines()]
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]['engine'], 'port')
                self.assertIsNone(rows[0]['error'])
                self.assertTrue(rows[0]['stopped_at_board'])
                self.assertIn('entrypoints', rows[0]['ports'])

if __name__=='__main__':unittest.main()


class CheckScreen(unittest.TestCase):
    """T78d: check.py compares the port's digests without the board's screen (the parent T78's
    "their digests without the screen"), against the original's screen-free digests; with the
    screen, nothing changes. Pure: no image, no match."""

    def setUp(self):
        from original_match import check
        self.check=check
        self.addCleanup(setattr,check,'SCREEN',check.SCREEN)

    def result(self,screen):
        board={'statistics':[1,2],'bars':[3],'screen_sha256':screen}
        keys=('score','half_time_score','goals','bookings','sendings_off','injuries','substitutions',
              'man_of_the_match','ticks','seed_after','squads_after')
        return dict({k:[] for k in keys},board=board,commentary=[{'text':'x'}])

    def test_without_the_screen_only_the_screen_is_left_out(self):
        c=self.check
        c.SCREEN=True
        self.assertNotEqual(c.result_digest(self.result('a')),c.result_digest(self.result('b')))
        c.SCREEN=False
        self.assertEqual(c.result_digest(self.result('a')),c.result_digest(self.result('b')))
        other=self.result('a');other['ticks']=[5]
        self.assertNotEqual(c.result_digest(self.result('a')),c.result_digest(other))

    def test_the_port_and_no_screen_compare_without_it_and_the_original_with_it(self):
        c=self.check
        self.assertTrue(c.EXPECTED_INTERACTIVE_NO_SCREEN and c.EXPECTED_KNOCKOUT_NO_SCREEN)
        self.assertNotEqual(c.EXPECTED_INTERACTIVE_NO_SCREEN,c.EXPECTED_INTERACTIVE)
        self.assertNotEqual(c.EXPECTED_KNOCKOUT_NO_SCREEN,c.EXPECTED_KNOCKOUT)
        for argv,screen in ((['--engine','port'],False),(['--no-screen'],False),([],True)):
            a=c.parser().parse_args(argv)
            self.assertEqual(not (a.no_screen or a.engine=='port'),screen,argv)
