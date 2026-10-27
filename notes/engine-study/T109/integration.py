#!/usr/bin/env python3
"""Reproduce a bounded source/evidence integration register, never new match outcomes."""
import argparse,json,subprocess
from collections import Counter
from pathlib import Path
from check import ROOT,BASE,pin,sha,write_new,validate,check_guard

ASM='static/goal-exe/code/'
LITERALS=[
 ('seg_0791_04.asm','21FC','shl ax, 1'),
 ('seg_0791_04.asm','2201','add byte ptr es:[di + 0x11], al'),
 ('seg_0791_04.asm','273B','call 0x2974'),
 ('seg_0791_04.asm','2752','mov al, byte ptr es:[di + 0x2d]'),
 ('seg_0791_05.asm','2BCA','sub ax, 0xb'),
 ('seg_0791_14.asm','8805','les di, ptr [0x7c16]'),
 ('seg_0791_14.asm','880D','cmp byte ptr es:[di + 0x90f], 0xd'),
 ('seg_0791_11.asm','685C','inc byte ptr [di - 0x64c4]'),
 ('seg_0791_11.asm','6879','cmp byte ptr [0x830e], 0'),
 ('seg_0791_11.asm','68B3','dec byte ptr [di - 0x64c4]'),
 ('seg_0791_11.asm','68B7','call 0x82eb'),
 ('seg_0791_16.asm','97DA','call 0xd733'),
 ('seg_0791_16.asm','9813','jne 0x9824'),
 ('seg_0791_12.asm','6EE5','mov ax, 3'),
 ('seg_0791_12.asm','6F17','mov ax, 5'),
 ('seg_0791_17.asm','A36A','mov byte ptr es:[di + 0xf], 5'),
 ('seg_0791_20.asm','C712','les di, ptr [0xa91b]'),
 ('seg_0791_20.asm','C718','mov byte ptr es:[di + 0xf], 0'),
 ('seg_0791_20.asm','CCEC','cmp ax, 0xb'),
 ('seg_0791_20.asm','CCEF','jbe 0xcd09'),
]


def titles(memory):
    return {role:bytes(memory[off+1:off+1+memory[off]]).decode('ascii').strip() for role in range(1,6) for off in [0xA29+11*role]}


def check_titles(memory):assert titles(memory)=={1:'CAPTAIN',2:'CORNER',3:'PENALTY',4:'FREE KICK',5:'GOAL KICK'}


def build(producer_commit=None):
    guards=[dict(path=ASM+n,address=a,instruction=i) for n,a,i in LITERALS]
    # This is a literal data read,not a UI mock or an executed prompt.
    data_path='static/goal-exe/data/ds_2581_01.hex';memory=bytearray(65536)
    for line in (ROOT/data_path).read_text().splitlines():
        cells=line.split('|')[0].split()
        if not cells or len(cells[0])!=4:continue
        try:off=int(cells[0],16);values=bytes.fromhex(' '.join(cells[1:]))
        except ValueError:continue
        memory[off:off+len(values)]=values
    check_titles(memory);title_negatives={}
    for role in [3,4,5]:
        altered=bytearray(memory);altered[0xA29+11*role+1]=ord('X')
        try:check_titles(altered)
        except AssertionError:title_negatives[str(role)]='altered original title rejected'
        else:raise AssertionError('title negative escaped')
    restart_path='docs/engine-study/restarts.md';old=subprocess.check_output(['git','show',BASE+':'+restart_path],cwd=ROOT).decode();new=(ROOT/restart_path).read_text()
    assert 'penalties-selected\nrole-4 player' in old and 'free-kick-selected\nrole-4 player' in new
    raw12=(ROOT/(ASM+'seg_0791_12.asm')).read_text();assert '6F88  B8 04 00        mov ax, 4' in raw12
    guards.append(dict(path=ASM+'seg_0791_12.asm',address='6F88',instruction='mov ax, 4'))
    for g in guards:check_guard(g,(ROOT/g['path']).read_text())
    issues=json.loads((Path(__file__).with_name('issues-v1.json')).read_text());assert len(issues['issues'])==20
    assert next(r for r in issues['issues'] if r['issue_number']==571)['state']=='closed'
    rows=[]
    def row(id,disposition,minimal,expected,actual,evidence,follow_up,reachability='Conditional source path;not a new observed full match.',limits=None):
        rows.append(dict(id=id,disposition=disposition,minimal_input=minimal,expected=expected,actual=actual,evidence=evidence,follow_up=follow_up,reachability=reachability,limits=limits or ['Source/evidence synthesis pending ES-R3;not exhaustive fidelity or natural frequency.']))
    row('cache-reset','original quirk','Identity present in managed pool and squad;cached pitch extra versus persistent player attributes.',
        'Do not assume one recovery/status update per fixture,or that pitch cache is continuously recomputed.',
        'F1F6 managed-pool BA4E precedes outer6CA7/B7FA squad update;overlap can update an identity twice.20E3 separately adds twice captain leadership to eleven pitch+11 bytes. CB7D restores temporary form/energy before later career updates.',
        ['docs/engine-study/lifecycle.md','docs/engine-study/audit-records.md',ASM+'seg_0791_04.asm'],
        '#546 retains membership/natural-incidence question;#514 retains its historical candidate bundle. No original fix.')
    row('side-bindings','documentation/test defect','Coherent pitch slot,country and player identity versus a deliberately mismatched raw binding.',
        'Effective team tactics use the bound side country,not an assumed player-country byte.',
        '26D7 at273B calls2974,then9B34/36 country lookup and+2D read.2BB1 maps pitch slots12..22 to1..11. Existing annotation shorthand differs on incoherent synthetic bindings;ordinary coherent bindings agree.',
        [ASM+'seg_0791_04.asm',ASM+'seg_0791_05.asm','docs/engine-study/positioning.md'],
        '#553 is the existing annotation correction;no duplicate issue or production change.')
    row('occupancy','intentional path difference','Ordinary live outfielder step into character1 at attribute7 versus13;draw/restore order retained.',
        'Picture cells can affect movement;render-only separation must preserve that simulation state.',
        '86D0 reads7C16 picture words;attribute0D bypasses the blocking-character test.8537 restores frombackground;8E24 restores only if full old glyph still matches. Occupancy bypasses are conditional,not universal.',
        ['docs/engine-study/movement.md',ASM+'seg_0791_14.asm'],
        'Preserve typed glyph/attribute and draw order in a future contract;#416 covers unrelated unvisited display effects.')
    row('score-counters','intentional path difference','Normal67B6goal with830Epending;accepted score versus goal-list capacity and shootout result.',
        'Provisional score,accepted scorer statistics,goal history and competition result need not be the same counter.',
        '685C increments score before6879offside gate;68B3 decrements it before82EB,skipping6443. Accepted goal-list rows saturate at11;D050uses fixture result forW/D/L andstored goals forGF/GA. Shootout tally/result differs from ordinary career goals.',
        [ASM+'seg_0791_11.asm','docs/engine-study/scoring.md','docs/engine-study/lifecycle.md','docs/engine-study/shootouts.md'],
        '#227 specific old playthrough attribution stays open;do not collapse tentative/cancelled events into final score.')
    row('modes','intentional path difference','Same nominal seed andteams under watched97D0,quickD733and silentB602routes.',
        'A speed/mode switch is not automatically the same simulation with fewer draws.',
        '97DA callsD733whenquickflag9A3Eset;afterwatched9564,9813can skipoffside/referee. Celebration6337consumes extra watched draws. Silent postmatch andquick trial/commit counters have distinct source paths.',
        [ASM+'seg_0791_16.asm','docs/engine-study/match-flow.md','docs/engine-study/scoring.md','docs/engine-study/lifecycle.md'],
        '#531 is the existing incomplete-celebration-RNG annotation. T107unrun;no paired score effect or null result.')
    row('save-load','unresolved','Save with active menu,proved Match,or live portframes;compare ordinary accepted event boundary.',
        'Whole continuation includes memory,registers,kit queue andany live Python call reconstruction,not only RNG word.',
        'Match.save refuses active menu/prover and unrecorded liveframes;version4can encode deterministic replay origin/actions/frames andload checks replay state. Originalaction replay is a separate mechanism. Current standalone sealed-delivery contract belongs to the other session.',
        ['runtime/original_match/match.py','docs/engine-study/match-flow.md','runtime/original_match/README.md'],
        '#394 remains direct DOS-wrapper proof limit;#400 is genuine checkpoint gap. This audit adds no new continuation run.',
        limits=['Source contract and retained tests are not every-manager-path natural coverage.','Do not claim a general standalone save/load delivery or force a synthetic state into a genuine checkpoint role.'])
    row('manager-continuations','documentation/test defect','Role3penalty,4free-kick,5goal-kick title/caller mapping;managed input waits distinct from selection arithmetic.',
        'Chapter prose must agree with original prompt titles and actual award role words.',
        'OriginalDS:0A29+11*role gives PENALTY/FREE KICK/GOAL KICK for3/4/5.6ECFuses3,near6F3Euses4,6F01uses5. Oldrestartparagraph calledrole4penalties-selected;corrected under#599. Genuine role/extra-time/message checkpoints are still missing under#400.',
        [ASM+'seg_0791_12.asm',data_path,restart_path,'runtime/original_match/match.py'],
        '#599 corrects wording only;#400 remains open for real original-key provenance;#544 retains partial/fallback-order reachability.',
        reachability='Title bytes/callers are literal source;no managed prompt was newly exercised.',
        limits=['No claim that missing role2..5or extra-time inputs now exist.','Historical T104outputs remain unchanged;the paragraph correction is separate from their numeric results.'])
    row('legacy-offside','unresolved','OldE015reported scorer/team-mate offside or apparently defending-side notification.',
        'Separate offside-line candidate,pending830E,notification56D9and actual82EBadjudication.',
        'Accepted source chapters trace those stages and67B6rollback,butdo not reconstruct exact old player/ball/phase state. A team-mate pending marker can matter at goal adjudication;specific playthrough attribution needs its actual continuation.',
        ['docs/engine-study/scoring.md','docs/engine-study/movement.md',ASM+'seg_0791_11.asm'],
        '#227 remains open;no new game-balance claim or fabricated old-input reproduction.',
        limits=['Source route is not proof of the exact historical player-side incident.'])
    row('coverage-gaps','unresolved','UncaughtA36Adirection4mutant,threeweak focused-unitedges,displacedDOSreturn andunvisiteddisplaystubs.',
        'Passing families or source agreement do not imply every edge is falsifiable or every stub state-free.',
        '#375still lacks complete read-before-overwrite/alias proof;#412focusedunitgaps remain;#394directproof return prediction misses displacement;#416unvisited effects remain. C718+F clears persistent-player tactics afterA91Bbinding,not pitchdirection.',
        ['docs/engine-study/audit-records.md',ASM+'seg_0791_17.asm',ASM+'seg_0791_20.asm','notes/engine-study/T109/T109a-v1.json'],
        'Reuse#375/#412/#394/#416/#591;no new production bug or silently closed coverage issue.')
    source_paths=[ASM+n for n in sorted({n for n,_,_ in LITERALS})]
    source_paths += ['docs/engine-study/'+n+'.md' for n in ['lifecycle','audit-records','positioning','movement','scoring','shootouts','match-flow']]
    source_paths += ['runtime/original_match/match.py','runtime/original_match/README.md',data_path]
    source_paths += ['static/goal-exe/named/'+n for n in ['seg_0791_02.c','seg_0791_06.c','seg_0791_07.c','seg_0791_08.c','seg_0791_11.c']]
    support=['notes/engine-study/T109/issues-v1.json','notes/engine-study/T109/T109a-v1.json',restart_path]
    path=str(Path(__file__).resolve().relative_to(ROOT));commit=producer_commit or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    return pin(dict(task='T109b',method=__doc__,sections=['Candidate register','Source contradictions and bounded examples','Remaining gaps and review scope'],limits=['Nine source/evidence groups;no fresh engine call or exhaustive fidelity claim.','T107owner-deferred;no match-effect estimate,null-result claim or new spending.'],candidates=rows,
                    summary=dict(groups=len(rows),dispositions=dict(Counter(r['disposition'] for r in rows)),new_reproduced_production_defects=0),
                    prompt_titles={str(k):v for k,v in titles(memory).items()},title_negative_controls=title_negatives,
                    correction=dict(issue=599,path=restart_path,historical_commit=BASE,historical_sha256=sha(old.encode()),current_sha256=sha(new.encode()),meaning='Role4isfree-kick-selected,notpenalties-selected;role5isgoal-kick-selected.'),
                    issue_snapshot=dict(path='notes/engine-study/T109/issues-v1.json',captured_utc=issues['captured_utc'],note='Historical snapshot;live labels remain authoritative.'),
                    producer=dict(commit=commit,path=path,sha256=sha(Path(__file__).read_bytes()))),source_paths,guards,support)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();path=Path(__file__).with_name('T109b-v2.json')
    old=json.loads(path.read_text()) if a.check else None;data=build(old['producer']['commit'] if old else None)
    if a.check:
        assert old==data;validate('T109b',data,(ROOT/'docs/engine-study/audit-integration.md').read_text());print('PASS:9integration groups;21literal guards;5prompt titles/3altered-title negatives;explicit gaps;no engine calls')
    else:write_new(path,data);print('wrote immutable integration candidate register;no engine calls')


if __name__=='__main__':main()
