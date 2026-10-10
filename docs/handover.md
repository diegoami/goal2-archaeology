# Session handover (goal2-archaeology, new machine)

Project-level only — no session-management notes. Pick one of Options A / B / C below.

## Wake-up (2 commands)

```bash
gh auth status                                    # confirm GitHub login
curl -sf localhost:8765/health                   # quota-tracker must be up
```

If either fails, do NOT dispatch — the harness's `quota-tracker recommend?tier=heavy`
falls back to `claude` (orchestrator family) when the quota-tracker is dead, which
breaks L27's heavy-review ladder.

## Live state at this handover

- `main` @ `d117509` = origin/main; clean working tree.
- **PR #112** OPEN (head `a8902df`, draft cleared). **Sol returned rework** with 2
  blocking findings, both R2-class:
  - **R1**: `scripted_keys.check_attribution` uses metadata-signature inequality, not
    per-request hash vs pre-send state. Sol fixture-demonstrates a later-bytes pass.
  - **R2**: 4 mutation shapes missing from `mutate_keys.py` (the `length > 0`
    mutation is the same class as R1).
- **#111** `status:rework`. The hand-over comment with the verbatim Sol review is
  on the issue.
- Worktrees at `~/goal2-archaeology-work/{T33,T34,T35}`:
  - **T33 + T34** carry uncommitted `.opencode/agents/{implementer,reviewer}.md`
    edits that belong to another session — **don't touch, don't stash, don't push**.
  - **T35** @ `a8902df`, branch `task/T35-request-attribution`. One uncommitted
    `runtime/human/recorder.py` (1-line privacy-test polish from round 2) and three
    untracked brief/log artifacts. **No `RUN-NOTES.md`** (round-3 mimo-pro had the
    pre-`d117509` prompt).

## Resources to read first

- `docs/running-notes.md` — live convention; `RUN-NOTES.md` at worktree root, git-
  ignored via the **shared** exclude (already applied); four rules incl.
  `git check-ignore -q RUN-NOTES.md` verify-or-stop.
- `scratch/briefs/T35-r3-brief.md` — T35 round-3 brief, **placeholders already
  filled** (PR #112, SHA `a8902df`, round-2 wall-clock kill, orphan patch path).
- `scratch/T35-other-session.patch` — orphan's converging design from rounds 1+2 (415
  lines; weigh, don't apply blindly).
- `docs/process.md`, `harness.json`, `docs/running-notes.md` — read before any dispatch.
- Six more briefs (`T36-stall-detection.md`, `T37-running-notes.md`, the simple +
  generic + delta RUN-NOTES variants) are queued for after T35 closes.

## Pick ONE next action

**Option A — finish T35.** Per L38 the next implementer moves up: `mimo-flash` and
`mimo-pro` (mimo family) have had their rounds. Next step on the ladder is `gpt-6.1-sol`
(openai) or `mm-m3` (minimax). Confirm with `quota-tracker recommend?tier=heavy` →
`pair.implementer` (family-rule preserved). Edit `T35-r3-brief.md` Implementer/Reviewer
lines and dispatch.

**Option B — start T36.** Stall detection (no-edit-or-commit + bash-non-trivial +
output-sanity). Land in one round on `mimo-flash`. Brief at
`scratch/briefs/T36-stall-detection.md`. Saves future rounds from mimo-pro-style
40-min analysis-only stalls.

**Option C — merge `a8902df` as best-effort.** Carries the R1 byte-hash-binding bug
Sol flagged. Only with explicit owner sign-off.

## Don'ts

- Don't push from T33 / T34 worktrees (their uncommitted `.opencode/agents/` edits
  belong to another session).
- Don't re-dispatch `mimo-pro` on T35 again — it took 40 minutes, 0 commits; it's had
  its chance.
- Don't set `claude` as an implementer fallback when other families are tight —
  `claude` is the orchestrator's family (L27).
- Don't merge `a8902df` without closing R1 + R2 (Option C).
- Don't write `.git/info/exclude` from inside a worktree (`.git` is a file there).

## Live references

- Handover comment on #111: `…/issues/111#issuecomment-6090303033`
- PR #112: `…/pull/112`
- Branch: `task/T35-request-attribution`
