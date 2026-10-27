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
            managed=7,substitutions=example.BUDGET,record_draws=True,ports=['all'],engine=engine)
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
        run=subprocess.run([sys.executable,'-B','-c',script],cwd=ROOT,env=dict(os.environ,PYTHONPATH=str(ROOT/'runtime')),capture_output=True,text=True,timeout=600)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)
        self.assertIn('"completed": true',run.stdout)

    def test_unimplemented_port_checkpoints_refuse_instead_of_loading_original(self):
        from original_match.match import MatchError
        m=Match(self.image,Fixture(7,19,index=21),managed=7,engine='port')
        with self.assertRaisesRegex(MatchError,'checkpoint'):m.save()


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
