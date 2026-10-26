#!/usr/bin/env python3
"""Source-pinned persistent-state layouts; unknown groups remain explicit."""
import argparse
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'notes/engine-study/foundations'))
from check import pin,sha,write_new
F023='findings/F023-the-stage-builders-write-the-competition-calendar-from-ranked-pots-and-a-points-sort-with-no-coin.md'


def require_sources(paths):
    for path in paths:
        if not (ROOT/path).is_file():raise FileNotFoundError(path)


def source_controls():
    require_sources([F023])
    try:require_sources(['findings/__missing_ES_R1_source__.md'])
    except FileNotFoundError:return {'required_F023':'present','missing_pinned_source':'rejected'}
    raise AssertionError('missing required source silently accepted')


def f(offset,width,name,meaning):return dict(offset=offset,width=width,name=name,meaning=meaning)


def build():
    require_sources([F023])
    country=[f(0,40,'squad','Twenty little-endian player-index words; slots 1..11 are starters, 12..20 bench; order changes can persist.'),
      f(40,1,'best_continent_rank','Initialised by 97CC; 63A4 lowers it only when the world-rank branch did not improve.'),
      f(41,1,'best_world_rank','Initialised by 97CC; 63A4 lowers it before the else-if test for the continental byte.'),
      f(42,1,'continent_rank','Ordinary continental rank 1..32; country-rating/development/result-expectation input.'),
      f(43,1,'world_rank','Ordinary world rank 1..128; country-rating and result-expectation input.'),
      f(44,1,'continent','Ordinary continent code 1..4; rating, venue-host lookup and competition/recovery routing.'),
      f(45,1,'team_tactics','Eight Pascal-set defaults, modified/reset by setup/AI/manager paths; player overrides are separate.'),
      f(46,1,'manager_index','Index into 3-byte manager entries; >128 means human-managed. Not itself manager ability.'),
      f(47,2,'ranking_points','Persistent ranking/competition points; not the quick engine line sums.'),
      f(49,70,'historical_totals_unexpanded','Persistent historical/season totals; D050 includes a season block at +3B. Exact subfield types/lifetimes are not all resolved in this foundation.'),
      f(119,48,'largest_result_records','D050 largest win/loss fixture-record area +77..A6; preserve as historical data, not player attributes.'),
      f(167,24,'streaks_unexpanded','D050 home/away/all streak/current-maximum area +A7..BE; subfield enumeration remains reader-specific.')]
    fixture=[f(0,1,'first_score_or_pending_mark','Side-0 score after play; pending marker such as FE/FF before play. Phase-dependent, not always a score.'),
      f(1,1,'second_score_or_group','Side-1 score after play; before play 5D94 writes the group number (0 for no group table); A3DE copies it to 9976.'),
      f(2,1,'kind','Competition/friendly kind; 1 is friendly; gates budgets, fouls, results/deciders and venue.'),
      f(3,1,'result_code','Played result: 0 side-0 winner, 1 side-1 winner, 2 draw; a silent decider coin may choose 0/1 despite equal score bytes.'),
      f(4,2,'first_country','Country for engine side 0; API first does not mean home.'),
      f(6,2,'second_country','Country for engine side 1; used by the venue-host equality flag.')]
    manager=[f(0,1,'managed_country','Country association; computer entries start with their country, human entries use 129..134.'),
      f(1,1,'ability','Unsigned manager ability; 0AA7 reads this byte to compute floor(ability/8)+16. TEAM Skill labels also read it.'),
      f(2,1,'result_delta','Signed manager result-delta accumulator; B6CC adds and clips to -127..127. Distinct from ability and country rank.')]
    game=[f(0,1,'human_count','Number of human managers at creation (ordinary 1..6).'),
      f(1,37,'manager_context_unexpanded','Manager/selection flags and context not fully typed here; preserve them.'),
      f(38,2,'fixture_index','Current fixture index used to locate the 8-byte fixture, not stored inside it.'),
      f(40,2,'fixture_count','Fixture-list count/context.'),f(42,4,'host_prefix_unexpanded','Includes the dummy/base host-table region; no further semantics assigned.'),
      f(46,10,'host_countries','Five host-country words: continent slots 1..4 and slot 5 selected by the calendar-class flag.'),
      f(56,2,'elapsed_year','Year/cycle offset: initialised to 0; incremented by the yearly progression.'),
      f(58,2,'initial_year','Initial calendar-base year from DOS year+1 made even, not the elapsed counter.'),
      f(60,1,'cycle_stage','Stage byte in the competition cycle.'),f(61,1,'option_3d_unexpanded','Initial option byte 1; exact UI meaning not established here.'),
      f(62,1,'option_3e_unexpanded','Initial option byte 2; exact UI meaning not established here.'),
      f(63,1,'speed_delay','Match speed/delay option; simulation determinism still requires the stated key discipline.'),
      f(64,1,'calendar_class','Initial year modulo 4==2 flag; chooses host slot 5 and stage calendar variant.'),
      f(65,205,'remaining_context_unexpanded','Other options, manager flags, pool viewports and strings within the 0x10E-byte allocation; not fully typed here.')]
    records={n:{'size':size,'fields':fields} for n,size,fields in [('country',191,country),('fixture',8,fixture),('manager-entry',3,manager),('game',270,game)]}
    for name,rec in records.items():
        assert sorted(k for f in rec['fields'] for k in range(f['offset'],f['offset']+f['width']))==list(range(rec['size'])),name
    addresses=['2139:0000','1771:9A40','1771:9B85','1771:10E7','1771:0AA7','1771:0AF8','1771:0B77','1771:5A03','0791:A4A1','0791:A6E4','0791:D44C','0791:D47E','0791:B6CC','0791:B7FA','0791:BC5D','0791:D050','000E:6CA7','000E:6970']
    return pin({'task':'T97a','sections':['Identity, indexing and ownership','Persistent layouts','Fixture routing and venue','Cross-match lifetime and unresolved groups'],
                'records':records,'manager_bonus':'floor(u8(manager[1])/8)+16','host_rule':'A6E4: second country unless result-kind set; else game host[calendar_class?5:continent(second)]; D44C compares host to second country',
                'analysis_sha256':sha(Path(__file__).read_bytes())},addresses+['1771:5D94','1771:97CC','1771:63A4','0791:A3DE'],
               ['runtime/original_match/image.py','runtime/original_match/port/setup.py','runtime/original_match/port/update.py','runtime/decoders/country.py',
                'static/goal-exe/annotations/fields.tsv','static/goal-exe/annotations/globals.tsv',F023])


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');ap.add_argument('--controls',action='store_true');a=ap.parse_args()
    if a.controls:print(json.dumps(source_controls(),indent=2));return
    path=ROOT/'notes/engine-study/T97/persistent-v2.json';data=build()
    if a.check:
        assert json.loads(path.read_text())==data,'persistent layout/source ledger differs';print('PASS: country191, fixture8, manager3 and game270 byte coverage; original source locations/hashes')
    else:write_new(path,data);print('wrote persistent layouts and venue/routing ledger')


if __name__=='__main__':main()
