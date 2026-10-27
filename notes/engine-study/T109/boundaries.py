#!/usr/bin/env python3
"""Source-only caller census and bounded attribution of immutable T106 discrepancies."""
import argparse,json,re,subprocess
from pathlib import Path
from check import ROOT,pin,sha,write_new,validate,check_guard,instruction

ASM='static/goal-exe/code/'
EXPECTED_CALLS={'3932','3944','3B73','3BCE','3CC1','3E80','3F8B','406C','5EA2','6AE1'}
LITERALS=[
 ('seg_0791_06.asm','34C4','sub sp, 6'),
 ('seg_0791_06.asm','3837','call far 214B:1EA1'),
 ('seg_0791_06.asm','3849','retf 8'),
 ('seg_214B_04.asm','1EA8','call 0x1ebc'),
 ('seg_214B_04.asm','1EAF','call 0x1e09'),
 ('seg_214B_04.asm','1EB3','call 0x1e8d'),
 ('seg_214B_04.asm','1E0C','sub sp, 8'),
 ('seg_0791_14.asm','8BB0','call 0x7621'),
 ('seg_0791_14.asm','8BB3','push bp'),
 ('seg_0791_14.asm','8BB4','call 0x8889'),
 ('seg_0791_14.asm','8889','push bp'),
 ('seg_0791_14.asm','888A','mov bp, sp'),
 ('seg_0791_14.asm','888C','sub sp, 2'),
 ('seg_0791_14.asm','888F','cmp byte ptr [0x8302], 0'),
]


def build(producer_commit=None):
    code=sorted((ROOT/ASM).glob('seg_0791*.asm'));calls=[]
    for path in code:
        lines=path.read_text().splitlines()
        for i,line in enumerate(lines):
            if re.search(r'\bcall 0x34c1$',line):
                off=line.split()[0];following=[s for s in lines[i+1:] if re.match(r'^[0-9A-F]{4} ',s)][:8]
                calls.append(dict(path=str(path.relative_to(ROOT)),line=i+1,address=off,following_instructions=following,
                                  limit='Eight lexical successor instructions,not a transitive alias/control-flow proof.'))
    assert len(calls)==10 and {r['address'] for r in calls}==EXPECTED_CALLS
    guards=[dict(path=ASM+name,address=off,instruction=expected) for name,off,expected in LITERALS]
    guards += [dict(path=r['path'],address=r['address'],instruction='call 0x34c1') for r in calls]
    for g in guards:check_guard(g,(ROOT/g['path']).read_text())
    launch=ROOT/'notes/engine-study/T106/launch';manifest=json.loads((launch/'manifest-v1.json').read_text())
    pairs=json.loads((launch/'out/manifest-v1-79e714555a81-comparisons.json').read_text())['comparisons']
    offsets=[0x3EDE,0x3EE0,0x3EE1,0x3EE2,0x3EE4,*range(0x3EE6,0x3EF0)]
    residues=[]
    for p in pairs:
        ro=json.loads((ROOT/p['original_record']['path']).read_text());rp=json.loads((ROOT/p['port_record']['path']).read_text())
        item=next(i for i in manifest['invocations'] if i['spec']['logical']==ro['logical']);state=item['input']
        ss=state['registers']['ss'];relative=[x-ss*16 for x in p['memory_diff_first_offsets']]
        assert relative==offsets and p['memory_diff_count']==15 and p['abi_equal'] and not p['register_differences']
        assert all(x<state['registers']['sp']<state['expected_return_sp'] for x in relative)
        assert ro['registers']['esp']==rp['registers']['esp']==state['expected_return_sp']==0x3F0C
        assert any(e['address']=='214B:1EA1' for e in rp['production_stub_entries'])
        residues.append(dict(case=p['case'],ss_offsets=[f'{x:04X}' for x in relative],below_entry_sp=True,below_return_sp=True,returned_sp='3F0C'))
    # Literal frame arithmetic,not a new execution or read-before-write proof.
    launch_bp=0x3F00-2;launch_local_bottom=launch_bp-6
    sound_entry=launch_local_bottom-4-4;sound_bp=sound_entry-2
    delay_entry=sound_bp-2-4;delay_bp=delay_entry-2;delay_bottom=delay_bp-8
    assert (sound_entry,sound_bp,delay_entry,delay_bp,delay_bottom)==(0x3EF0,0x3EEE,0x3EE8,0x3EE6,0x3EDE)
    rows=[
        dict(id='launch-stack',minimal_input='T106 launch baseline cases:entry SP3F00;muted native sound still executes;port sound entry is declared void stub.',expected='Field/ABI comparison may agree while omitted nested frames leave physical stack residue.',actual='All3pairs:15differing bytes,SS3EDE..3EEF subset;returnedSP3F0C;allcapturedregisters/field/ABI equal.',disposition='unresolved',reachability='Observed synthetic direct calls only.',limits=['Source frame depth and reached1EA1 omission explain a plausible residue region;no isolated native ablation/byte-writer trace.','No complete transitive read-before-overwrite or stack-alias proof;not whole-program dead-state classification.'],follow_up='#591:retain mismatch and explicit liveness/causal gap;no mask or repair.',evidence=['notes/engine-study/T106/report-v1.json',ASM+'seg_214B_04.asm',ASM+'seg_0791_06.asm']),
        dict(id='wall-flags',minimal_input='T106 near/far wall calls;ordinary8AE9continues at8BB3.',expected='A gameplay effect from flags needs a caller reading them before replacement.',actual='Only direct7621caller is8BB0;8BB3pushBP/call8889;888C SUB SP,2 and888F CMP replace arithmetic flags before8894conditional. DF unchanged and compared.',disposition='unsupported suspicion',reachability='Normal source tick continuation;bare synthetic wall calls did not execute8889.',limits=['Static local continuation proof;does not extend to arbitrary external/indirect callers.','Arithmetic flags remain physically different in T106;no complete-machine-state equality.'],follow_up='#591 records the discrepancy;standard continuation consumes no inherited arithmetic flags;no production bug established.',evidence=[ASM+'seg_0791_14.asm','runtime/original_match/port/runtime.py','notes/engine-study/T106/T106b-v1.json']),
        dict(id='launch-callers',minimal_input='All direct call0x34c1instructions in seg0791raw listings.',expected='Caller context is required before claiming all below-SP residue dead.',actual='Tenliteral calls at3932,3944,3B73,3BCE,3CC1,3E80,3F8B,406C,5EA2,6AE1. Immediate successors use caller locals/DS,another call or epilogue;5EA2returns directly afterepilogue.',disposition='unresolved',reachability='Static direct-call census,not dynamic reach counts.',limits=['Lexical windows do not follow every jump/callee/alias;tail return can propagate scratch state.','No proof of absence of indirect callers or later uninitialised-local reads.'],follow_up='#591 remains open for complete liveness or a sensitive original-backed continuation if required by a future contract.',evidence=[ASM+'seg_0791_06.asm',ASM+'seg_0791_07.asm',ASM+'seg_0791_10.asm',ASM+'seg_0791_11.asm']),
        dict(id='production-stubs',minimal_input='DeclaredT73sound entry1EA1 versus native muted call chain1EBC/1E09/1E8D.',expected='Historical ALL equality only covers its compared paths/observation boundaries.',actual='T73declares1EA1void removal;native body allocates nested frames. Standalone1E09port separately preserves its completed busy-wait frame,but1EA1stub does not invoke it.',disposition='intentional path difference',reachability='1EA1 reached in T106launch;unvisited stateful display boundaries remain separately unresolved.',limits=['Declared omission is not proof every native body is state-free or all bare calls exact.','Historical#416zero-entry census is not current universal removability evidence;no claim of natural manager-path coverage.'],follow_up='Keep#416forremainingboundarycoverage;#591forbare-launchresidue;reuseT73evidence,notnewALLruns.',evidence=['runtime/original_match/port/display.py','runtime/original_match/port/runtime.py','experiments/E036-match-port/notes/T73.md',ASM+'seg_214B_04.asm']),
    ]
    sources=[str(p.relative_to(ROOT)) for p in code]+[ASM+'seg_214B_04.asm','runtime/original_match/port/display.py','runtime/original_match/port/runtime.py','runtime/original_match/port/motion.py','experiments/E036-match-port/notes/T73.md']
    sources += ['static/goal-exe/named/'+n for n in ['seg_0791_03.c','seg_0791_07.c','seg_0791_08.c','seg_214B_02.c']]
    support=['notes/engine-study/T106/report-v1.json','notes/engine-study/T106/T106b-v1.json',str((launch/'manifest-v1.json').relative_to(ROOT)),str((launch/'out/manifest-v1-79e714555a81-comparisons.json').relative_to(ROOT))]
    path=str(Path(__file__).resolve().relative_to(ROOT));commit=producer_commit or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    data=pin(dict(task='T109a',method=__doc__,sections=['Observed residue and frame arithmetic','Wall flags at the ordinary continuation','Direct callers and unresolved boundaries'],limits=['Source-based proposed attribution pending ES-R3;zero new engine calls.','Literal listing guards protect named instructions;candidate integrity is not behavioural proof.'],candidates=rows,call_census=calls,residue=residues,frame_arithmetic=dict(sound_entry=f'{sound_entry:04X}',sound_bp=f'{sound_bp:04X}',delay_entry=f'{delay_entry:04X}',delay_bp=f'{delay_bp:04X}',delay_local_bottom=f'{delay_bottom:04X}'),producer=dict(commit=commit,path=path,sha256=sha(Path(__file__).read_bytes()))),sources,guards,support)
    return data


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();path=Path(__file__).with_name('T109a-v1.json')
    old=json.loads(path.read_text()) if a.check else None;data=build(old['producer']['commit'] if old else None)
    if a.check:
        assert old==data;validate('T109a',data,(ROOT/'docs/engine-study/audit-boundaries.md').read_text());print('PASS:4candidates;10direct launch callers;24literal guards;3residue cases;no engine calls')
    else:write_new(path,data);print('wrote immutable boundary/caller audit;no engine calls')


if __name__=='__main__':main()
