# Effective skill: exact arithmetic and worked traces

The skill used in an action is a pipeline, not the bar on the player card. Ability/profile/natural
role produce a base skill; current condition, a cached placement flag, a manager-derived extra
and side/venue context then change the value. This chapter expresses the original readers in
named arithmetic and checks them against retained original-call results.

The [numerical ledger](../../notes/engine-study/T98/skill-v1.json) pins source/data hashes and
records every worked input/intermediate value. These are proposed source interpretations and
analytical checks, not fresh matches or a new original-code execution.

## Inputs and finite-width operations

From the [player dictionary](player-fields.md), A is unsigned ability (+04), P profile (+05),
C natural/club position (+07), F form (+0C) and E energy (+0E). e is the skill element (ordinary
displayed domain 1..12). From the [live state](transient-state.md), H is the cached placement flag,
K the pitch manager-extra byte, s the pitch-slot identity, h the DS:80FC flag and q the event code.

Use `U16(x)=x mod 65536`, `I8(b)=b` below 128 and `b-256` otherwise, and floor division on
the nonnegative quantities below. Do not replace the low-word multiplication with unlimited
integer multiplication followed by division. The skill reader itself does not reject an
unavailable player; caller/selection predicates are separate.

The source uses one-based element/profile/class indices over DS base addresses. When rebasing
them into zero-based arrays, preserve the implied dummy prefix rather than shortening the
addressable domain. The static DS extract is used here; saved E020 windows are compared with it.

## Effective skill pipeline

Original routines: `1771:3A06` (derived skill), `3947` (display), `0791:278A` (effective
value), `A260` (cached binding values), `1771:0AA7` (manager bonus) and `0791:2974` (side).

```text
class  = DS8[0x6D25 + 12*C + e]
weight = DS8[0x6DCD + 12*P + class]
product = U16(weight * (A+1))
D0 = product // 32
bar_length = product // 256
D = D0 // 2 if H != 0 else D0

form_term = I8(F)+1 if I8(F) < 32 else 0
B = U16(form_term + (32 if e >= 12 else I8(E)))
V0 = U16(B*D) // 256 + D // 4

extra_gate = DS8[0x769+e] != 0 or (e == 1 and q in {3,4})
V1 = U16(V0 + (K if extra_gate else 0))
V = U16(V1 + (V1 // 16 if s < 12 and h != 0 else 0))
```

```mermaid
flowchart LR
  A[Ability, profile, natural role] --> B[Class and weight lookup]
  B --> C[Derived skill D0]
  C --> D[Cached placement halving]
  D --> E[Condition term plus quarter skill]
  E --> F[Element/event-gated manager extra]
  F --> G[Side1 host-context share]
  G --> H[Effective value for a gate or duel]
  B --> I[Displayed bar, with divisor 256]
```

For ordinary elements 1..12, the table adds K unconditionally for **2, 4, 11 and 12**.
Keeping (1) adds it for event codes 3 and 4. The byte 0x18 encoding that set is not event 24.
The gate is not a test of whether the player is a goalkeeper. A260 assigns K to all bound players
as `floor(u8(manager_ability)/8)+16+32`, using the persistent player's country.

Likewise s<12 is a side test: active slots 1..11 are side1, including keeper slot1.
It is not an outfield-only predicate. The final share is one sixteenth of the value **after**
the extra, and all divisions round at their actual stage.

The display relation is `bar_length = D0 // 8`; D0 can retain 0..7 points hidden by a bar.
Conversely, H halves D before the condition/quarter terms and leaves the later K untouched.
Therefore it need not halve the final value. Cached K/H also mean an arbitrary mid-match raw
record edit is not equivalent to performing the normal rebind/setup path.

## Worked traces

Unless specified otherwise, the examples use A=180, P=8, C=2, F=31, E=32, slot13, no venue
share, event0 and K=56 (a possible bound extra). The ledger states every exception, including
keeper/natural-role and raw-byte cases. They are controlled local inputs, not complete match
fixtures. The condition-plus-quarter column shows the two terms before K.

| Example | e | F/E bytes | D after placement | B word | Condition + quarter | K added | Share | Final V |
| --- | ---: | --- | ---: | ---: | --- | ---: | ---: | ---: |
| healthy-tackling | 3 | 31/32 | 147 | 64 | 36+36 | 0 | 0 | **72** |
| form32-tackling | 3 | 32/32 | 147 | 32 | 18+36 | 0 | 0 | **54** |
| energy1-tackling | 3 | 31/1 | 147 | 33 | 18+36 | 0 | 0 | **54** |
| placement-tackling | 3 | 31/32 | 73 | 64 | 18+18 | 0 | 0 | **36** |
| shooting-extra | 11 | 31/32 | 84 | 64 | 21+21 | 56 | 0 | **98** |
| placement-shooting | 11 | 31/32 | 42 | 64 | 10+10 | 56 | 0 | **76** |
| penalty-energy1 | 12 | 31/1 | 107 | 64 | 26+26 | 56 | 0 | **108** |
| penalty-energy32 | 12 | 31/32 | 107 | 64 | 26+26 | 56 | 0 | **108** |
| keeper-side1-host | 1 | 31/32 | 147 | 64 | 36+36 | 0 | 4 | **76** |
| keeper-side0-context | 1 | 31/32 | 147 | 64 | 36+36 | 0 | 0 | **72** |
| keeper-event3 | 1 | 31/32 | 147 | 64 | 36+36 | 56 | 0 | **128** |
| synthetic-negative-form | 3 | 128/1 | 147 | 65410 | 183+36 | 0 | 0 | **219** |
| profile16-last-role | 12 | 31/32 | 130 | 64 | 32+32 | 56 | 0 | **120** |
| ability255-display-edge | 1 | 31/32 | 208 | 64 | 52+52 | 0 | 0 | **104** |

The ordinary tackling example selects class1, weight26: `26*181=4706`, D0=147 and bar=18.
At F31/E32, B=64 and the value is 36+36=72. At F32/E32, the form contribution disappears:
B=32 and the value falls to 18+36=54. This discontinuity is in the source; more form is not
monotonically better across that boundary.

Placement halves tackling's D147 to D73, producing V36 here. Shooting illustrates why that is
not a universal final-value halving: D84 becomes D42, but K56 remains, so V98 becomes V76.

Element12 substitutes 32 for energy in this reader; the E1 and E32 penalty traces both give108.
Energy can still affect availability and other actions. This is not a claim that an exhausted or
injured player is always eligible to take a penalty.

For the keeper example, slot1 with the host flag receives 72//16=4, while slot12 does not.
Event3 instead activates K56, giving128 without a venue share. These traces separate slot,
event and role conditions that older short descriptions can conflate.

The negative-form case is deliberately synthetic: byte128 means -128, giving B=65410 after
word wrapping and V219. It is not evidence that this state occurs naturally or that lower
confidence is a winning strategy. The ability255 edge gives a display-formula length26; F008's
observed new-game maximum25 does not by itself justify a universal raw-byte clamp.

## Validation scope and limitations

The independently written arithmetic reproduces **209 retained original literal-call returns**
from E020: 155 ordinary/boundary cases, 12 event cases and 42 fitness-variation cases; zero
mismatches. Deliberate changes are caught against those recorded returns:

| Control | Recorded cases that disagree |
| --- | ---: |
| Skill divisor31 instead of32 | 138 |
| Form cutoff33 instead of32 | 21 |
| Omit placement halving | 2 |

These are probe-design counts, not frequencies in football play. The retained calls use profile8
and club position2; they do not validate every profile/role combination. Element11's worked
gate is source-backed and linked to F015/T42's earlier correction; it is not another new E020
original-call observation. No whole half or match was rerun here.

**[Table-window limitation (#477)](https://github.com/diegoami/goal2-archaeology/issues/477):** the retained class window has168 bytes but valid one-based indices
reach168; the profile window has192 bytes but indices reach204. Using those windows in the old
analytical helper raises IndexError for ordinary argument domains such as club13/element12 or
profile16. The current port reads full guest memory and is not shown faulty by this helper error.
This chapter uses the complete static DS extract, verifies its overlap with every retained window
and preserves all old records unchanged. The wider examples are analytical predictions from
that source, not newly measured original returns.

The value V is neither a probability nor a performance rating. A caller may quantise it through
287C or use it as an opposing-draw bound, with branch-dependent random consumption. T99 explains
those decisions; higher local values do not prove a monotone result at one fixed match seed.

```bash
python3 -B notes/engine-study/foundations/check.py --task T98a
python3 -B notes/engine-study/T98/math.py --skill --check
```
