# Readability options made concrete

The assembly-like Python is preserving effects that a football-only formula does not describe.
A practical route is to improve names and isolate a numerical core behind an explicit adapter,
then decide separately whether a different state representation is worth its proof cost.
This chapter compares alternatives against the [twelve obligations](rewrite-contract.md).

## How to read the sketches

These are **documentation pseudocode**, not a new backend, implementation prototype or measured
speed/readability result. “Before” is a normalized excerpt of the pinned operation, not the
entire port. “After” names a proposed organization. A source-pinned ledger records the omitted
machine work and retained counterexamples: [T110b-v2](../../notes/engine-study/T110/T110b-v2.json).
The [producer](../../notes/engine-study/T110/options.py) only assembles strings and copies old
evidence; it does not evaluate the sketches or invoke an engine.

Read the named original before the raw listing and port. The strength example follows named
seg_1771_03.c:377E, raw seg_1771_05.asm:377E..3821 and attributes.player_strength.
Movement follows named seg_0791_08.c:86D0/8889 and raw seg_0791_14.asm, with the existing T101
ledger. Match._advance supplies the host completion slice. All primary bytes are pinned at m7;
new T110a artifacts have separate exact hashes.

## Four representative changes

### record-view

Name shared storage while preserving the existing address calculation, aliasing, read width and write sites.

Before, normalized:

```text
off = (base_off + low_word(player_index * 0x14)) & 0xffff
raw_energy = mem.u8((seg << 4) + ((off + 0x0e) & 0xffff))
mem.w8((seg << 4) + ((off + 0x10) & 0xffff), status, at=writer_site)
```

Proposed organization:

```text
player = PlayerView.bind_same_pointer_and_index(memory, pointer, player_index)
raw_energy = player.read_u8(EnergyRaw)
player.write_u8(StatusRaw, status, at=writer_site)
# Every accessor delegates to the existing wrapped address and write hook.
```

**Counterexample:** With seg=0x2000, record offset=0xfffe and field offset4, the start address is0x20002, not0x30002. A detached copy also stops reflecting an overlapping write.

**Machine work retained:** No automatic cache refresh, field clamping, bit repacking, wide write substitution or re-resolution of a captured far pointer. Existing Rec behavior and writer-site identity remain in the adapter.

**Validation:** Exact Rec address/read/write tests and later full boundary traces; this sketch is not executed.

**Limits:** The example fixes the starting address only; backend semantics of a multi-byte read are retained. Immutable snapshots are useful only at an explicit effect-free boundary, not as implicit replacements for live views.

### strength-core

Express the finite arithmetic of377E as a numerical core while keeping unavailable/placement queries and machine effects in their original order.

Before, normalized:

```text
v = (p.u8(4) - 0x3e + (s8(p.u8(0x0e)) & 0xffff)) & 0xffff
c = s8(p.u8(0x0c))
if c >= 0x20:
    q, dx = idiv(s16(v), 0x10)
    v = (v - q) & 0xffff
else:
    v = (v + c) & 0xffff
# Signed clamp, original frame writes, placement query, optional halving follow.
```

Proposed organization:

```text
word = U16(U8(ability_raw) + I8(energy_raw) - 62)
if I8(form_raw) < 32:
    word = U16(word + I8(form_raw))
else:
    word = U16(word - trunc_toward_zero(I16(word), 16))
clamped_strength = clamp(I16(word), 0, 256)
# Adapter keeps unavailable query before this block, placement query after it,
# then halves when required and reproduces original registers/locals/sites.
```

**Counterexample:** Retained healthy/form32 rows give226 and183; form is not monotone across32. The clamp-before-placement row gives128. Clamping after halving or treating a byte as unsigned changes a branch.

**Machine work retained:** A scalar return is insufficient: the adapter may need intermediate words, quotient/remainder and branch information, or retain explicit original operations until full boundary equality is shown.

**Validation:** Reuse retained T98 cases, then require candidate-versus-accepted-port full boundary state/effect comparisons and independent original oracles before implementation claims.

**Limits:** Pseudocode below projects the numerical result only. The original wrapper's AX/DX, frame locals, caller-visible effects and exceptional behavior are not returned by this scalar sketch.

### occupancy-step

A named movement operation must retain per-attempt reset, character/attribute occupancy and conditional draw/effect ordering.

Before, normalized:

```text
current_word = old_drawn_word
apply_direction_byte_to_current()
if direction != 5:
    reject_if_outside_original_bounds()
    if live_and_ordinary_nonholder_nonchallenger:
        read_picture_character_and_attribute()
        reject_if_attribute_not_13_and_character_in_original_set()
#8889 draws rand(5) for each failure and calls this attempt again.
```

Proposed organization:

```text
repeat:
    candidate = step_from_same_drawn_position(direction)
    reproduce_original_attempt_writes_and_sites(candidate)  # before readers
    accepted = direction_is_standstill(direction)
    if not accepted:
        accepted = inside_original_bounds(candidate)
        if accepted and original_occupancy_guard_applies(player):
            accepted = picture_allows(character(candidate), attribute(candidate))
    retain_original_validation_helper_effects_and_return(accepted)
    if accepted: break
    direction = draw_main_rng(5)
# Retain the separate original sprite/background update after movement.
```

**Counterexample:** The retained blocked-step starts at[0,0], rejects[1,0] and accepts[0,1] after two main draws. Ignoring occupancy accepts[1,0] with one draw. Character1/attribute7 and character1/attribute13 differ.

**Machine work retained:** A pure legality predicate can help explanation, but candidate writes occur even on failure and reset from the drawn position every attempt. Preserve coordinate bounds, exemptions, packed bytes and restoration order; do not replace the picture with a boolean grid.

**Validation:** Reused T101 blocked-step/source controls; any later implementation needs ordered RNG, complete picture and write/site traces.

**Limits:** Supplied draw examples are not newly executed seeded fixtures. The sketch begins after8889's original target restriction/axis selection; it omits the update_player handler and energy tail.

### event-continuation

Name adapter phases while preserving pending event boundaries and F1F6-before-B7FA completion.

Before, normalized:

```text
stopped = machine.run(current_return_boundary)
clear_current_menu_context()
if stopped is not None: return
flush_pending_observed_writes()
if phase == 'run_match':
    capture_fixture_after()
    phase = 'player_update'
    call_original_boundary(B7FA)
else:
    phase = 'done'
    finish_public_result()
```

Proposed organization:

```text
stop = resume_current_phase_without_reordering_effects()
clear_current_menu_context()
if stop.is_event_or_decision: return_pending_boundary()
else:
    flush_pending_observed_writes()
    on_run_match_return: capture_fixture_then_enter_player_update()
    on_player_update_return: finish_public_result()
# Remaining events/answers/frames/records/RNG must reconstruct exactly on supported load.
```

**Counterexample:** Returning a completed result at the full-time board omits B7FA's later player update. Deferring events until result assembly loses their original write-time stamps. Match equality alone does not prove the #427 live-Core caller continuation.

**Machine work retained:** The host call stack is not automatically serializable. Queues, waiting/refused answers, replay origin/actions, guest frames and return addresses are representation work; an enum alone does not preserve them.

**Validation:** Existing whole-stream, answer/refusal and supported original-checkpoint comparisons; new phase representation needs its own complete reconstruction proof.

**Limits:** This is the admitted Match completion slice, not the full campaign router or a live-Core bridge. At m7 engine=port checkpoint save/load remains refused; no transition sketch implements T78c.

A snapshot is still useful when its read boundary and lifetime are deliberate. A shared
view and a snapshot answer different questions; do not turn a cached manager/placement value
into a property that silently recomputes it. Field names also need raw/signed distinctions.

The six copied strength examples are healthy226, form32183, upper-clamp256,
clamp-before-placement128, available-zero-strength0 and injured-zero-energy0. The last two
share a numerical result but have different branches. T98's376 reused original returns remain
a bounded historical numerical projection, not a new all-state proof from these sketches.
The blocked-step example retains its supplied draws and explicit synthetic/local scope.

## Four architecture options

| Option | Immediate readability value | State/effect work that remains |
| --- | --- | --- |
| memory-views | Replace repeated offsets with meaningful fields over existing Rec/Mem. | Wrapping, aliasing, unknown bytes, writer width/sites, cache lifetime. |
| pure-rules | Expose a deterministic numerical rule and its inputs. | Call order, intermediate words/registers, frame effects and original oracles. |
| explicit-transitions | Make phases, pending decisions and terminal conditions visible. | Suspended nested calls, queues, refusals, replay/checkpoint state and exact effect order. |
| semantic-rewrite | Use domain types and algorithms throughout. | Replacement of all relevant numeric, random, occupancy, continuation and external-observable semantics. |

### memory-views

**Benefit:** Expose field meaning while reusing existing Rec/Mem and precise effect adapters.

**Risk:** Copies, cache refreshes, packed-bit writes and accessor ordering can change storage semantics.

**Dependencies:** Field meanings/unknown bytes; Existing wrapping/view helpers; Boundary write/site tests.

**Contract:** Existing machine-boundary contract; extend names without adopting a weaker one.

### pure-rules

**Benefit:** Make a small deterministic numerical rule testable and readable apart from guest plumbing.

**Risk:** Inputs may be cached/context-dependent; a returned scalar omits frame/register/effect behavior.

**Dependencies:** Pure input/output boundary; Independent numerical oracle; An adapter whose required effects remain exact.

**Contract:** Existing boundary contract retained by a separately proved adapter; result-only parity is insufficient.

### explicit-transitions

**Benefit:** Make match phases and pending decisions inspectable and potentially serializable.

**Risk:** A phase enum hides nested generators, deferred events, menu/refusal state and original ordering.

**Dependencies:** Complete continuation model; Pending event/answer state; Checkpoint and replay proof.

**Contract:** Machine-boundary preservation unless the owner explicitly chooses a different public-API representation contract.

### semantic-rewrite

**Benefit:** Use domain records and algorithms throughout, potentially isolating all machine representation at adapters.

**Risk:** Highest risk of lost finite arithmetic, occupancy, RNG consumption, rare paths and external continuation behavior.

**Dependencies:** Explicit owner compatibility choice; Coverage and oracle inventory; Numeric/runtime replacement; End-to-end and downstream proof.

**Contract:** No automatic compatibility level: removing DOS state needs explicit owner scope; changed football semantics are a separate project.

## What remains to prove

These options are not mutually exclusive, but their obligations cannot be counted away as
“already ported.” m7 already has a plain-memory execution option and helpers; removing Unicorn
dependency is a different achievement from replacing its representation with domain code.

An in-place change should first preserve the accepted port's complete observed boundary
state/effects and retain independent original comparisons under the disclosed contract.
Existing scratch flags, launch residue #591, unvisited display paths and original-key gaps
remain limitations, not permission to weaken equality. A smaller domain model needs an
explicit owner contract and consumer audit before representation details can be dropped.

The [live-Core request #427](https://github.com/diegoami/goal2-archaeology/issues/427) is also
separate: Match's F1F6→B7FA adapter does not prove natural caller-frame or outer-news/tournament
continuation. No option above silently delivers that bridge, sealed records-only packaging,
T79's broad fidelity sheet or a scoring-effect estimate. T110c prices explicit work scopes,
states the assumptions and proposes a bounded future prototype for an owner decision.

The historical v1 ledger placed attempted-position writes after validation in its proposed
movement sketch. v2 corrects that order: original86D0 writes current position before bounds
and occupancy readers. Both old ledger and structural validation remain immutable; their
passing checks did not establish that the sketch preserved effect order.
