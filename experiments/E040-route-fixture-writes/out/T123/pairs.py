"""Fresh CPython original / denied PyPy state+tables sealed comparisons.

The legal-eleven choice is explicitly attached by this comparison harness to
ordinary Match's existing team-menu event. Production never installs it.
"""
import argparse,hashlib,json,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(ROOT/'tools'),str(HERE)]
import fixtures as F

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),default=lambda v:v.hex() if isinstance(v,bytes) else str(v)).encode()).hexdigest()

def candidate(state,tables):
    from tests.test_route_sealed import _denials
    assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
    _denials()
    from original_match import route as R,Match
    from original_match.match import TEAM_MENU
    from original_match.route_team import PreMatchPlan,choose_eleven
    from original_match.port.tables import from_record
    initial=digest(state);step=R.play_round(state,from_record(tables),R.DEFAULT_KEYS)
    choices=[];events=[]
    while step.status=='match':
        m=step.match;assert type(m) is Match and m.engine=='port' and m.opts['tail'] is False
        def select(replay,m=m):
            if not replay and m.st['menu_context']=='pre_match' and m.side is not None:
                squad=m._squad(m.opts['managed']);changes=choose_eleven(squad,m._player)
                choices.append({'country':m.opts['managed'],'before':squad,'swaps':changes})
                m._menu=PreMatchPlan(m.side,subs=changes)
        m.m.at(TEAM_MENU,select)
        events.extend((e.kind,e.data) for e in m.events())
        old=step;step=R.resume_round(old.continuation,m)
        before=digest(step.state)
        try:R.resume_round(old.continuation,m)
        except ValueError:pass
        else:raise AssertionError('consumed match accepted')
        assert digest(step.state)==before
    assert initial==digest(state)
    return {'state':step.state,'pages':[dict(p.__dict__,cells=p.cells.hex()) for p in step.news_pages],
      'record':step.record,'played':step.played_fixtures,'events':events,'choices':choices,'status':step.status}

def parent(opts):
    from original_match import route as R
    from original_match.image import Image
    from original_match.machine import MEM_SIZE
    from original_match.port.tables import to_record
    from port_test_runtime import call_in_pypy
    start=time.monotonic();image=F.image(opts.case);state=image.state(image.tables)
    oracle=R.Route(image,entry='play_round',record_writes=False,match_entry=True);oracle.call()
    expected=Image(oracle.header+oracle.m.read(0,MEM_SIZE)+oracle.tail);expected.tables=image.tables
    actual=call_in_pypy('test_route_sealed', '_pair_candidate',args=(state,to_record(image.tables)))
    a=actual['state'];b=expected.state(image.tables)
    if a!=b:
        import base64,zlib
        x=zlib.decompress(base64.b64decode(a['memory']));y=zlib.decompress(base64.b64decode(b['memory']))
        differences=[i for i,(u,v) in enumerate(zip(x,y)) if u!=v]
    else:differences=[]
    pages=[dict(p.__dict__,cells=p.cells.hex()) for p in oracle.news_history]
    row={'case':opts.case,'elapsed_s':round(time.monotonic()-start,4),'state_equal':a==b,
         'state_digests':[digest(b),digest(a)],'different_bytes':len(differences),'first_different_offsets':differences[:30],
         'pages_equal':actual['pages']==pages,'page_count':len(pages),'page_digests':[digest(pages),digest(actual['pages'])],
         'status':actual['status'],'played':actual['played']}
    with Path(opts.out).open('x') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n')
    assert row['state_equal'] and row['pages_equal'],row

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--out',required=True);parent(p.parse_args())
