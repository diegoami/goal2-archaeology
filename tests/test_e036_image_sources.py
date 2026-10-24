"""#419: image/spec binding and complete source-specific calendar coverage."""
import copy,json,tempfile,unittest
from pathlib import Path
from unittest import mock
from tests.test_e036_compare import family,families,records,compare_module as compare,ROOT,record
sources=family.image_sources
OUT=ROOT/'experiments/E036-match-port/out/m4-419'

class ImageSources(unittest.TestCase):
    def spec(self):return families.load_family(OUT/'source-specs-1/FS.json').matches[0]

    def test_legacy_specs_stay_byte_for_byte_bound_to_old_references(self):
        receipt=json.loads((OUT/'old74-binding-1.json').read_text())
        self.assertTrue(receipt)
        current={m.id:m for f in families.discover().values() for m in f.matches}
        rows=records.read_log(ROOT/'experiments/E036-match-port/families/display/reference-all-rare-20261024-v1.jsonl')
        self.assertEqual(len(rows),74)
        for row in rows:
            spec=current[row['id']]
            self.assertEqual(spec.sha256,row['spec_sha256'])
            self.assertEqual(spec.image_sha256,row['image_sha256'])
            self.assertNotIn('image_sha256',spec.spec())

    def test_unknown_image_is_refused(self):
        with self.assertRaises(sources.SourceError):sources.get('unregistered')
        with self.assertRaises(sources.SourceError):sources.get(True)

    def test_wrong_memory_image_refused_before_match_construction(self):
        from original_match import Image
        image=mock.Mock(spec=Image);image.sha256.return_value='0'*64
        with mock.patch('original_match.Match') as match:
            with self.assertRaisesRegex(family.Refused,'does not match'):family.run_match(image,self.spec())
            match.assert_not_called()

    def test_wrong_cached_file_never_becomes_an_image(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/sources.get('E031-stage8')['asset']).write_bytes(b'wrong')
            with mock.patch('original_match.Image.from_bytes') as make:
                with self.assertRaisesRegex(sources.SourceError,'wrong source hash'):sources.load('E031-stage8',d)
                make.assert_not_called()

    def test_private_source_has_no_automatic_download(self):
        with tempfile.TemporaryDirectory() as d,mock.patch.object(sources.subprocess,'run') as run:
            with self.assertRaisesRegex(sources.SourceError,'private source'):sources.load('T86-stage8',d)
            run.assert_not_called()

    def test_nondefault_source_enters_spec_digest_and_checkpoint_identity(self):
        spec=self.spec()
        self.assertEqual(spec.spec()['image_sha256'],sources.get('E031-stage8')['sha256'])
        self.assertEqual(family.checkpoint_key(spec,[],[],[])['image_sha256'],spec.image_sha256)
        other=copy.copy(spec);other.image='T86-stage8'
        self.assertNotEqual(spec.sha256,other.sha256)

    def test_comparator_refuses_source_swap_in_either_log_and_missing_bindings(self):
        spec=self.spec();r=records.read_log(OUT/'FS-native-raw-3.jsonl')[0];expected={spec.id:spec.sha256}
        self.assertTrue(compare.check({spec.id:r},{spec.id:r},expected,image_sha256={spec.id:spec.image_sha256})[1])
        swapped=copy.deepcopy(r);swapped['image_sha256']=sources.get('T86-stage8')['sha256']
        for ref,candidate in ((swapped,r),(r,swapped)):
            with self.assertRaisesRegex(compare.Malformed,'another image'):compare.check({spec.id:ref},{spec.id:candidate},expected,image_sha256={spec.id:spec.image_sha256})
        with self.assertRaisesRegex(compare.Malformed,'missing declared image'):compare.check({spec.id:r},{spec.id:r},expected,image_sha256={})

    def test_extended_calendar_is_required_and_last_block_remains_compared(self):
        r=records.read_log(OUT/'FS-native-raw-3.jsonl')[0]
        self.assertEqual(len(r['after']['ranges']['records']),105)
        shortened=copy.deepcopy(r);shortened['after']['ranges']['records']=shortened['after']['ranges']['records'][:92]
        with self.assertRaises(records.SchemaError):records.validate(shortened)
        changed=copy.deepcopy(r);changed['after']['ranges']['records'][-1]='0'*64
        self.assertIn(('after.ranges.records','records+0x1A000'),compare.differences(r,changed,True,True))
        self.assertEqual(records.ranges_for_source()['records'],(262990,93648))
        self.assertEqual(records.ranges_for_source(self.spec().image_sha256)['records'],(262990,106640))

    def test_single_worker_uses_each_specs_image(self):
        specs=[families.discover()['F40'].matches[0],self.spec()]
        def rec(image,spec,*args,**kwargs):
            value=record(specs[0].id);value.update(id=spec.id,family=spec.family,spec_sha256=spec.sha256,image_sha256=spec.image_sha256);return value
        with tempfile.TemporaryDirectory() as d,mock.patch.object(sources,'load',side_effect=lambda key,cache:key) as load,mock.patch.object(family,'run_match',side_effect=rec) as run:
            family.run_family(specs,str(Path(d)/'out.jsonl'),say=lambda x:None)
            self.assertEqual([x.args[0] for x in load.call_args_list],['E006','E031-stage8'])
            self.assertEqual([x.args[0] for x in run.call_args_list],['E006','E031-stage8'])

if __name__=='__main__':unittest.main()
