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
import sys
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


def memory_component(parr, carr, tup, ticks):
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

    far(0xA917, COUNTRY_AT)
    far(0xA91B, PLAYER_AT)
    far(0xA923, STATE_AT)
    mem[PLAYER_AT:PLAYER_AT + len(parr)] = parr
    mem[COUNTRY_AT:COUNTRY_AT + len(carr)] = carr
    mem[STATE_AT:STATE_AT + len(tup)] = tup
    mem[0x449] = 0x03
    mem[0x46C:0x470] = ticks.to_bytes(4, "little")
    return bytes(mem)


def savestate_bytes(rows, parr, carr, tup, ticks):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("Save_Remark", b"")
        z.writestr("Vga", zlib.compress(screen_component(rows)))
        z.writestr("Memory", zlib.compress(b"\x00" * MEM_BASE + memory_component(parr, carr, tup, ticks)))
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
        data = savestate_bytes(*state)
        name = f"snap-{n:04d}-20261007T17000{n}Z.sav"
        (session / "snapshots" / name).write_bytes(data)
        index.append({"seq": n, "file": f"snapshots/{name}", "bytes": len(data),
                      "sha256": hashlib.sha256(data).hexdigest(),
                      "utc": f"2026-10-07T17:00:0{n}.000Z", "elapsed_s": n * 20.0, "origin": "watcher"})
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
        # state 2 -> 3: the hand-checked bytes, squads and records
        self.assertEqual(self.diffobs(obs, "snap-0002", "screen changed"), "yes")
        self.assertEqual(self.diffobs(obs, "snap-0002", "[A923] byte changes"), STATE_CHANGES_2_3)
        self.assertEqual(self.diffobs(obs, "snap-0002", "country 1 squad changes"),
                         "slot 19: 20 -> 2561")
        self.assertEqual(self.diffobs(obs, "snap-0002", "country 1 player record changes"),
                         "player 5: 0x3: 40 -> 41")
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
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s


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
        session = self.workdir("gate")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(tiny_zip())
        clock = FakeClock()
        sends = []
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=sends.append, alive=lambda: True,
                             log=lambda m: None)
        entries = w.run(quit_after=45.0)
        self.assertEqual(len(sends), 3)
        for argv in sends:
            self.assertEqual(argv[:2], ["xdotool", "key"])
            self.assertIn("--window", argv)
            self.assertIn("77", argv)


class Cadence(Base):
    def test_ticks_at_the_cadence_from_zero(self):
        session = self.workdir("cadence")
        (session / "snapshots").mkdir(parents=True)
        live = session / "state.sav"
        live.write_bytes(tiny_zip())
        clock = FakeClock()
        w = recorder.Watcher(session, live, "77", FakeDbx(), {"DISPLAY": ":0"}, clock=clock,
                             sleep=clock.sleep, xrun=lambda a: None, alive=lambda: True,
                             log=lambda m: None)
        entries = w.run(quit_after=45.0)
        self.assertEqual([e["elapsed_s"] for e in entries], [0.5, 20.5, 40.5])
        self.assertEqual([e["seq"] for e in entries], [1, 2, 3])


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
            w.wait_stable()

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


if __name__ == "__main__":
    unittest.main()
