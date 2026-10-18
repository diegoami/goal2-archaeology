#!/usr/bin/env python3
"""T61: the milestone table. For each routine of row T61: the executions per match counted on the unhooked ALL
(reach-entries.jsonl), the calls the port made in the ported run (a ported record's port_calls), and whether the two
are equal in every match.

    python3 -B experiments/E036-match-port/out/T61/summary.py REACH.jsonl PORTED.jsonl [--compare FILE]

Per family: matches reaching the routine, calls per match (min-max, mean) and the total. The last line counts the
routines whose port's calls equal the counted entries in every match."""
import collections
import json
import sys

NAMES = {
    "0AA7": "manager_bonus", "0B77": "is_managed", "0E24": "country_colour", "0E6C": "formation_label",
    "2E20": "player_name_colour", "2E93": "player_name", "2FAD": "player_height", "2FFB": "player_hardness",
    "3041": "is_two_footed", "3088": "foot_index", "30D9": "player_leadership", "3179": "out_of_place_flag",
    "3216": "player_unavailable", "33CD": "force_tactic4_off", "3431": "set_player_tactics",
    "34E7": "reset_own_tactics", "377E": "player_strength", "3A06": "derived_skill", "3A82": "squad_slot_of_player",
    "3E2F": "pick_mark_target", "3EF8": "set_marking_words", "5A03": "fixture_kind_in_result_set"}


def load(path):
    return {json.loads(line)["id"]: json.loads(line) for line in open(path)}


def main():
    reach, ported = load(sys.argv[1]), load(sys.argv[2])
    ids = sorted(set(reach) & set(ported))
    print(f"{len(ids)} matches in both logs ({len(reach)} counted, {len(ported)} ported)")
    print("routine      name                       matches   calls/match min-max (mean)        total   ported = counted")
    equal_all = 0
    for short, name in NAMES.items():
        address = "1771:" + short
        per = [reach[i]["counts"].get(address, 0) for i in ids]
        calls = [ported[i]["port_calls"].get(address, 0) for i in ids]
        same = per == calls
        equal_all += same
        reaching = sum(1 for c in per if c)
        mean = sum(per) / len(per)
        print(f"{address}  {name:<26} {reaching:>3}/{len(ids):<3}  {min(per):>7}-{max(per):<9} ({mean:>11.1f}) {sum(per):>12}   {'yes' if same else 'NO'}")
    by_family = collections.defaultdict(list)
    for i in ids:
        by_family[reach[i]["family"]].append(i)
    print()
    for fam, members in sorted(by_family.items()):
        print(f"{fam}: {len(members)} matches")
        for short, name in NAMES.items():
            address = "1771:" + short
            per = [reach[i]["counts"].get(address, 0) for i in members]
            print(f"   {address} {name:<26} {sum(1 for c in per if c):>2}/{len(members):<2} {min(per):>7}-{max(per):<7} ({sum(per) / len(per):>10.1f})")
    print()
    print(f"{equal_all} of {len(NAMES)} routines: the port's calls equal the counted entries in every match")


if __name__ == "__main__":
    main()
