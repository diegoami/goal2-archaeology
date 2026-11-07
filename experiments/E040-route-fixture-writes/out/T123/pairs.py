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

def candidate(state,tables,diagnostics=False):
    from tests.test_route_sealed import _denials
    assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
    _denials()
    from original_match import route as R,Match
    from original_match.match import TEAM_MENU
    from original_match.route_team import PreMatchPlan,choose_eleven
    from original_match.port.tables import from_record
    initial=digest(state);step=R.play_round(state,from_record(tables),R.DEFAULT_KEYS)
    choices=[];events=[];observed=[];stub_calls={}
    while step.status=='match':
        m=step.match
        for address in ((0x3E275,0xB8000+18*160+34*2+1) if diagnostics else ()): 
            m.m.watch(address,1,lambda old,new,address=address,m=m:observed.append([address,old[0],new[0],m.m.where(m.m.reg('cs'),m.m.reg('ip')),m.m.pc()]))
        assert type(m) is Match and m.engine=='port' and m.opts['tail'] is False
        def select(replay,m=m):
            if not replay and m.st['menu_context']=='pre_match' and m.side is not None:
                squad=m._squad(m.opts['managed']);changes=choose_eleven(squad,m._player)
                choices.append({'country':m.opts['managed'],'before':squad,'swaps':changes})
                m._menu=PreMatchPlan(m.side,subs=changes)
        m.m.at(TEAM_MENU,select)
        events.extend((e.kind,e.data) for e in m.events())
        stub_calls.update({e.address:m.ports.calls.get(e.address,0) for reg,_ in m.ports.loaded for e in reg.entries.values() if e.stub and m.ports.calls.get(e.address)})
        old=step;step=R.resume_round(old.continuation,m)
        before=digest(step.state)
        try:R.resume_round(old.continuation,m)
        except ValueError:pass
        else:raise AssertionError('consumed match accepted')
        assert digest(step.state)==before
    assert initial==digest(state)
    return {'state':step.state,'pages':[dict(p.__dict__,cells=p.cells.hex()) for p in step.news_pages],
      'record':step.record,'played':step.played_fixtures,'events':events,'choices':choices,'status':step.status,'observed':observed,'stub_calls':stub_calls}

def parent(opts):
    from original_match import route as R
    from original_match.image import Image
    from original_match.machine import MEM_SIZE
    from original_match.port.tables import to_record
    from port_test_runtime import call_in_pypy
    start=time.monotonic();image=F.image(opts.case);state=image.state(image.tables)
    observed=[]
    class ObservedMatch(R.RouteMatch):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            for address in ((0x3E275,0xB8000+18*160+34*2+1) if getattr(opts,"diagnostics",False) else ()): 
                self.m.watch(address,1,lambda old,new,address=address:observed.append([address,old[0],new[0],self.m.where(self.m.reg('cs'),self.m.reg('ip')),self.m.pc()]))
    from unittest.mock import patch
    with patch.object(R,'RouteMatch',ObservedMatch):
        oracle=R.Route(image,entry='play_round',record_writes=False,match_entry=True);oracle.call()
    expected=Image(oracle.header+oracle.m.read(0,MEM_SIZE)+oracle.tail);expected.tables=image.tables
    actual=call_in_pypy('test_route_sealed', '_pair_candidate',args=(state,to_record(image.tables),getattr(opts,'diagnostics',False)))
    a=actual['state'];b=expected.state(image.tables)
    private=ROOT/'.cache/t123/pairs';private.mkdir(parents=True,exist_ok=True)
    for label,value in [('original',b),('sealed',a)]:
        path=private/(opts.case+'-'+Path(opts.out).stem+'-'+label+'.json')
        with path.open('x') as stream:json.dump(value,stream)
    if a!=b:
        import base64,zlib
        x=zlib.decompress(base64.b64decode(a['memory']));y=zlib.decompress(base64.b64decode(b['memory']))
        differences=[i for i,(u,v) in enumerate(zip(x,y)) if u!=v]
    else:differences=[]
    pages=[dict(p.__dict__,cells=p.cells.hex()) for p in oracle.news_history]
    transcript=lambda records,kind:[list(e) for e in records if e[0]==kind]
    draws_equal=digest(transcript(oracle.record,'rng'))==digest(transcript(actual['record'],'rng'))
    keys_equal=digest(transcript(oracle.record,'key'))==digest(transcript(actual['record'],'key'))
    original_choices=[choice for e in oracle.record if e[0]=='team' for choice in e[1]['choices']]
    choices_equal=digest(original_choices)==digest(actual['choices'])
    row={'schema':'t123-paired-route/1','sources':sources(),'input_asset_sha256':F.runner.expected(next(c[3] for c in F.runner.CASES if c[0]==opts.case)),'input_state_sha256':digest(state),'case':opts.case,'elapsed_s':round(time.monotonic()-start,4),'state_equal':a==b,
         'state_digests':[digest(b),digest(a)],'different_bytes':len(differences),'first_different_offsets':differences[:30],
         'pages_equal':actual['pages']==pages,'page_count':len(pages),'page_digests':[digest(pages),digest(actual['pages'])],
         'ordered_draws_equal':draws_equal,'draw_count':len(transcript(oracle.record,'rng')),'draw_digests':[digest(transcript(oracle.record,'rng')),digest(transcript(actual['record'],'rng'))],
         'ordered_keys_equal':keys_equal,'key_count':len(transcript(oracle.record,'key')),'key_digests':[digest(transcript(oracle.record,'key')),digest(transcript(actual['record'],'key'))],
         'comparison_choices_equal':choices_equal,'status':actual['status'],'played':actual['played'],'attribute_observations':[observed,actual['observed']],'reached_match_stubs':actual['stub_calls']}
    with Path(opts.out).open('x') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n')
    assert row['state_equal'] and row['pages_equal'] and draws_equal and keys_equal and choices_equal,row

def sources():
    paths=list((ROOT/'runtime/original_match').glob('*.py'))+list((ROOT/'runtime/original_match/port').glob('*.py'))
    paths += [Path(__file__),HERE/'fixtures.py',ROOT/'tests/test_route_sealed.py',HERE.parents[1]/'runner.py']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def sealed_check():
    """Check a current immutable fourteen-case bundle, creating one when absent."""
    import datetime,types
    frozen=sources();checks=('state_equal','pages_equal','ordered_draws_equal','ordered_keys_equal','comparison_choices_equal')
    bundles=sorted(HERE.glob('paired-*'),reverse=True)
    for bundle in bundles:
        paths=[bundle/(case[0]+'.jsonl') for case in F.runner.CASES]
        if not all(p.is_file() for p in paths):continue
        rows=[json.loads(p.read_text()) for p in paths]
        if all(row.get('sources')==frozen and all(row[k] for k in checks) for row in rows):
            print('sealed E040: all14 current-source original/PyPy paired states/draws/keys/pages/choices exact:',bundle.relative_to(ROOT));return 0
    bundle=HERE/('paired-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    bundle.mkdir()
    for case in F.runner.CASES:
        print('sealed fresh pair',case[0],flush=True)
        parent(types.SimpleNamespace(case=case[0],out=str(bundle/(case[0]+'.jsonl')),diagnostics=False))
        assert sources()==frozen,'source changed during paired batch'
    print('sealed E040: all14 fresh original/PyPy paired states/draws/keys/pages/choices exact:',bundle.relative_to(ROOT));return 0


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--out',required=True);p.add_argument('--diagnostics',action='store_true');parent(p.parse_args())
