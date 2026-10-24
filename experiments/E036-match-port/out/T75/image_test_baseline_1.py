"""Both new image tests fail on fixed pre-task main with the real image available."""
import hashlib,io,json,subprocess,tarfile,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent/'image-baseline-1';OUT.mkdir(exist_ok=False)
BASE='bf650a337794ffd82e8e1471d45bfb6c5b753fd4'
with tempfile.TemporaryDirectory(prefix='T75-image-base-') as raw:
 tree=Path(raw);archive=subprocess.check_output(['git','archive',BASE,'runtime'],cwd=ROOT)
 with tarfile.open(fileobj=io.BytesIO(archive)) as tf:tf.extractall(tree,filter='data')
 (tree/'tests').mkdir();(tree/'tests/__init__.py').write_text('');source=(ROOT/'tests/test_original_match.py').read_bytes();(tree/'tests/test_original_match.py').write_bytes(source)
 (tree/'.cache').mkdir();(tree/'.cache/dl').symlink_to(ROOT/'.cache/dl',target_is_directory=True)
 tests=['tests.test_original_match.OriginalTests.test_selection_port_refused_eleven_keeps_swap_and_original_message','tests.test_original_match.CompetitiveTests.test_selection_port_substitution_budget_per_side']
 r=subprocess.run(['/home/diego/.local/bin/python3.12','-B','-m','unittest',*tests],cwd=tree,capture_output=True,text=True)
 (OUT/'tests.log').write_text(r.stdout+r.stderr)
 receipt={'baseline':BASE,'tests_sha256':hashlib.sha256(source).hexdigest(),'returncode':r.returncode,'command_tests':tests,'expected_failure':'no port module selection','skipped': 'skipped=' in r.stderr}
 (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 assert r.returncode!=0 and 'no port module' in r.stderr and 'skipped=' not in r.stderr,r.stderr
