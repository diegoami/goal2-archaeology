#!/usr/bin/env python3
"""Pin the control-flow reading and project the source's clock-counter ordering."""
import argparse
import ast
import json
import re
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'notes/engine-study/foundations'))
from check import pin,sha,write_new


def frame_calls():
    path=ROOT/'runtime/original_match/port/frame.py';tree=ast.parse(path.read_text())
    table=next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SITES' for t in n.targets))
    sites=ast.literal_eval(table);result={}
    for name in ['match_tick_loop','watched_match_engine']:
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
        calls=[]
        for c in ast.walk(fn):
            if isinstance(c,ast.Call) and isinstance(c.func,ast.Name) and c.func.id=='go' and isinstance(c.args[0],ast.Constant):
                at=c.args[0].value;target,far,ret,pops=sites[at]
                calls.append({'python_line':c.lineno,'source_call_site':f'0791:{at:04X}','target':target,'return':ret,'far':far,'argument_words_popped':pops})
        result[name]=sorted(calls,key=lambda x:x['python_line'])
    assert [c['target'] for c in result['match_tick_loop']]==['0791:D733','0791:0C65','0791:15B9','0791:9564','0791:8CF5','0791:9119','0791:970C']
    return result


def clock_projection():
    # Only the ordinary counter projection; excludes ABI, drawing, sound and other writes.
    subtick=36;remaining=10;elapsed=81;rows=[]
    for call in range(1,38):
        advanced=False
        if subtick!=0:subtick-=1
        else:remaining-=1;elapsed+=1;subtick=36;advanced=True
        if call in {1,36,37}:rows.append(dict(call=call,subtick=subtick,remaining=remaining,elapsed=elapsed,advanced=advanced))
    assert [r['subtick'] for r in rows]==[35,0,36] and rows[-1]['advanced'] and remaining==9
    return {'scope':'Derived eligible-call counter projection of970C; not original execution or a full clock model',
            'initial':{'subtick':36,'remaining':10,'elapsed':81,'live_gate':1},'rows':rows,
            'eligible_calls_between_advances':37,'live_gate_zero':'counter projection unchanged'}


def draw_bindings():
    rows=[]
    for part,pc,target,condition in [
      ('04',0x2682,'214B:06B1','setup: rand(16)-1, 255 table entries'),
      ('14',0x8A2E,'214B:06FA','movement: off-target sprint-axis coin'),
      ('14',0x8AD1,'214B:06B1','movement: rand(5) after a failed move'),
      *[('18',pc,'214B:06B1',meaning) for pc,meaning in [
        (0xB1DA,'attempt: opponent midfield'),(0xB1EC,'attempt: own midfield'),
        (0xB20E,'after midfield win: twice opponent defence'),(0xB220,'after midfield win: own attack'),
        (0xB23F,'after defence win: opponent keeper'),(0xB251,'after defence win: own attack')]]]:
        path=f'static/goal-exe/code/seg_0791_{part}.asm'
        hits=[(n,line) for n,line in enumerate((ROOT/path).read_text().splitlines(),1) if line.startswith(f'{pc:04X} ')]
        assert len(hits)==1 and hits[0][1].endswith('call far '+target),(path,pc)
        n,line=hits[0]
        rows.append(dict(source_call_site=f'0791:{pc:04X}',target=target,condition=condition,
                         file=path,line=n,instruction_sha256=sha(line.encode())))
    return rows


def branch_projection():
    # A local calculation from B19D/0688, not an original call or a match fixture.
    def attempt(mid,force_all=False):
        seed=0;rows=[]
        for stage,a,b,op,own in [('midfield',mid,2,'B1DA','B1EC'),('defence',8,2,'B20E','B220'),('keeper',8,2,'B23F','B251')]:
            values=[]
            for at,bound in [(op,b),(own,a)]:
                seed=(seed*0x7ABD+0x1B0F)&65535;value=(seed*bound>>16)+1
                rows.append(dict(site='0791:'+at,bound=bound,value=value,seed_after=seed));values.append(value)
            if values[1]<=values[0] and not force_all:break
        next_seed=(seed*0x7ABD+0x1B0F)&65535
        return dict(own_midfield=mid,trace=rows,draw_count=len(rows),end_seed=seed,
                    next_common_rand100=(next_seed*100>>16)+1,next_common_seed=next_seed)
    rows=[attempt(1),attempt(8)];broken=[attempt(1,True),attempt(8,True)]
    assert [r['draw_count'] for r in rows]==[2,4]
    assert [r['next_common_rand100'] for r in rows]==[97,53]
    assert rows[0]['end_seed']!=rows[1]['end_seed']
    assert [r['draw_count'] for r in broken]==[6,6] and broken[0]['end_seed']==broken[1]['end_seed']
    return dict(scope='Source-derived one-attempt projection at entry seed 0; own lines [2,1,mid,8], opponent [2,1,2,2]. No original execution or whole-match reachability claim.',
                examples=rows,consume_all_six_control='rejected: loses early-exit draw counts and falsely aligns end seeds')


def historical_rng():
    path='experiments/E011-q010-watched-engine/rng-counts.txt';raw=(ROOT/path).read_text()
    ticks,draws=map(int,re.search(r'ticks (\d+), main-seed draws (\d+)',raw).groups())
    assert (ticks,draws)==(2077,91985)
    distributions={}
    for label in ['ball phases (95F2 block entries)','8A2E coins']:
        line=next(line for line in raw.splitlines() if line.startswith(label+' per 9564 sweep:'))
        counts={int(k):int(n) for k,n in re.findall(r'(\d+):(\d+)',line)}
        assert sum(counts.values())==ticks
        distributions[label]=counts
    return dict(source=path,ticks=ticks,main_draws=draws,mean_main_draws_per_tick=draws/ticks,
                ball_phases_per_sweep_range=[min(distributions['ball phases (95F2 block entries)']),max(distributions['ball phases (95F2 block entries)'])],
                sprint_coins_per_sweep_range=[min(distributions['8A2E coins']),max(distributions['8A2E coins'])],
                scope='Historical instrumented E011 second half only; not universal counts or new measurements')


def build():
    calls=frame_calls();clock=clock_projection()
    addresses=['0791:F1F6','0791:A4A1','0791:F098','0791:9564','0791:D733','0791:D47E','0791:97D0','0791:970C','0791:B7FA',
      '0791:998C','0791:983F','0791:9955','0791:98C4','0791:9A32','0791:9B0C','0791:9B5B','0791:A10A','0791:15B9','0791:0C65','0791:8AE9','0791:9372']
    return pin({'task':'T100','sections':['Code layers and machine fidelity','Fixture-to-result control flow','One ordinary watched iteration','Clock and half boundaries','Randomness, events and saved continuations'],
                'checks':{'tick_loop_lexical_guest_sites':len(calls['match_tick_loop']),'watched_lexical_guest_sites':len(calls['watched_match_engine']),
                          'clock_projection_eligible_interval':37,'scope':'Static order and declared arithmetic projection, not dynamic coverage'},
                'lexical_frame_calls':calls,'clock_projection':clock,
                'ordinary_match_sequence':['0791:A4A1','0791:ED8A','0791:F098','summary/tail'],
                'original_router_continuation':['conditional B71C then B6CC per side (managed involvement and non-friendly gate)','4E0E for each managed side','0791:B7FA'],
                'kit_continuation':['0791:F1F6','0791:B7FA; omits outer-router B71C/B6CC/4E0E'],
                'rng_draw_sites':draw_bindings(),'branch_rng_projection':branch_projection(),'historical_rng':historical_rng(),
                'setup_reseed':{'word':'U16(fixture_index*(elapsed_year+1))','foul_fill_draws':255,'bound':16,'stored_value':'draw-1','before_optional_kit_seed_override':True},
                'play_match_sequence':['0791:998C','0791:9955','0791:9A32','write fixture score/result','optional9B0C/9B5B/A10A','watched settling98C4/9955'],
                'analysis_sha256':sha(Path(__file__).read_bytes())},addresses+['0791:2648','0791:8889','0791:B19D','214B:0688','214B:06B1','214B:06FA','000E:6CA7','000E:4E0E','0791:B71C','0791:B6CC'],
               ['runtime/original_match/port/frame.py','runtime/original_match/port/guest.py','runtime/original_match/port/mem.py','runtime/original_match/port/__init__.py',
                'runtime/original_match/port/postmatch.py','runtime/original_match/port/quick.py','runtime/original_match/match.py','runtime/original_match/machine.py','runtime/original_match/README.md',
                'static/goal-exe/code/seg_0791_16.asm','static/goal-exe/code/seg_0791_23.asm','findings/F013-the-watched-engine-tick-map.md',
                'static/goal-exe/code/seg_0791_04.asm','static/goal-exe/code/seg_0791_14.asm','static/goal-exe/code/seg_0791_18.asm','static/goal-exe/code/seg_000E_09.asm','experiments/E011-q010-watched-engine/rng-counts.txt'])


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');a=ap.parse_args();path=ROOT/'notes/engine-study/T100/flow-v2.json';data=build()
    if a.check:
        assert json.loads(path.read_text())==data,'flow/source/clock projection differs';print('PASS:7 tick-loop and',data['checks']['watched_lexical_guest_sites'],'sweep lexical sites;37 eligible-clock interval; source routes/hashes')
    else:write_new(path,data);print('wrote source-linked flow/clock projection ledger')


if __name__=='__main__':main()
