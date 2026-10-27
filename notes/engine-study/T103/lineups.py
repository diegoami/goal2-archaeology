#!/usr/bin/env python3
"""Source-derived lineup/ordering projections with supplied strengths; no engine execution."""
from pathlib import Path
import sys
from common import ROOT,make_ledger,run
sys.path.insert(0,str(ROOT/'notes/engine-study/T98'))
from tables import load_ds


def bench_map(rows):
    result={}
    for slot,natural,strength,available in rows:
        if available and (natural not in result or strength>result[natural][1]):result[natural]=[slot,strength]
    return result


def replacement(starter_strength,bench_strength,played,natural,bench_natural,*,available=True,placement=False,slot=2,found=True):
    if found and (bench_strength>starter_strength or played!=natural and bench_natural==played):return True
    return not available or placement or slot==1 and natural!=0


def incoming_role(outgoing_played,incoming_natural):
    return incoming_natural if any(outgoing_played in g and incoming_natural in g for g in [{5,6},{7,10},{8,11},{12,13}]) else outgoing_played


def quicksort(rows):
    rows=list(rows)
    def sort(lo,hi):
        i,j=lo,hi;pivot=rows[(lo+hi)//2][1]
        while True:
            while rows[i][1]<pivot:i+=1
            while rows[j][1]>pivot:j-=1
            if i<=j:rows[i],rows[j]=rows[j],rows[i];i+=1;j-=1
            if i>j:break
        if lo<j:sort(lo,j)
        if i<hi:sort(i,hi)
    if rows:sort(0,len(rows)-1)
    return rows


def calculations():
    read,_,_=load_ds()
    bench=bench_map([(12,2,90,True),(15,2,90,True),(18,2,100,True),(19,2,120,False),(20,5,200,True)])
    assert bench=={2:[18,100],5:[20,200]}
    assert bench_map([(12,2,90,True),(15,2,90,True)])[2][0]==12
    prefs=[read(0x99a+8*5+i) for i in range(1,read(0x99a+8*5)+1)]
    assert prefs==[1,3,4,7,8,6,5]
    selected=0
    for natural in prefs:
        if natural in {1:12,5:18}:selected={1:12,5:18}[natural]
    assert selected==18
    decisions=[replacement(100,90,2,5,2),replacement(100,90,2,2,2),replacement(100,100,2,2,2),replacement(100,101,2,2,2),replacement(100,90,2,2,2,available=False),replacement(100,90,0,2,2,slot=1)]
    assert decisions==[True,False,False,True,True,True]
    assert [incoming_role(7,10),incoming_role(2,5),incoming_role(12,13)]==[10,2,13]
    # AD8F clears the chosen natural role map, only callsAC67 on outgoing player, not all remaining bench.
    before=bench_map([(12,2,90,True),(18,2,100,True)])
    after=dict(before);after.pop(2);after.update(bench_map([(18,5,70,True)]))
    assert 2 not in after and bench_map([(12,2,90,True),(18,5,70,True)])[2][0]==12
    equal=quicksort([['A',2,2],['B',2,2]])
    assert [r[0] for r in equal]==['B','A']
    # Saved positions must travel with each identity through temporary unavailability sentinel14.
    sorted_rows=quicksort([['A',14,2],['B',1,1],['C',3,3]])
    assert [[r[0],r[2]] for r in sorted_rows]==[['B',1],['C',3],['A',2]]
    assert [read(0xf3a),read(0xf3b),read(0xf3c),read(0xf3d)]==[1,12,11,20]
    return dict(prematch_map={str(k):v for k,v in bench.items()},strict_tie_slot=12,role5_preferences=prefs,last_preference_selected=selected,
                replacement_cases=decisions,incoming_roles=[10,2,13],after_local_map_update={str(k):v for k,v in after.items()},
                remaining_role2_player_ignored_by_map=12,equal_sort=[r[0] for r in equal],restored_identity_roles=[[r[0],r[2]] for r in sorted_rows],
                controls={'reuse-inmatch-last-map':'rejected:equal90 keeps12 rather than15',
                          'choose-best-overall':'rejected:ordered natural preferences can chooseweaker candidate',
                          'never-replace-with-weaker':'rejected:natural-role correction admits100->90',
                          'always-inherit-role':'rejected:7 with natural10 becomes10',
                          'rebuild-entire-map-after-swap':'rejected:role2 remaining12 does not automaticallyreappear',
                          'stable-sort':'rejected:equalA/B becomeB/A'})


def build():
    calc=calculations()
    rows=[
      ('0791:A3DE','Fixture countries/host/decider/reseed;unmanaged side B11F then34E7 thenBD83.', ['9B34/36','7C36','80FC','player+F'],'AI selection/tactics run at setup;managed choices skipped.'),
      ('0791:AC67','Available bench identity maps natural role to strictly strongest377E;tie retains earlier.', ['99A2','player+7','3216/377E'],'Prematch map differs from inmatch C7EB last-slot map.'),
      ('0791:AD8F','Clear selected natural map;swap squadwords;role exceptions sets5/6,7/10,8/11,12/13;outgoing restore+7;AC67 onlyoutgoing.', ['99A2','player+6/+7','CSAD0F..AD6F'],'Role transfer is not universal inheritance;map is locally updated,not fullyrescanned.'),
      ('0791:AFA3','Scan starters1..11;ordered AAE8;strict stronger thennatural-role correction;else availability/placement/keeper fallback.', ['377E','3179','3216','AAE8/A9B8'],'Greedy ordered selection,not global bestXI search.'),
      ('0791:B11F','Clear14-byte benchmap;AC67 slots12..20;AFA3;sort52CC.', ['99A2','country.squad'],'One initial best-per-role construction;choices affectlater candidates.'),
      ('1771:517A','Middle-key recursive quicksort of squadwords;swap parallel savedrole bytes.', ['player+6','parent savedbytes'],'Equal keys can swap;order matters to subsequent first/last scans.'),
      ('1771:52CC','SortXI1..11 andbench12..20 separately;managed unavailable temporaryrole14;restore peridentity.', ['0F3A/0F3C','0B77','3216'],'Does not move benchintoXI or change restored roles by itself.'),
      ('1771:53E8','Middle-pivot poolword quicksort with parallel byte swaps.', ['A927','parent savedroles'],'Raw pool indices differ from one-based squad indices;ties not stable.'),
      ('1771:5532','Currentmanager80 poolwords;save positions,zeroidentity sentinel14,quicksort,restore.', ['6D18','game+1','pool_indices','player+6'],'Empty-slot sorting differs from managed squad availability sorting.'),
    ]
    examples=[
      dict(id='strict-bench-tie',inputs={'bench':[[12,2,90],[15,2,90],[18,2,100]],'available':True},steps=['12first','15equalnotreplace','18strictgreater'],prediction={'natural2_slot':18,'tie_only_slot':12},limits='Supplied377E values,not engine/skill calculations;inmatch C7EB hasdifferentrule.'),
      dict(id='weaker-natural-correction',inputs={'starter_strength':100,'bench_strength':90,'starter_played':2,'starter_natural':5,'bench_natural':2},steps=['strictstrongerfalse','starterawayfromnatural andbenchmatchesplayed','AD8F admitted'],prediction={'replace':True,'incoming_role':2},limits='AAE8 candidate assumedeligible/available;no generalbest-XIclaim.'),
      dict(id='map-depletion',inputs={'bench_role2':[[12,90],[18,100]],'chosen_slot':18,'outgoing_natural':5,'outgoing_strength':70},steps=['initialrole2->18','AD8Fclearsrole2','outgoingnowslot18 updatesrole5only','remainingrole2slot12notrescanned'],prediction={'map':{'5':[18,70]},'role2_entry_present':False},limits='Source-conditioned greedy frontier;naturalincidence andmatchqualityimpactnotestablished.'),
      dict(id='sort-carries-identity',inputs={'records':[['A',14,2],['B',1,1],['C',3,3]],'columns':'identity,temporarykey,savedrole'},steps=['partitionbytemporarykey','swapidentityandsavedbyte','restoreownrole'],prediction={'identity_roles':calc['restored_identity_roles'],'equal_two_order':['B','A']},limits='Smallpartitionexample,notfull20/80-rosterorABIexecution.'),
    ]
    return make_ledger('T103b',Path(__file__).resolve(),['The greedy selection sequence','Role transfer and candidate depletion','Sorting and visible formation','Worked checks and limits'],rows,examples,calc,['setup','selection'],addresses=['0791:AAE8','0791:A9B8','0791:C7EB','1771:377E','1771:3179','1771:3216'])


if __name__=='__main__':run('T103b',build)
