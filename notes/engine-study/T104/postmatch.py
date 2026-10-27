#!/usr/bin/env python3
"""Source-derived persistence/recovery projections; no guest, port or match execution."""
from pathlib import Path
import sys
from common import ROOT, make_ledger, run
sys.path.insert(0, str(ROOT / 'notes/engine-study/T98'))
from tables import load_ds, s8, s16


def ban(status):
    status &= ~128
    if status & 32: status |= 128
    status &= ~32
    if status & 16:
        if status & 8: status = (status | 128) & ~8
        else: status |= 8
    return status & ~16


def confidence(value, delta):
    return max(1, min(32, s16((s8(value) + delta) & 65535)))


def recover(fitness, energy, participating, first, second, cap, heal=False):
    value = s8(fitness)
    if energy == 0: value += first - second  # rand2 then rand8
    elif participating: value += second - first  # rand2 then rand8
    else:
        value += second - first  # rand3 then rand2
        if value < 16: value += 1
    value = s16(value & 65535)
    value = 1 if value < 1 else min(value, cap)
    return [value, value if s8(energy) > 0 or heal else energy]


def rolled(base, first, second):
    value = (base + second - first) & 255  # managed ordered draws
    if s8(value) > 32: value = 32
    energy = value
    if s8(value) < 1: value = 1
    return [value, energy]


def mom(rows, previous=777):
    best, winner = 1, previous
    for identity, slot, status, raw in rows:
        if slot >= 12 and not status & 4: continue
        if raw == 32767: continue
        value = s16(raw)
        if value > 5000: value = s16((value - 10000) & 65535)
        if value > best: best, winner = value, identity
    return winner


def calculations():
    read, _, _ = load_ds()
    bases = [read(0xe82+i) for i in range(4)]
    assert bases == [16, 13, 32, 25]
    statuses = [ban(v) for v in [128,32,16,24,48,4]]
    assert statuses == [0,128,8,128,136,4]
    assert ban(ban(16) | 16) == 128 and ban(128) == 0
    recovery = [recover(20,0,True,1,8,32), recover(20,0,True,1,8,32,True),
                recover(20,5,True,1,8,32), recover(15,5,False,3,1,32),
                recover(24,5,True,1,8,25)]
    assert recovery == [[13,0],[13,13],[27,27],[14,14],[25,25]]
    assert rolled(16,17,1) == [1,0] and rolled(16,1,48) == [32,32]
    restore = [[saved, fit if s8(energy)>0 else energy] for saved,fit,energy in [(14,20,4),(14,20,0),(14,20,255)]]
    assert restore == [[14,20],[14,0],[14,255]]
    rows = [(101,2,0,95),(102,12,4,10095),(103,13,0,200),(104,3,0,32767)]
    assert mom(rows)==101 and mom(rows[1:])==102
    assert mom([(101,2,0,1)])==777
    assert confidence(31,3)==32 and confidence(1,-3)==1
    assert confidence(confidence(31,3),-1)==31 and confidence(31,2)==32
    # Equal stored goals with a PK winner: result-based records and goal-based margin differ.
    assert abs(s8(2)-s8(2))==0
    def aggregate(total_a,total_b,first_a,second_a,parity):
        return int(total_b>total_a or (total_b==total_a and second_a>=first_a))
    assert [aggregate(2,2,1,1,p) for p in [0,1]]==[1,1]
    groups=[['A',4,3,5],['B',4,3,5],['C',6,0,1],['D',4,3,6]]
    ordered=sorted(groups,key=lambda r:(r[1],r[2],r[3]),reverse=True)
    assert [r[0] for r in ordered]==['C','D','A','B']  # keys only; not original exchange-sort tie stability
    return dict(fitness_bases_caps=bases,status_cases=statuses,recovery_cases=recovery,
                roll_low_high=[rolled(16,17,1),rolled(16,1,48)],restore_cases=restore,
                man_of_match={'first_tie':101,'bench_participant_alone':102,'all_low_retains_previous':777},
                clipped_sequence=[32,31],penalty_fixture={'goals':[2,2],'result':0,'absolute_margin':0,'season_winner_increment':1},
                aggregate_equal_parities=[1,1],group_key_order=[r[0] for r in ordered],
                controls={'restore-injury-from-fitness':'rejected:zero energy remains zero at CB7D',
                          'copy-energy-after-lower-clamp':'rejected:managed extreme fitness1/energy0',
                          'drop-substitute-offset-test':'rejected:10095 is decoded95, strict tie keeps101',
                          'ban-needs-participation':'rejected:status transition applies every nonzero squad word',
                          'combine-confidence-clips':'rejected:31+3 clipped32 then-1 yields31, not32',
                          'aggregate-parity-tiebreak':'rejected:equality jumps jae before parity branch'})


def build():
    calc=calculations()
    rows=[
      ('0791:CAB0','Scan both squads 1..20; bench needs status element3; skip7FFF, signed perf>5000 subtract10000; strict max starts1.', ['player+10/+12','7C3A'], 'First equal rating wins; below-threshold scan retains previous winner word.'),
      ('0791:CB7D','Restore saved form for nonzero squad words; only signed-positive energy is replaced by current fitness.', ['9B07','player+C/+D/+E'], 'Live fatigue disappears here but energy-zero injury remains before later recovery.'),
      ('0791:D016','Increment current venue and overall streak bytes.', ['country streak record+3+venue/+5'], 'Byte wrapping is preserved.'),
      ('0791:D032','Clear current venue and overall streak bytes.', ['country streak record+3+venue/+5'], 'A draw clears win/loss streaks but extends nonwin/nonloss.'),
      ('0791:D050','Update season W/D/L/goals, current/max streaks and largest decisive result records with >= margin replacement.', ['fixture+0/+1/+3','country+3B/+77/+A7..BE'], 'Result byte can name a shootout winner despite tied stored goals; largest equal margins can replace.'),
      ('0791:E929','Recompute group tables then render selected country table.', ['8757','9976','1771:958D'], 'Repeated call recomputes from fixture records, not incremental double points.'),
      ('0791:F1F6','Setup/menu; save form20, initial XI perf55; play; MOM; summary/groups; restore state; AI reset; country records; managed pool tail.', ['9B07','9A3E','0C1E/1F/20','A923+1'], 'Does not itself call B7FA; outer router owns subsequent fixture-player updates.'),
      ('1771:59D8','Stage membership CS59B8 selects second table bank.', ['game+3C','CS59B8={3,4,7,8}'], 'Table address depends on stage and snapshot.'),
      ('1771:82BD','Rebuild four-country table from matching played fixture slots25..36, points2/1/0, descending points/GD/GF exchange sort.', ['fixture+0/+1/+2','table entry8bytes'], 'No fresh tie coin and no direct result-byte win bonus.'),
      ('1771:85F7','Stage6 rebuilds aggregate records2401..2408 once both legs played; total tie uses second first-side goals >= first.', ['fixture goals','aggregate+3','870A jae'], 'Parity-looking tie branch is unreachable on equality; inherited F023 original quirk.'),
      ('1771:8757','Rebuild stage2/3/5/7 groups, stage6 aggregates; stage7 one continent, stage3 two groups.', ['CS8737','1110/1112','game+3C/+40'], 'Competition refresh has stage-specific scope.'),
      ('0791:B27F','Clear old suspension, red becomes next suspension; current booking toggles carried booking or next suspension; clear red/current yellow.', ['player+10 elements8/6/5/4'], 'Called for nonparticipants too; no calendar duration byte.'),
      ('0791:B364','Signed old form plus word delta then clamp1..32 on every call.', ['player+C'], 'Multiple clipped calls cannot be merged algebraically.'),
      ('0791:B6CC','Signed manager delta accumulator plus amount, clamp -127..127.', ['A91F+3*manager+2'], 'Accumulator differs from manager ability+1; later season folding is separate.'),
      ('0791:B71C','Opponent-minus-own country rating /32 truncation; decisive signed margin with side/fixture-set-dependent doubling.', ['1771:10E7','1771:5C60','1771:5A03','fixture+3'], 'Penalty winner at tied stored goals may have zero margin contribution.'),
      ('0791:B7FA','Both nonzero squads: XI/status3 caps++, recovery/result form, extra participating-bench jitter; unused bench jitter/recovery; bans all.', ['player+8/+C/+D/+E/+10','managed-any','5A8F'], 'Managed pool updates may precede this; unplayed kind0 uses another route.'),
      ('0791:BA4E','Update managed pool80 identities: recovery flag0 or reroll, form rand4 second-first, status unless fixturekind0.', ['6D18','pool_indices','7C2A'], 'A selected pool player can receive another later B7FA update; order and RNG consumption matter.'),
      ('1771:10E7','Rating=((33-rank)*(5-continent)+129-order)/2 with signed arithmetic.', ['country+2A/+2B/+2C'], 'Country ranking contributes to result-form delta, not a direct new ability write.'),
      ('1771:3558','Age>peak+4 selects B16/13; managed B+rand3B-rand(B+1), latter first; unmanaged B+rand2B; upper clamp32, energy copy, lower fitness1.', ['player+1/+2/+D/+E','0E82'], 'Ordered writes can produce fitness1 with energy0 at legal RNG extreme.'),
      ('1771:3651','Age>peak+3 cap32/25; injury draw2-draw8; participant reverse delta; unused draw2-draw3 plus1 below16; conditional healing.', ['player+1/+2/+D/+E','0E84','rand-is-one3'], 'Signed-positive energy heals automatically; other energy needs coin, including injury zero.'),
      ('1771:5A38','Friendlykind1 compares supplied country continent with fixture second country.', ['fixture+2/+6','country+2C'], 'Cross-continent sideA only; sideB compares itself and is false.'),
      ('1771:5A8F','Gradual when 5A38 or fixturekind belongs to DS0F3E.', ['5A38','5A03','0F3E'], 'Otherwise reroll3558 replaces fitness/energy immediately.'),
      ('1771:5C60','Absolute difference after signed extension of both goal bytes.', ['fixture+0/+1'], 'Normal low scores equal ordinary margin; raw >=128 is a width edge.'),
      ('0791:B3B7','Increment scorer_count byte then update/insert top3 competition rows with strict count comparison; snapshot bank5.', ['player+11','A93F','game+40'], 'Annual top-scorer byte differs from career goals word; ties do not displace solely on equality.'),
    ]
    examples=[
      dict(id='managed-watched-tail',inputs={'saved_form':14,'live_form':18,'fitness':20,'energy':4,'status':16,'caps':3,'result_delta':3,'gradual':True,'draw2':1,'draw8':8},
           steps=['F1F6 MOM before restore','CB7D restores14,20','managed pool may update shared identities first; this example excludes that membership','outer B7FA caps4,recovery27/27,form17','B27F current booking16 becomes carried8'],
           prediction={'form':17,'fitness':27,'energy':27,'caps':4,'status':8},limits='Conditional annotated subsequence; pool nonmembership assumed. Not an executed natural fixture or a prediction for every selected pool player.'),
      dict(id='injury-persistence',inputs={'fitness':20,'energy':0,'draw2':1,'draw8':8,'heal_coin':False},steps=['CB7D leaves zero','3651 fitness13','failed heal leaves energy0'],prediction={'fitness':13,'energy':0},limits='Supplied legal draw outcomes; no probability or independent draw-stream claim.'),
      dict(id='roll-write-order',inputs={'managed':True,'base':16,'first_rand17':17,'second_rand48':1},steps=['raw fitness0','upper clamp no change','copy energy0','lower fitness clamp1'],prediction={'fitness':1,'energy':0},limits='Source-admitted RNG extreme, not established natural frequency; original and port agree on write order.'),
      dict(id='penalty-result-reader',inputs={'fixture_goals':[2,2],'fixture_result':0,'rating_difference':0},steps=['D050 counts side0 win,goals2each','5C60 margin0','B71C rank0+margin0 remains0'],prediction={'winner_season_wins_delta':1,'result_form_delta':0},limits='Phase-aware fixture result; no PK kicks executed, goal-based group readers are distinct.'),
    ]
    return make_ledger('T104e',Path(__file__).resolve(),['Post-match order and path boundaries','What persists and what is restored','Recovery and availability','Country and competition consumers'], rows,examples,calc,['postmatch','update','rare'], addresses=['000E:6CA7','000E:6970','0791:B602','0791:BB2F','1771:5A03'],sources=['findings/F023-the-stage-builders-write-the-competition-calendar-from-ranked-pots-and-a-points-sort-with-no-coin.md'])


if __name__=='__main__': run('T104e', build)
