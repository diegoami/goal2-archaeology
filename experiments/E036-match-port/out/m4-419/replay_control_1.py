"""The source-selection unit must fail against the prior E006-only diagnostic."""
import importlib.util,io,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/'runtime')]
from tests.test_e036_image_sources import ImageSources

def run():
 result=unittest.TextTestRunner(stream=io.StringIO()).run(ImageSources('test_replay_diagnostic_loads_the_selected_source'))
 return {'passed':result.wasSuccessful(),'failures':len(result.failures),'errors':len(result.errors)}
baseline=run();assert baseline['passed']
original=importlib.util.spec_from_file_location
with tempfile.TemporaryDirectory(prefix='m4-419-old-locate-') as d:
 path=Path(d)/'locate.py';path.write_bytes(subprocess.check_output(['git','show','158790a0:experiments/E036-match-port/locate.py'],cwd=ROOT))
 def redirected(name,location,*args,**kw):return original(name,path if name=='m4_locate' else location,*args,**kw)
 with mock.patch.object(importlib.util,'spec_from_file_location',side_effect=redirected),mock.patch('original_match.assets.reference_image',return_value=b'old-source'),mock.patch('original_match.Image.from_bytes',return_value=object()):mutant=run()
receipt={'baseline':baseline,'prior_diagnostic_commit':'158790a0620c486a5c8dad0e0670cc6064151e8d','prior_diagnostic':mutant,'caught':not mutant['passed']}
with (OUT/'replay-control-1.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt));assert receipt['caught']
