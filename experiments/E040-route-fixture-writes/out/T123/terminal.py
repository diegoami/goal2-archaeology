"""Natural annual boundaries and supported in-season ageing/builders.

Primary inputs are original-returned C/D/T124t frames. World constructor inputs
are advanced only by the original constructor/tail to its actual77C2 return.
No stage, fixture, result, squad, rank or year is edited by preparation.
"""
import argparse,hashlib,importlib.util,json,sys,time,types
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(ROOT/'tools'),str(HERE)]
import pairs as P

def natural_input(case):
    spec=importlib.util.spec_from_file_location('_t123_dprepare',HERE.parent/'T124d/prepare.py');D=importlib.util.module_from_spec(spec);spec.loader.exec_module(D)
    if case=='continental':
        receipt=HERE.parent/'T124t/continuation-context.jsonl'
        cp=next(r['checkpoint'] for r in map(json.loads,receipt.read_text().splitlines()) if r.get('status')=='round' and r['round']==3)
        r=D.load(cp);constructor=None
    elif case=='ageing-continental':
        receipt=HERE.parent/'T124c/natural-groups-input-v1.jsonl'
        cp=next(r['checkpoint'] for r in map(json.loads,receipt.read_text().splitlines()) if r.get('status')=='returned-call' and r['call']==11)
        r=D.load(cp);constructor=None
    else:
        receipt=HERE.parent/'T124d/natural-inputs-v1.jsonl';phase='finals' if case=='world' else 'groups'
        entry=next(r for r in map(json.loads,receipt.read_text().splitlines()) if r.get('status')=='constructor-entry' and r['phase']==phase)
        cp=entry['checkpoint'];r=D.load(cp);constructor=entry['target']
        assert r.m.run(r.m.lin('000E:77C2'),300,fresh=True) is None
        assert r.m.reg('sp')==0x3EEE
    from original_match.image import Image
    from original_match.machine import MEM_SIZE
    from original_match.port.tables import load
    image=Image(r.header+r.m.read(0,MEM_SIZE)+r.tail);image.tables=load(ROOT/'static/goal-exe/tables')
    return r,image,{'source':cp,'source_receipt':str(receipt.relative_to(ROOT)),'source_receipt_sha256':D.sha(receipt.read_bytes()),
                    'original_constructor_to_77C2':constructor,'input_context':D.context(r),'input_memory_sha256':D.sha(image.memory_component()),'game':D.game(r.m)}

def candidate(state,tables,waiting):
    from tests.test_route_sealed import _denials
    assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
    _denials()
    from original_match import route as R,port,Match
    from original_match.match import TEAM_MENU
    from original_match.route_team import choose_eleven,PreMatchPlan
    from original_match.port.tables import from_record
    counts={k:0 for k in ('000E:70B9','1771:8208','1771:80DA')}
    def wrapped(fn,address):
        def body(mem,variant):
            counts[address]+=1;value=fn(mem,variant)
            if isinstance(value,types.GeneratorType):return (yield from value)
            return value
        return body
    for registry,_ in port.load(['all']):
        for address in counts:
            if address in registry.entries:
                entry=registry.entries[address];entry.fn=wrapped(entry.fn,address)
    keys=R.Keys(R.DEFAULT_KEYS);keys.waiting=waiting;tables=from_record(tables)
    pages=[];records=[];completed=[];first=P.digest(state)
    for _ in range(64):
        step=R.play_round(state,tables,keys)
        while step.status=='match':
            m=step.match;assert type(m) is Match
            def select(replay,m=m):
                if not replay and m.st['menu_context']=='pre_match' and m.side is not None:
                    m._menu=PreMatchPlan(m.side,subs=choose_eleven(m._squad(m.opts['managed']),m._player))
            m.m.at(TEAM_MENU,select)
            for event in m.events():pass
            step=R.resume_round(step.continuation,m)
        pages.extend(dict(page.__dict__,cells=page.cells.hex()) for page in step.news_pages)
        records.extend(step.record);completed.extend(step.played_fixtures)
        state=step.state
        if step.status=='deferred-rollover' or any(e[0]=='round_end' for e in step.record):break
    else:raise AssertionError('natural stage boundary not reached')
    if step.status=='deferred-rollover':
        before=dict(counts);again=R.play_round(state,tables,None)
        assert again.state==state and again.status==step.status and not again.played_fixtures and not again.news_pages
        assert counts==before and not counts['1771:8208'] and not counts['1771:80DA']
    else:assert counts['1771:80DA']==1 and counts['1771:8208']==1
    return {'state':state,'pages':pages,'record':records,'completed':completed,'counts':counts,'waiting_key':keys.waiting,'status':step.status}

def parent(opts):
    from original_match import route as R
    from original_match.image import Image
    from original_match.machine import MEM_SIZE,GuestError
    from original_match.port.tables import to_record
    from port_test_runtime import call_in_pypy
    start=time.monotonic();r,image,lineage=natural_input(opts.case);before=P.digest(image.state(image.tables))
    waiting=r.keys.waiting;annual=opts.case in ('continental','world')
    if annual:r.m.at('000E:70E6',lambda replay:None if replay else r.m.stop('t123-natural-terminal'))
    for _ in range(64):
        try:r.call()
        except GuestError:
            if not annual or r.m.stop_reason!='t123-natural-terminal':raise
            break
        if any(e[0]=='round_end' for e in r.record):break
    else:raise AssertionError('reference boundary not reached')
    expected=Image(r.header+r.m.read(0,MEM_SIZE)+r.tail);expected.tables=image.tables
    actual=call_in_pypy('test_route_sealed','_terminal_candidate',args=(image.state(image.tables),to_record(image.tables),waiting))
    reference=expected.state(image.tables);pages=[dict(p.__dict__,cells=p.cells.hex()) for p in r.news_history]
    transcript=lambda record,kind:[list(e) for e in record if e[0]==kind]
    row={'schema':'t123-natural-boundary/1','case':opts.case,'lineage':lineage,'sources':{**P.sources(),str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
         'input_state_sha256':before,'state_equal':reference==actual['state'],'state_digests':[P.digest(reference),P.digest(actual['state'])],
         'pages_equal':pages==actual['pages'],'page_count':len(pages),'page_digests':[P.digest(pages),P.digest(actual['pages'])],
         'draws_equal':P.digest(transcript(r.record,'rng'))==P.digest(transcript(actual['record'],'rng')),'draw_count':len(transcript(r.record,'rng')),
         'keys_equal':P.digest(transcript(r.record,'key'))==P.digest(transcript(actual['record'],'key')),'waiting_key_equal':r.keys.waiting==actual['waiting_key'],
         'status':actual['status'],'production_calls':actual['counts'],'completed_fixtures':actual['completed'],'elapsed_s':round(time.monotonic()-start,4)}
    private=ROOT/'.cache/t123/terminal';private.mkdir(parents=True,exist_ok=True)
    for arm,value in [('original',reference),('sealed',actual['state'])]:
        with (private/(Path(opts.out).stem+'-'+arm+'.json')).open('x') as stream:json.dump(value,stream)
    with Path(opts.out).open('x') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n')
    assert all(row[k] for k in ('state_equal','pages_equal','draws_equal','keys_equal','waiting_key_equal')),row

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--case',choices=['continental','world','ageing-continental','ageing-world'],required=True);p.add_argument('--out',required=True);parent(p.parse_args())
