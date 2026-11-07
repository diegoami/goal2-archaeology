"""Declared two-manager/skip supplement to the natural stage2-to3 call.
Only manager count/identity/announcement flag assignments differ from C's input;
fixtures, results, stage, year and RNG remain original-built and untouched.
"""
import argparse,hashlib,json,sys,types
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];sys.path[:0]=[str(ROOT),str(ROOT/'runtime'),str(ROOT/'tools'),str(HERE)]
import pairs as P
import terminal_v2 as T

def candidate(state,tables,waiting):
    from original_match import port
    calls=[];entry=port._module_registry('stages').entries['000E:60CB'];original=entry.fn
    def observed(mem,variant):
        country=mem.arg(0);off,seg=mem.farptr(mem.DS*16+0xA917)
        calls.append([country,mem.u8(seg*16+off+191*country+46)])
        value=original(mem,variant)
        if isinstance(value,types.GeneratorType):return (yield from value)
        return value
    entry.fn=observed
    actual=T.candidate(state,tables,waiting);actual['manager_calls']=calls;return actual

def run(out,skip):
    from original_match.image import Image
    from original_match.machine import MEM_SIZE
    from original_match.port.tables import to_record
    from port_test_runtime import call_in_pypy
    r,image,lineage=T.natural_input('ageing-continental');m=r.m;g=m.far(0xA923);manager=m.far(0xA91F);countries=m.far(0xA917);fx=m.far(0xA92B)
    old=m.read(manager+3*129,1)[0];start=m.word_at(g+0x26);end=m.word_at(g+0x28)
    remaining={int.from_bytes(m.read(fx+8*(n-1)+off,2),'little') for n in range(start,end) for off in (4,6)}
    other=next(c for c in range(1,129) if c!=old and c not in remaining and m.read(countries+191*c+46,1)[0]<=128)
    changes=[]
    for label,address,value in [('manager_count',g,2),('existing_country_manager2_tag',countries+191*old+46,130),('manager2_country',manager+3*130,old),('second_country_manager1_tag',countries+191*other+46,129),('manager1_country',manager+3*129,other),('manager1_announcement_enabled',g+0x48,0),('manager2_announcement_skip',g+0x49,int(skip))]:
        before=m.read(address,1)[0];m.write(address,bytes([value]));changes.append({'field':label,'linear':address,'before':before,'after':value})
    initial=Image(r.header+m.read(0,MEM_SIZE)+r.tail);initial.tables=image.tables;waiting=r.keys.waiting;calls=[]
    def entered(replay):
        if not replay:
            country=m.stack_word(4);calls.append([country,m.read(countries+191*country+46,1)[0]])
    m.at('000E:60CB',entered);r.call();assert any(e[0]=='round_end' for e in r.record)
    expected=Image(r.header+m.read(0,MEM_SIZE)+r.tail);expected.tables=image.tables
    actual=call_in_pypy('experiments.E040-route-fixture-writes.out.T123.managers','candidate',args=(initial.state(image.tables),to_record(image.tables),waiting))
    reference=expected.state(image.tables);pages=[dict(page.__dict__,cells=page.cells.hex()) for page in r.news_history]
    transcript=lambda record,kind:[list(e) for e in record if e[0]==kind]
    expected_calls=[[other,129]]+([] if skip else [[old,130]])
    row={'schema':'t123-two-manager-outer/1','case':'skip-manager2' if skip else 'both-managers','input':lineage,'declared_manager_only_changes':changes,
      'sources':{**P.sources(),str(Path(__file__).relative_to(ROOT)):hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),str(Path(T.__file__).relative_to(ROOT)):hashlib.sha256(Path(T.__file__).read_bytes()).hexdigest()},
      'state_equal':reference==actual['state'],'state_digests':[P.digest(reference),P.digest(actual['state'])],
      'pages_equal':pages==actual['pages'],'page_count':len(pages),'ordered_page_sha256':P.digest(pages),
      'ordered_draws_equal':P.digest(transcript(r.record,'rng'))==P.digest(transcript(actual['record'],'rng')),
      'ordered_keys_equal':P.digest(transcript(r.record,'key'))==P.digest(transcript(actual['record'],'key')),
      'manager_calls_equal':calls==actual['manager_calls']==expected_calls,'manager_calls':actual['manager_calls'],
      'waiting_key_equal':r.keys.waiting==actual['waiting_key'],'production_calls':actual['counts']}
    with Path(out).open('x') as stream:stream.write(json.dumps(row,sort_keys=True)+'\n')
    assert all(row[k] for k in ('state_equal','pages_equal','ordered_draws_equal','ordered_keys_equal','manager_calls_equal','waiting_key_equal')),row
    assert len(pages)==(1 if skip else 2)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--skip-manager2',action='store_true');a=p.parse_args();run(a.out,a.skip_manager2)
