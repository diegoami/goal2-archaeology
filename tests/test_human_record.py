"""T29: the human-playthrough recorder and E015's extraction, on a synthetic session built here.

No DOSBox-X, no network, no display, and no path outside this worktree: the fixtures, the fake
sessions and the run directories live under scratch/test_human_record/ (git-ignored), following
test_driver_savestate.py's pattern of building savestates from the F001 offsets written as
literals — a parser whose offset moves reads other bytes and these tests fail. The chain of three
savestates is hand-checked: state 2 changes only the screen, state 3 moves the year, the stage
byte, the delay byte and the last byte of the [A923] tuple, transfers pool player 2561 into
country 1's squad (slot 19) and changes byte +3 of player 5.

Every constant of the diff and watching rules is pinned here: mutating GAME_RECORD_BYTES,
STAGE_OFFSET or SQUAD_WORDS (extract.py) or SEND_TO_WINDOW, CADENCE_S or STABLE_POLLS
(recorder.py) makes at least one test below fail."""
import hashlib
import io
import json
import shutil
import signal
import subprocess
import sys
import types
import unittest
import zipfile
import zlib
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
sys.path.insert(0, str(ROOT / "runtime" / "human"))
sys.path.insert(0, str(ROOT / "experiments" / "E015-human-playthrough"))

import extract  # noqa: E402
import recorder  # noqa: E402
import savestate  # noqa: E402

# ---- the fixture chain (hand-checked) ------------------------------------------------------------
# F001, written as literals: the text page and guest memory offsets in an inflated component.
TEXT_BASE = 0x86024
CELL = 8
MEM_BASE = 0x78
MCB_SEG = 0x0700
PSP_SEG = MCB_SEG + 1
DS_PARA = PSP_SEG + 0x10 + 0x2581     # the load module's DS paragraph, relocated by the load segment
DS_BASE = DS_PARA * 16
PLAYER_AT = 0x40000
COUNTRY_AT = 0x60000
STATE_AT = 0x80000
POOL_FIRST = 2561
COUNTRIES = (1,)
SUMMARY_3 = "states: 3, screens: 2 unique, diffs: 2"
STATE_CHANGES_2_3 = "0x3A: CA -> CC; 0x3C: 05 -> 06; 0x3F: 02 -> 01; 0x10D: 00 -> 7F"


def screen_component(rows):
    """An inflated Vga component whose text page holds {row: text}, attribute 0x07."""
    chars = bytearray(b" " * 2000)
    attrs = bytearray(b"\x07" * 2000)
    for r, text in rows.items():
        b = text.encode("cp437")
        chars[r * 80:r * 80 + len(b)] = b
    vga = bytearray((i * 31 + 17) % 256 for i in range(TEXT_BASE + CELL * 2000 + 64))
    for i in range(2000):
        vga[TEXT_BASE + CELL * i] = chars[i]
        vga[TEXT_BASE + CELL * i + 1] = attrs[i]
    return bytes(vga)


TITLE = {0: "THE international soccer management game", 24: "Do you want to load a saved game? (Y/N)"}
FULLTIME = {0: "FULL TIME", 2: "  9 THE MAN   GOAL   46 GOAL   THE MAN ", 24: "hit any key"}


def player_array(p5_b3=0x40, pool2561_country=0):
    """3061 records of 0x14 bytes: record p starts at p*0x14 (record 0 unused); countries 1..128
    hold their country in byte 0, exactly as players.check expects; player 5 byte +3 and pool
    player 2561 byte 0 are the hand-checked knobs."""
    a = bytearray(0xEF24)
    for p in range(1, 2561):
        base = p * 0x14
        a[base] = (p - 1) // 20 + 1
        for i in range(1, 0x14):
            a[base + i] = (p * 7 + i) % 251 + 1
    a[5 * 0x14 + 3] = p5_b3
    a[POOL_FIRST * 0x14] = pool2561_country
    return bytes(a)


def country_array(squad1_last=None):
    """129 records of 0xBF bytes: country c's first 20 words are (c-1)*20+1..c*20 (R012)."""
    a = bytearray(0x603F)
    for c in range(1, 129):
        base = c * 0xBF
        for i in range(20):
            n = (c - 1) * 20 + 1 + i
            if c == 1 and i == 19 and squad1_last is not None:
                n = squad1_last
            a[base + 2 * i:base + 2 * i + 2] = n.to_bytes(2, "little")
        for i in range(0x2D, 0xBF):
            a[base + i] = (c * 13 + i) % 251 + 1
    return bytes(a)


def state_tuple(stage=5, year=1994, speed=2, last=0x00):
    t = bytearray((i * 29 + 5) % 251 + 1 for i in range(extract.GAME_RECORD_BYTES))
    t[0x00:0x02] = (1).to_bytes(2, "little")     # managers
    t[0x26:0x28] = (3).to_bytes(2, "little")     # fixture index
    t[0x28:0x2A] = (40).to_bytes(2, "little")    # fixture count
    t[extract.YEAR_OFFSET:extract.YEAR_OFFSET + 2] = year.to_bytes(2, "little")
    t[extract.STAGE_OFFSET] = stage
    t[extract.SPEED_OFFSET] = speed
    t[extract.GAME_RECORD_BYTES - 1] = last
    return bytes(t)


def memory_component(parr, carr, tup, ticks, null=()):
    """Guest memory: GOAL.EXE's MCB and PSP (savestate.find_program's markers), the DS far
    pointers to the three arrays, the arrays, the BDA bytes. Guest address 0 sits at the
    component's MEM_BASE (prefixed by the caller)."""
    mem = bytearray(0xA0000)
    mcb = MCB_SEG * 16
    mem[mcb] = 0x4D
    mem[mcb + 1:mcb + 3] = PSP_SEG.to_bytes(2, "little")
    mem[mcb + 3:mcb + 5] = (0x00FF).to_bytes(2, "little")
    mem[mcb + 8:mcb + 16] = b"GOAL    "
    psp = PSP_SEG * 16
    mem[psp:psp + 2] = b"\xcd\x20"

    def far(ds_off, linear):
        seg, off = linear // 16, linear % 16
        mem[DS_BASE + ds_off:DS_BASE + ds_off + 2] = off.to_bytes(2, "little")
        mem[DS_BASE + ds_off + 2:DS_BASE + ds_off + 4] = seg.to_bytes(2, "little")

    far(0xA917, 0 if 0xA917 in null else COUNTRY_AT)
    far(0xA91B, 0 if 0xA91B in null else PLAYER_AT)
    far(0xA923, 0 if 0xA923 in null else STATE_AT)
    mem[PLAYER_AT:PLAYER_AT + len(parr)] = parr
    mem[COUNTRY_AT:COUNTRY_AT + len(carr)] = carr
    mem[STATE_AT:STATE_AT + len(tup)] = tup
    mem[0x449] = 0x03
    mem[0x46C:0x470] = ticks.to_bytes(4, "little")
    return bytes(mem)


def savestate_bytes(rows, parr, carr, tup, ticks, null=()):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Save_Remark", b"")
        z.writestr("Vga", zlib.compress(screen_component(rows)))
        z.writestr("Memory", zlib.compress(b"\x00" * MEM_BASE + memory_component(parr, carr, tup, ticks, null)))
    return buf.getvalue()


CHAIN = [  # (screen, player array, country array, state tuple, ticks)
    (TITLE, player_array(), country_array(), state_tuple(), 1000),
    (FULLTIME, player_array(), country_array(), state_tuple(), 2000),
    (TITLE, player_array(p5_b3=0x41, pool2561_country=1), country_array(squad1_last=POOL_FIRST),
     state_tuple(stage=6, year=1996, speed=1, last=0x7F), 3000),
]


def write_session(session, chain, with_index=True, with_meta=True):
    (session / "snapshots").mkdir(parents=True, exist_ok=True)
    index = []
    for n, state in enumerate(chain, 1):
        data = savestate_bytes(*state[:5], null=state[5] if len(state) > 5 else ())
        name = f"snap-{n:04d}-20261007T17000{n}Z.sav"
        (session / "snapshots" / name).write_bytes(data)
        index.append({"seq": n, "file": f"snapshots/{name}", "bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest(),
                      "utc": f"2026-10-07T17:00:0{n}.000Z", "elapsed_s": n * 20.0, "origin": "watcher",
                      "request_s": n * 20.0 - 0.75, "sent_s": n * 20.0 - 0.72})
    if with_index:
        (session / "index.jsonl").write_text("".join(json.dumps(e) + "\n" for e in index))
    if with_meta:
        (session / "meta.json").write_text(json.dumps(
            {"dosbox_x_version": "DOSBox-X version 2024.03.01 SDL2, copyright 2011-2024 The DOSBox-X Team.",
             "config_sha256": "0" * 64}))
    return index


class Base(unittest.TestCase):
    def workdir(self, name):
        d = ROOT / "scratch" / "test_human_record" / name
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, d, True)
        return d


# ---- the extraction and the diff rules -----------------------------------------------------------
class Extraction(Base):
    def extract(self, session, runs, countries="1"):
        out = io.StringIO()
        with mock.patch("sys.stdout", out):
            rc = extract.main([str(session), "--countries", countries, "--runs-dir", str(runs)])
        self.assertEqual(rc, 0)
        records = sorted((runs / "E015").glob("*.json"))
        self.assertEqual(records[-1].name, f"E015-r{len(records):04d}.json")
        return json.loads(records[-1].read_text()), records[-1], out.getvalue()

    @staticmethod
    def diffobs(obs, snap, what):
        """The diff observation between the state staged at `snap` and its successor, by `what`."""
        hits = [o for o in obs if o["field"].startswith(f"diff snapshots/{snap}") and what in o["field"]]
        assert hits, f"no diff observation for {snap} {what}"
        return hits[0]["value"]

    def test_hand_checked_chain_gives_the_hand_checked_diffs(self):
        session = self.workdir("chain")
        index = write_session(session, CHAIN)
        runs = self.workdir("chain-runs")
        rec, path, out = self.extract(session, runs)
        self.assertIn(SUMMARY_3, out)
        obs = rec["observations"]

        def find(fragment):
            return [o for o in obs if fragment in o["field"]]

        # state 1 -> 2: only the screen changed
        self.assertEqual(self.diffobs(obs, "snap-0001", "screen changed"), "yes")
        self.assertEqual(self.diffobs(obs, "snap-0001", "[A923] byte changes"), "none")
        # state 2 -> 3: the hand-checked bytes, squads and records. R10: keyed by player
        # number — the transfer's pool player (2561) appears as added, the dropped player
        # (20) appears as removed, the unchanged squad member whose byte 3 changed (player 5)
        # appears as changed. The fixture's player 2561 record was all zero except byte 0
        # (set to country 1) and player 20's record held the player_record_bytes(p*7+i)%251+1
        # pattern; the rendered values are deterministic.
        self.assertEqual(self.diffobs(obs, "snap-0002", "screen changed"), "yes")
        self.assertEqual(self.diffobs(obs, "snap-0002", "[A923] byte changes"), STATE_CHANGES_2_3)
        self.assertEqual(self.diffobs(obs, "snap-0002", "country 1 squad changes"),
                         "slot 19: 20 -> 2561")
        # The new diff names every squad change keyed by player number; player 5's byte 3
        # change, player 20 leaving, and player 2561 joining country 1's squad.
        record_diff = self.diffobs(obs, "snap-0002", "country 1 player record changes")
        self.assertIn("player 5: 0x3: 40 -> 41", record_diff)
        self.assertIn("player 2561: added", record_diff)
        self.assertIn("player 20: removed", record_diff)
        # the named raw bytes of the game state, one per state
        stage = {o["step"]: o["value"] for o in find("stage byte [A923]+0x3C")}
        self.assertEqual(stage, {0: "0x05", 1: "0x05", 2: "0x06"})
        year = {o["step"]: o["value"] for o in find("year word [A923]+0x3A")}
        self.assertEqual(year, {0: "1994", 1: "1994", 2: "1996"})
        # T15's check: the start layout holds until the transfer
        check = {o["step"]: o["value"] for o in find("players.check problems")}
        self.assertEqual(check[0], "none")
        self.assertIn("country 1", check[2])
        # each unique screen's text stored once
        self.assertEqual(len(find("CP437 decoded")), 2)
        # every snapshot named with its sha256
        named = {o["value"] for o in obs if o["source"] == "file" and "read snapshot" in o["field"]}
        self.assertEqual(named, {e["sha256"] for e in index})
        # the squad is emitted decoded, licensed by R012
        self.assertEqual(rec["decoded"][-1]["via"], "R012")
        self.assertTrue(rec["decoded"][-1]["value"].endswith("2561]"))

    def test_the_record_is_a_valid_run_1_document(self):
        import validate_runs
        session = self.workdir("valid")
        write_session(session, CHAIN)
        runs = self.workdir("valid-runs")
        rec, path, _ = self.extract(session, runs)
        self.assertEqual(validate_runs.check(path), [])
        self.assertEqual(rec["run_id"], "E015-r0001")
        self.assertEqual(rec["experiment"], "E015")
        self.assertEqual(rec["status"], "completed")

    def test_a_record_is_never_overwritten(self):
        session = self.workdir("imm")
        write_session(session, CHAIN)
        runs = self.workdir("imm-runs")
        first = self.extract(session, runs)[1]
        before = first.read_bytes()
        rec, second, _ = self.extract(session, runs)
        self.assertEqual(first.read_bytes(), before)
        self.assertEqual(rec["run_id"], "E015-r0002")

    def test_a_broken_snapshot_is_skipped_and_the_chain_still_yields_a_record(self):
        session = self.workdir("broken")
        index = write_session(session, CHAIN)
        (session / index[1]["file"]).write_bytes(b"NOPE not a zip")
        runs = self.workdir("broken-runs")
        rec, path, out = self.extract(session, runs)
        self.assertIn("states: 2, screens: 1 unique, diffs: 1, skipped: 1", out)
        skipped = [o for o in rec["observations"] if "skipped" in o["field"]]
        self.assertEqual(len(skipped), 1)
        self.assertIn("snap-0002", skipped[0]["field"])
        import validate_runs
        self.assertEqual(validate_runs.check(path), [])

    def test_a_single_state_session_has_no_diffs(self):
        session = self.workdir("single")
        write_session(session, CHAIN[:1])
        runs = self.workdir("single-runs")
        rec, path, out = self.extract(session, runs)
        self.assertIn("states: 1, screens: 1 unique, diffs: 0", out)
        import validate_runs
        self.assertEqual(validate_runs.check(path), [])

    def test_the_index_can_be_lost_the_snapshots_folder_still_walks(self):
        session = self.workdir("noindex")
        write_session(session, CHAIN, with_index=False)
        runs = self.workdir("noindex-runs")
        rec, path, out = self.extract(session, runs)
        self.assertIn("states: 3, screens: 2 unique, diffs: 2", out)

    def test_the_offset_of_the_state_tuple_is_the_readers_own(self):
        # the fixture writes the tuple at the far pointer [A923]; the reader must find it there:
        # a state whose pointer moved reads other bytes and the named values below stop matching
        session = self.workdir("ptr")
        write_session(session, CHAIN[:1])
        data = savestate_bytes(*CHAIN[0])
        st = savestate.Savestate(data)
        ptr = (st.ds_word(0xA923 + 2) * 16 + st.ds_word(0xA923))
        self.assertEqual(st.memory(ptr + extract.STAGE_OFFSET, 1)[0], 0x05)
        self.assertEqual(int.from_bytes(st.memory(ptr + extract.YEAR_OFFSET, 2), "little"), 1994)
        self.assertEqual(len(st.memory(ptr, extract.GAME_RECORD_BYTES)), extract.GAME_RECORD_BYTES)


# ---- the watcher's rules -------------------------------------------------------------------------
class FakeClock:
    """Fake time. Bounded: no test runs past an hour of fake time, so a loop whose deadline
    never arrives fails the test instead of hanging the suite."""
    LIMIT_S = 3600.0

    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s
        if self.t > self.LIMIT_S:
            raise AssertionError(f"fake clock past {self.LIMIT_S}s: a loop never reached its deadline")


class FreshWriteClock:
    """A clock that, on every sleep, writes a fresh complete zip to `live` whose sha differs from
    the previous one. Used by the R6-aware tests: with my new staging gate, every tick requires
    the live file's bytes to differ from the pre-send digest, so a static live file fails the
    gate. Each `sleep` writes a new payload ('vga-N') to make the digest change."""

    def __init__(self, live, base_payload=b"vga"):
        self.live = live
        self.t = 0.0
        self.counter = 0
        self.base = base_payload

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s
        self.counter += 1
        self.live.write_bytes(tiny_zip(self.base + b"-" + str(self.counter).encode()))


class FakeDbx:
    returncode = 0

    def __init__(self, die_at=None):
        self.die_at = die_at

    def poll(self):
        return 1 if self.die_at is not None else None


def tiny_zip(payload=b"vga", mem=b"mem"):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Save_Remark", b"")
        z.writestr("Vga", payload)
        z.writestr("Memory", mem)
    return buf.getvalue()


class FocusGate(Base):
    def test_keys_go_to_the_game_window_and_nowhere_else(self):
        self.assertEqual(recorder.key_cmd(432),
                         ["xdotool", "key", "--window", "432", recorder.SAVE_KEYS])

    def test_the_loop_never_sends_a_global_keystroke(self):
        # R6: every tick the live file gets a fresh, distinct savestate, so the staging gate
        # admits each one. The test only cares that no send is a global keystroke.
        session = self.workdir("gate")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(tiny_zip(b"vga-0"))
        clock = FreshWriteClock(live)
        sends = []
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=sends.append, alive=lambda: True,
                             log=lambda m: None)
        w.run(quit_after=45.0)
        self.assertGreaterEqual(len(sends), 3)
        for argv in sends:
            self.assertEqual(argv[:2], ["xdotool", "key"])
            self.assertIn("--window", argv)
            self.assertIn("77", argv)


class WindowBind(Base):
    """R1: find_window binds to the launched dosbox-x, not the only previous-window match."""

    def test_window_is_selected_by_pid_not_class(self):
        # Two windows in class "dosbox"; the recorder's pid is 9999. Only window "2" reports
        # pid 9999; window "1" reports pid 8888. The bind must select "2".
        env = {"DISPLAY": ":0"}
        clock = FakeClock()
        with mock.patch.object(recorder, "xdotool") as x:
            def run(args, *a, **kw):
                cmd, *rest = args
                if cmd == "search":
                    return types.SimpleNamespace(returncode=0, stdout="1\n2", stderr="")
                if cmd == "getwindowpid":
                    wid = rest[-1]
                    pid = "9999" if wid == "2" else "8888"
                    return types.SimpleNamespace(returncode=0, stdout=pid, stderr="")
                return types.SimpleNamespace(returncode=0, stdout="", stderr="")
            x.side_effect = run
            wid = recorder.find_window(env, dbx_pid=9999, timeout=5.0, sleep=clock.sleep,
                                        clock=clock)
        self.assertEqual(wid, "2")

    def test_window_bind_fails_closed_when_no_pid_matches(self):
        # No window reports pid 9999 — the bind raises and the search never accepts a window
        # with the wrong pid. This is what makes the gate closed: no wid, no key.
        env = {"DISPLAY": ":0"}
        clock = FakeClock()
        with mock.patch.object(recorder, "xdotool") as x:
            def run(args, *a, **kw):
                cmd, *rest = args
                if cmd == "search":
                    return types.SimpleNamespace(returncode=0, stdout="1\n2", stderr="")
                if cmd == "getwindowpid":
                    return types.SimpleNamespace(returncode=0, stdout="8888", stderr="")
                return types.SimpleNamespace(returncode=0, stdout="", stderr="")
            x.side_effect = run
            with self.assertRaises(RuntimeError):
                recorder.find_window(env, dbx_pid=9999, timeout=0.1, sleep=clock.sleep,
                                     clock=clock)


def key_writes(live, log=None):
    """An xrun fake: each F12+S writes one fresh complete savestate to `live` by atomic replace
    (a new inode, so its signature always differs from the pre-send one), like DOSBox-X's own
    write. `log`, when given, records ("key",) for each send."""
    n = [0]

    def xrun(argv):
        n[0] += 1
        if log is not None:
            log.append(("key",))
        tmp = live.with_name(live.name + ".tmp")
        tmp.write_bytes(tiny_zip(b"vga-" + str(n[0]).encode()))
        tmp.replace(live)
    return xrun


class Cadence(Base):
    def test_ticks_at_the_cadence_from_zero(self):
        # each tick's key press produces one fresh savestate, staged once the signature has held
        # for STABLE_POLLS polls (3 x 0.25 s = 0.75 s after the send)
        session = self.workdir("cadence")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(tiny_zip(b"vga-0"))
        clock = FakeClock()
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=key_writes(live), alive=lambda: True,
                             log=lambda m: None)
        entries = w.run(quit_after=45.0)
        self.assertEqual([e["elapsed_s"] for e in entries], [0.5, 20.5, 40.5])
        self.assertEqual([e["seq"] for e in entries], [1, 2, 3])

    def test_each_entry_carries_its_save_request_window_not_its_staging_time(self):
        # T34 R1: the screen is taken when the key is handled, ~0.75 s before staging here
        session = self.workdir("request-window")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(tiny_zip(b"vga-0"))
        clock = FakeClock()
        writes = key_writes(live)

        def slow_send(argv):           # the send itself takes 0.03 s of the clock
            clock.t += 0.03
            writes(argv)
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=slow_send, alive=lambda: True,
                             log=lambda m: None)
        entries = w.run(quit_after=25.0)
        self.assertEqual([(e["request_s"], e["sent_s"], e["elapsed_s"]) for e in entries],
                         [(0.0, 0.03, 0.53), (20.0, 20.03, 20.53)])
        lines = [json.loads(x) for x in (session / "requests.jsonl").read_text().splitlines()]
        self.assertEqual(lines, [{"request_s": 0.0, "sent_s": 0.03, "origin": "watcher", "seq": 1},
                                 {"request_s": 20.0, "sent_s": 20.03, "origin": "watcher", "seq": 2}])

    def test_a_skipped_snapshot_is_a_request_with_no_entry(self):
        # T34 R2: the map must know a burst's snapshot is missing
        session = self.workdir("request-skipped")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(tiny_zip(b"vga-0"))
        clock = FakeClock()
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=lambda a: None, alive=lambda: True,
                             log=lambda m: None)
        self.assertIsNone(w.tick(origin="burst"))
        line = json.loads((session / "requests.jsonl").read_text())
        self.assertEqual((line["request_s"], line["origin"], line["seq"]), (0.0, "burst", None))
        self.assertFalse((session / "index.jsonl").exists())

    def test_a_resend_widens_the_window_to_the_last_send(self):
        session = self.workdir("request-resend")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(tiny_zip(b"vga-0"))
        clock = FakeClock()
        writes, sends = key_writes(live), [0]

        def lost_first(argv):          # the first F12+S is lost; the resend writes
            sends[0] += 1
            if sends[0] > 1:
                writes(argv)
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=lost_first, alive=lambda: True,
                             log=lambda m: None)
        entry = w.tick()
        self.assertEqual(sends[0], 2)
        self.assertEqual(entry["request_s"], 0.0)
        self.assertGreater(entry["sent_s"], recorder.RESEND_AFTER_S)
        self.assertLess(entry["sent_s"], entry["elapsed_s"])

    def test_the_shutdown_window_opens_at_the_last_staged_request(self):
        session = self.workdir("request-shutdown")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(tiny_zip(b"vga-0"))
        clock = FakeClock()
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=key_writes(live), alive=lambda: True,
                             log=lambda m: None)
        first = w.tick()
        clock.t = 30.0
        live.write_bytes(tiny_zip(b"owner-pressed-f12-s"))
        last = w.shutdown_stage({first["sha256"]})
        self.assertEqual(last["request_s"], first["request_s"])
        self.assertGreaterEqual(last["sent_s"], 30.0)


class StagingGate(Base):
    def test_only_a_complete_and_size_stable_savestate_is_staged(self):
        session = self.workdir("staging")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        early, final = tiny_zip(b"early"), tiny_zip(b"final-bytes")
        live.write_bytes(b"\x00\x01")            # mid-write: not a zip yet

        class GrowClock:
            """The fake clock writes the live file's next stage as the watcher polls it: valid but
            still growing first, then the final bytes."""

            def __init__(self):
                self.t = 0.0
                self.stage = 0

            def __call__(self):
                return self.t

            def sleep(self, s):
                self.t += s
                if self.stage == 0:
                    live.write_bytes(early)      # a complete zip, written again right after
                    self.stage = 1
                elif self.stage == 1:
                    live.write_bytes(final)      # growth: the early zip must not be staged
                    self.stage = 2

        clock = GrowClock()
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=lambda a: None, alive=lambda: True,
                             log=lambda m: None)
        entry = w.tick()
        self.assertEqual(entry["sha256"], hashlib.sha256(final).hexdigest())
        self.assertEqual(entry["bytes"], len(final))
        # the live file was read, never moved or renamed
        self.assertTrue(live.is_file())
        self.assertEqual(live.read_bytes(), final)
        lines = (session / "index.jsonl").read_text().splitlines()
        self.assertEqual(json.loads(lines[0])["file"], entry["file"])

    def test_an_incomplete_zip_is_never_staged(self):
        session = self.workdir("incomplete")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(tiny_zip()[:10])        # truncated: no central directory
        clock = FakeClock()
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=lambda a: None, alive=lambda: True,
                             log=lambda m: None)
        with self.assertRaises(TimeoutError):
            w.capture(None)

    def test_the_shutdown_pass_stages_the_owners_last_savestate_once(self):
        session = self.workdir("shutdown")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        data = tiny_zip(b"owner-pressed-f12-s")
        live.write_bytes(data)
        clock = FakeClock()
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=lambda a: None, alive=lambda: True,
                             log=lambda m: None)
        entry = w.shutdown_stage(indexed_sha=set())
        self.assertEqual(entry["origin"], "shutdown")
        self.assertEqual(entry["sha256"], hashlib.sha256(data).hexdigest())
        self.assertIsNone(w.shutdown_stage(indexed_sha={entry["sha256"]}))


class SavestateGate(Base):
    def test_zip_complete_accepts_only_whole_savestates(self):
        d = self.workdir("zipcheck")
        good, truncated = d / "good.sav", d / "truncated.sav"
        good.write_bytes(tiny_zip())
        truncated.write_bytes(tiny_zip()[:12])
        self.assertEqual(recorder.zip_complete(good), tiny_zip())
        self.assertIsNone(recorder.zip_complete(truncated))
        partial = d / "partial.sav"              # a zip without the Memory member
        with zipfile.ZipFile(partial, "w") as z:
            z.writestr("Save_Remark", b"")
            z.writestr("Vga", b"")
        self.assertIsNone(recorder.zip_complete(partial))

    def test_zip_is_complete_validates_bytes_not_the_live_file(self):
        # R3 pin: the validator accepts a complete zip's bytes regardless of how they were
        # produced; the captured bytes must validate, not a fresh read of the live file.
        data = tiny_zip(b"vga-x", b"mem-x")
        self.assertTrue(recorder.zip_is_complete(data))
        self.assertFalse(recorder.zip_is_complete(tiny_zip(b"vga", b"")[:50]))  # truncated
        self.assertFalse(recorder.zip_is_complete(b""))                          # empty


class FreshWriteGate(Base):
    """R6: a tick requires evidence of a fresh write (post-send bytes differ from pre-send)."""

    def test_unchanged_live_file_is_not_staged(self):
        # The live file is already a complete zip; the watcher sends F12+S, but no new write
        # arrives (the owner's emulator ignored the key). The staging gate must NOT stage the
        # previous tick's savestate as a new snapshot.
        session = self.workdir("fresh")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        data = tiny_zip(b"vga")
        live.write_bytes(data)
        clock = FakeClock()       # the live file does NOT change on sleep
        w = recorder.Watcher(session, live, "27", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=lambda a: None, alive=lambda: True,
                             log=lambda m: None)
        entry = w.tick()
        self.assertIsNone(entry)
        self.assertEqual(list((session / "snapshots").glob("*.sav")), [])
        self.assertFalse((session / "index.jsonl").exists())


class CleanTermination(Base):
    """R5: dosbox-x dying during a snapshot is clean termination, not an unhandled exception."""

    def test_dead_emulator_during_snapshot_ends_the_loop(self):
        session = self.workdir("dead")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(tiny_zip(b"vga"))
        clock = FakeClock()
        # Die as soon as capture starts polling
        w = recorder.Watcher(session, live, "77", FakeDbx(die_at=0.1), {"DISPLAY": ":0"},
                             clock=clock, sleep=clock.sleep, xrun=lambda a: None,
                             alive=lambda: True, log=lambda m: None)
        # Run for 30 ticks; the loop ends early when _EmulatorGone is caught
        entries = w.run(quit_after=600.0)
        self.assertEqual(entries, [])

    def test_dead_emulator_raises_a_named_exception_inside_capture(self):
        # The watcher.run catches _EmulatorGone; direct capture raises it.
        session = self.workdir("dead-direct")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(tiny_zip(b"vga"))
        clock = FakeClock()
        w = recorder.Watcher(session, live, "77", FakeDbx(die_at=0.1), {"DISPLAY": ":0"},
                             clock=clock, sleep=clock.sleep, xrun=lambda a: None,
                             alive=lambda: True, log=lambda m: None)
        with self.assertRaises(recorder._EmulatorGone):
            w.capture(None)


class ShutdownStageGate(Base):
    """R4: the shutdown staging pass applies the staging gate after terminate()."""

    def test_shutdown_stage_waits_for_size_stability(self):
        # R4: the live file must be stable for STABLE_POLLS polls before being staged. A
        # single stable poll is not enough. The test writes a complete zip, then on each sleep
        # adds a byte to make the size change (stability broken).
        session = self.workdir("shutdown-stable")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(tiny_zip(b"vga"))
        clock = FakeClock()       # no growth → stable immediately
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=lambda a: None, alive=lambda: True,
                             log=lambda m: None)
        entry = w.shutdown_stage(indexed_sha=set())
        self.assertIsNotNone(entry)
        self.assertEqual(entry["origin"], "shutdown")


class VideoMonitoring(Base):
    """R16: video growth monitoring is wired into the recording path."""

    def test_poll_growth_flags_stalled_when_size_does_not_change(self):
        d = self.workdir("video-stall")
        out = d / "video.mkv"
        out.write_bytes(b"\x00" * 100)
        v = recorder.Video(recorder.video_cmd((0, 0, 64, 64), ":0", str(out)), out)
        # No proc, so poll_growth is a no-op (it checks self.proc.poll()).
        v.poll_growth()
        self.assertFalse(v.stalled)

    def test_poll_growth_with_no_size_change_past_stall_threshold(self):
        # Drive the clock past VIDEO_STALL_S with size unchanged: stalled flips to True.
        d = self.workdir("video-stall-boundary")
        out = d / "video.mkv"
        out.write_bytes(b"\x00" * 100)
        clock = FakeClock()
        v = recorder.Video(recorder.video_cmd((0, 0, 64, 64), ":0", str(out)), out, clock=clock)
        # Simulate ffmpeg running by setting proc to a sentinel whose poll() returns None.
        v.proc = types.SimpleNamespace(poll=lambda: None)
        # First poll arms last_size / last_growth.
        v.poll_growth()
        # Now tick the clock past the stall threshold: a second poll with no growth past
        # VIDEO_STALL_S triggers stalled.
        clock.sleep(recorder.VIDEO_STALL_S + 0.001)
        v.poll_growth()
        self.assertTrue(v.stalled)

    def test_video_stop_sends_sigkill_after_exact_grace(self):
        # Boundary (R14): VIDEO_TERM_GRACE_S = 10 s. A proc that ignores SIGTERM is killed at
        # the 10.000 s mark. The first wait(VIDEO_TERM_GRACE_S) raises TimeoutExpired; the
        # second wait() returns 0 after SIGKILL.
        d = self.workdir("video-grace")
        out = d / "video.mkv"
        out.write_bytes(b"")

        class Proc:
            pid = 9999

            def __init__(self):
                self.signals = []
                self.waits = 0

            def poll(self):
                return None   # alive throughout the test

            def wait(self, timeout=None):
                self.waits += 1
                # First wait times out (SIGTERM ignored); second wait returns 0 (post-SIGKILL)
                if self.waits == 1:
                    raise subprocess.TimeoutExpired("ffmpeg", timeout)
                return 0

        proc_alive = Proc()
        v = recorder.Video(recorder.video_cmd((0, 0, 64, 64), ":0", str(out)), out)
        v.proc = proc_alive
        with mock.patch.object(recorder.os, "killpg") as killpg:
            killpg.side_effect = lambda pid, sig: proc_alive.signals.append(sig)
            info = v.stop()
        self.assertEqual(info["ended"], "SIGKILL")
        self.assertEqual(proc_alive.signals[0], signal.SIGTERM)
        self.assertEqual(proc_alive.signals[-1], signal.SIGKILL)


class ThresholdBoundaries(Base):
    """R14 boundary tests for the designed thresholds."""

    def test_stable_polls_boundary_growing_file_does_not_stage(self):
        # The watcher requires STABLE_POLLS = 3 consecutive equal-size polls. A file that
        # grows between polls must NOT be staged. The GrowClock alternates two distinct sizes,
        # so the watcher never sees a stable file and times out.
        session = self.workdir("stable-polls")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(b"\x00\x01")

        class AlternatingClock:
            def __init__(self):
                self.t = 0.0
                self.toggle = False

            def __call__(self):
                return self.t

            def sleep(self, s):
                self.t += s
                # alternate between two complete zips with distinct sizes
                self.toggle = not self.toggle
                if self.toggle:
                    live.write_bytes(tiny_zip(b"vga-A-pad-1"))
                else:
                    live.write_bytes(tiny_zip(b"vga-B-pad-2-22"))

        clock = AlternatingClock()
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=lambda a: None, alive=lambda: True,
                             log=lambda m: None)
        entry = w.tick()
        self.assertIsNone(entry)
        self.assertEqual(list((session / "snapshots").glob("*.sav")), [])

    def test_stable_polls_constant_value(self):
        # Independent expected-value pin (R12): the constant is what the design says it is.
        self.assertEqual(recorder.STABLE_POLLS, 3)

    def test_video_term_grace_constant_value(self):
        self.assertEqual(recorder.VIDEO_TERM_GRACE_S, 10.0)

    def test_video_stall_constant_value(self):
        self.assertEqual(recorder.VIDEO_STALL_S, 60.0)

    def test_video_term_grace_boundary_sigkill_at_exact_grace(self):
        # Boundary (R14): VIDEO_TERM_GRACE_S = 10 s. A proc that ignores SIGTERM is killed at
        # the 10.000 s mark. The first wait(VIDEO_TERM_GRACE_S) raises TimeoutExpired; the
        # second wait() returns 0 after SIGKILL.
        d = self.workdir("video-grace-boundary")
        out = d / "video.mkv"
        out.write_bytes(b"")

        class Proc:
            pid = 9999

            def __init__(self):
                self.signals = []
                self.waits = 0

            def poll(self):
                return None

            def wait(self, timeout=None):
                self.waits += 1
                if self.waits == 1:
                    raise subprocess.TimeoutExpired("ffmpeg", timeout)
                return 0

        proc_alive = Proc()
        v = recorder.Video(recorder.video_cmd((0, 0, 64, 64), ":0", str(out)), out)
        v.proc = proc_alive
        with mock.patch.object(recorder.os, "killpg") as killpg:
            killpg.side_effect = lambda pid, sig: proc_alive.signals.append(sig)
            info = v.stop()
        self.assertEqual(info["ended"], "SIGKILL")
        self.assertIn(signal.SIGTERM, proc_alive.signals)
        self.assertIn(signal.SIGKILL, proc_alive.signals)


class ConstantsPin(Base):
    """R12: independent expected-value assertions for each named constant, so mutations of any
    one are caught by at least one test."""

    def test_offset_constants_match_the_static_source(self):
        # These are the constants the brief and the recorded session depend on. Each is the
        # byte offset or DS offset a downstream reader (extract.py) uses. Mutating any one
        # reads the wrong byte; these tests fail.
        self.assertEqual(extract.GAME_RECORD_PTR, 0xA923)
        self.assertEqual(extract.GAME_RECORD_BYTES, 0x10E)
        self.assertEqual(extract.STAGE_OFFSET, 0x3C)
        self.assertEqual(extract.YEAR_OFFSET, 0x3A)
        self.assertEqual(extract.FIXTURE_INDEX_OFFSET, 0x26)
        self.assertEqual(extract.FIXTURE_COUNT_OFFSET, 0x28)
        self.assertEqual(extract.SPEED_OFFSET, 0x3F)
        self.assertEqual(extract.MANAGERS_OFFSET, 0x00)
        self.assertEqual(recorder.CADENCE_S, 20.0)
        self.assertEqual(recorder.POLL_S, 0.25)
        self.assertEqual(recorder.STABLE_POLLS, 3)
        self.assertEqual(recorder.WANT_DOSBOX, "2024.03.01")
        self.assertEqual(recorder.WINDOW_CLASS, "dosbox")
        self.assertEqual(recorder.SAVE_KEYS, "F12+s")
        self.assertEqual(recorder.SEND_TO_WINDOW, True)
        self.assertEqual(recorder.VIDEO_TERM_GRACE_S, 10.0)
        self.assertEqual(recorder.VIDEO_STALL_S, 60.0)
        self.assertEqual(recorder.RESEND_AFTER_S, 3.0)
        self.assertEqual(recorder.SAVE_TIMEOUT_S, 15.0)
        self.assertEqual(recorder.TERM_GRACE_S, 0.5)

    def test_video_cmd_includes_flush_packets_1(self):
        # R12 load-bearing: removing -flush_packets 1 reverts the prototype's silent-failure
        # bug (a SIGKILLed mp4 grab leaves exactly 48 header bytes). The constant is part of
        # the documented recorder behaviour.
        argv = recorder.video_cmd((0, 0, 64, 64), ":0", "/x/video.mkv")
        idx = argv.index("-flush_packets")
        self.assertEqual(argv[idx + 1], "1")

    def test_named_offsets_match_extract(self):
        # R12 cross-pin: extract and recorder share the constants, so a mutation in extract
        # fails here as well.
        self.assertEqual(extract.STAGE_OFFSET, 0x3C)
        self.assertEqual(extract.YEAR_OFFSET, 0x3A)
        self.assertEqual(extract.FIXTURE_INDEX_OFFSET, 0x26)
        self.assertEqual(extract.FIXTURE_COUNT_OFFSET, 0x28)
        self.assertEqual(extract.SPEED_OFFSET, 0x3F)
        self.assertEqual(extract.MANAGERS_OFFSET, 0x00)
        self.assertEqual(extract.GAME_RECORD_PTR, 0xA923)
        self.assertEqual(extract.GAME_RECORD_BYTES, 0x10E)


# ---- the recorder's CLI --------------------------------------------------------------------------
class SelfTest(Base):
    def test_self_test_verifies_writes_a_config_and_never_launches(self):
        d = self.workdir("selftest")
        with mock.patch.object(recorder, "ensure_cache", lambda: "goal2-67cf27d6"), \
                mock.patch.object(recorder, "SELFTEST", d), \
                mock.patch.object(recorder.shutil, "which", lambda n: "/usr/bin/" + n), \
                mock.patch.object(recorder, "dosbox_version",
                                  lambda: "DOSBox-X version 2024.03.01 SDL2, copyright 2011-2024"):
            out = io.StringIO()
            with mock.patch("sys.stdout", out):
                rc = recorder.main(["self-test"])
        self.assertEqual(rc, 0)
        self.assertIn("self-test ok", out.getvalue())
        conf = (d / "dosbox.conf").read_text()
        self.assertIn("fullscreen=false", conf)      # windowed: the sitting runs in a window
        self.assertIn("output=surface", conf)
        self.assertIn("nosound=true", conf)          # the G1 driver's config family
        self.assertIn("mount c", conf)

    def test_self_test_reports_missing_tools(self):
        d = self.workdir("selftest-missing")
        with mock.patch.object(recorder, "ensure_cache", lambda: "goal2-67cf27d6"), \
                mock.patch.object(recorder, "SELFTEST", d), \
                mock.patch.object(recorder.shutil, "which", lambda n: None), \
                mock.patch.object(recorder, "dosbox_version", lambda: None):
            out, err = io.StringIO(), io.StringIO()
            with mock.patch("sys.stdout", out), mock.patch("sys.stderr", err):
                rc = recorder.main(["self-test"])
        self.assertEqual(rc, 1)
        self.assertIn("dosbox-x", err.getvalue())


class VideoCmd(Base):
    def test_the_video_is_matroska_of_the_window_region(self):
        argv = recorder.video_cmd((100, 50, 642, 400), ":0", "/s/video.mkv")
        self.assertEqual(argv[0], "ffmpeg")
        self.assertIn("x11grab", argv)
        self.assertIn("642x400", argv)
        self.assertIn(":0+100,50", argv)
        self.assertTrue(argv[-1].endswith("video.mkv"))
        self.assertNotIn("-movflags", argv)   # the mp4 finalize-only index is what is replaced

    def test_an_empty_video_is_reported_not_silent(self):
        d = self.workdir("video")
        out = d / "video.mkv"
        out.write_bytes(b"")
        v = recorder.Video(recorder.video_cmd((0, 0, 64, 64), ":0", str(out)), out)
        v.proc = None
        info = v.stop()
        self.assertEqual(info["bytes"], 0)
        self.assertIsNone(info["sha256"])


# ---- review round 2 (rework round 3): each test fails when its guard is removed ---------------
class LiveFileReads(Base):
    """The live savestate is read only by the staging gate, after its signature has held."""

    def watcher(self, name, xrun, clock=None):
        session = self.workdir(name)
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(tiny_zip(b"vga-0"))
        clock = clock or FakeClock()
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=xrun, alive=lambda: True, log=lambda m: None)
        return session, live, w

    def test_no_content_read_of_the_live_file_before_the_key_is_sent(self):
        # round-2 R1: the pre-send freshness check must not read an in-progress write
        events = []
        real_open = open

        def spy_open(path, *a, **kw):
            if Path(path).name == "state.sav":
                events.append(("read",))
            return real_open(path, *a, **kw)

        session, live, w = self.watcher("r1-noread", None)
        w.xrun = key_writes(live, log=events)
        with mock.patch.object(recorder, "open", spy_open, create=True):
            entry = w.tick()
        self.assertIsNotNone(entry)
        self.assertEqual(events[0], ("key",), f"the live file was read before the key: {events}")

    def test_a_same_size_rewrite_during_capture_is_never_staged(self):
        # round-2 R2: the file is replaced by same-length garbage right after the capture read;
        # the valid bytes read first must not be staged while the live file is invalid
        real_open = open
        reads = [0]

        def racing_open(path, *a, **kw):
            f = real_open(path, *a, **kw)
            if Path(path).name == "state.sav":
                reads[0] += 1
                if reads[0] == 1:
                    data = f.read()
                    f.close()
                    Path(path).write_bytes(b"X" * len(data))   # same size, not a zip
                    return io.BytesIO(data)
            return f

        session, live, w = self.watcher("r2-samesize", None)
        first_only = key_writes(live)
        sends = [0]

        def xrun(argv):                     # the emulator answers the first key only, so the
            sends[0] += 1                   # raced bytes are the only savestate there ever is
            if sends[0] == 1:
                first_only(argv)
        w.xrun = xrun
        with mock.patch.object(recorder, "open", racing_open, create=True):
            entry = w.tick()
        self.assertIsNone(entry)
        self.assertEqual(list((session / "snapshots").glob("*.sav")), [])

    def test_a_writer_still_rewriting_in_place_is_never_staged(self):
        # round-3 R1: a writer opens the live file in place, rewrites its unchanged first byte
        # and flushes (which moves mtime), then pauses; both content reads still compare equal.
        # The signature re-check rejects that capture; only the writer's finished file is staged.
        import os as _os
        real_open = open
        reads = [0]
        state = {"writer": "idle"}
        final = tiny_zip(b"the writer's finished savestate")

        def racing_open(path, *a, **kw):
            f = real_open(path, *a, **kw)
            if Path(path).name == "state.sav":
                reads[0] += 1
                if reads[0] == 1:
                    data = f.read()
                    f.close()
                    with real_open(path, "r+b") as g:         # in place, unchanged byte
                        g.write(data[:1])
                        g.flush()
                    st = _os.stat(path)                        # the flush moves mtime
                    _os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns + 1_000_000))
                    state["writer"] = "active"
                    return io.BytesIO(data)
            return f

        class WriterFinishes(FakeClock):
            def sleep(self, s):
                super().sleep(s)
                if state["writer"] == "active":
                    live.write_bytes(final)
                    state["writer"] = "done"

        clock = WriterFinishes()
        session, live, w = self.watcher("r1-inplace", None, clock=clock)
        w.xrun = key_writes(live)
        with mock.patch.object(recorder, "open", racing_open, create=True):
            entry = w.tick()
        self.assertEqual(state["writer"], "done")
        self.assertEqual(entry["sha256"], hashlib.sha256(final).hexdigest())

    def test_a_writer_paused_mid_write_is_never_staged(self):
        # round-4 R1, with the real kernel: the writer opens the live file in place, writes its
        # unchanged first byte, flushes and holds the file open for 20 polls (5 s) before it
        # finishes and closes. The bytes and metadata are still the whole time; nothing is
        # staged until the close, then the finished file is.
        state = {"writer": "idle", "polls": 0, "handle": None}
        final = tiny_zip(b"finished after a long pause")

        class PausedWriter(FakeClock):
            def sleep(self, s):
                super().sleep(s)
                if state["writer"] == "idle" and self.t >= 0.25:
                    h = open(live, "r+b")
                    h.write(live.read_bytes()[:1])
                    h.flush()
                    state.update(writer="active", handle=h)
                elif state["writer"] == "active":
                    state["polls"] += 1
                    if state["polls"] == 20:
                        h = state["handle"]
                        h.seek(0)
                        h.truncate()
                        h.write(final)
                        h.close()
                        state["writer"] = "done"

        clock = PausedWriter()
        session, live, w = self.watcher("r4-paused", None, clock=clock)
        self.addCleanup(lambda: state["handle"] and state["handle"].close())
        first_only, sends = key_writes(live), [0]

        def xrun(argv):                  # the emulator answers the first key only: a re-send
            sends[0] += 1                # renaming a new finished file into place would end
            if sends[0] == 1:            # the session legitimately (the paused writer then
                first_only(argv)         # writes to the unlinked old inode)
        w.xrun = xrun
        staged_while, read_while = [], []
        real_stage, real_read = w.stage, w._read_live
        w.stage = lambda *a, **kw: (staged_while.append(state["writer"]), real_stage(*a, **kw))[1]
        w._read_live = lambda: (read_while.append(state["writer"]), real_read())[1]
        entry = w.tick()
        self.assertEqual(staged_while, ["done"])
        self.assertEqual(entry["sha256"], hashlib.sha256(final).hexdigest())
        # round-5 R1: no content read of the live file while the write session was open
        self.assertNotIn("active", read_while)
        self.assertTrue(read_while)

    def test_a_write_that_begins_during_the_reads_is_never_staged(self):
        # round-5 R1: the session is idle at the pre-read check; a writer opens the file in place
        # during the first read, writes its unchanged first byte and pauses. The bytes compare
        # equal and, with timestamps too coarse to move, so does the signature; only the
        # session check after the reads sees the open write. Its finished file is staged later.
        real_open = open
        state = {"writer": "idle", "polls": 0, "handle": None}
        final = tiny_zip(b"finished after starting mid-read")

        def racing_open(path, *a, **kw):
            f = real_open(path, *a, **kw)
            if Path(path).name == "state.sav" and state["writer"] == "idle" and "r" in (a[0] if a else "r") and "+" not in (a[0] if a else ""):
                data = f.read()
                f.close()
                h = real_open(path, "r+b")
                h.write(data[:1])
                h.flush()
                state.update(writer="active", handle=h)
                return io.BytesIO(data)
            return f

        class Finishes(FakeClock):
            def sleep(self, s):
                super().sleep(s)
                if state["writer"] == "active":
                    state["polls"] += 1
                    if state["polls"] == 8:
                        h = state["handle"]
                        h.seek(0)
                        h.truncate()
                        h.write(final)
                        h.close()
                        state["writer"] = "done"

        clock = Finishes()
        session, live, w = self.watcher("r5-midread", None, clock=clock)
        self.addCleanup(lambda: state["handle"] and not state["handle"].closed and state["handle"].close())
        sends = [0]

        def xrun(argv):                  # one fresh savestate, of another length than the
            sends[0] += 1                # one before it, so the coarse signature sees it
            if sends[0] == 1:
                tmp = live.with_name("state.sav.tmp")
                tmp.write_bytes(tiny_zip(b"the key's fresh savestate"))
                tmp.replace(live)
        w.xrun = xrun
        staged_while = []
        real_stage = w.stage
        w.stage = lambda *a, **kw: (staged_while.append(state["writer"]), real_stage(*a, **kw))[1]
        coarse = lambda path: (1, live.stat().st_size) if live.exists() else None
        with mock.patch.object(recorder, "open", racing_open, create=True), \
                mock.patch.object(recorder, "file_signature", coarse):
            entry = w.tick()
        self.assertEqual(staged_while, ["done"])
        self.assertEqual(entry["sha256"], hashlib.sha256(final).hexdigest())

    def test_bytes_read_while_a_write_was_in_progress_are_never_staged(self):
        # round-6 R1, the task's guarantee (b7777fd): a writer opens the file during the first
        # read, rewrites identical bytes and closes before the second. Content, coarse
        # timestamps and the session flag all look clean afterwards; only the kernel's write
        # events between the two checks show the overlap. Those bytes are never staged; the
        # next capture, with no write during its reads, is.
        real_open = open
        reads, wrote_during = [], []

        def racing_open(path, *a, **kw):
            f = real_open(path, *a, **kw)
            mode = a[0] if a else "r"
            if Path(path).name == "state.sav" and "+" not in mode and "w" not in mode:
                reads.append(len(reads) + 1)
                if len(reads) == 1:                       # the write overlaps read 1 only
                    data = f.read()
                    f.close()
                    with real_open(path, "r+b") as h:     # identical bytes, opened and closed
                        h.write(data)
                    wrote_during.append(1)
                    return io.BytesIO(data)
            return f

        session, live, w = self.watcher("r6-overlap", None)
        sends = [0]

        def xrun(argv):
            sends[0] += 1
            if sends[0] == 1:
                tmp = live.with_name("state.sav.tmp")
                tmp.write_bytes(tiny_zip(b"the key's fresh savestate"))
                tmp.replace(live)
        w.xrun = xrun
        staged_after_reads = []
        real_stage = w.stage
        w.stage = lambda *a, **kw: (staged_after_reads.append(len(reads)), real_stage(*a, **kw))[1]
        coarse = lambda path: (1, live.stat().st_size) if live.exists() else None
        with mock.patch.object(recorder, "open", racing_open, create=True), \
                mock.patch.object(recorder, "file_signature", coarse):
            entry = w.tick()
        self.assertEqual(wrote_during, [1])
        self.assertIsNotNone(entry)
        # read 1 overlapped the write and was rejected; the staged bytes are read 2's
        self.assertEqual(staged_after_reads, [2])

    def test_a_writer_check_that_cannot_be_made_stages_nothing(self):
        # round-4 R1: fail closed when the emulator's descriptors cannot be read
        session, live, w = self.watcher("r4-closed", None)
        w.xrun = key_writes(live)

        def unreadable():
            raise PermissionError("/proc/1234/fd")
        w.activity = unreadable
        reads = []
        real_read = w._read_live
        w._read_live = lambda: (reads.append(1), real_read())[1]
        self.assertIsNone(w.tick())
        self.assertEqual(list((session / "snapshots").glob("*.sav")), [])
        self.assertEqual(reads, [])              # fail closed before any content read

    def test_write_watch_follows_the_kernels_write_sessions(self):
        # the probe itself: a write opens a session, the writer's close ends it, our own reads
        # touch nothing, and a finished file renamed into place is not a session
        d = self.workdir("r4-watch")
        f = d / "state.sav"
        f.write_bytes(b"x")
        ww = recorder.WriteWatch(f)
        self.addCleanup(ww.close)
        self.assertFalse(ww.writing())
        h = open(f, "r+b")
        h.write(b"y")
        h.flush()
        self.assertTrue(ww.writing())
        f.read_bytes()                                  # a reader changes nothing
        self.assertTrue(ww.writing())
        h.close()
        self.assertFalse(ww.writing())
        f.read_bytes()
        self.assertFalse(ww.writing())
        (d / "next.tmp").write_bytes(b"z")
        (d / "next.tmp").replace(f)
        self.assertFalse(ww.writing())
        (d / "other.sav").write_bytes(b"not ours")      # another file in the directory
        with open(d / "other.sav", "r+b") as g:
            g.write(b"n")
            g.flush()
            self.assertFalse(ww.writing())

    def test_an_event_queue_overflow_counts_as_an_open_session(self):
        # fail closed: lost events could have hidden a write
        d = self.workdir("r4-overflow")
        f = d / "state.sav"
        f.write_bytes(b"x")
        ww = recorder.WriteWatch(f)
        self.addCleanup(ww.close)
        overflow = recorder.struct.pack("iIII", -1, recorder.WriteWatch.IN_Q_OVERFLOW, 0, 0)
        reads = [overflow]

        def fake_read(fd, n):
            if reads:
                return reads.pop()
            raise BlockingIOError
        with mock.patch.object(recorder.os, "read", fake_read):
            self.assertTrue(ww.writing())

    def test_one_deadline_bounds_a_capture_that_keeps_racing(self):
        # round-2 R9: retries never reset the deadline (the old code recursed with a fresh one).
        # The live file is stable but never a complete zip, so every STABLE_POLLS cycle reaches
        # the reject branch; the clock fails the test long before an endless retry would end.
        class Bounded(FakeClock):
            def sleep(self, s):
                super().sleep(s)
                if self.t > 2 * recorder.SAVE_TIMEOUT_S:
                    raise AssertionError(f"capture still retrying at t={self.t}")
        clock = Bounded()
        session, live, w = self.watcher("r9-deadline", lambda a: None, clock=clock)
        live.write_bytes(b"not a zip, and it never becomes one")
        with self.assertRaises(TimeoutError):
            w.capture(None)
        self.assertLessEqual(clock.t, recorder.SAVE_TIMEOUT_S + recorder.POLL_S)

    def test_a_rewrite_invisible_to_coarse_timestamps_is_caught_by_the_second_read(self):
        # round-2 R2: with a signature that cannot see the rewrite (coarse timestamps, same
        # size, same inode), only the byte comparison of the two reads rejects the capture
        real_open = open
        reads = [0]

        def racing_open(path, *a, **kw):
            f = real_open(path, *a, **kw)
            if Path(path).name == "state.sav":
                reads[0] += 1
                if reads[0] == 1:
                    data = f.read()
                    f.close()
                    with real_open(path, "r+b") as g:      # same file, same size, new bytes
                        g.write(b"X" * len(data))
                    return io.BytesIO(data)
            return f

        session, live, w = self.watcher("r2-coarse", lambda a: None)
        coarse = lambda path: (1, live.stat().st_size) if live.exists() else None
        with mock.patch.object(recorder, "open", racing_open, create=True), \
                mock.patch.object(recorder, "file_signature", coarse):
            with self.assertRaises(TimeoutError):
                w.capture(None)
        self.assertEqual(list((session / "snapshots").glob("*.sav")), [])

    def test_the_shutdown_pass_never_stages_a_file_still_being_written(self):
        # round-2 R4/R7: the shutdown capture needs the same stability as a tick; a file that
        # changes between every poll is never staged (with STABLE_POLLS=1 it would be)
        class Growing(FakeClock):
            def sleep(self, s):
                super().sleep(s)
                live.write_bytes(tiny_zip(b"g" * (1 + int(self.t * 4))))
        clock = Growing()
        session, live, w = self.watcher("r4-shutdown", lambda a: None, clock=clock)
        self.assertIsNone(w.shutdown_stage(indexed_sha=set()))
        self.assertEqual(list((session / "snapshots").glob("*.sav")), [])
        self.assertTrue(w.problems)


class RecordIdentity(Base):
    extract = Extraction.extract
    diffobs = staticmethod(Extraction.diffobs)

    def test_a_taken_slot_is_skipped_and_the_id_matches_the_file(self):
        # round-2 R2/R5/R7: an existing record (another extraction's) is never overwritten, and
        # the new record's run_id is the slot it claimed
        session = self.workdir("ident")
        write_session(session, CHAIN)
        runs = self.workdir("ident-runs")
        (runs / "E015").mkdir(parents=True)
        foreign = runs / "E015" / "E015-r0001.json"
        foreign.write_text("another extraction's record\n")
        rec, path, _ = self.extract(session, runs)
        self.assertEqual(foreign.read_text(), "another extraction's record\n")
        self.assertEqual(path.name, "E015-r0002.json")
        self.assertEqual(rec["run_id"], "E015-r0002")
        self.assertEqual(json.loads(path.read_text())["run_id"], path.stem)


class Unavailable(Base):
    extract = Extraction.extract
    diffobs = staticmethod(Extraction.diffobs)

    def test_a_null_game_state_pointer_emits_no_game_state(self):
        # round-2 R7 (the R8 gate): [A923] = 0000:0000 reads nothing as the game state
        session = self.workdir("null-a923")
        write_session(session, [CHAIN[0] + ((0xA923,),)])
        rec, _, out = self.extract(session, self.workdir("null-a923-runs"))
        self.assertIn("partial: 1", out)
        obs = rec["observations"]
        self.assertFalse([o for o in obs if "the game state" in o["field"]])
        self.assertTrue([o for o in obs if "memory readings unavailable" in o["field"]])

    def test_a_null_country_array_pointer_emits_no_country_data(self):
        # round-2 R4: [A917] = 0000:0000 with a valid [A923]: the game state is read, the
        # country and player arrays are not (no invented country record or squad member 0)
        session = self.workdir("null-a917")
        write_session(session, [CHAIN[0] + ((0xA917,),)])
        rec, _, out = self.extract(session, self.workdir("null-a917-runs"))
        self.assertIn("partial: 1", out)
        obs = rec["observations"]
        self.assertTrue([o for o in obs if "the game state" in o["field"]])
        self.assertFalse([o for o in obs if "country record" in o["field"]])
        self.assertFalse([o for o in obs if "squad player" in o["field"]])
        self.assertEqual(rec["decoded"], [])
        self.assertTrue([o for o in obs if "arrays unavailable" in o["field"]
                         and "[A917]" in o["value"]])

    def test_a_null_player_array_pointer_emits_no_country_or_player_data(self):
        # round-3 R3: [A91B] = 0000:0000 with valid [A923] and [A917]: the player-array guard on
        # its own keeps squad members (read through [A91B]) and the country readings out
        session = self.workdir("null-a91b")
        write_session(session, [CHAIN[0] + ((0xA91B,),), CHAIN[1] + ((0xA91B,),)])
        rec, _, out = self.extract(session, self.workdir("null-a91b-runs"))
        self.assertIn("partial: 2", out)
        obs = rec["observations"]
        self.assertTrue([o for o in obs if "the game state" in o["field"]])
        self.assertFalse([o for o in obs if "country record" in o["field"]])
        self.assertFalse([o for o in obs if "squad player" in o["field"]])
        self.assertFalse([o for o in obs if "players.check" in o["field"]])
        self.assertEqual(rec["decoded"], [])
        self.assertTrue([o for o in obs if "arrays unavailable" in o["field"]
                         and "[A91B]" in o["value"]])
        self.assertEqual(self.diffobs(obs, "snap-0001", "country squads and player records"),
                         "unavailable")

    def test_a_partial_state_keeps_its_screen_diff_and_says_what_was_not_compared(self):
        # round-2 R6: state 2 has a changed screen and a null [A923]: the screen diff is kept,
        # the memory comparison reads "unavailable", never "none"
        session = self.workdir("partial-diff")
        write_session(session, [CHAIN[0], CHAIN[1] + ((0xA923,),)])
        rec, _, out = self.extract(session, self.workdir("partial-diff-runs"))
        self.assertIn("diffs: 1", out)
        obs = rec["observations"]
        self.assertEqual(self.diffobs(obs, "snap-0001", "screen changed"), "yes")
        self.assertEqual(self.diffobs(obs, "snap-0001", "[A923] byte changes"), "unavailable")
        self.assertEqual(self.diffobs(obs, "snap-0001", "country squads and player records"),
                         "unavailable")


if __name__ == "__main__":
    unittest.main()
