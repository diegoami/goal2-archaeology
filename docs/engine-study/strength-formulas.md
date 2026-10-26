# Strength, availability and placement

The original has two different numerical readers. Watched actions usually use the
[effective skill pipeline](attribute-formulas.md). Quick/silent goal-trial line strengths use
`1771:377E`, with ability, energy, form, availability and the placement test. Setup and computer
tactic comparisons can also call this strength reader on watched paths. Quick foul/selection
paths can still read 278A: do not turn a simplified quick model into a claim that quick play
never uses derived skills.

The [source/numerical ledger](../../notes/engine-study/T98/strength-v1.json) retains the worked
inputs, intermediates, 376 reused original literal returns and falsifying controls.

## Strength is a different reader

Let A be unsigned ability, F/E the form/energy bytes, and U16/I8/I16 the usual wrapping/signed
interpretations. `trunc_div` truncates toward zero, as x86 signed division does.

```text
if 3216 reports unavailable:
    strength = 0
else:
    W = U16(A + I8(E) - 62)
    if I8(F) < 32:
        W = U16(W + I8(F))
    else:
        W = U16(W - trunc_div(I16(W), 16))
    S = clamp(I16(W), 0, 256)
    strength = S // 2 if 3179 reports placement cost else S
```

There is no separate fitness, height, shooting or passing term in this reader. Profile/natural
role can still affect its placement predicate through foot/two-footedness. The quick builder
`1771:0BC4` then adds the manager bonus **only when strength is nonzero**, routes contributions
through the played-position line table and applies selected tactic shares and the side1 flag.
A valid/available player with zero computed strength is therefore different from one contributing
a positive point plus the manager term.

```mermaid
flowchart LR
  A[Availability 3216] --> B[Ability plus signed energy minus 62]
  B --> C[Form addition or high-form sixteenth loss]
  C --> D[Signed clamp to 0..256]
  D --> E[Placement halving 3179]
  E --> F[Quick line builder: nonzero manager bonus]
  F --> G[Role/tactic line contributions]
  G --> H[Quick trial contests]
```

The temporary strength is a word and can equal256 even though stored ability is a byte.
Clamping before placement matters; replacing the whole expression with a byte or changing the
order is not an equivalent readable rewrite. Negative intermediate divisions may lead to the
same final zero after clipping while still differing in registers/stack: this calculator checks
the numerical return, not the port's full machine-state/ABI fidelity.

## Availability and placement

`3216` rejects signed energy below1, then status elements8,6,3 in that order. A current booking
or explicit marking override alone does not reject the player. This predicate is separate from
the card's exact-zero injury label and from a zero numerical strength.

`3179` is not a generic played_role != natural_role penalty. It flags:

- A right-index player who is not two-footed on played flank codes3,7,10.
- A left-index player on codes4,8,11, whether or not the separate two-footed predicate is true.
- Exactly one of played/natural role being goalkeeper (code0).

Foot index is table-driven by player_index mod3 and natural role; two-footedness tests
peak_age+profile==30. Thus a different centre role can leave strength unchanged, while changing
a flank or crossing the goalkeeper boundary can halve it. Movement/line allocation and the
underlying skill profile can still change the player's usefulness even with no placement flag.

The asymmetry and the retained probe's non-natural peak-age fixture are explained in
[the derived-trait chapter](player-derived.md). Range-valid worked tuples do not establish that
the full new-game generator produces those exact records or that a particular lineup occurs.

## Worked strength traces

Unless changed, examples use A225/F31/E32, player1, played/natural role2, profile8 and peak27.
The ledger states every change, including player index, fitness and synthetic input cases.
Intermediate words are displayed here as signed values; unavailable cases stop before them.
Status is the stored byte (4 substituted,16 current booking,32 red,64 marking override,128 ban).

| Example | A | F/E | Played/club | Status | Unavailable reason | Start | After form | Clamped | Placement | Strength |
| --- | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| healthy | 225 | 31/32 | 2/2 | 0 | — | 195 | 226 | 226 | 0 | **226** |
| form32 | 225 | 32/32 | 2/2 | 0 | — | 195 | 183 | 183 | 0 | **183** |
| energy1 | 225 | 31/1 | 2/2 | 0 | — | 164 | 195 | 195 | 0 | **195** |
| fitness0-same-strength | 225 | 31/32 | 2/2 | 0 | — | 195 | 226 | 226 | 0 | **226** |
| different-centre-role | 225 | 31/32 | 5/2 | 0 | — | 195 | 226 | 226 | 0 | **226** |
| left-index-right-flank | 225 | 31/32 | 4/2 | 0 | — | 195 | 226 | 226 | 1 | **113** |
| left-two-footed-right-flank | 225 | 31/32 | 4/2 | 0 | — | 195 | 226 | 226 | 1 | **113** |
| right-index-left-flank | 225 | 31/32 | 3/2 | 0 | — | 195 | 226 | 226 | 1 | **113** |
| right-two-footed-left-flank | 225 | 31/32 | 3/2 | 0 | — | 195 | 226 | 226 | 0 | **226** |
| keeper-outfield | 225 | 31/32 | 2/0 | 0 | — | 195 | 226 | 226 | 1 | **113** |
| outfielder-in-goal | 225 | 31/32 | 0/2 | 0 | — | 195 | 226 | 226 | 1 | **113** |
| injured-zero-energy | 225 | 31/0 | 2/2 | 0 | energy | — | — | — | — | **0** |
| substituted-off | 225 | 31/32 | 2/2 | 4 | status-element-3 | — | — | — | — | **0** |
| booked-only | 225 | 31/32 | 2/2 | 16 | — | 195 | 226 | 226 | 0 | **226** |
| sent-off | 225 | 31/32 | 2/2 | 32 | status-element-6 | — | — | — | — | **0** |
| mark-override-only | 225 | 31/32 | 2/2 | 64 | — | 195 | 226 | 226 | 0 | **226** |
| suspended | 225 | 31/32 | 2/2 | 128 | status-element-8 | — | — | — | — | **0** |
| upper-clamp | 255 | 31/127 | 2/2 | 0 | — | 320 | 351 | 256 | 0 | **256** |
| clamp-before-placement | 255 | 31/127 | 4/2 | 0 | — | 320 | 351 | 256 | 1 | **128** |
| available-zero-strength | 0 | 1/1 | 2/2 | 0 | — | -61 | -60 | 0 | 0 | **0** |
| synthetic-negative-form | 180 | 128/1 | 2/2 | 0 | — | 119 | -9 | 0 | 0 | **0** |

For A225/E32, the start is195. Form31 adds31, giving226. Form32 instead subtracts
trunc(195/16)=12, giving183. This is the original over-confidence boundary, not a smooth
monotone morale bonus.

Changing only fitness to0 leaves this reader's226 unchanged; it does not show that fitness is
irrelevant to recovery or that such a raw record is a normal healthy state. Changing centre role2
to5 also leaves the scalar unchanged, but the line builder and movement rules still differ.

At the upper edge, 255+127-62+31=351 clips to256; placement then gives128. Halving351 first
would give175, a different result. The available-zero case instead clips a negative value to0
without being unavailable. A synthetic negative-form case produces0 here, whereas the other
reader's unsigned low-product arithmetic can produce a large value: formulas cannot be merged
by assuming the same condition treatment.

## Validation and interpretation limits

The source-derived calculation reproduces **376 retained original literal returns**, zero
mismatches: 172 strength cases,21 fitness variations and183 structural/edge cases. Controls
against those recorded returns are caught:

| Control | Recorded disagreements |
| --- | ---: |
| Form cutoff33 instead of32 | 18 |
| Clamp maximum255 instead of256 | 11 |
| Ignore availability | 46 |

These are counts of synthetic test cases, not event rates or gameplay effects. The calculations
also verify the retained foot-table windows against the static extract. They do not rerun a
binary routine, half or match, and do not prove all aliases or machine-state side effects.
The earlier foot probe and wider worked tuples retain their declared natural-range limitations.

At new-game squad creation `1771:97CC` seeds from the country before making its players.
The base squads are consequently correlated, repeatable outputs under the same data—not
independent random rosters merely because their creation code calls rand. This statement does
not extend to every later pool/development path. Our controlled field traces are not samples
from that generation distribution.

The [player fields](player-fields.md), [persistent context](match-fields.md) and
[live state](transient-state.md) explain inputs and cached values. T99 connects scalar bounds
to gates/opposed contests; none of the local differences above is a measured win-rate change.

```bash
python3 -B notes/engine-study/foundations/check.py --task T98b
python3 -B notes/engine-study/T98/math.py --strength --check
```
