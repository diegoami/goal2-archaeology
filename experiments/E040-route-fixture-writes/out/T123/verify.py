"""Read-only final source/input/proof binding verification; no original execution."""
import hashlib,json,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(HERE)]
import pairs as P
from original_match.machine import REGS
from original_match.image import Image

def sha(data):return hashlib.sha256(data).hexdigest()
def load(path):return json.loads((ROOT/path).read_text())
def main(index):
    x=json.loads(Path(index).read_text());assert x['schema']=='t123-acceptance/1'
    for path,digest in {**x['source_hashes'],**x['file_hashes']}.items():assert sha((ROOT/path).read_bytes())==digest,('changed',path)
    for path,digest in x['source_hashes'].items():assert sha(subprocess.check_output(['git','show',x['source_freeze_commit']+':'+path],cwd=ROOT))==digest,('freeze source',path)
    for path,cp in x['private_inputs'].items():
        data=(ROOT/path).read_bytes();assert sha(data)==cp['sha256'],('private input',path)
        if 'context' in cp:
            assert set(cp['context']['regs'])==set(REGS) and 'waiting_key' in cp['context']
            assert not Image(data).build_problems(),path
    for path,digest in x['private_retained_hashes'].items():assert sha((ROOT/path).read_bytes())==digest,('private retained',path)
    current=P.sources();expected_ids=[case[0] for case in P.F.runner.CASES];assert set(x['corpus'])==set(expected_ids) and len(expected_ids)==14
    draw_count=0;pages=0
    for case,path in x['corpus'].items():
        row=load(path);assert row['case']==case and row['sources']==current
        assert all(row[k] for k in ('state_equal','pages_equal','ordered_draws_equal','ordered_keys_equal','comparison_choices_equal','all16_returned_cpu_equal'))
        assert row['different_bytes']==0 and row['returned_context_count']>=1
        assert all(pair[0]==pair[1] for pair in (row['state_digests'],row['draw_digests'],row['key_digests'],row['page_digests']))
        draw_count+=row['draw_count'];pages+=row['page_count']
    for case,path in x['natural'].items():
        row=load(path);assert row['case']==case
        assert all(row[k] for k in ('state_equal','pages_equal','draws_equal','keys_equal','waiting_key_equal'))
        for p,d in row['sources'].items():assert x['source_hashes'][p]==d
        start={'continental':4,'world':8,'ageing-continental':2,'ageing-world':6}[case];assert row['lineage']['game']['stage']==start
        annual=case in ('continental','world');assert row['status']==('deferred-rollover' if annual else 'complete')
        assert row['production_calls']['000E:70B9']==1
        for target in ('1771:8208','1771:80DA'):assert row['production_calls'][target]==int(not annual)
        assert row['completed_fixtures']
    both=load(x['managers']['both']);skip=load(x['managers']['skip'])
    for row in (both,skip):
        assert all(row[k] for k in ('state_equal','pages_equal','ordered_draws_equal','ordered_keys_equal','manager_calls_equal','waiting_key_equal'))
        for p,d in row['sources'].items():assert x['source_hashes'][p]==d
    assert both['manager_calls']==[[1,129],[16,130]] and both['page_count']==2
    assert skip['manager_calls']==[[1,129]] and skip['page_count']==1
    ci=load(x['ci_fixture']);assert ci['real_gh_downloads']==1 and ci['missing_cache_populated_exactly'] and ci['actual_original_pending_state_and_all16_regs_equal'] and len(ci['required_original_classes_no_skip'])==5
    returned=load(x['return_effects']);assert returned['all16_returned_registers_propagated'] and not returned['register_differences'] and returned['consumed_resume_memory_and_record_unchanged']
    assert returned['actual_return_registers']==returned['first_6F1D_registers'] and set(returned['actual_return_registers'])==set(REGS)
    pending=load(x['pending_history']);assert pending['unfinished_fixture3_excluded'] and pending['completed_fixture_indices']==[1,2]
    history=load(x['completed_history']);assert history['cases']==14 and len(history['rows'])==14
    assert {r['case'] for r in history['rows']}==set(expected_ids)
    for row in history['rows']:assert row['missing_record_detected'] and row['wrong_result_detected']
    preserved=load(x['preservation']);assert preserved['status']=='passed'
    assert sum(row['old_function_count'] for row in preserved['source_audits'])==218
    assert sum(row['preserved_old_entries'] for row in preserved['registries'].values())==111
    for row in preserved['source_audits']:assert row['current_sha256']==sha((ROOT/row['path']).read_bytes())
    audit=load(x['call_audit']);assert audit['status']=='passed' and audit['routines']==8 and audit['listing_calls']==16
    for path,digest in audit['sources'].items():assert sha((ROOT/path).read_bytes())==digest
    diagnosis=[json.loads(line) for line in (ROOT/x['t117_diagnosis']).read_text().splitlines()]
    assert len(diagnosis)==2 and all(row['events_equal'] and row['memory_equal'] for row in diagnosis)
    assert not diagnosis[0]['result_equal_after_asserted_zero_metadata_removal'] and diagnosis[1]['result_equal_after_asserted_zero_metadata_removal']
    assert diagnosis[0]['00DB_calls']-diagnosis[1]['00DB_calls']==4
    assert all(not any(row['new_existing_module_calls'].values()) for row in diagnosis)
    t117=(ROOT/x['t117_test']).read_text();assert 'Ran 10 tests' in t117 and t117.rstrip().endswith('OK')
    before=(HERE/'t123-before-final-v4.log').read_text();assert 'Ran 21 tests' in before and 'ALL authored methods fail' in before and 'skipped=' not in before
    focused=(HERE/'t123-focused-final-v6.log').read_text();assert 'Ran 23 tests' in focused and focused.rstrip().endswith('OK')
    display=(HERE/'t123-preserved-display-pypy-v1.log').read_text();assert 'Ran 83 tests' in display and display.rstrip().endswith('OK')
    print(json.dumps({'status':'passed','source_hashes':len(x['source_hashes']),'public_hashes':len(x['file_hashes']),'private_inputs':len(x['private_inputs']),
       'private_retained':len(x['private_retained_hashes']),'E040_pairs':14,'ordered_draw_events':draw_count,'E040_pages':pages,
       'natural_paths':4,'manager_supplements':2,'actual_return_registers':16,'preserved_functions':218,'preserved_old_ABIs':111,'owned_routines':8,'listing_calls':16},sort_keys=True))
if __name__=='__main__':main(sys.argv[1])
