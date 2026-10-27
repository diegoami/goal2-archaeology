#!/usr/bin/env python3
"""Reproduce a bounded source/evidence integration register, never new match outcomes."""
import argparse,json,subprocess
from collections import Counter
from pathlib import Path
from check import ROOT,BASE,pin,sha,write_new,validate,check_guard

ASM='static/goal-exe/code/'
INTERVENING='2ec0fff4b05c4f04735b481b2193f2cea760f3da'
REJECTED_REVIEW='eee8fae4b3e6ed74e07d6aeda0398dbf0e76c628'
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
 ('seg_0791_04.asm','215F','mov al, byte ptr [di + 0x764]'),
 ('seg_0791_04.asm','2169','call 0x1fdd'),
 ('seg_0791_12.asm','6D97','mov al, byte ptr [di + 0x764]'),
 ('seg_0791_12.asm','6DA1','call 0x1fdd'),
 ('seg_0791_04.asm','2074','push word ptr [bp + 6]'),
 ('seg_0791_04.asm','20A0','call 0x278a'),
 ('seg_0791_04.asm','20A4','push word ptr [bp + 6]'),
 ('seg_0791_04.asm','20AD','call 0x278a'),
 ('seg_0791_04.asm','1FFD','cmp word ptr [bp + 4], 5'),
 ('seg_0791_04.asm','200C','mov al, byte ptr [di + 0x764]'),
]


def titles(memory):
    return {role:bytes(memory[off+1:off+1+memory[off]]).decode('ascii').strip() for role in range(1,6) for off in [0xA29+11*role]}


def check_titles(memory):assert titles(memory)=={1:'CAPTAIN',2:'CORNER',3:'PENALTY',4:'FREE KICK',5:'GOAL KICK'}


def selection_skills(memory):return {role:memory[0x764+role] for role in range(2,6)}


def check_selection_skills(memory):assert selection_skills(memory)=={2:7,3:12,4:12,5:2}


def check_selection_prose(text,memory):
    """Preserve role AND selection skill; titles alone cannot establish this claim."""
    check_selection_skills(memory);text=' '.join(text.lower().split())
    names={2:'kicking',12:'penalties'}
    for role,label in [(3,'penalty'),(4,'free-kick'),(5,'goal-kick')]:
        element=selection_skills(memory)[role]
        clause=f'role {role} (the {label} taker, automatically selected by {names[element]}, element {element})'
        assert clause in text,('missing role/selection-skill distinction',role)


def selection_controls(memory,text,old_title_only):
    """Literal table/prose guards,not new taker executions or behavioural mutants."""
    result={}
    for role in range(2,6):
        altered=bytearray(memory);altered[0x764+role]^=1
        try:check_selection_skills(altered)
        except AssertionError:result[f'changed-skill-byte-role{role}']='rejected'
        else:raise AssertionError('skill-byte negative escaped')
    clean=' '.join(text.split())
    for role,label,skill,element in [(3,'penalty','penalties',12),(4,'free-kick','penalties',12),(5,'goal-kick','kicking',2)]:
        old=f'role {role} (the {label} taker, automatically selected by {skill}, element {element})'
        assert old in clean
        altered=clean.replace(old,f'role {role} (the {label} taker)',1)
        try:check_selection_prose(altered,memory)
        except AssertionError:result[f'dropped-selection-skill-role{role}']='rejected'
        else:raise AssertionError('prose skill omission escaped')
    try:check_selection_prose(old_title_only,memory)
    except AssertionError:result['prior-title-only-599-edit']='rejected'
    else:raise AssertionError('the false-positive correction still passes')
    return result


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
    old_title_only=subprocess.check_output(['git','show',REJECTED_REVIEW+':'+restart_path],cwd=ROOT).decode()
    assert 'penalties-selected\nrole-4 player' in old
    check_selection_skills(memory);check_selection_prose(new,memory)
    skill_controls=selection_controls(memory,new,old_title_only)
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
        'For the original backend, Match.save refuses active menu/prover and unrecorded liveframes;version4can encode deterministic replay origin/actions/frames andload checks replay state. T78b at2ec0fff4 separately adds explicit engine selection and refuses port-backend checkpoints in that assembly slice. Originalaction replay is separate;standalone sealed delivery belongs to the other session.',
        ['runtime/original_match/match.py','docs/engine-study/match-flow.md','runtime/original_match/README.md'],
        '#394 remains direct DOS-wrapper proof limit;#400 is genuine checkpoint gap. This audit adds no new continuation run.',
        limits=['Source contract and retained tests are not every-manager-path natural coverage.','Do not claim a general standalone save/load delivery or force a synthetic state into a genuine checkpoint role.'])
    row('manager-continuations','unsupported suspicion','Role titles versus the skill used by automatic selection; managed input waits remain separate.',
        'Read both title table DS:0A29+11*role and selection-skill table DS:0764+role through their actual consumers.',
        'Roles3/4/5 are PENALTY/FREE KICK/GOAL KICK; automatic skill elements are12/12/2. The old penalties-selected role4 and kicking-selected role5 wording was correct. #599 conflated titles with selection skills and is withdrawn under#603. The guide now names both quantities explicitly; genuine checkpoints remain missing under#400.',
        [ASM+'seg_0791_04.asm',ASM+'seg_0791_12.asm',data_path,restart_path,'docs/engine-study/marking.md'],
        '#603 retracts the false positive #599;#400 remains open for original-key provenance;#544 retains partial/fallback-order reachability.',
        reachability='Literal source table/caller interpretation; no managed prompt or taker routine newly executed.',
        limits=['Automatic selection criteria do not constrain a managed manual choice.','Titles/skill-byte/prose negatives are separate literal guards,not engine mutants.','Historical T104/T109v1/v2 outputs remain immutable;v3 supersedes the false-positive attribution.'])
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
    source_paths += ['docs/engine-study/'+n+'.md' for n in ['lifecycle','audit-records','positioning','movement','scoring','shootouts','match-flow','marking']]
    source_paths += [str(p.relative_to(ROOT)) for pattern in ['F021*.md','F022*.md'] for p in (ROOT/'findings').glob(pattern)]
    source_paths += ['runtime/original_match/match.py','runtime/original_match/README.md',data_path]
    source_paths += ['static/goal-exe/named/'+n for n in ['seg_0791_02.c','seg_0791_06.c','seg_0791_07.c','seg_0791_08.c','seg_0791_11.c']]
    support=['notes/engine-study/T109/issues-v1.json','notes/engine-study/T109/T109a-v1.json',restart_path]
    path=str(Path(__file__).resolve().relative_to(ROOT));commit=producer_commit or subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    return pin(dict(task='T109b',method=__doc__,sections=['Candidate register','Source contradictions and bounded examples','Remaining gaps and review scope'],limits=['Nine source/evidence groups;no fresh engine call or exhaustive fidelity claim.','T107owner-deferred;no match-effect estimate,null-result claim or new spending.'],candidates=rows,
                    summary=dict(groups=len(rows),dispositions=dict(Counter(r['disposition'] for r in rows)),new_reproduced_production_defects=0),
                    prompt_titles={str(k):v for k,v in titles(memory).items()},title_negative_controls=title_negatives,
                    automatic_selection_skills={str(k):v for k,v in selection_skills(memory).items()},selection_negative_controls=skill_controls,
                    correction=dict(issue=603,withdrawn_false_positive=599,path=restart_path,historical_commit=BASE,historical_sha256=sha(old.encode()),rejected_candidate=REJECTED_REVIEW,rejected_title_only_sha256=sha(old_title_only.encode()),current_sha256=sha(new.encode()),meaning='Original skill wording was correct:free-kick role4 uses penalties12;goal-kick role5 uses kicking2;role3 also uses12.'),
                    issue_snapshot=dict(path='notes/engine-study/T109/issues-v1.json',captured_utc=issues['captured_utc'],note='Historical snapshot;live labels remain authoritative.'),
                    producer=dict(commit=commit,path=path,sha256=sha(Path(__file__).read_bytes()))),source_paths,guards,support,
               source_commits={p:INTERVENING for p in ['runtime/original_match/match.py','runtime/original_match/README.md']})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args();path=Path(__file__).with_name('T109b-v3.json')
    old=json.loads(path.read_text()) if a.check else None;data=build(old['producer']['commit'] if old else None)
    if a.check:
        assert old==data;validate('T109b',data,(ROOT/'docs/engine-study/audit-integration.md').read_text());print(f'PASS:9integration groups;{len(data["guards"])}literal guards;5titles/4selection skills;3title+8skill/prose negatives;no engine calls')
    else:write_new(path,data);print('wrote immutable integration candidate register;no engine calls')


if __name__=='__main__':main()
