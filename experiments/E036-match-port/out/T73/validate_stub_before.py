"""Prove prospective replacement tests fail on the still-active pre-classification bodies."""
import hashlib,io,json,subprocess,sys,tarfile,tempfile
from pathlib import Path
from prepare_stub_patch import ROOT,D,T,build_tests
out=ROOT/'experiments/E036-match-port/out/T73/prospective-stub-classification-v2'
receipt=json.loads((out/'receipt.json').read_text())
runtime=(ROOT/D).read_bytes();tests=build_tests((ROOT/T).read_text()).encode()
assert hashlib.sha256(runtime).hexdigest()==receipt['source_sha256'][D]
assert hashlib.sha256(tests).hexdigest()==receipt['proposed_sha256'][T]
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
paths=['runtime','tests/test_e036_compare.py','experiments/E036-match-port/family.py','experiments/E036-match-port/compare.py','experiments/E036-match-port/families.py','experiments/E036-match-port/records.py','experiments/E036-match-port/families']
archive=subprocess.check_output(['git','archive',head,*paths],cwd=ROOT)
with tempfile.TemporaryDirectory(prefix='t73-before-stubs-') as temporary:
 into=Path(temporary)
 with tarfile.open(fileobj=io.BytesIO(archive)) as tf:tf.extractall(into,filter='data')
 (into/T).write_bytes(tests)
 p=into/'experiments/E036-match-port/out/T73/static-inventory.json';p.parent.mkdir(parents=True);p.write_bytes((ROOT/'experiments/E036-match-port/out/T73/static-inventory.json').read_bytes())
 result=subprocess.run([sys.executable,'-B','-m','unittest','tests.test_port_display'],cwd=into,capture_output=True,text=True,timeout=180)
 text=result.stdout+result.stderr
 (out/'before-classification.log').open('x').write(text+'exit '+str(result.returncode)+'\n')
expected=['test_skill_bar_removal_preserves_even_nonzero_skill_inputs','test_removed_statistics_bar_preserves_zero_and_nonzero_inputs','test_removed_manager_status_preserves_all_argument_bands','test_removed_rating_label_calls_no_rating_or_text_helpers','test_removed_speaker_off_keeps_incoming_result_and_creates_no_frame','test_removed_tone_frequency_preserves_enabled_and_disabled_inputs','test_removed_tone_preserves_zero_frequency_and_creates_no_frame']
assert result.returncode!=0 and all('FAIL: '+name+' (' in text for name in expected),text
assert text.count('FAIL: ')==7 and 'FAILED (failures=7)' in text,text
report={'head':head,'scope':'prospective tests on old63-body runtime; no active edits','runtime_sha256':hashlib.sha256(runtime).hexdigest(),'proposed_tests_sha256':hashlib.sha256(tests).hexdigest(),'unit_exit':result.returncode,'expected_failing_tests':expected,'all_seven_replacement_tests_fail_before_classification':True}
(out/'before-classification-receipt.json').open('x').write(json.dumps(report,indent=2)+'\n')
print('Seven replacement tests fail before classification; the other75 pass.',flush=True)
