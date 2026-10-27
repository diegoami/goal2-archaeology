#!/usr/bin/env python3
"""Frozen sampling/cost design from retained records; no engine or match execution."""
import json,math,random,statistics
from pathlib import Path
from common import ROOT,ledger,run

TIMING_FILES=['experiments/E036-match-port/out/T57/reference.jsonl','experiments/E036-match-port/out/T57/trial-all-20261017.jsonl','experiments/E036-match-port/out/T57/rerun.jsonl','experiments/E036-match-port/out/T77/all-actions-1-40090586451/all-actions-1.jsonl']
EXPECTED_SEEDS={
 'A':[19516,45597,29364,29966,32093,25195,20121,5461,34317,21250,41924,11439,15368,7679,62584,62568],
 'B':[21433,28214,60620,19017,24009,22008,28455,32509,14616,11233,56722,59893,14753,12441,5270,45020]}
ARMS=['E16-Q0','E16-Q1','E32-Q0','E32-Q1']


def interaction(values):
    assert len(values)==4 and all(v in [0,1] and v is not None for v in values)
    return (values[1]-values[0])-(values[3]-values[2])


def timings(path):
    rows=[json.loads(line) for line in (ROOT/path).read_text().splitlines() if line.strip()]
    assert all(r.get('error') is None for r in rows)
    f40=[r for r in rows if r['id'].startswith('F40/')]
    return dict(path=path,n=len(rows),kits=sorted({r['kit'] for r in rows}),F40_n=len(f40),F40_cpu_median=statistics.median(r['cpu_s'] for r in f40),F40_cpu_max=max(r['cpu_s'] for r in f40),cpu_median=statistics.median(r['cpu_s'] for r in rows),cpu_max=max(r['cpu_s'] for r in rows),cpu_sum=sum(r['cpu_s'] for r in rows),wall_median=statistics.median(r['wall_s'] for r in rows),wall_max=max(r['wall_s'] for r in rows))


def calculations():
    seeds={c:random.Random(10520261027+i).sample(range(65536),16) for i,c in enumerate(['A','B'])}
    assert seeds==EXPECTED_SEEDS and not set(seeds['A'])&set(seeds['B'])
    schedule=[]
    for block in range(16):
        for ci,context in enumerate(['A','B']):
            order=ARMS.copy();random.Random(10500000+2*block+ci).shuffle(order)
            for arm in order:schedule.append(dict(context=context,block=block+1,seed=seeds[context][block],arm=arm))
    assert len(schedule)==128 and len({(r['context'],r['seed'],r['arm']) for r in schedule})==128
    witnesses=[dict(context=c,seed=seeds[c][0],arm=a,observer=False) for c in ['A','B'] for a in ['E16-Q0','E32-Q1']]
    assert len(witnesses)==4
    timing_rows=list(map(timings,TIMING_FILES));old=timing_rows[0];new=timing_rows[-1]
    assert [r['cpu_max'] for r in timing_rows[:3]]==[21.072,28.708,17.619]
    assert all(r['kits']==['2'] for r in timing_rows[:3])
    assert old['n']==62 and new['n']==74
    assert [old['cpu_median'],old['cpu_max']]==[14.4,21.072]
    assert [new['cpu_median'],new['cpu_max']]==[1549.8785,2851.377]
    median_seconds=132*old['cpu_median'];max_seconds=132*old['cpu_max']
    assert abs(median_seconds-1900.8)<1e-8 and abs(max_seconds-2781.504)<1e-8
    width=4*math.sqrt(math.log(2/(0.05/2))/(2*16))
    assert abs(width-1.4802071873007983)<1e-12
    need=math.ceil(16*math.log(80)/(2*0.1**2))
    assert need==3506 and need*2*4==28048
    context_sum=math.floor(16*width)+1;aggregate_sum=math.floor(32*width)+1
    direct=math.sqrt(math.log(40)/4);direct_n=math.ceil(4*math.log(40)/0.01)
    assert (context_sum,aggregate_sum,direct_n)==(24,48,1476)
    assert 1.4375<=width<1.5 and 47/32<=width<48/32
    assert [interaction(v) for v in [[0,1,0,0],[1,0,0,1],[1,1,1,1]]]==[1,-2,0]
    try:interaction([0,1,None,0])
    except AssertionError:pass
    else:raise AssertionError('missing outcome imputed')
    return dict(seed_sampler='separate random.Random(10520261027+i).sample(range(65536),16), i=A0/B1; no resampling',seeds=seeds,schedule=schedule,noninterference_witnesses=witnesses,
                primary=dict(outcome='indicator managed country scores at least one retained fixture goal in the friendly',arm_order=ARMS,block_interaction='(E16Q1-E16Q0)-(E32Q1-E32Q0)',block_range=[-2,2],contexts=2,blocks_per_context=16,planned_cells=128,context_weights=[0.5,0.5]),
                pre_execution_owner_decision='T107 spending/design must be explicitly decided under#571 before execution;no bound or cap changed here',
                precision=dict(minimum_observed_context_sum=context_sum,minimum_observed_aggregate_sum=aggregate_sum,alternative_direct_aggregate_halfwidth=direct,alternative_direct_blocks_for_point1=direct_n,alternative_adopted=False,context_alpha=0.025,simultaneous_alpha=0.05,hoeffding_halfwidth=width,aggregate_halfwidth=width,target_halfwidth=0.1,required_blocks_per_context=need,required_matches=28048),
                timing_sources=timing_rows,current_kit_at_design='4',all_retained_original_max_projection=132*max(r['cpu_max'] for r in timing_rows[:3]),projected_original_cpu_s={'historical_median':median_seconds,'historical_max_each':max_seconds},
                caps={'T106':{'top_level_invocations_including_setup_control_repeat':60,'ordinary_target_calls':36,'cpu_s':600,'wall_s':900,'one_invocation_cpu_s':5,'one_invocation_wall_s':10,'workers':1},
                      'T107':{'primary_matches':128,'witness_matches':4,'total_match_attempts':132,'cpu_s':3600,'wall_s':5400,'one_match_cpu_s':45,'one_match_wall_s':60,'workers':1,'calibration_primary_matches':8},'combined_cpu_s':4200,'combined_wall_s':6300,'additional_all_port_full_matches':0},
                controls={'arm-count-as-N':'rejected:128cells are32seed-context blocks,not128 independent interactions',
                          'reuse-seeds-as-extra-context-replicates':'rejected:contexts are fixed,not random draws from footballpopulation',
                          'independent-marginal-CI':'rejected:compute block interactions first,keep allfour arms together',
                          'precision-0.1-with16blocks':'rejected:conservative halfwidth1.4802;need3506blocks/context for0.1',
                          'impute-failed-match-zero':'rejected:Noneoutcome fails;report incomplete ratherthan salvageprimaryestimate',
                          'port-runtime-equals-original':'rejected:retained medians1549.8785vs14.4,withhost/profile qualifications',
                          'add-batches-until-significant':'rejected:fixedcount orresource/validitystop,noeffect-basedextension',
                          'unaccounted-wall-records':'rejected:36normal targetcallsplussetup/controls/repeatsallwithin60'})


def build():
    calc=calculations()
    rows=[
      ('seed-blocks','Freeze16 uniform-without-replacement mainseed words percontext from separate named sampler streams; exactlists/schedule inledger,actualsetsdisjoint,noresampling.', 'Independent unit is a seed/context block carrying four potential outcomes; different contexts remain fixed strata.','PRNG-generated Monte Carlo design targets each fixed context’s finite seed universe,not independent football fixtures or synchronized laterdraws.'),
      ('estimands','PrimaryY=managedscored>=1 retainedfriendlygoal. I=(Y16Q1-Y16Q0)-(Y32Q1-Y32Q0);equalmeanA/B. Othergate/statistic contrasts exploratory.', 'One prespecified boundedprimarynet-effect interaction;source localgate directiondoesnot dictatewholematchgoals.','Friendlyscenario/liveenergyinterventiononly;no claim about naturally generated condition,allcountries,formationrank ornewstandaloneengine.'),
      ('uncertainty','Compute16blockI values/context; finite-uniform-seed Hoeffding range4 bound at97.5% percontext;clip[-2,2],averagecontextintervals forsimultaneous95% target. ReportrawSD/counts asdescriptive.', 'Preservepairedblock covariance;unionboundcoversbothcontextswithoutassumingcontextsareindependentnewfixtures.','Nominal samplingcoverageassumesuniformseedselection;deterministicPRNG/pseudorandomsimulation limitations explicit. Halfwidth1.4802 requires contextsum>=24/32 or aggregatesum>=48/64 to excludezero;spending decision#571 remains before execution;noequivalenceor0.1-effectclaim.'),
      ('multiplicity','Oneprimaryinteraction;contextintervalsfamilyalpha0.05;allshots/goals/possession/actionratios/playeroutcomes labelledexploratory withno confirmatorypvaluesorbest-settingselection.', 'Avoid selectingthemostfavourableofmanycorrelatedoutcomes orstatisticaltargets.','Anynewcontrast/batch requiresseparatelypreregisteredfollow-up;descriptivepatterns arenotconfirmedcausalmechanisms.'),
      ('stopping','Fixed128primary+4witnessmax;first8primarytimingscalibrate blind to outcomes. Stopbeforefurtherlaunch if132*max(first8cpu)>3600;stoponvalidity/noninterferencefailure orhardcaps. Nostatisticalpeekingextension.', 'Cap cost with observableruntimeevidenceandpreservefailed/interruptedattempts.','Runtime/validitystops canbeinformative;incompleteprimarydataset getsnofullplanned primaryestimate orequivalenceclaim.'),
      ('compute','T106<=60top-levelcalls inclsetup/control/repeat,600CPUs/900walls;T107<=132attempts,3600CPUs/5400walls;oneworkerthroughheavy. Combined4200CPUs/6300walls;zeroadditionalfull-portmatches.', 'Allthree retained kit2 originalruns max17.619..28.708 gives132 upper projection2325.708..3789.456s;currentkit4 feasibility is unmeasured and gated by calibration;74all-port med1549.8785 makes duplicationexpensive.','Differenthosts/profile/contention;projectionsnotnewbenchmarks. IncludechildCPU/initialisation andfailedattempts;wall excludesonlyqueuedslotwait recordedseparately.'),
      ('reproducibility','Fourfixedwitnesses rerunsamefirstseed/context andarm withpassiveobserverdisabled,activeeditretained;compareinputs/results/draws/strictmemoryexceptobserveronlyoutputs. Archiveeveryattempt,newexclusiveoutputs.', 'Separatethepassiveobservereffectfromtheactualinterventionandtestdeterminismwithoutopportunisticseedchoice.','Noport-onlysensitivityorneworiginalkeys. Source/inputidentitydrift refusesbeforelaunch;oldrawoutputsneveroverwritten.'),
      ('completion','Require128uniquecompleteprimarycells,all4witnesses,validphase/inputs/return,actualgateobservations andresourceaccounting;explicitzeroopportunitiesandrefusals. PublishN/effects/intervals/failures/deviationsfirst.', 'Preventduplicates,partialblocks,silentdropsortimeoutsfrommanufacturingprecision.','Failurepublishesaspartial/inconclusive;neverreplacewithquickmode,mock,anotherfixtureorweakenedassertion. T106/T107implementationstillneedsexecutablecontractsafterES-R2.'),
    ]
    examples=[dict(inputs={'binary_outcomes_E16Q0_Q1_E32Q0_Q1':[0,1,0,0]},expected={'block_interaction':1},limits='Synthetic arithmetic example,notnewmatchdata.'),
              dict(inputs={'blocks_per_context':16,'contexts':2,'arms':4,'witnesses':4},expected={'primary':128,'independent_blocks':32,'attempt_cap':132},limits='Fourarms/ticks/eventsnotindependentreplicates;contextsarenotrandomfootballsample.'),
              dict(inputs={'range':4,'n':16,'alpha_per_context':0.025},expected={'conservative_halfwidth':calc['precision']['hoeffding_halfwidth'],'blocks_for_halfwidth0.1':3506},limits='Samplingboundunderuniformseeddesign,notpowerguarantee;ordinarysmallneteffects likelyinconclusive.'),
              dict(inputs={'retained_original_cpu_median':14.4,'retained_original_cpu_max':21.072,'matches':132},expected=calc['projected_original_cpu_s'],limits='Historicalcostprojectiononly;freshcalibrationandhardcaparemandatory,noengineexecutionhere.')]
    return ledger('T105b',Path(__file__).resolve(),['Frozen seed blocks and estimands','Precision and multiplicity','Compute caps and stopping','Completion, reproducibility and delivery'],[dict(topic=t,decision=d,why=w,limits=l) for t,d,w,l in rows],examples,calc,['0791:2648','0791:5049','0791:F098'],['runtime/original_match/match.py','experiments/E036-match-port/family.py','experiments/E036-match-port/records.py',*TIMING_FILES],['notes/engine-study/T105/T105a-v2.json','experiments/E036-match-port/out/T77/main-integrated-final-audit-1.json'])


if __name__=='__main__':run('T105b',build)
