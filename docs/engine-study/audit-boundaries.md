# Which observed differences can reach a caller?

The wall arithmetic flags are overwritten before the ordinary tick continuation uses them.
The fifteen differing launch-stack bytes are observed callee-frame residue with a plausible
sound-boundary explanation, but a complete transitive liveness argument is still absent.
Neither result establishes a new field/ABI port defect. These source-based attributions remain
proposed until independent ES-R3 review.

The [four-candidate ledger](../../notes/engine-study/T109/T109a-v1.json) and
[source reproducer](../../notes/engine-study/T109/boundaries.py) retain the ten direct launch
call sites, frame arithmetic, T106 comparisons and 24 literal instruction expectations. The
corresponding altered-listing negatives check those expectations independently of the authored
candidate descriptions. Record/schema controls establish completeness, not semantic truth.
This audit makes no new original/port call and changes no production code or comparison mask.

## Observed residue and frame arithmetic

In each T106 launch baseline, all selected field values, declared return ABI and captured
registers match. Full memory differs at fifteen offsets below entry SP=3F00 and returned
SP=3F0C: SS:3EDE,3EE0..3EE2,3EE4,3EE6..3EEF. These bytes remain part of the unmasked
physical comparison. Calling them deallocated at this return does not prove no later code
can observe them through an alias or reused, uninitialised local.

The source supplies a specific candidate explanation. `34C1` pushes BP and allocates six
local bytes. Near its tail it pushes two words and calls far `214B:1EA1` at `3837`.
The native sound routine calls frequency setup `1EBC`, busy-wait `1E09` and speaker-off
`1E8D`, even with the speaker muted. Muting suppresses hardware work, not those frames.
The production T73 `1EA1` entry is an explicit void stub and does not make those nested calls.

| Frame point with synthetic launch entry SP=3F00 | SP/BP offset |
| --- | --- |
| Native sound entry | 3EF0 |
| Sound BP after saving caller BP | 3EEE |
| Native delay entry after argument and far return | 3EE8 |
| Delay BP | 3EE6 |
| Delay's eight-byte local bottom | 3EDE |

This region contains every differing byte. The retained raw comparisons do not identify the
last native writer for each byte and there was no isolated ablation of just this body. Thus
the frame calculation is a source-supported explanation consistent with the observations,
not complete causal isolation. The separate production `1E09` port preserves its completed
busy-wait frame when entered directly; that does not make an omitted parent `1EA1` execute it.

## Wall flags at the ordinary continuation

The fifteen wall baseline pairs match every memory byte and the declared return ABI,
including direction flag. Arithmetic EFLAGS differ; near slot 18 has original 0x246 versus
port 0x293. Existing `port/runtime.py` documents scratch arithmetic flags unless a caller
needs them. The actual caller is decisive, not that policy sentence alone.

The only literal direct `7621` call in segment 0791 is `8BB0`, under player update `8AE9`.
On return, `8BB3` pushes BP and `8BB4` calls the nested movement step `8889`. Its prologue is
`PUSH BP; MOV BP,SP; SUB SP,2`. `SUB` replaces the arithmetic flags without reading their
old values. `888F` then compares DS:8302 with zero before the first conditional at `8894`.
Neither push, move nor call consumes inherited arithmetic flags. Direction flag is unaffected
by these instructions and was equal in the observed pairs.

This proves the ordinary local continuation does not use those returned arithmetic flags.
It does not establish all-register equality, an arbitrary external caller contract, or dynamic
coverage of `8889` by these bare wall calls. The difference remains disclosed in T106.

## Direct callers and unresolved boundaries

The raw segment-0791 census finds ten direct launch calls: `3932`, `3944`, `3B73`, `3BCE`,
`3CC1`, `3E80`, `3F8B`, `406C`, `5EA2` and `6AE1`. The ledger retains eight lexical successor
instructions for each, without pretending every successor lies on the executed path.
For example, `3935` jumps to `3947`; `3B76` sets flight then compares the receiver;
`3CC4` loads the caller's event local before commentary; `5EA5` immediately restores its
frame and returns. These windows show context, not a complete alias or data-flow proof.

The launch routine itself continues through `333F` and its own epilogue. The caller windows
do not establish that a later nested routine cannot reuse a residual word without writing it.
They also do not exclude an indirect call or a caller forwarding scratch flags through its
return. No launch register difference was observed in the three tested pairs, so this is a
limit on a global claim, not evidence of a second register bug.

[Issue #591](https://github.com/diegoami/goal2-archaeology/issues/591) therefore stays open for
full caller/alias liveness or a justified sensitive continuation if the chosen compatibility
contract requires it. No new run is necessary to retain this honest unresolved classification.
Historical T73 ALL equality still covers its recorded families and boundaries; it cannot erase
a mismatching bare-call result. Conversely, that result alone does not invalidate the historical
family comparison. [Issue #416](https://github.com/diegoami/goal2-archaeology/issues/416) retains
the separate unvisited stateful-display boundary question. Zero historical entries prove neither
unreachability nor removability, and its historical counts are not a fresh census here.
