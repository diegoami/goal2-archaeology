# Record, indexing and evidence audit

The record audit confirms two ordinary-domain failures in a legacy analytical helper and
corrects incomplete descriptions of cached extras and taker identities. It also preserves
existing test/annotation defects and an unresolved surviving mutation. No new production
engine defect is established by these five examined candidates.

The [candidate ledger](../../notes/engine-study/T108/T108b-v1.json) records minimal changes,
expected/actual source behaviour, dispositions, primary sources and reachability limits.
[records.py](../../notes/engine-study/T108/records.py) repeats the cheap legacy helper checks,
verifies instruction anchors and hashes the historical reports. It does not execute original
or port engine routines, rerun the old mutants, or launch matches. Candidate attributions are
proposed pending independent ES-R2 review.

## Windows and identity

**Short one-based table windows fail inside their declared domains.** The legacy
`runtime/model/keeping.py:skill_value` takes class/profile byte windows and indexes them
relative to the original DS bases. Its documentation supplies lengths 168 and 192, but
the indices are one-based within each row. Index 168 needs 169 bytes; index 204 needs 205.

| Ability / profile / natural role / element | Old helper result | Complete-source result |
| --- | --- | ---: |
| 180 / 8 / 13 / 12 | Class-window IndexError at index 168 | 107 |
| 180 / 16 / 2 / 3 | Profile-window IndexError at index 193 | 135 |

The audit reproduces both exceptions and matches those literal complete-source results,
also retained in T98's immutable window report. The original/port engine reads the complete
memory layout; it does not use these short windows. Classify this as a legacy analytical
helper/data-window defect, not a port bug. [#477](https://github.com/diegoami/goal2-archaeology/issues/477)
remains open for versioned/rebased windows and boundary coverage. Padding missing evidence
with zero would invent a different value and is not an acceptable repair.

**The cached skill extra has more than one writer.** `A260` initially binds manager bonus
plus 32 into pitch `+11`. `20E3` adds twice the captain's leadership to each of the side's
eleven bytes; `278A` later decides which element/event uses the resulting byte. For one
application, initial 56 and leadership four give 64. The byte example 250+14 becoming eight
illustrates storage width only, without claiming that a natural fixture reaches it.

The [effective-skill chapter](attribute-formulas.md), [derived-trait dictionary](player-derived.md)
and [live-state dictionary](transient-state.md) now include that contribution. Their previous
numeric examples remain valid because they supply the cached byte as an input. T97's additive
v4 ledger names it `cached_skill_extra`; older ledgers remain intact. Captain effects are
element/event-gated and are not a universal bonus to every displayed skill or to quick-engine
line strength.

**Taker words hold identities, not slot numbers.** `9976+10*side+2*role` stores an own player's
identity. `6B65` searches squad slots 1..11 for the first matching word and returns 12 when
absent. A stored player identity 314 at squad slot 11 resolves to 11; treating 314 itself as
the slot changes the mechanism. `A920` is a separate resolver through the player's country
and returns a pitch slot (last match, zero when absent). The opponent marking table at
`9A3E` is different again. Raw edits that break country/squad bindings require their own
reachability assumptions.

The all-unavailable `1F3C` case remains an original edge with unresolved natural reachability:
the winner local is written only when an available candidate is accepted, yet is returned
after the loop. A readable rewrite must not silently replace an inherited stack value with
zero while claiming full byte-tuple compatibility. Whether to reject such states is a later
compatibility/design decision, not an engine fix made by this audit.

## A surviving mutation is not a dead-store proof

[#375](https://github.com/diegoami/goal2-archaeology/issues/375) records the T68 mutant changing
`A36A`'s initial pitch run direction from five to four. Its retained O8 comparison has eight
identical cases: eight expected-different checks fail to catch it. That historical output
is preserved and hashed here; those failures are not eight new passing fidelity checks.

Static reading narrows the question. On reaching `8889`, the on-target branch assigns five,
and both coin/axis branches assign a direction before the move test. That overwrites the
initial direction before the later activity check and player draw on that route. But `8AE9`
runs a state handler first, so this observation alone is not a complete read-before-overwrite
proof through every earlier action path or alias.

There is a tempting false explanation in the substitution tail. `C718` writes zero to
`es:[di+0xF]`, but `C712` has just loaded the persistent-player array pointer `DS:A91B`
after multiplying the bound player index by the **20-byte player stride**. That write clears
player tactics. `A36A` instead writes pitch direction on a **22-byte pitch record**.
Equal offsets do not identify equal fields. Likewise the nearby `C6FA` performance-word
write is not a pitch-state write. Names and typed bindings are essential to a readable rewrite.

The audit therefore leaves #375 **unresolved**: the initial direction may be dead on the
observed paths, or existing records may omit a consequence. Resolving that needs a complete
path/alias argument or a justified observation that catches the mutant. No write, digest,
mask or acceptance assertion has been removed or weakened here.

## Test and annotation limits

The independent historical review [#412](https://github.com/diegoami/goal2-archaeology/issues/412)
reports three edge mutations surviving 25 unit tests, with the captain edge also surviving
seven S comparisons. This audit checks the source instructions and reuses that report;
it does not rerun those mutants or present the old counts as new measurements.

| Edge | Original instruction / rule | Remaining gap |
| --- | --- | --- |
| Position code 13 | `EC89` compares with 0x0D; validity loop includes 13. | A warning at code 1 alone does not cover code 13. |
| Captain at squad slot 11 | `CCEC/CCEF` compares with 11 and branches `jbe`; 11 is valid. | A `>=11` invalidity mutant survives existing evidence. |
| Y/N wait | `0BD0` loads 0x258, or 600 polls. | A 601-poll mutant survives the existing focused tests. |

The last constant belongs to `0B7C`'s replay/save/summary Y/N question, not the separate
captain/taker selection prompt's 1000-poll path. Nor does a nominal timing calibration
establish an invariant real-time duration on every host. #412 remains open for its three
missing focused tests; current port source agrees with the listing.

Two annotation contradictions also remain explicit. The `278A` annotation omits element 11
from the extra table, whose actual nonzero ordinary elements are **2,4,11,12**
([#494](https://github.com/diegoami/goal2-archaeology/issues/494)). The `4354` annotation's
final sentence says `2C86` clamps a destination, while its instructions multiply both
coordinate bytes by attack direction and do not clamp
([#512](https://github.com/diegoami/goal2-archaeology/issues/512)). The readable chapters use
the instruction-backed meanings. Regeneration is a separate scoped annotation change;
this audit does not rewrite raw/named history or invalidate earlier immutable ledgers silently.

Finally, the foundations already disclose arithmetic observations that cannot distinguish
some altered rules: retained skill cases do not separate host-share removal/order, and
retained strength cases do not separate halving order or signed floor/truncation changes.
The T98 validation-scope report is reused by hash. A matching final result or a green family
therefore proves only the stated observations, not every intermediate arithmetic choice.

Across both audit chapters there are nine named candidate groups, explicit negative results,
known documentation/tooling defects and remaining path questions. The audit is not exhaustive
over all record tuples, live continuations or private inputs. Future experiments should select
questions with unresolved consequences, rather than spending a new campaign to rediscover
already understood source arithmetic or repeat accepted T79 fidelity work.
