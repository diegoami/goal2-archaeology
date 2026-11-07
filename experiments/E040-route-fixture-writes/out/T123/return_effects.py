"""Observe actual ordinary Match return and the route's first6F1D continuation."""
import argparse,hashlib,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(ROOT/'tools'),str(HERE)]
import pairs as P

def candidate(state,tables):
    from tests.test_route_sealed import _denials
    _denials()
    from original_match import route as R,Match
    from original_match.machine import REGS,MEM_SIZE
    from original_match.port.tables import from_record
    from original_match.match import TEAM_MENU
    from original_match.route_team import choose_eleven,PreMatchPlan
    step=R.play_round(state,from_record(tables),R.DEFAULT_KEYS);m=step.match;assert type(m) is Match
    def select(replay):
        if not replay and m.st['menu_context']=='pre_match' and m.side is not None:m._menu=PreMatchPlan(m.side,subs=choose_eleven(m._squad(m.opts['managed']),m._player))
    m.m.at(TEAM_MENU,select)
    for event in m.events():pass
    actual={k:m.m.reg(k) for k in REGS};cont=step.continuation;seen=[]
    cont.m.at('000E:6F1D',lambda replay:None if replay else seen.append({k:cont.m.reg(k) for k in REGS}))
    result=R.resume_round(cont,m);assert len(seen)==1
    differences={k:[actual[k],seen[0][k]] for k in REGS if actual[k]!=seen[0][k]}
    before=hashlib.sha256(cont.m.read(0,MEM_SIZE)).hexdigest();before_record=P.digest(cont.record)
    try:R.resume_round(cont,m)
    except ValueError:pass
    else:raise AssertionError('consumed match accepted')
    assert hashlib.sha256(cont.m.read(0,MEM_SIZE)).hexdigest()==before and P.digest(cont.record)==before_record
    return {'all16_returned_registers_propagated':not differences,'register_differences':differences,
            'actual_return_registers':actual,'first_6F1D_registers':seen[0],
            'consumed_resume_memory_and_record_unchanged':True,'final_state_sha256':P.digest(result.state)}

if __name__=='__main__':
    from port_test_runtime import call_in_pypy
    from original_match.port.tables import to_record
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--expect-before',action='store_true');args=p.parse_args()
    start=time.monotonic();image=P.F.image();r=call_in_pypy('experiments.E040-route-fixture-writes.out.T123.return_effects','candidate',args=(image.state(image.tables),to_record(image.tables)))
    row={'schema':'t123-actual-return-effects/1','case':'E040-r0004','sources':{**P.sources(),str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},'elapsed_s':round(time.monotonic()-start,4),**r}
    with Path(args.out).open('x') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n')
    assert row['all16_returned_registers_propagated']!=args.expect_before
