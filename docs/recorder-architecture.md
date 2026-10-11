# Recorder architecture

> Purpose: name the boundary between the parts of the GOAL2 recorder that are game-agnostic
> and the parts that are GOAL2-specific, so the next DOS game on DOSBox-X (or the owner of a
> second title) sees exactly what to reuse, copy, or write.

## Three layers, one worktree

```
                           ┌──────────────────────────────────────────────────────────┐
                           │ Experiment (one per game)                                │
                           │   experiments/<E>-<slug>/{extract,keymap,mutate_keys}.py │
                           │     • screen digest                                       │
                           │     • expected screen/key map                            │
                           │     • reproducible scripted sittings                      │
                           └──────────────────────────────────────────────────────────┘
                                          ▲                          ▲
                                          │                          │
                              screen digest│                          │expected-map shape
                                          │                          │
                           ┌──────────────┴──────────────────────────┴───────────────┐
                           │ Game plugin (today: GOAL2)                              │
                           │   • plugins/goal2/ — or, today,                        │
                           │     runtime/driver/savestate.py (G1), the "screen      │
                           │     digest" wrapper around screen text, and the       │
                           │     bit that emits the human-readable headlines        │
                           └────────────────────────────────────────────────────────┘
                                          ▲                          ▲
                                          │                          │
                                       file│                        bytes│strings
                                          │                          │
                           ┌──────────────┴──────────────────────────┴───────────────┐
                           │ Recorder core (game-agnostic)                           │
                           │   runtime/human/recorder.py                              │
                           │     • file_signature (inode,size,mtime,ctime)           │
                           │     • staged-capture gate (inotify, single writer)      │
                           │     • per-request path                                   │
                           │     • request ownership / _fast_consumed ledger         │
                           │     • stability fallback (never reads live on fast)     │
                           │   runtime/human/play.sh (Xephyr, dosbox-x wrapper)      │
                           │   experiments/E015-human-playthrough/scripted_keys.py  │
                           │     • check_attribution (recorder self-invariant)       │
                           │     • check_request_windows (recorder self-invariant)   │
                           │     • burst, mapped-coverage checks                      │
                           └──────────────────────────────────────────────────────────┘
```

## What's in the recorder core

`runtime/human/recorder.py` is game-agnostic. Everything it does is in terms of a file, a
file signature, and a sequence of writes — never GOAL2's screen text, GOAL2's savestate byte
layout, or any UI. Concretely:

- `file_signature(path)` — `inode, size, mtime_ns, ctime_ns`; metadata only, never reads bytes.
- The capture loop polls the file's signature until it differs from `pre_sig`, the signature
  taken before the key was sent. If no fresh signature appears, retry until the deadline.
- `_fast_consumed` — the `(events, sig)` ledger that orders overlapping saves; nothing in
  here is GOAL2.
- The "fresh arrival" path (T35 R1 fix): a capture is the pipeline's head when it began
  (`entry_head`), or the pipeline has already ordered the saves by consumption
  (`_fast_consumed is not None`). Otherwise `_AttributionLost`. This is a property of the
  recorder's invariants, not of any game.
- The stability fallback: after the fast path gives up, the only source the fallback may read
  is the per-request path (the bytes the recorder itself wrote at acceptance). It never reads
  the live savestate — because the live savestate says nothing about whose save is on it
  (T35 R1 hazard; the r4 Sol review surfaced this and T35 closed it).
- `note_request(request, sent, origin, seq, superseded=False, pre_sig=None, accept_sig=None)`
  is the request-line writer (T35 R2 added `pre_sig`). It writes the per-request path bytes
  under `req_path`; that's the single source of truth the staging reads back.

`runtime/human/play.sh` is also game-agnostic. The interesting generic pieces:

- Spawns DOSBox-X on a private nested X server (Xephyr), so a key logger attached to that
  display only sees what was typed into the game. Other programs are not on the display and
  cannot be captured — a structural guarantee, not a filter.
- The 20-second snapshot cadence is a TODO for replays; can move to a config flag.
- Single writer; inotify write-session gate; live savestate never staged while a write is open.
- Optional `--video` records the Xephyr window, not the owner's desktop.

## What's a recorder self-invariant (the guard layer)

`experiments/E015-human-playthrough/scripted_keys.py`'s `check_attribution`,
`check_request_windows`, the burst-count check, and the mapped-coverage check are
recorder-level guarantees. They take a screen digest as a key, but the shape of each check is
generic. They're all about: "did the recorder prove ownership of the bytes it staged, did it
miss a request, did it count bursts correctly, did every screen have keys that produced it?"

The T35 follow-up (PR #106 + #112) made those guards real — the absent-of-`superseded` guard
became "per-request path hash matches `pre_sig`", and the stability-fallback's "fall back to
the live savestate" became "never read the live savestate on the fast path".

## The coaching kit: pause, notes, live view (T39b)

The owner coaches the main session while playing; three pieces serve that, all game-agnostic:

- **Pause.** The session's mapper file (`mapper.map`, the one the G1 config's `[sdl] mapperfile`
  names) is DOSBox-X 2024.03.01's complete default bind set, saved by its own mapper editor
  (`runtime/human/dosbox-x-2024.03.01-default.map`, checked by sha256), with `hand_pause` also on
  F12+P (taken from the screenshot event). The file must be complete: a mapper file DOSBox-X finds
  replaces its default binds. DOSBox-X's pause ends on the Pause key only (an XTEST Pause with the
  window focused or an XSendEvent Pause; `T39b-probe-resume-20261011-01.log`), so F12+P typed
  while paused makes the recorder press Pause itself (XTEST, the window focused), marked `by:
  recorder` in `keys.jsonl` (however late the logger delivers it: an injection never expires) and
  left out of the owner's presses and bursts. Only a fresh P press resumes: the held pausing P and
  its autorepeat never do. A title that cannot be read is "unknown", and holds every send until a
  read answers. The extraction can name other injected keys (`extract.py --injected`). The pause swallows every key and
  every save request while it lasts (none is deferred), and appends ` PAUSED` to the window
  title (`experiments/E015-human-playthrough/T39b-probe-pause-20261011-01.log`). The watcher reads
  the pause from that title — after every key event, every `PAUSE_POLL_S` and again right before
  every send — logs each pause and resume to `pauses.jsonl`, sends no save request while paused
  (cadence ticks inside the pause are skipped; key groups wait), requests the pause's snapshot
  (`origin: resume`) right after the resume, never re-sends a request a pause followed, and
  refuses (superseded) a write past the event count at a pause that began after its request:
  such a write landed after the resume. `keymap.py` counts a paused span as no time in its
  quiet-gap rule.
- **A clean end.** Closing the window ends Xephyr, and the key logger on its display ends first:
  the loop ends the sitting (no key may go unlogged) and `play()` names it `window-closed` when
  DOSBox-X has exited, `key-logger-stopped` when not. Any error still writes `ended` and
  `stop_reason` to `meta.json` and its traceback to `session.log`.
- **Saved games.** `play.sh` copies the newest `.GL` of the previous sessions (or `--load FILE.GL`;
  `--fresh` none) into the session's game copy before launch and records it in `meta.json`.
- **Notes.** `runtime/human/note.py <session> "text"` appends UTC, the monotonic clock and the
  text to `notes.jsonl`; `extract.py` places each note, and each pause and resume, between the
  two states whose screens (their request windows) it falls between.
- **Live view.** `runtime/human/live.py <session>` prints the newest staged snapshot's screen and
  the keys since its previous call; it only reads the session (its key cursor lives in
  `scratch/human/live/`).

None of the three adds a reader of the outer display: the title is the nested display's game
window, and a note is text passed on the command line.

## What's GOAL2-specific (today's plugin)

This is everything the recorder delegates to because GOAL2 has a specific byte layout and a
specific text-screen space:

- `runtime/driver/savestate.py`'s G1 driver — reads GOAL2's savestate byte layout. Replace with
  one driver per game.
- `experiments/E015-human-playthrough/keymap.py` — reads a session (snapshots, index,
  `keys.jsonl`) and emits the screen/key map. The screen digest (a hash of the screen text +
  a readable headline) and the expected transitions are GOAL2's. Replace with one
  `extract.py` per game.
- The 8a09 / acceptance scenarios in `tests/test_human_record.py` reference GOAL2 screens.
  Each game's plugin would carry its own.

A concrete cut: replace `runtime/driver/savestate.py` with a `savestate_*.py` strategy behind
an interface; have `play.sh` take a `--savestate-driver` flag. Move the G1 driver to
`plugins/goal2/` (or an `examples/goal2/`.)

## What's reusable across the project (process, not code)

The orthogonal-layers lesson (process.md §2, commit 21fb3d2; documented in
`goal2-archaeology-work/lessons/T34-too-big-split-by-orthogonal-layer.md` and
`memory/task-sizing-by-orthogonal-layer.md`) — split each task by orthogonal layer, one PR per
layer, Done-when is per-layer. T34 conflated 5 layers and the rework rounds each surfaced a
defect in a different layer; T35 is the first sub-task of that per-layer split.

Static first (U32, CLAUDE.md rule 22) — the named view
`static/goal-exe/named/{seg_*.c, scan.c}` is the recorder plugin's source for cross-checks;
the recorder's correctness is partly a function of getting the byte-layout right against the
decompiled output, not just running the game.

Evidence as release assets (CLAUDE.md rule 20) — every measured output (run records, probe
logs, timings) under a tracked path, never deleted or overwritten, originals out and hashed.
The recorder's immutable records are an instance of this — the run/1 record is the artefact
that another game's plugin would also produce, in the same shape.

The implementer/reviewer family rule (L27) — the recorder's correctness depends on a
non-implementer-family reviewer auditing the request-attribution logic every time; the
defects in T34 each came from a reviewer's family finding what the implementer's missed.

## Constraints if we package it (the question that prompted this doc)

These are real, and they all have answers, but none of them are reasons not to do it:

- **Vendoring**: the repo is a flat research tree. A library extraction adds a top-level
  `recorder/` (or `pyproject.toml`'s `[tool.hatch.build.targets.wheel]` only-include). In-tree
  callers switch from `from runtime.human import ...` to `from recorder import ...`.
- **Tests**: the recorder's own suite gets stub fixtures (a temp file a fixture producer
  writes; no DOSBox-X). `tests/test_human_record.py` and `tests/test_human_keys.py` are
  close to portable as-is; the Xephyr cases stay in `tests/static` and out of the package.
- **Extras**: `recorder[xvfb]` depends on `xvfbwrapper`, `python-xlib`, `python-evdev`.
- **Distribution**: **private** (CLAUDE.md rule 18 — GOAL2 is private; a public wheel would
  leak fixtures and the byte-layout references). The package's own tests use generic
  fixtures; the GOAL2 plugin and its fixtures stay in this repo under `experiments/E015/` or
  a private `plugins/goal2/`.
- **SemVer**: 0.x until T35's R1+R2 land and the package has been used by a second game;
  1.0 then.
- **Effort**: ~half a session for the extraction itself; the boundary doc you're reading is
  the first step.

## What's *not* in scope for the extraction (yet)

- Replaying a session's keys into the game (a T34 hazard, deferred to a future task).
- The bot that plays GOAL2 autonomously (different problem; uses a different driver).
- Sharing `play.sh`'s Xephyr nest script across games (the recipe is reusable but each game's
  binary paths and savestate paths differ; keep `play.sh` per-game until a second game
  asks for it).

## Where the cut goes today

Even without an extraction, the boundary is in the code:

- A reviewer reading `runtime/human/recorder.py` for a defect can do so without ever reading a
  byte of GOAL2's screen text.
- A new plugin for game X can write its own extract/keymap and read its own savestate bytes
  without changing recorder.py.
- The four-guard CI framework (`check_attribution`, `check_request_windows`, burst,
  mapped-coverage) is independent of any game's text.

The next concrete step, after T35 merges, is to formalise that boundary in code (the strategy
pattern for the savestate reader, the entry point behind a `recorder.record()` console_script,
the exclusion of GOAL2-only fixtures from the wheel). The doc exists so that step has
something to refer back to.
