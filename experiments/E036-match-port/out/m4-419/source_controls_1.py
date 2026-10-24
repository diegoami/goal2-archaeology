"""Causal controls for per-source memory, comparison and calendar bindings."""
import io,json,sys,unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from tests.test_e036_image_sources import ImageSources,sources,family,compare,records,families

def run(name):
 result=unittest.TextTestRunner(stream=io.StringIO()).run(ImageSources(name))
 return {'test':name,'passed':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors)}
checks=[('memory-binding','test_wrong_memory_image_refused_before_match_construction'),('comparison-binding','test_comparator_refuses_source_swap_in_either_log_and_missing_bindings'),('calendar-extent','test_extended_calendar_is_required_and_last_block_remains_compared'),('spec-binding','test_nondefault_source_enters_spec_digest_and_checkpoint_identity')]
baseline=[run(test) for _,test in checks];assert all(x['passed'] for x in baseline)
original_check=compare.check;original_spec=families.MatchSpec.spec
patches=[mock.patch.object(sources,'validate_image',lambda image,key:None),mock.patch.object(compare,'check',lambda *args,**kw:original_check(*args,**{**kw,'image_sha256':None})),mock.patch.object(records,'ranges_for_source',lambda digest=None:records.RANGES),mock.patch.object(families.MatchSpec,'spec',lambda self:{k:v for k,v in original_spec(self).items() if k!='image_sha256'})]
results=[]
for (name,test),patch in zip(checks,patches):
 with patch:result=run(test)
 result.update(name=name,caught=not result['passed']);results.append(result)
receipt={'baseline':baseline,'controls':results,'all_caught':all(x['caught'] for x in results)}
with (OUT/'source-controls-1.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt));assert receipt['all_caught']
