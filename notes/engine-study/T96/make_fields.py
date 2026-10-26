#!/usr/bin/env python3
"""Generate the interpreted player-field inventory from the explicit source-reading ledger."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "notes/engine-study/foundations"))
from check import pin, write_new

# offset, width, name, meaning, primary readers, primary writers, influence/lifetime.
ROWS = [
 (0,1,"country","Owning country index; ordinary countries are 1..128; record zero is not a normal player.","1771:0BC4","1771:96D3","Persistent identity; resolves country defaults/management, not an independent talent score."),
 (1,1,"age","Unsigned age; new-game samples are not a universal legal range.","1771:32EB 1771:30D9 1771:7F40","1771:96D3 1771:7E4A","Persistent; ability evolution, leadership and recovery/retirement routes; no standalone age multiplier in 278A."),
 (2,1,"peak_age","Creation-time age parameter controlling the ability curve; also an input to two-footedness.","1771:32EB 1771:3041","1771:3291","Persistent; indirect skill scale and recovery effects; the displayed card does not show a peak-age field."),
 (3,1,"rating","Creation ceiling/rating parameter, conventionally called potential; not a stored skill.","1771:32EB 1771:2FFB 1771:30D9","1771:96D3","Persistent; ability curve and derived hardness/leadership. Raising it alone is not the same as raising current ability."),
 (4,1,"ability","Current ability/skill scale, an interpretive name supported by its arithmetic use.","1771:3A06 1771:3947 1771:377E","1771:32EB","Persistent; directly scales derived skills and quick/silent strength; recomputed during ageing."),
 (5,1,"skill_profile","Profile selector, normally 1..16 at creation; shapes a curve rather than storing twelve independent values.","1771:3A06 1771:3947 1771:2FFB 1771:3041 1771:30D9","1771:96D3","Persistent; skills, hardness, leadership and two-footedness. Profile numbers are not a simple quality ranking."),
 (6,1,"position","Current played position code, normally 0..13; zero is the goalkeeper role.","1771:3179 1771:0BC4 0791:419C","1771:96D3 0791:BC5D 0791:C5DC","Persistent squad role; formation/movement/line allocation and placement penalty; distinct from club position."),
 (7,1,"club_position","Natural/club position code, normally 0..13; feeds class, height and foot tables.","1771:3A06 1771:2FAD 1771:3088 1771:3179","1771:96D3","Persistent; moving played position does not rewrite the natural skill profile."),
 (8,2,"caps","Little-endian 16-bit appearance count; +09 is the high byte, not another attribute.","1771:42BC 1771:7F40","0791:B7FA","Persistent history; participant update increments it, retirement can read it. No identified direct skill term."),
 (10,2,"goals","Little-endian 16-bit recorded goals count; distinct from the seasonal scorer byte.","1771:42BC","0791:6443 0791:B602","Persistent history/statistic; update and attribution depend on the goal route, not a talent input."),
 (12,1,"morale","Player confidence/form. Arithmetic reads s8; result clipping is 1..32, while live adjustment can reach other bytes.","0791:278A 1771:377E 1771:13D0","1771:96D3 0791:7CC5 0791:B364 0791:CB7D","Live and persistent; directly affects skill/strength. Match snapshots distinguish transient team swings from saved form."),
 (13,1,"fitness","Persistent condition/recovery baseline; not the same field as current energy.","1771:3558 1771:3651 1771:42BC 0791:CB7D","1771:3558 1771:3651","Indirect match influence through restored energy and recovery; no identified direct arithmetic term in 278A/377E."),
 (14,1,"energy","Current energy, read signed for availability/strength. Zero means injury on the card; signed-negative bytes are unavailable too.","1771:3216 0791:278A 1771:377E","1771:3558 1771:3651 0791:CB7D 0791:8AE9 0791:D733 0791:7D56","Live and persistent; skill/strength/chance/availability effects. Ordinary match decay stops at 1 and does not decrement fitness."),
 (15,1,"own_tactic_set","Pascal-set byte: elements 1..4 are values, elements 5..8 enable the respective overrides.","0791:26D7 1771:0BC4","1771:3431 0791:BC5D","Persistent/managed controls with setup/reset rules; a clear override-enable bit means use the country's setting."),
 (16,1,"status","Packed flags, not an ordinal status score; element k occupies bit k-1.","1771:3216 1771:3EF8 1771:42BC","0791:798D 0791:7B77 0791:C5DC 0791:B27F","Mixed lifetime: carried booking/ban, live booking/send-off, substituted-off and protect-zone flags; distinguish each flag."),
 (17,1,"scorer_count","Season/year scorer-table count; separate byte from the recorded goals word.","0791:B3B7","0791:B3B7 1771:7FB1","Persistent within its season/year accounting; scorer-table maintenance and yearly clearing, not a shot-skill input."),
 (18,2,"performance","Signed rating word with sentinels/encoding: 0x7FFF blank, 55 starter baseline, +10000 substitute marker.","1771:42BC 0791:CAB0 0791:8062","0791:F1F6 0791:1E53 0791:C5DC","Live match assessment; commentary deltas, man of the match and automatic substitution decisions. It is not an independent skill."),
]


def main():
    fields, addresses = [], set()
    for offset,width,name,meaning,reads,writes,effect in ROWS:
        readers,writers=reads.split(),writes.split()
        addresses.update(readers+writers)
        fields.append({"offset":offset,"width":width,"name":name,"meaning":meaning,
                       "representation":"u16 little-endian" if width==2 else "u8 storage; signedness is reader-specific",
                       "primary_readers":readers,"primary_writers":writers,"effect_and_lifetime":effect})
    data=pin({"task":"T96a","sections":["Record and identity","Stored fields","How to interpret influence","Bounds and uncertainty"],
              "records":{"player":{"size":20,"fields":fields}},
              "access_scope":"All 20 bytes have a field owner; listed readers/writers are primary routes, not an exhaustive alias-resolved site census."},
             addresses,["runtime/original_match/image.py","runtime/original_match/port/attributes.py",
                        "static/goal-exe/annotations/fields.tsv","findings/F007-player-values-are-made-at-a-new-game-from-a-seed-per-country-not-from-the-dos-time.md",
                        "findings/F008-the-player-screen-draws-12-skills-as-bars-derived-from-three-record-bytes.md",
                        "findings/F018-energy-is-expended-in-matches-and-restored-from-fitness.md",
                        "findings/F021-energy-and-form-set-a-players-strength-fitness-is-never-read-in-a-match.md"])
    write_new(ROOT / "notes/engine-study/T96/fields.json",data)
    print("wrote player-field ledger: 17 fields, 20 bytes; primary source locations pinned")


if __name__=="__main__":
    main()
