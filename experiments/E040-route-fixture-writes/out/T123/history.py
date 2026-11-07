"""Independent pending exclusion and completed-calendar history validation."""
import argparse,base64,hashlib,json,sys,zlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(ROOT/'tools'),str(HERE)]
import pairs as P

def decoded(memory,game,fixtures,start,end):
    return [{'fixture':n,'first':int.from_bytes(memory[fixtures+8*(n-1)+4:fixtures+8*(n-1)+6],'little'),
      'second':int.from_bytes(memory[fixtures+8*(n-1)+6:fixtures+8*(n-1)+8],'little'),'kind':memory[fixtures+8*(n-1)+2],
      'score':list(memory[fixtures+8*(n-1):fixtures+8*(n-1)+2]),'winner_flag':memory[fixtures+8*(n-1)+3]} for n in range(start,end)]

def pending(state,tables):
    from tests.test_route_sealed import _denials
    _denials()
    from original_match import route as R,Match
    from original_match.port.tables import from_record
    step=R.play_round(state,from_record(tables),R.DEFAULT_KEYS)
    assert step.status=='match' and type(step.match) is Match and not step.match.over and not step.match.inputs
    return {'played':step.played_fixtures,'pending_index':step.match.opts['index'],'actual_match':True,'state_sha256':P.digest(step.state)}

def main(opts):
    from original_match.image import Image
    from original_match.port.tables import load,to_record
    from port_test_runtime import call_in_pypy
    tables=load(ROOT/'static/goal-exe/tables')
    if opts.pending:
        source=P.F.image();reference,context,fixture=P.F.entry();start=source.fixture_index();end=reference.fixture_index()
        expected=decoded(reference.memory,reference.far(0xA923),reference.far(0xA92B),start,end)
        actual=call_in_pypy('experiments.E040-route-fixture-writes.out.T123.history','pending',args=(source.state(tables),to_record(tables)))
        assert [r['fixture'] for r in expected]==[1,2] and end==3
        assert P.digest(actual['played'])==P.digest(expected) and actual['pending_index']==3
        assert actual['state_sha256']==P.digest(reference.state(tables))
        result={'status':'passed','case':'E040-r0004','actual_pending_ordinary_match':True,'unfinished_fixture3_excluded':True,
                'completed_fixture_indices':[1,2],'original_completed_records_sha256':P.digest(expected),'original_pending_state_sha256':actual['state_sha256']}
    else:
        rows=[]
        for receipt in sorted(Path(opts.bundle).glob('E040-r*.jsonl')):
            r=json.loads(receipt.read_text());case=r['case'];initial=P.F.image(case)
            suffix=hashlib.sha256(str(receipt.resolve()).encode()).hexdigest()[:12]
            private=ROOT/'.cache/t123/pairs'/(case+'-'+receipt.stem+'-'+suffix+'-original.json')
            final=Image.from_state(json.loads(private.read_text()),tables);start,end=initial.fixture_index(),final.fixture_index()
            assert end>start,(case,start,end)
            expected=decoded(final.memory,final.far(0xA923),final.far(0xA92B),start,end)
            assert P.digest(r['played'])==P.digest(expected),case
            missing=r['played'][1:];wrong=json.loads(json.dumps(r['played']));wrong[0]['winner_flag']^=1
            assert P.digest(missing)!=P.digest(expected) and P.digest(wrong)!=P.digest(expected)
            rows.append({'case':case,'fixture_indices':[v['fixture'] for v in expected],'completed_records_sha256':P.digest(expected),
                         'receipt_sha256':hashlib.sha256(receipt.read_bytes()).hexdigest(),'private_original_state_sha256':hashlib.sha256(private.read_bytes()).hexdigest(),
                         'missing_record_detected':True,'wrong_result_detected':True})
        assert len(rows)==14,len(rows)
        result={'status':'passed','cases':14,'method':'decode actual original post-call calendar from source cursor to final cursor, preserving ordinal order; no port completion watcher reused','rows':rows}
    result['sources']={**P.sources(),str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    with Path(opts.out).open('x') as stream:json.dump(result,stream,sort_keys=True,indent=2);stream.write('\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--pending',action='store_true');p.add_argument('--bundle');p.add_argument('--out',required=True);main(p.parse_args())
