#!/usr/bin/env python3
"""Source-derived effective-control and menu-state examples; no engine/key execution."""
from pathlib import Path
import sys
from common import ROOT, make_ledger, run
sys.path.insert(0,str(ROOT/'notes/engine-study/T98'))
from tables import load_ds


def effective(team, own, k):
    return bool((own if k<5 and own & (1<<(k+3)) else team) & (1<<(k-1)))


def cycle(team, own, k):
    value, enable = 1<<(k-1), 1<<(k+3)
    if not own & enable: return (own | enable) & ~value
    if not own & value: return own | value
    return (own & ~enable & ~value) | (team & value)


def derive(own, role, profile, ability):
    if (profile-(ability&1))&255 < 4: own=(own | 128)&~8
    if role in [0,1,3,4]: own |= 17
    elif role==2:
        if profile<14: own |= 16
        own |= 34
    return own


def calculations():
    read,_,_=load_ds()
    order=[read(0x6bbf+i) for i in range(1,9)]
    assert order==[5,6,7,1,2,3,4,8]
    states=[0]
    for _ in range(3):states.append(cycle(1,states[-1],1))
    assert states==[0,16,17,1]
    assert [effective(1,s,1) for s in states]==[True,False,True,True]
    assert effective(0,255,5) is False and effective(16,0,5) is True
    values=[derive(0,*row) for row in [(0,10,100),(2,10,100),(2,14,100),(5,3,101),(2,3,101)]]
    assert values==[17,50,34,128,178]
    assert derive(17,2,10,100)==51 and derive(0,2,10,100)==50
    assert effective(0,51,1) and not effective(0,50,1)
    def mark(old,protected,team_man,automatic,role=2,slot=3):
        if slot==2 and role==1:old=0
        return old if protected else automatic if team_man else 0
    assert [mark(205,p,t,211) for p,t in [(True,False),(True,True),(False,False),(False,True)]]==[205,205,0,211]
    assert mark(205,True,False,211,role=1,slot=2)==0
    roles=[0,2,2,3,4,5,6,7,8,12,13]
    group=[read(0xd5c+r) for r in roles]
    assert [group.count(i) for i in range(4)]==[1,4,4,2]
    available=[True]*11;available[1]=False
    assert [sum(ok and g==i for ok,g in zip(available,group)) for i in range(1,4)]==[3,4,2]
    assert ((13+1)%14)==0
    return dict(menu_order=order,own_cycle=states,effective_cycle=[True,False,True,True],derived_masks=values,
                derive_without_clear=51,fresh_derive=50,protected_mark_cases=[205,205,0,211],protected_slot2_sweeper=0,formation_all='4-4-2',formation_missing_cb='3-4-2',
                controls={'bit-index-k-instead-k-1':'rejected:team element5 is mask16',
                          'own-controls5-through8':'rejected:own255/team0 gives e5 false',
                          'two-state-own-editor':'rejected:inherit/off/on/return sequence has three distinct modes',
                          'BBFF-clears-overrides':'rejected:old17->51, fresh0->50',
                          'team-zonal-clears-manual':'rejected:protected205 survives',
                          'formation-counts-unavailable':'rejected:available-only label becomes3-4-2'})


def matrix():
    effects=[
      ('position: stay back/push forward; keeper stay/leave box',['0791:42CB','0791:4532','0791:4A28','0791:4E28','1771:0BC4'],'Changes line class/depth predicates and selected holder choices; role/possession conditional.'),
      ('possession: keep ball/quick pass',['0791:5049'],'Adds coin opportunity to holder action gate; no fixed pass completion probability.'),
      ('passing: short/long; keeper throw/kick',['0791:3111'],'Changes initial candidate cutoff/comparison; own-half nonkeeper forces long mode; fallback drops distance filter.'),
      ('tackling: avoid injury/go in hard',['0791:4DA9','0791:D5C1'],'Bypasses one foul-opportunity gate; hardness contest/cards/injury remain conditional.'),
      ('pitch: half/full',['0791:4649','0791:4A28','0791:4B64','1771:0BC4'],'Changes defensive depth; half-pitch follow guard is qualified by opposed directions and legal target bounds in marking chapter.'),
      ('defence: sag/stand',['0791:4649','0791:4B64','0791:5729','1771:0BC4'],'Changes depth and defending ball-approach predicate; context can trade pressure against shape.'),
      ('line: safe/trap',['0791:4532','0791:4B64'],'Changes advancement while holding; offside8CF5 reads geometry, not this bit directly.'),
      ('mark: zonal/man',['1771:3EF8','0791:47C5'],'Refresh automatic opponent identities by role preferences; protected manual words survive except slot2 sweeper clearing, zero-word fallback can still follow an opponent.'),
    ]
    rows=[]
    for k,(name,readers,effect) in enumerate(effects,1):
        rows.append(dict(id=f'team-{k}',name=name,write=f'1771:1981 XOR country+2D mask{1<<(k-1)}',readers=readers,effect=effect,
                         refresh='Ordinary effective readers see bit at next call; e8 rebuilds marking; ED8A changed flag9B55 and exit230C refresh cached layout.',
                         persistence='Managed current country byte survives F1F6; BC5D/AI setup or other explicit reset restores R008, route dependent.',
                         limits='Team edit requires managed and not replay; own override shadows1..4. Quick aggregate reads1/5/6 and foul4, not every watched mechanism. No net-benefit claim.'))
    for k in range(1,5):
        rows.append(dict(id=f'own-{k}',write=f'1771:4B61 cycles own+F elements{k} and{k+4}',readers=['0791:26D7','1771:0BC4','1771:3BD3'],effect=f'Inherit/off/on for team element{k}; role-specific labels do not create another stored tactic.',refresh='Value readers next call; in-match9B55/layout refresh; derived3431 can set bits again.',persistence='Persistent player+F until reset/derive; BBFF derives without clearing, BC5D/34E7 clear first.',limits='Only1..4 overridden; manual editor is not a raw XOR of team byte.'))
    extra=[
      ('played-role','1771:4952 writes player+6; C restores+7, otherwise cycle0..13',['0791:419C','0791:42CB','1771:3179','1771:3EF8','1771:0E6C'],'Posts/depth, foot/keeper placement flag, automatic pairing and display label change.','Marks immediately if setup;9B55 and230C rebind full layout; no stored formation ID.'),
      ('manual-mark','1771:49B8 status element7 plus9A3E opponent identity',['1771:3EF8','0791:47C5'],'Cycle inherit/protected-zone/available opposite2..11; role<2 clears protection.','Only setup/available player role>=2 and enabled editor row; refresh3EF8 preserves protected word except slot2 role1 is zeroed first.'),
      ('captain','CC7B returns identity to9978 side leader',['0791:20E3','0791:278A'],'Leadership adds2L to rebound cached extra; not a universal all-skill team bonus.','230C resets initial cache before20E3; normal menu exit matters.'),
      ('set-piece-takers','CC7B roles2..5 return identities in9976 side table',['0791:6B65','0791:6FEE','0791:74C2','0791:7621'],'Different event/restart rules, location and availability can override designated identities.','Resolve identities to live squad; invalid/absent pick fallback, separate full PK order9B93.'),
      ('selection','E44F/E022 managed roster/pool edits and swap request',['0791:EA09','0791:C5DC'],'Availability, budget, keeper count and role caps constrain accepted choices.','Rebind/sort/form/mark swaps; prematch pool exchange differs from in-match substitution.'),
      ('pace','9372 edits game+3F delay',['0791:9564','0791:0C0B'],'Presentation delay setting; shootout saves/changes/restores; no stored player pace skill.','Byte UI bounds and raw primitive semantics differ; do not infer more simulated minutes from wall time.'),
      ('quick','9372 quick-mode choice;9A3E/9A3F',['0791:97D0','0791:D733','0791:A10A'],'Select watched ticks versus minute aggregate result; shootout forces watched.','Mode/cached restore; outer silentD47E is another route, not this toggle.'),
      ('controller','country+2E manager mapping and context',['1771:0B77','0791:A3DE','0791:C173','0791:ED8A'],'Managed sides preserve decisions and skip computer policy; no-managed fixtures have different input seed hook.','Controller is fixture/config context, not a mid-match tactic; synthetic reassignment must keep mapping coherent.'),
    ]
    for identity,write,readers,effect,refresh in extra:
        rows.append(dict(id=identity,write=write,readers=readers,effect=effect,refresh=refresh,persistence='See named source and linked lifecycle/identity chapter; role/mark/taker state persists or is rebuilt by explicit reset/rebind, mode is transient.',limits='Mechanism and admitted menu context only; raw edits do not prove natural reach or average advantage.'))
    return rows


def build():
    calc=calculations()
    meanings=[
      ('0791:26D7','Own override1..4 else side-country current byte;2974 determines side,not player country0.', ['player+F','pitch+D','9B34/36'],'Team changes can be shadowed by personal override.'),
      ('1771:1981','Managed/nonreplay team editor toggles row mapping5,6,7,1,2,3,4,8.', ['country+2D','0C20','6BBF'],'Eight visible choices map to nonsequential bits.'),
      ('1771:4925','Shift code0..13 through bytewrap1..14 and clear syntheticDown key.', ['player+6','A976'],'Role13 wraps to0,not14.'),
      ('1771:4952','Nonzero player C restoresnatural+7 elseadvance;flag9B55andmarkrefresh ifsetup.', ['player+6/+7','0C1F/0C1E'],'Changes played role rather than immutable natural role.'),
      ('1771:49B8','Cycle default/protectedzero/opponentidentity2..11 skippingunavailable;role<2 clearsprotection.', ['player+10 e7','9A3E'],'Protected zone is a specific override,not merely team zonal.'),
      ('1771:4B61','Ownrow1..4 inherit/off/on;fifthmarkrow requiressetup,role>=2,availabilityandcallerflag.', ['player+F','0F38','0C1F'],'Three states and conditional row availability must survive a readable rewrite.'),
      ('1771:33CD','Set own element8 and clear4.', ['player+F'],'Overrides hard tackling off.'),
      ('1771:3431','Hardness<4 softoverride;roles0/1/3/4push;role2profile<14positionenable thenquickoverride.', ['player+5/+3/+6/+F'],'Derives from own fields;does not clear existing overrides.'),
      ('1771:34E7','Clear+F then3431 fornonzero20 squadwords.', ['country.squad','player+F'],'Fresh derivation differs fromBBFF rederivewithoutclear.'),
      ('1771:3E2F','Opposingranges13/12,9..11,5..8,1,2..4;prefrows1..4;opponentsdescending,ownfirstmatching.', ['0EF4','parent role arrays'],'Pairings depend on role and slot order,not marking skill maximisation.'),
      ('1771:3EF8','Buildrolesexcludingown sweeper/unavailable/protected;removeexplicit targets;pair,thenretainprotectedorinstallautomaticifteam8;slot2role1 is cleared before all pairing/protection.', ['9A3E','player+10 e7','country+2D e8'],'Manual identities can persist with teammanoff;keeperoutsideassignment.'),
      ('1771:0E6C','CountavailableXI byDS0D5C and print defence-midfield-attack.', ['player+6','3216','0D5C'],'Same label can hide different roles/feet/posts;unavailable changes label withoutroleedit.'),
    ]
    examples=[
      dict(id='override-cycle',inputs={'team':1,'own':0,'element':1},steps=['inherit on','firstEnter forcedoff','secondEnter forcedon','thirdEnter inherit withcopiedvalue'],prediction={'own_bytes':calc['own_cycle'],'effective':[True,False,True,True]},limits='Source state transitions,not genuine UI key evidence.'),
      dict(id='derive-is-not-reset',inputs={'old_own':17,'role':2,'profile':10,'ability':100},steps=['3431adds16/32/2','oldbit1survives','clearfirstinsteadgives50'],prediction={'without_clear':51,'fresh':50},limits='Supplied representable fields;does notassertnormalfrequency ofrolechanges.'),
      dict(id='manual-mark-vs-team',inputs={'protected':True,'old_opponent_identity':205,'team_man':False,'played_role':2,'slot':3},steps=['3EF8excludesprotectedmarkerfromauto','retainsword despite team8off'],prediction={'mark_word':205},limits='Assumes nonsweeper slot3 and valid opponent identity;slot2/role1 clears the word even if protected.'),
      dict(id='formation-is-derived',inputs={'played_roles':[0,2,2,3,4,5,6,7,8,12,13],'unavailable_slot':2},steps=['allavailablegroupcounts1/4/4/2','3216excludescentrebackslot2'],prediction={'all':'4-4-2','with_unavailable':'3-4-2'},limits='Display-count projection;no completepitch/formation rendering.'),
    ]
    ledger=make_ledger('T103a',Path(__file__).resolve(),['The control-to-code matrix','Overrides, edits and refresh','Formation and marking choices','Predictions and limits'],meanings,examples,calc,['menus','attributes','positioning'],addresses=['0791:2974','0791:230C','0791:20E3','0791:ED8A','0791:3111','0791:5049','0791:4DA9','0791:4532','0791:4649','0791:4B64','0791:4A28','0791:4E28','0791:5729','0791:47C5','0791:9372','0791:97D0','1771:0BC4'])
    ledger['control_matrix']=matrix()
    return ledger


if __name__=='__main__':run('T103a',build)
