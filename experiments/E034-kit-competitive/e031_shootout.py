#!/usr/bin/env python3
"""E034: the kit's shoot-out against the original's own, as E031 saw it in DOSBox-X (an independently obtained run).

    python3 -B experiments/E034-kit-competitive/e031_shootout.py --out experiments/E034-kit-competitive/out/<new>.json

E031's session g1 kept a DOSBox-X savestate at the start of its last-16 shoot-out (Belgium v Holland, 2-2 after
extra time; release play-the-game-states, out/states.tsv, step 3874: the screen "penalty shoot out PRESS ANY KEY").
Its CPU is inside penalty_shootout 0791:A10A, in the message wait 214B:04F8 called at A132. This script walks the
savestate's BP chain to A10A's frame and run_match's, puts the CPU back at A10A's entry with A10A's own return
address on the stack (0C0B raises the speed byte, which A10A saves and restores and which changes no match; 2929
clears the pitch records' state bytes: running them again changes nothing the kicks read), and lets the kit run
the rest of the original's own call chain: the shoot-out, the full-time board, run_match's tail, its return to
route_fixture, then B7FA as the kit does. The managed side's order is E031's, read from E031's last order screen
(step 3932, and the 11th pick by Enter at 3933). The reference is E031's screens (out/g1/steps.jsonl and
screens.jsonl): the commentary panel's lines, merged over the screens from step 3933 to the end of the shoot-out.
The check: E031's lines are, in order, a subsequence of the kit's shoot-out commentary; the takers E031 saw
("<name> to shoot" or "shot from <name>") are the kit's kicks' takers in the same order; the goals E031 saw ("**** GOAL **** by") are
the kit's scored kicks."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))
from original_match import Image  # noqa: E402
from original_match import match as M  # noqa: E402
from original_match.machine import Machine, MEM_SIZE  # noqa: E402
from emul.watched_match import cpu_state  # noqa: E402

STATE = ROOT / ".cache" / "dl" / "3ea57029282b849f-g1-03874-shootout-start.sav"
STATE_SHA = "3ea57029282b849fd3114a995178f35e48c420c768f0702b9d3b7d48600dc1fc"
G1 = ROOT / "experiments" / "E031-play-the-game" / "out" / "g1"
ORDER_STEP, FIRST_KICK_STEP, LAST_STEP = 3932, 3933, 4640
MESSAGE_RETURN = "0791:A137"        # A10A's call of 214B:04F8 at A132
PANEL_ROWS, PANEL_COLS = (1, 2, 3), (32, 67)   # the commentary panel of the match screen, between the borders at
#                                                 columns 31 and 67 (E031 step 3933)


def e031_screens():
    screens = {}
    for line in (G1 / "screens.jsonl").open():
        r = json.loads(line)
        screens[r["digest"]] = r["text"]
    steps = {}
    for line in (G1 / "steps.jsonl").open():
        r = json.loads(line)
        steps[r["n"]] = r
    return steps, screens


def e031_order(steps, screens):
    """The numbered picks on E031's last order screen: [(k, shown name)] (the right column, ':X k')."""
    text = screens[steps[ORDER_STEP]["digest"]]
    picks = []
    for row in text.split("\n"):
        tail = row[63:]
        if ":" in tail and tail.rstrip()[-2:].strip().isdigit():
            name, k = tail[:tail.index(":")].strip(), int(tail.rstrip()[-2:])
            if name:
                picks.append((k, name))
    return sorted(picks)


def e031_lines(steps, screens):
    """The commentary panel's lines over E031's screens, merged where consecutive panels overlap."""
    seen, first = [], None
    for n in range(FIRST_KICK_STEP, LAST_STEP + 1):
        st = steps.get(n)
        if st is None or st["digest"] not in screens:
            continue
        rows = screens[st["digest"]].split("\n")
        if len(rows) < 4 or len(rows[1]) <= PANEL_COLS[1] or rows[1][PANEL_COLS[0] - 1] != "\u2502" \
                or rows[1][PANEL_COLS[1]] != "\u2502" or "versus" not in rows[2]:
            continue                              # not the match screen (row 2 holds 'versus' between the teams)
        teams = (rows[1][12:27], rows[3][12:27])  # the two names (the score beside them changes)
        first = first or teams
        if teams != first:
            break                                 # another match on the match screen (E031's next fixture)
        panel = [rows[r][PANEL_COLS[0]:PANEL_COLS[1]].strip() for r in PANEL_ROWS]
        panel = [p for p in panel if p]
        if not panel or not any(c.isalpha() for c in "".join(panel)):
            continue
        k = min(len(seen), len(panel))
        while k and seen[-k:] != panel[:k]:
            k -= 1
        seen.extend(panel[k:])
    return seen[seen.index("---- PENALTIES ----"):]      # the shoot-out's own lines


def frame_of(m, regs, ret):
    """The BP of the frame whose far return address is `ret` ('SSSS:OOOO'): found by scanning the savestate's stack
    from SP up for the address pair (the CPU is in the BIOS's key wait, below the game's frames, so there is no BP
    chain to walk from it); the frame's BP points at the saved BP just below the return address."""
    ss, sp = regs["SS"], regs["ESP"] & 0xFFFF
    seg, off = ret.split(":")
    want = (int(off, 16), m.seg(int(seg, 16)))
    hits = [a - 2 for a in range(sp, 0xFFFC, 2)
            if (m.word_at(ss * 16 + a), m.word_at(ss * 16 + a + 2)) == want]
    if len(hits) != 1:
        sys.exit(f"{len(hits)} frames return to {ret} on the savestate's stack (one is needed)")
    return hits[0]


def at_shootout(data):
    """A Match whose machine is at A10A's entry in E031's state, with the kit's state as a fresh match has it."""
    image = Image.from_savestate(data)
    regs = cpu_state(data)
    self = M.Match.__new__(M.Match)
    self.timeout_s = 60
    self.m = m = Machine(image.memory, image.load)
    self.image_header, self.image_tail = image.header, bytes(image.memory[MEM_SIZE:])
    self.image_sha256, self.inputs = image.sha256(), []
    msg_bp = frame_of(m, regs, MESSAGE_RETURN)            # 214B:04F8's frame: its saved BP is A10A's
    a10a_bp = m.word_at(regs["SS"] * 16 + msg_bp)
    run_bp = frame_of(m, regs, M.RUN_MATCH_RETURN)       # run_match's frame: its argument, the fixture
    fx_off = m.word_at(regs["SS"] * 16 + run_bp + 6)
    fx_seg = m.word_at(regs["SS"] * 16 + run_bp + 8)
    first, second = m.rd(0x9B34), m.rd(0x9B36)
    kind = m.read(fx_seg * 16 + fx_off + 2, 1)[0]
    managed = next(c for c in (first, second) if m.read(m.far(M.COUNTRIES_PTR) + M.COUNTRY_SIZE * c + M.MANAGER, 1)[0] > 0x80)
    self.opts = {"first": first, "second": second, "index": m.rd_far(M.GAME_PTR, 0x26), "managed": managed,
                 "captain": None, "seed": None, "ticks": False, "record_draws": False, "delay_byte": None,
                 "kind": kind, "substitutions": None}
    self.side = 0 if managed == first else 1
    self.fixture_ptr = (fx_seg, fx_off)
    self.st = M.fresh_state(self._players_now([first, second]))
    self.st.update(live=True, stage="extra_time", half_time_score=[0, 0], minute=m.rd(M.MINUTE),
                   score=[m.rd(M.SCORE, 1), m.rd(M.SCORE + 1, 1)])
    for team in (0, 1):            # the scorer rows the match wrote before the state was taken
        a = m.DS * 16 + M.SCORERS + M.SCORERS_SIDE * team
        self.st["scorers"][team] = [[m.word_at(a + 3 * k), m.read(a + 3 * k + 2, 1)[0]] for k in range(1, 12)
                                    if m.word_at(a + 3 * k)]
    self._queue, self._menu, self._result, self._names = [], None, None, None
    self._hooks()
    ss = regs["SS"]
    for name, value in (("ss", ss), ("sp", (a10a_bp + 2) & 0xFFFF), ("bp", m.word_at(ss * 16 + a10a_bp)),
                        ("ds", m.DS), ("es", m.DS), ("cs", m.seg(0x791)), ("eip", 0xA10A)):
        m.set_reg(name, value)
    self.end_lin = m.lin(M.RUN_MATCH_RETURN)
    return self, {"a10a_bp": a10a_bp, "run_match_bp": run_bp, "fixture": [fx_seg, fx_off], "kind": kind,
                  "first": first, "second": second, "managed": managed,
                  "a10a_returns_to": m.where(m.seg(0x791), m.word_at(ss * 16 + a10a_bp + 2))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    out = Path(ap.parse_args().out)
    if out.exists():
        sys.exit(f"{out} exists: never overwritten")
    data = STATE.read_bytes()
    if hashlib.sha256(data).hexdigest() != STATE_SHA:
        sys.exit(f"{STATE}: not the E031 state {STATE_SHA}")
    steps, screens = e031_screens()
    order_shown, lines_seen = e031_order(steps, screens), e031_lines(steps, screens)
    match, where = at_shootout(data)
    name = match._text()[0]
    events, order = [], None
    for ev in match.events():
        events.append(ev)
        if ev.kind == "decision":
            d = ev.data
            if d["context"] == "shootout_order":
                by_name = {name(w): w for w in d["available"]}
                order = []
                for _, shown in order_shown:
                    hits = [w for n, w in by_name.items() if shown.endswith(n) or shown.split()[-1] == n.split()[-1]]
                    if len(hits) != 1:
                        sys.exit(f"E031's pick {shown!r} matches {hits} of {sorted(by_name)}")
                    order.append(hits[0])
                match.answer(shootout_order=order)
            else:
                match.answer()
    r = match.result()
    so = [e for e in events if e.kind == "commentary" and any(x.kind == "shootout" for x in events[:events.index(e)])]
    kit_lines = [e.data["text"] for e in so]
    j, missing = 0, []
    for line in lines_seen:                       # E031's lines, in order, inside the kit's
        k = next((i for i in range(j, len(kit_lines)) if kit_lines[i] == line), None)
        if k is None:
            missing.append(line)
        else:
            j = k + 1
    kicks = r["shootout"]["kicks"] if r["shootout"] else []
    seen_takers = []                              # a kick's taker is named by "X to shoot" and "shot from X"; a
    for x in lines_seen:                          # screen sample may miss one of the two, never both here
        who = x[:-len(" to shoot")] if x.endswith(" to shoot") else x[len("shot from "):] if x.startswith(
            "shot from ") else None
        if who and (not seen_takers or seen_takers[-1] != who):
            seen_takers.append(who)
    seen_goals = [x.split(" by ", 1)[1] for x in lines_seen if x.startswith("**** GOAL **** by")]
    kit_takers = [k["name"] for k in kicks]
    kit_goals = [k["name"] for k in kicks if k["scored"]]
    report = {
        "state": STATE.name, "state_sha256": STATE_SHA, "where": where, "e031_order_screen": order_shown,
        "order_answered": order, "order_names": [name(w) for w in order or []],
        "e031_lines": lines_seen, "kit_shootout_lines": kit_lines,
        "e031_lines_not_in_kit_order": missing,
        "takers": {"e031": seen_takers, "kit": kit_takers, "equal": seen_takers == kit_takers},
        "goals": {"e031": seen_goals, "kit": kit_goals, "equal": seen_goals == kit_goals},
        "kit_kicks": [[k["team"], k["name"], k["scored"]] for k in kicks],
        "kit_result": {k: r[k] for k in ("score", "winner", "kind", "extra_time", "shootout")},
        "events": {k: sum(e.kind == k for e in events) for k in sorted({e.kind for e in events})},
    }
    report["pass"] = not missing and report["takers"]["equal"] and report["goals"]["equal"] and bool(kicks)
    with out.open("x") as f:
        json.dump(report, f, indent=1)
    print(json.dumps({k: report[k] for k in ("pass", "e031_lines_not_in_kit_order", "takers", "goals")}, indent=1)[:3000])


if __name__ == "__main__":
    main()
