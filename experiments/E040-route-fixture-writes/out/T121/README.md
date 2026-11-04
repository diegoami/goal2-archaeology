# T121 fixture routing

[confirmed: F010, F030, F039; upstream ab6ade71 and the listing addresses in
`runtime/original_match/port/route.py`]. The ten routines are translated with
`Regs` and guest calls; `F1F6` stays Match's sealed boundary and `4E0E` stays the
original's until T122. The six news helpers include both mandatory `6685`
`214B:06B1(3)` draws. The annotations add names for the previously unnamed news
layout helpers; the named view is regenerated with Ghidra 12.1.4.

The proof uses the existing runner, for example:

```
source .cache/cloud.env
tools/heavy.sh t121-proof -- python3 -B experiments/E040-route-fixture-writes/prove.py \
  --ports route,silent --out experiments/E040-route-fixture-writes/out/T121
```

[designed: T121] The runner retains T120's outer and inner passes. With route
installed, the inner pass also omits `6CA7` and `6685`, so the original wrappers
call the individual ports. Every call must be proved or nested; the outer pass
must finish exactly one `6CA7` proof before the harness returns. The unit test
also proves E80D alone with the original 6C21. A separate original-backed
E80D leaf test answers both Y and N through the Route key policy, using the
call frame transcribed from 6C21 (SP3EB2, BP3EC0, return 000E:6C71).

The existing `bb2f` and `silent-kind-0` inputs remain. Two additional declared
synthetic cases reach the task's branches without claiming them as published
play: `news-cb` takes E040-r0004's first silent fixture, changes kind 1 to 203,
and moves the exclusive calendar end to 2, so that one completed fixture reaches
6685 without a managed match. `finals-3` takes E040-r0010's managed fixture 22,
changing kind 2 to 3 to visit the finals mark. Each old byte is checked and each
edit is recorded. Originals and states remain release assets, not tree files.

[derived: T121; route.py's 6F18 and port/guest.py's Call] A translated caller
jumps directly to F1F6, bypassing the call instruction 6F18. The optional harness
`match_entry=True` therefore performs the same Match handoff at the real F1F6
entry, with the far-call frame already on the guest stack. Both proof runs
visit that same site, so Prover replays the handoff's complete writes and
register changes. The input comparison still checks all memory against Match's
constructor; the returned SS/SP/BP/DS and destination are checked. The default
harness continues stopping at 6F18. A return hook lets Prover finish the outer
call before the harness stops (Unicorn's `until` stops before hooks).

The falsifiers are `route.finals-mark-dropped`,
`route.confidence-managed-only` and `route.news-second-draw-dropped`.

Model: Codex GPT-6 (inherited session model).
