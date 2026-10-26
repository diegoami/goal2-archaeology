#!/usr/bin/env python3
"""Pin the control-flow reading and project the source's clock-counter ordering."""
import argparse
import ast
import json
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


def build():
    calls=frame_calls();clock=clock_projection()
    addresses=['0791:F1F6','0791:A4A1','0791:F098','0791:9564','0791:D733','0791:D47E','0791:97D0','0791:970C','0791:B7FA',
      '0791:998C','0791:983F','0791:9955','0791:98C4','0791:9A32','0791:9B0C','0791:9B5B','0791:A10A','0791:15B9','0791:0C65','0791:8AE9','0791:9372']
    return pin({'task':'T100','sections':['Code layers and machine fidelity','Fixture-to-result control flow','One ordinary watched iteration','Clock and half boundaries','Randomness, events and saved continuations'],
                'checks':{'tick_loop_lexical_guest_sites':len(calls['match_tick_loop']),'watched_lexical_guest_sites':len(calls['watched_match_engine']),
                          'clock_projection_eligible_interval':37,'scope':'Static order and declared arithmetic projection, not dynamic coverage'},
                'lexical_frame_calls':calls,'clock_projection':clock,
                'ordinary_match_sequence':['0791:A4A1','0791:ED8A','0791:F098','summary/tail','separate0791:B7FA'],
                'play_match_sequence':['0791:998C','0791:9955','0791:9A32','write fixture score/result','optional9B0C/9B5B/A10A','watched settling98C4/9955'],
                'analysis_sha256':sha(Path(__file__).read_bytes())},addresses,
               ['runtime/original_match/port/frame.py','runtime/original_match/port/guest.py','runtime/original_match/port/mem.py','runtime/original_match/port/__init__.py',
                'runtime/original_match/port/postmatch.py','runtime/original_match/port/quick.py','runtime/original_match/match.py','runtime/original_match/machine.py','runtime/original_match/README.md',
                'static/goal-exe/code/seg_0791_16.asm','static/goal-exe/code/seg_0791_23.asm','findings/F013-the-watched-engine-tick-map.md'])


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');a=ap.parse_args();path=ROOT/'notes/engine-study/T100/flow.json';data=build()
    if a.check:
        assert json.loads(path.read_text())==data,'flow/source/clock projection differs';print('PASS:7 tick-loop and',data['checks']['watched_lexical_guest_sites'],'sweep lexical sites;37 eligible-clock interval; source routes/hashes')
    else:write_new(path,data);print('wrote source-linked flow/clock projection ledger')


if __name__=='__main__':main()
