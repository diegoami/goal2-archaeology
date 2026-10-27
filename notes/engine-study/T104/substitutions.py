#!/usr/bin/env python3
"""Source-derived substitution guards/bindings; no original/port engine execution."""
from pathlib import Path
import sys
from common import ROOT,make_ledger,run

sys.path.insert(0,str(ROOT/'notes/engine-study/T98'))
from tables import load_ds,s8,s16


def allowed(permission,budget,replaying=False):return permission and budget>0 and not replaying


def refusal(first,second,bench_available=True,sent_off=False):
    if (first<=11)==(second<=11):return 'same-block'
    if not bench_available:return 'incoming-unavailable'
    if sent_off:return 'outgoing-sent-off'
    return None


def pairwise_sort(rows):
    result=list(rows)
    for i in range(len(result)):
        for j in range(i+1,len(result)):
            if result[j][1]<result[i][1]:result[i],result[j]=result[j],result[i]
    return result


def auto_due(remaining,performance,budget=1,energy=32,status=0,slot=2):
    return budget!=0 and 2<=slot<=11 and not status&32 and s8(energy)>0 and 1<remaining<35 and s16(performance)<90-remaining


def valid_roles(roles,available,*,in_match=True,empty=False):
    if empty or (not in_match and not all(available)):return False
    counts=[sum(r==p and ok for r,ok in zip(roles,available)) for p in range(14)]
    return counts[0]==1 and all(n<=3 for n in counts[1:])


def calculations():
    read,_,_=load_ds()
    assert [allowed(True,2),allowed(False,2),allowed(True,0),allowed(True,2,True)]==[True,False,False,False]
    assert [refusal(3,15),refusal(3,8),refusal(12,18),refusal(3,15,False),refusal(3,15,True,True)]==[
        None,'same-block','same-block','incoming-unavailable','outgoing-sent-off']
    assert ((0-1)&255)==255  # primitive edge, not a normal admitted UI operation
    bench_map={}
    for slot,natural in [(12,2),(15,7),(18,2)]:bench_map[natural]=slot
    assert bench_map[2]==18
    prefs=[read(0x99a+8*2+i) for i in range(1,read(0x99a+8*2)+1)]
    assert prefs==[2]
    selected=0
    for natural in prefs:
        if natural in bench_map:selected=bench_map[natural]
    assert selected==18 and selected!=12
    # AI copies outgoing played role2; managed swap retains incoming played role7.
    assert [2,7]==[2 if ai else 7 for ai in [True,False]]
    old_marks=[205,0]
    managed_marks=[old_marks[1],0]  # clear outgoing field before swap
    ai_marks=[old_marks[1],old_marks[0]]
    assert managed_marks==[0,0] and ai_marks==[0,205]
    rows=[('A',14),('B',14),('C',1)]
    ordered=pairwise_sort(rows)
    assert [r[0] for r in ordered]==['C','B','A']
    assert [r[0] for r in sorted(rows,key=lambda r:r[1])]==['C','A','B']
    role=4;profile=5;peak=25;natural=2;index=1
    foot=read(0xe60+14*read(0xe7c+index%3)+natural);two=profile+peak==30
    bench_eligible=two or foot==1
    placement=(foot==0 and role in [4,8,11]) or (not two and foot!=0 and role in [3,7,10])
    assert [foot,two,bench_eligible,bool(placement)]==[0,True,True,True]
    due=[auto_due(34,55),auto_due(35,55),auto_due(2,88),auto_due(2,87),auto_due(34,10055)]
    assert due==[True,False,False,True,False]
    roles=[0,2,2,3,4,7,8,9,13,13,13];all_ok=[True]*11
    assert valid_roles(roles,all_ok)
    too_many=roles.copy();too_many[7]=13
    assert not valid_roles(too_many,all_ok)
    missing=all_ok.copy();missing[1]=False
    assert valid_roles(roles,missing) and not valid_roles(roles,missing,in_match=False)
    assert not valid_roles(roles,all_ok,empty=True)
    assert 56+2*2==60 and 56+2*7==70 and (60+2*7)!=70
    return dict(managed_admission=[True,False,False,False],bench_natural_map=bench_map,centre_back_preference=prefs,
                selected_bench=selected,ai_managed_incoming_roles=[2,7],managed_ai_mark_pairs=[managed_marks,ai_marks],
                pairwise_order=[r[0] for r in ordered],stable_sort_control=['C','A','B'],
                foot_case={'foot':foot,'two_footed':two,'bench_eligible':bench_eligible,'placement_flag':int(placement)},
                performance_window_cases=due,captain_cache_intermediate_final=[60,70],
                bind_effects={'incoming_energy':12,'incoming_performance':10055,'activity':0,'run_direction':5,'state_timer':0,
                              'initial_cached_extra':56,'after_leadership4':64,'budget2_after':1,'snapshot_request':1},
                controls={'first-bench-role-wins':'rejected:12 instead of18','stable-sort-replacement':'rejected:unavailableA/B order differs',
                          'copy-role-on-managed-swap':'rejected:incoming7 retained,not2','unify-foot-predicates':'rejected:eligible two-footed left player still hasplacement1',
                          'inclusive-performance-cutoff':'rejected:performance88 atremaining2 does not qualify',
                          'add-captain-without-rebind':'rejected:74 instead of70'})


def build():
    calc=calculations()
    rows=[
        ('8062','At stoppage/minute:AI performance/window scan withbudget;managed notice/menu under request,keeper/time/budget gates.', ['831B','player+12/+E/+10','9B3A/9B40/9B41'],'A request,permission to select,and completed swap are separate states.'),
        ('A260','Bind slot to country squad identity;initial manager+32 cache and placement flag,no energy write.', ['pitch+6/+D/+11/+13','9B34','0AA7','3179'],'Cached values refresh at binding rather than every persistent-record edit.'),
        ('A2E6','Bind,initialise point/old point,colours/offsets,timer0,activity0 and direction5.', ['0644','pitch+0/+2/+5/+B/+10/+14/+F'],'Initialises live record without refilling incoming player energy/fitness.'),
        ('A920','Resolve player through own country to lastmatching first-eleven slot plus sidebase;0 ifabsent.', ['player+0','country.squad','0668/9B36'],'Player identity and pitch address stay distinct.'),
        ('A9B8','Available bench maxcompatibility grade by outgoing position andnatural role,halved for non-two-footed flank mismatch;strict greater.', ['08D5','player+7','3041/3088'],'Compatibility fallback is not a universal highest-ability/keeping selection.'),
        ('AAE8','Walk outgoing-role preference table,read last available natural-role map;flank gate,two-foot exemption;last passing preference wins.', ['099A','99A2','player+6/+7','3041/3088'],'Role/foot order can dominate quality ratings in automatic replacement.'),
        ('C5DC','Mark outgoing substituted off,rebind incoming/reset performance,AI own tactics rederive,preserve old point,captain placeholder around230C,budget-- andsnapshot.', ['player+10/+12/+F','9B07/9978','9B3A/9B55','230C'],'One substitution crosses persistent,live,cache,identity and continuation state.'),
        ('C7EB','Scan available bench12..20 into natural-role map,later slots overwrite earlier.', ['99A2','country.squad','player+7','3216'],'Map keeps one slot perrole,not a scored list.'),
        ('C88D','Zero-budget energy-zero outgoing routes to removal;otherwise choosebench/fallback,copy outgoing playedrole,swapassociated fields andC5DC.', ['9B3A','player+E/+6','AAE8/A9B8','C48D'],'Normal callers supply the allowance protocol;primitive budget decrement has no self-guard.'),
        ('DE27','Pane-aware cursor:one-based squad index orraw pool index.', ['0C1B','parent pane','DDCB'],'UI coordinate is not a persistent player ID.'),
        ('DE51','Return pointer to country squad word orpool_indices raw-index word.', ['country.squad','pool_indices','pane'],'Pointer/base/index conventions differ between panes.'),
        ('E022','Two-mark managed swap rejects same block,incomingunavailable,outgoingred;clear outgoing marking,swapwords/form,refresh thenclearrequest.', ['0C1B','9A3E/9B07','C5DC','9B40'],'Managed swap retains incoming played role rather than AI copy.'),
        ('E2A0','Choose slot hint screen by squadcursor<=11 orbench.', ['0C1B','4840/4720/4740'],'Presentation describes current mode;it does not itselfauthorise a swap.'),
        ('E44F','Inmatch Enter commits onlyoutside replay withpermission andbudget;otherwise requesttoggle. Position/tactic edits differ;pool exchange isout-of-match.', ['0C1F/0C20','9B41/9B3A/9B40','E022'],'UI gate supplies preconditions absent fromlower-level primitives.'),
        ('E949','Managed side sets manager context andopensE44F;unmanaged routeopens1771:50F1 team view.', ['country+2E','game+1','E44F/1771:50F1'],'Controller context matters for which selection operations canrun.'),
        ('EA09','Validate managed elevens:empty/ineligible prematch,available keeper count andmax3 forroles1..13;restoreparent context.', ['country.squad','3216','player+6','0C1F'],'Play gate includesrole13;unavailable inmatchrecords handled differently fromprematch.'),
    ]
    rows=[('0791:'+a,m,f,e) for a,m,f,e in rows]
    examples=[
        dict(id='managed-substitution',inputs={'outgoing_slot':3,'bench_slot':18,'budget':2,'permission':1,'incoming_energy':12,'incoming_played_role':7,'outgoing_played_role':2},
             steps=['inmatchnonreplayE44F admission','E022 block/availability/red checks','swapcountry/form/marking fields','C5DC oldstatus3,rebind,performance10055,activity0,no energyrefill','230C sort/cache/postrefresh,budget1,snapshotrequest'],
             prediction={'incoming_role':7,'energy':12,'performance':10055,'budget':1,'snapshot_request':1},
             limits='Partial source transaction;full roster-dependent sort,drawing andmenu inputs not executed. Actual incoming pitch index canchange on resort.'),
        dict(id='ai-centre-back-map',inputs={'outgoing_role':2,'available_bench_roles':[[12,2],[18,2]],'preference_table':[2]},
             steps=['C7EB role2 overwrittenbyslot18','AAE8 useslastmap result','C88D copiesplayed2 before refresh'],
             prediction={'bench_slot':18,'incoming_played_role':2},limits='No quality comparison inthismap route;available/unique binding assumptions. Fallbacks andfull AI decision policy separate.'),
        dict(id='foot-rule-difference',inputs={'player_index':1,'natural_role':2,'profile':5,'peak_age':25,'new_played_role':4},
             steps=['foot tablegivesleft0;two-foot predicate true','bench filter accepts two-footed','3179 left/right-flank branchstillreturns1 on binding'],
             prediction=calc['foot_case'],limits='Range-valid source case,not observed naturalfrequency. Do not unify two different compatibility predicates.'),
        dict(id='captain-menu-refresh',inputs={'initial_extra':56,'temporary_placeholder_leadership':2,'new_selected_leadership':7},
             steps=['C5DC placeholder during230C canyieldintermediate60','normal ED8A exitcalls230C again','A260 resets56 before20E3 adds14'],
             prediction={'intermediate':60,'after_normal_exit':70},limits='Source call-order projection,not allraw direct-entry/reentrantcontexts. Negative audit ofan immediate cache-bug suspicion,not a newmatch proof.'),
    ]
    return make_ledger('T104c',Path(__file__).resolve(),['Admission and identity layers','Automatic versus managed replacement','The rebind, cache and sort transaction','Worked checks and remaining boundaries'],
                       rows,examples,calc,['discipline','selection','menus','frame','attributes','positioning'],
                       addresses=['0791:230C','0791:20E3','0791:ED8A','1771:3179','0791:0691','0791:C48D'],
                       sources=['static/goal-exe/calls.tsv'])


if __name__=='__main__':run('T104c',build)
