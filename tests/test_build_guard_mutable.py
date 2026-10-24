"""[designed: T85/#396] Sampled data coverage must exclude the original's live display-mode byte.

[confirmed: registered listing 0791:9422–9443 / 214B:1D6F; T84's unchanged E031 g1 checkpoint 3874]
No guest execution or state construction is needed: static writer evidence and the original saved image suffice.
Copied-image corruptions below are refusal controls, never inputs to a game run.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import build
from original_match.image import Image,_relocations

NAME = '3ea57029282b849f-g1-03874-shootout-start.sav'
SHA = '3ea57029282b849fd3114a995178f35e48c420c768f0702b9d3b7d48600dc1fc'
SOURCE = ROOT/'.cache/dl'/NAME
BASELINE = json.loads((ROOT/'notes/396/baseline.json').read_text())


class Coverage(unittest.TestCase):
    def test_only_the_proven_mutable_byte_is_removed_and_all_code_is_retained(self):
        covered = {o for s,n in build.DATA_RANGES for o in range(s,s+n)}
        self.assertNotIn(0x066A,covered)
        self.assertIn(0x0669,covered);self.assertIn(0x066B,covered)
        self.assertEqual(len(covered),BASELINE['data_bytes']-1)
        self.assertEqual(hashlib.sha256(json.dumps(sorted(covered|{0x066A})).encode()).hexdigest(),BASELINE['coverage_sha256'])
        code = [build.CODE_SIZE,build.CODE_BLOCK,build.SEGMENTS,build.RELOCATION_DELTAS,build.CODE_SHA256]
        self.assertEqual(hashlib.sha256(json.dumps(code).encode()).hexdigest(),BASELINE['code_metadata_sha256'])

    def test_regeneration_cannot_reintroduce_the_observed_key_writer(self):
        spec=importlib.util.spec_from_file_location('guard_generator',ROOT/'experiments/E033-original-match-kit/build_guard.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        self.assertEqual(set(module.MUTABLE_DATA),{0x066A})
        self.assertEqual(module.guard_ranges(list(range(0x668,0x66D)),set()),[(0x668,2),(0x66B,2)])
        self.assertEqual(module.guard_ranges(list(range(0x668,0x66D)),{0x66B}),[(0x668,2),(0x66C,1)])
        # The exact pointer argument and writer are independently visible in the registered listing.
        listing=(ROOT/'static/goal-exe/code/seg_0791_15.asm').read_text()
        self.assertIn('9422  BF 6A 06',listing)
        self.assertIn('9443  9A 6F 1D 4B 21',listing)
        helper=(ROOT/'static/goal-exe/named/seg_214B_02.c').read_text().split('// ---- 214B:1D6F',1)[1].split('// ----',1)[0]
        self.assertIn('*param_4 = (byte)local_4',helper)


@unittest.skipUnless(SOURCE.exists(),'private unchanged E031 checkpoint absent; see notes/396/README.md')
class OriginalCheckpoint(unittest.TestCase):
    def image(self):
        raw=SOURCE.read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),SHA)
        return Image.from_savestate(raw)

    def test_real_shootout_checkpoint_is_accepted_without_any_memory_edits(self):
        self.assertEqual(self.image().build_problems(),[])

    def test_adjacent_immutable_data_corruption_is_still_refused(self):
        image=self.image();image.memory[image.DS*16+0x0669]^=1
        self.assertIn('data DS:0400..07FF',image.build_problems())

    def test_code_and_relocation_corruption_are_still_refused(self):
        for offset in (0x0791*16+0x9422,_relocations()[0]):
            with self.subTest(offset=offset):
                image=self.image();image.memory[image.load*16+offset]^=1
                self.assertTrue(any(p.startswith('code ') for p in image.build_problems()))


if __name__=='__main__':unittest.main()
