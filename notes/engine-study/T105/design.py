#!/usr/bin/env python3
"""Design/source arithmetic only. This file cannot construct or execute a game engine."""
from pathlib import Path
from common import ROOT,ledger,run

IMAGE_SHA='e0afff6751747233f6ab8b9ba73dab0790b7509f15257ed7ae24f528b935657d'
MEMORY_SHA='87400f6a866e0798f61a9f3ab3bfcaa322469fa6b238b0061f1b7ab2b6a3f979'


def probes():
    launch=[
      dict(id='launch-zero',target=[0,0],expected={'velocity':[0,-1],'timer':2,'event':6,'projected':[0,-2]},alternative='zero displacement stays idle'),
      dict(id='launch-small',target=[1,0],expected={'velocity':[1,-1],'timer':2,'event':6,'projected':[2,-2]},alternative='zero secondary delta always means zero secondary velocity'),
      dict(id='launch-diagonal',target=[7,14],expected={'velocity':[1,2],'timer':7,'event':7,'projected':[7,14]},alternative='divide every timer by two, giving10 and projection10/20'),
    ]
    wall=[
      dict(id='wall-near',spot=[0,25],holder_direction=1,expected={'targets':[[2,30],[1,30],[0,30],[-1,30],[-2,30]]},alternative='far-wall formula applies already below26'),
      dict(id='wall-far-positive',spot=[0,26],holder_direction=1,expected={'targets':[[-3,-28],[-3,-27],[-3,-26],[-3,-25],[-3,-24]]},alternative='normalise far-wall y to the positive spot side'),
      dict(id='wall-far-negative',spot=[0,-26],holder_direction=-1,expected={'targets':[[-3,28],[-3,29],[-3,30],[-3,31],[-3,32]]},alternative='mirror both axes of positive-side wall, including x'),
    ]
    for p in launch:
        p.update(routine='0791:34C1',intervention={'ball':[0,0],'event_argument':6,'holder_slot':2,'receiver_slot':2,'keeper':False,'skill_duration_branch':False},
                 unit='one complete target call per backend',reachability='Deliberately edited live geometry; zero/small target natural incidence unresolved #529.',
                 control='One altered-rule candidate is a falsifier, never an oracle expectation.')
    for p in wall:
        p.update(routine='0791:7621',intervention={'defending_relative_slots':[7,8,9,10,11],'normal_direction':True,'defending':True,'abs_y_minus_abs_x_gt10':True},
                 unit='five complete target calls per backend, one for each defending relative slot',reachability='Edited restart geometry with valid side/direction/slot bindings; natural far-wall incidence unresolved #540.',
                 control='Reject changed boundary/sign/axis alternative; check guards with a separate non-wall record.')
    return launch+wall


def local_gate_counts(energy):
    """Enumerate source LCG starting words, not an engine/routine or match."""
    bound=energy//2;off=on=0
    for seed in range(65536):
        first=(seed*0x7abd+0x1b0f)&65535
        second=(first*0x7abd+0x1b0f)&65535
        off+=first*bound//65536==0
        on+=first<32768 or second*bound//65536==0
    return [off,on]


def observer_projection(events):
    """Design-only activation matching; actual native observer is not implemented here."""
    active={};pending=set();counts={'opportunities':0,'actions':0,'completions':0}
    for frame,activation,site in events:
        key=(frame,activation)
        if site=='5049':active[frame]=activation
        elif active.get(frame)!=activation:continue
        elif site=='52DD':pending.add(key);counts['opportunities']+=1
        elif site=='5326' and key in pending:counts['actions']+=1
        elif site=='532C' and key in pending:pending.remove(key);counts['completions']+=1
        if site=='return':pending.discard(key);active.pop(frame,None)
    return counts


def calculations():
    observed=observer_projection([(100,1,'5049'),(100,1,'532C'),(100,1,'return'),(100,2,'5049'),(100,2,'52DD'),(100,2,'5326'),(100,2,'532C'),(100,2,'return'),(100,3,'5049'),(100,3,'532C')])
    assert observed=={'opportunities':1,'actions':1,'completions':1}
    counts={str(e):local_gate_counts(e) for e in [16,32]}
    assert counts=={'16':[8192,36866],'32':[4096,34815]}
    assert counts['16'][1]!=36864 and counts['32'][1]!=34816
    assert 36866-8192==28674 and 34815-4096==30719
    cases=probes();assert len(cases)==6
    assert sum(1 if p['routine'].endswith('34C1') else 5 for p in cases)*2==36
    assert [p['expected']['timer'] for p in cases[:3]]==[2,2,7]
    assert cases[1]['expected']['velocity']!=[1,0] and cases[4]['expected']['targets'][0]!=[-3,28]
    return dict(observer_shared_exit_projection=observed,probe_cases=cases,reference_and_port_target_calls=36,local_gate_finite_seed_counts=counts,
                local_quick_increment_counts={'16':28674,'32':30719},finite_seed_denominator=65536,
                contexts=[dict(id='A',fixture=[7,19,21,1],managed=7),dict(id='B',fixture=[19,7,21,1],managed=7)],
                arms=[dict(id=f'E{e}-Q{q}',energy=e,tactic2=bool(q)) for e in [16,32] for q in [0,1]],
                intervention_boundary={'country_team2':'before Match construction through countries record list','own_enable2':'clear mask32 on each nonzero managed squad identity before construction','energy':'one declared F098 entry write after common setup and captain seed, signed-positive managed squad records only','other_fields':'preserve natural/played roles,ability,profile,form,fitness,status,all other tactics and caches'},
                controls={'seed-rebuilds-table':'rejected:late seed override does not rerun2648',
                          'pre_match-public-answer':'rejected:no public pre_match decision in DECIDED_AT_MENU',
                          'energy-before-setup-is-isolated':'rejected:opponent BD03/BD83 can react before kickoff',
                          'independent-coin-formula-exact':'rejected:finiteLCG on counts36866/34815 differ from36864/34816',
                          'all-six-probes-one-call-each':'rejected:wall case needs five records,36 reference/port calls',
                          'completed-Match-omits-B7FA':'rejected:Match._advance calls PLAYER_UPDATE before _finish',
                          'live-score-always-fixture-goals':'rejected:PK tally and quick scratch/rollback phases differ'})


def build():
    calc=calculations()
    decisions=[
      ('provenance','Use hash-verified published E006 image and original registered build. Friendly7/19,index21 and its side reversal,managed7; common input snapshot per block.', 'Existing kit/family source gives reproducible legal API inputs without collecting new private/genuine keys.','Both fixtures are constructed; reversal changes host/cursor and is not evidence of a naturally played calendar fixture.'),
      ('interventions','Four arms E16/32 x team2off/on. Clear own2enable on all managed squad identities in common constructor records; set team2 per arm; declare energy edits at F098 after common setup.', 'Freeze AI lineup/tactic setup across energy arms; avoid pretending a pre-setup energy edit is a pure live-energy intervention.','Synthetic research write at actual boundary; read back every arm before first sweep, forbid silent rebind/reseed/fitness refill.'),
      ('seed-boundary','Match seed enters at managed captain prompt after2648; freeze index/year,table bytes/cursor,setup snapshot and actual seed; same seed only pairs initial state.', 'Setup uses index*(year+1),generates255 table bytes and sets cursorsecond country; optional main override does not undo AI or table setup.','Treatment paths consume conditional draws; trace divergence rather than claim later synchronized draws.'),
      ('instrumentation','Passive native52DD opportunity,5326 action,532C counts only after52DD in the SAME managed5049 activation,with entry nonce/frame and pending cleared on exit; phase-aware Match/fixture/board outcomes and before/after player state.', 'Connect observed gate opportunities to the exact5049 branch and avoid scorer-commentary/statistic conflation.','Existing runner needs a declared F098 edit/passive observer extension; validate noninterference and hook reach before measurements; port-only raw hooks unsupported.'),
      ('probes','Six fixed direct34C1/7621 cases in calculations; original code and full registered port,real nested callees,no stubbing. Independent literal outputs,ABI return/SP/completion and source fingerprints.', 'Corroborate small/zero launch and wall boundary/sign mechanisms with few calls,without rerunning broad fidelity.','Synthetic fields and guards need complete immutable construction manifest before first call; does not establish natural incidence.'),
      ('batch','Original-backed watched-friendly four-arm sensitivity,PlayOn policy,default substitutions/captain,delay0; two fixed contexts. Final seeds,counts,caps and inference in T105b.', 'Existing original path is inexpensive relative to all-port full matches; current strict T77 evidence and selected T106 comparisons remain distinct.','No standalone/default change and no T79 substitution. No port-only sensitivity matches in first batch; later use requires accepted standalone fidelity and separate cost decision.'),
      ('controls','Preflight exact inputs/cohort/readbacks,baseline XI eligibility,no-op edit and passive observer witnesses,repeated fixed cases; expected literal/altered-rule separation.', 'Completion alone cannot show the intended bit/energy intervention reached the gate or that instrumentation did not alter execution.','Failures/refusals/zero opportunities require explicit disposition,no replacement seeds or hidden task weakening.'),
      ('deferrals','Defer broad formation rankings,many attributes,natural rare-path frequency,unavailable PK cursor,shot-tail probe and full port sensitivity. Fix #561 documentation qualifiers now.', 'Local source answers already exist; choose a small useful corroboration and bounded exploratory net effect before more spending.','Deferred questions remain open with issues; no original-bug fix or spec promotion.'),
    ]
    examples=[dict(inputs={'energy':16,'starting_seed_words':'all65536','branch':'5049 local gate only'},expected={'off':8192,'on':36866,'difference':28674},limits='Source enumeration at a fixed gate,not normal opportunity distribution or full-match effect;LCG correlation retained.'),
              dict(inputs={'probe_cases':6,'wall_records_per_case':5,'backends':2},expected={'reference_and_port_target_calls':36},limits='Setup,negative/repeat invocations also consume the later cap;not just sixcalls.'),
              dict(inputs={'fixture_goals':[2,2],'fixture_result':0,'working_PK_tally':[3,2]},expected={'regulation_plus_ET_goals':[2,2],'winner_side':0},limits='Representation rule only;first batch uses friendlykind1 and cannot run PK.'),
              dict(inputs={'energy_edit_time':'F098 after common setup','team2':True},expected={'setup_AI_frozen_across_energy_arms':True,'own2_enable':False,'fitness_unchanged':True},limits='Readback assertions required in future implementation;this design does not execute a hook.')]
    sources=['runtime/original_match/match.py','runtime/original_match/image.py','runtime/original_match/assets.py','runtime/original_match/port/setup.py','runtime/original_match/port/ball.py','runtime/original_match/port/restarts.py','experiments/E036-match-port/families/F40.json','experiments/E036-match-port/families.py','experiments/E036-match-port/image_sources.py','experiments/E036-match-port/records.py','tests/test_port_ball.py','tests/test_port_restarts.py']
    artifacts=['notes/engine-study/T102/T102b-v1.json','notes/engine-study/T104/T104a-v1.json','notes/engine-study/T103/T103a-v2.json','notes/engine-study/T104/T104e-v1.json']
    return ledger('T105a',Path(__file__).resolve(),['Questions, provenance and interventions','Selected direct probes','The four-arm match design','Instrumentation, controls and deferrals'],[dict(topic=t,decision=d,why=w,limits=l) for t,d,w,l in decisions],examples,calc,['0791:2648','0791:34C1','0791:7621','0791:5049','0791:F098','0791:F1F6','0791:B7FA','214B:0688','214B:06FA'],sources,artifacts)


if __name__=='__main__':run('T105a',build)
