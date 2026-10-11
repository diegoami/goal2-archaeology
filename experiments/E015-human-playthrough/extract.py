#!/usr/bin/env python3
"""E015's extraction pass: walk one sitting's savestate chain (runtime/human/play.sh's session
folder) and emit one immutable `run/1` record in runs/E015/ — the sitting mined into raw
readings, no question answered here (that is each question's own task, e.g. T28's corroboration).

    python3 experiments/E015-human-playthrough/extract.py <session-dir> [--countries 1,4]
                                                          [--runs-dir runs] [--machine ubuntu-24-04-wsl2]

Per staged savestate (skipping, never failing on, one that does not parse — the owner's sitting
is unscripted and a partial chain is a valid record):
- the text screen (chars+attributes digest and CP437 text, each unique screen stored once);
- the game state: 0x10E bytes at the far pointer DS:A923 (the allocation `2139:0000` makes for
  it, static/goal-exe/code/seg_2139_01.asm), plus its named raw bytes: managers +0x00, fixture
  index +0x26, fixture count +0x28, year word +0x3A, stage byte +0x3C, speed byte +0x3F (F002,
  F004, F006);
- for each chosen country c: its 0xBF country record at [A917] (its first 20 words are the
  squad, R012 — emitted decoded with that licence), and the player records of the squad's
  current members — keyed by player number so a transfer's pool player is included in the diff
  even when the squad changes (R10);
- `players.check`'s verdict on the arrays (T15), so a state where the layout is not the start
  layout (transfers happened) is visible in the record instead of silently read wrong.

Between consecutive parsed states, a structured diff: the changed bytes of the game state, the
squad changes per country, the changed bytes per current squad member's player record, and
whether the screen changed.

The record names every file the pass read with its sha256 (snapshots, index, meta, config,
video), so the chain stays checkable after the session folder (git-ignored: savestates and
videos never enter the tree) is gone. Every file is hashed regardless of parse success
(rework round 2 R11 — the prior `was` "sha256 mismatch" and "not a savestate this reader
parses" states had no observation). The savestates themselves are published as evidence
(tools/publish_evidence.py). Records are never overwritten: the pass takes the next free
E015-r<nnnn> and creates it with O_CREAT|O_EXCL (rework round 2 R2 — a check-then-write race
on the path file would otherwise let two concurrent calls return E015-r0001.json).

Memory readings are marked `memory_unavailable` when GOAL.EXE cannot be located in the guest
or when the game state pointer at [A923] is 0000:0000 (rework round 2 R8 — the prior code
read IVT bytes at linear 0 as the game state tuple); the screen is still preserved. The
country and player arrays are checked the same way through their own far pointers [A917] and
[A91B] (`arrays_unavailable`; review round 2 R4), and a diff whose side lacks a reading says
"unavailable", never "none" (R6). A record's run_id is the slot it claimed (R5). A broken
final JSONL line is skipped, not fatal (rework round 2 R7 — abrupt termination used to leave
a partial line that raised JSONDecodeError before any state was extracted).

Standard library only, plus the G1 driver's modules."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime" / "driver"))
import driver  # noqa: E402  (host_times, SET_ID)
import players  # noqa: E402
import savestate  # noqa: E402

# ---- constants of the diff rules (each pinned by tests/test_human_record.py) ---------------------
# F002 / static/goal-exe/code/seg_2139_01.asm: `2139:0000` allocates 0x10E bytes for the game state;
# the far pointer to it is held at DS:A923 (the data-segment offset used by every routine that
# touches it). The named offsets inside the tuple are the static-known fields the screens and
# the bot depend on (F002, F004, F006); changing any one reads the wrong byte.
GAME_RECORD_PTR = 0xA923       # DS offset of the far pointer to the game state (R12 mutation pin)
GAME_RECORD_BYTES = 0x10E      # allocation, 2139:0000 (R12 mutation pin)
STAGE_OFFSET = 0x3C            # the stage byte inside it (F004: 2 or 5 = "qualifying"; R12 pin)
YEAR_OFFSET = 0x3A             # the year word (F004: GetDate's year + 1, made even; R12 pin)
FIXTURE_INDEX_OFFSET = 0x26    # the fixture index word; R12 pin (was 0x27 in a missed mutation)
FIXTURE_COUNT_OFFSET = 0x28    # the fixture count word; R12 pin
SPEED_OFFSET = 0x3F            # the match delay byte, 0 fastest (F006); R12 pin (was 0x40 in a
                               # missed mutation)
MANAGERS_OFFSET = 0x00         # the manager count word (F011); R12 pin (was 1 in a missed mutation)
SQUAD_WORDS = players.SQUAD    # 20 words of a country record name its squad (R012)
N_COUNTRIES = players.SQUAD_COUNTRIES  # 128 countries own squads (1771:9A40)
DEFAULT_COUNTRIES = "1"


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def short_commit():
    return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def hexs(b):
    return b.hex(" ")


def read_index(session):
    """The staged chain in order: index.jsonl's lines when present (valid prefix only — a
    truncated final line from abrupt termination is skipped, never fatal: rework round 2 R7),
    else the snapshots folder sorted by name (names carry the UTC stamp and the sequence).

    Returns (entries, malformed_count) so the record can name the dropped lines."""
    index = Path(session) / "index.jsonl"
    entries, malformed = [], 0
    if index.is_file():
        with open(index, "rb") as f:
            for raw in f:
                try:
                    line = raw.decode("utf-8").strip()
                except UnicodeDecodeError:
                    malformed += 1
                    continue
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    malformed += 1
                    continue
    else:
        for p in sorted((Path(session) / "snapshots").glob("*.sav")):
            entries.append({"file": f"snapshots/{p.name}", "seq": None, "sha256": None})
    return entries, malformed


def squad_words(country_record):
    """The first SQUAD_WORDS words of a country record: the squad's player numbers (R012)."""
    return [int.from_bytes(country_record[2 * i:2 * i + 2], "little") for i in range(SQUAD_WORDS)]


def player_record_bytes(player_array, n):
    """The 0x14 bytes of player `n` in the player array: n*0x14..(n+1)*0x14. Records are 1-indexed
    (record 0 is unused). Reading the current squad by player number — not by slot — is what
    rework round 2 R10 pinned: a transfer's pool player is a squad member in the *new* state and
    was not in the *old* one, so a slot-keyed diff silently omitted the change."""
    return player_array[n * players.PLAYER_SIZE:(n + 1) * players.PLAYER_SIZE]


def read_snapshot(session, entry, countries):
    """Read the staged file's bytes and hash them (every read happens, every read is hashed —
    rework round 2 R11). Returns a state dict carrying the file identity and, if available, the
    screen text; errors are reported in `error`, never raised."""
    out = {"entry": entry, "file": entry["file"],
           "label": f"{entry['seq']} ({entry['file']})" if entry.get("seq") else entry["file"],
           "memory_unavailable": None, "arrays_unavailable": None, "program_error": None,
           "state_tuple": None,
           "country_array": None, "player_array": None, "check_problems": None,
           "countries": {}, "screen_digest": None, "screen_text": None, "program": None,
           "state_ptr": None, "state_linear": None, "error": None}
    p = Path(entry["file"])
    if not p.is_absolute():
        p = Path(session) / entry["file"]
    out["path"] = p
    try:
        data = p.read_bytes()
    except OSError as e:
        out["error"] = f"unreadable: {e}"
        return out
    out["bytes"] = len(data)
    out["sha256"] = hashlib.sha256(data).hexdigest()
    if entry.get("sha256") and entry["sha256"] != out["sha256"]:
        out["error"] = f"sha256 mismatch: index says {entry['sha256']}, file is {out['sha256']}"
        return out
    try:
        st = savestate.Savestate(data)
    except (zipfile.BadZipFile, ValueError, OSError, KeyError) as e:
        out["error"] = f"not a savestate this reader parses: {e}"
        return out
    try:
        sc = st.screen()
    except ValueError as e:
        out["error"] = f"screen read failed: {e}"
        return out
    out["screen_digest"] = sc.digest()
    out["screen_text"] = sc.text()
    try:
        prog = st.program()
    except ValueError as e:
        out["program_error"] = str(e)
        out["memory_unavailable"] = "GOAL.EXE not located in the guest (no MCB+PSP)"
        return out
    out["program"] = prog.describe()
    # rework round 2 R8: refuse to read the game-state tuple when [A923] is uninitialized (the
    # far pointer holds 0000:0000), and refuse to read the country/player arrays when their
    # pointers are. Linear 0 is the IVT; reading it would be data, not a game state.
    try:
        ptr = players.far_pointer(st, GAME_RECORD_PTR)
    except ValueError as e:
        out["memory_unavailable"] = f"[A923] read failed: {e}"
        return out
    out["state_ptr"] = f"{ptr[0]:04X}:{ptr[1]:04X}"
    out["state_linear"] = ptr[2]
    if ptr[2] == 0:
        out["memory_unavailable"] = "game state pointer [A923] is 0000:0000 (uninitialized)"
        return out
    try:
        out["state_tuple"] = st.memory(ptr[2], GAME_RECORD_BYTES)
    except ValueError as e:
        out["memory_unavailable"] = f"game state memory read failed: {e}"
        return out
    # round 3 (review round 2 R4): the country and player arrays have their own far pointers,
    # [A917] and [A91B]; each is checked like [A923] before anything is read through it. An
    # uninitialized one makes the arrays unavailable while the game state above stays valid.
    for name, off in (("[A917] (country array)", players.COUNTRIES_PTR),
                      ("[A91B] (player array)", players.PLAYERS_PTR)):
        try:
            aptr = players.far_pointer(st, off)
        except ValueError as e:
            out["arrays_unavailable"] = f"{name} read failed: {e}"
            return out
        if aptr[2] == 0:
            out["arrays_unavailable"] = f"pointer {name} is 0000:0000 (uninitialized)"
            return out
    try:
        out["country_array"] = players.countries(st)
        out["player_array"] = players.players(st)
    except ValueError as e:
        out["arrays_unavailable"] = f"country or player array read failed: {e}"
        return out
    out["check_problems"] = players.check(out["player_array"], out["country_array"])
    for c in countries:
        crec = players.record(out["country_array"], players.COUNTRY_SIZE, c)
        # rework round 2 R9: country record c lives at (base + c * COUNTRY_SIZE), not
        # (c - 1) * COUNTRY_SIZE. The prior address claimed offset 0x90 for country 1 while
        # reading at 0xBF; the test fixture pins the correct address (0x600BF for country 1
        # when COUNTRY_AT=0x60000).
        base_addr = players.far_pointer(st, players.COUNTRIES_PTR)[2] + c * players.COUNTRY_SIZE
        squad = squad_words(crec)
        members = {n: player_record_bytes(out["player_array"], n) for n in squad}
        out["countries"][c] = {"record": crec, "record_linear": base_addr,
                               "squad": squad, "members": members,
                               "members_base": players.far_pointer(st, players.PLAYERS_PTR)[2]}
    return out


def byte_changes(before, after):
    """The changed bytes of two equal-length byte strings: [{offset, before, after}], hex."""
    return [{"offset": f"0x{i:X}", "before": f"{b:02X}", "after": f"{a:02X}"}
            for i, (b, a) in enumerate(zip(before, after)) if b != a]


def diff_states(prev, cur):
    """The structured diff between two parsed states (diff rules: game-state bytes, squad words
    per chosen country, current squad members' records per chosen country keyed by player
    number — rework round 2 R10 — and whether the screen changed)."""
    d = {"after_seq": cur["entry"].get("seq", cur["file"]), "screen_changed": False,
         "state_changes": [], "squad_changes": [], "record_changes": []}
    if prev.get("screen_digest") != cur.get("screen_digest"):
        d["screen_changed"] = True
    # round 3 (review round 2 R6): a side without readings makes the comparison unavailable
    # (None), which the record renders as such — never as "none" (unchanged).
    if prev.get("state_tuple") is not None and cur.get("state_tuple") is not None:
        d["state_changes"] = byte_changes(prev["state_tuple"], cur["state_tuple"])
    else:
        d["state_changes"] = None
    d["countries_compared"] = bool(prev.get("countries")) and bool(cur.get("countries"))
    for c in prev.get("countries", {}):
        pc, cc = prev["countries"][c], cur.get("countries", {}).get(c)
        if not cc:
            continue
        # squad slot moves (R012): the first SQUAD_WORDS words of the country record
        for slot, (b, a) in enumerate(zip(pc["squad"], cc["squad"])):
            if b != a:
                d["squad_changes"].append({"country": c, "slot": slot, "before": b, "after": a})
        # current squad members' records keyed by player number: a transfer's pool player
        # is in the union of prev and cur, and the diff names them by player number (R10).
        all_n = sorted(set(pc["members"]) | set(cc["members"]))
        for n in all_n:
            pr = pc["members"].get(n)
            cr = cc["members"].get(n)
            if pr is None:
                d["record_changes"].append(
                    {"country": c, "player": n, "status": "added", "changes": None,
                     "after": hexs(cr)})
                continue
            if cr is None:
                d["record_changes"].append(
                    {"country": c, "player": n, "status": "removed", "changes": None,
                     "before": hexs(pr)})
                continue
            ch = byte_changes(pr, cr)
            if ch:
                d["record_changes"].append({"country": c, "player": n, "status": "changed",
                                             "changes": ch})
    return d


def named_bytes(state):
    """The game state's named raw bytes, one (field, value) pair each; raw values, E004-style
    field names. Skipped when the state tuple was unavailable (R8)."""
    t = state.get("state_tuple")
    if t is None:
        return []

    def word(off):
        return int.from_bytes(t[off:off + 2], "little")

    return [(f"managers word [A923]+0x{MANAGERS_OFFSET:02X}", str(word(MANAGERS_OFFSET))),
            (f"fixture index word [A923]+0x{FIXTURE_INDEX_OFFSET:02X}",
             str(word(FIXTURE_INDEX_OFFSET))),
            (f"fixture count word [A923]+0x{FIXTURE_COUNT_OFFSET:02X}",
             str(word(FIXTURE_COUNT_OFFSET))),
            (f"year word [A923]+0x{YEAR_OFFSET:02X}", str(word(YEAR_OFFSET))),
            (f"stage byte [A923]+0x{STAGE_OFFSET:02X}", f"0x{t[STAGE_OFFSET]:02X}"),
            (f"match delay byte [A923]+0x{SPEED_OFFSET:02X} (0 fastest)",
             f"0x{t[SPEED_OFFSET]:02X}")]


def claim_record(runs_dir, rec):
    """Write `rec` as the next free E015-r<nnnn>.json. Records are immutable (L207): the slot is
    claimed with O_CREAT|O_EXCL, and on EEXIST (another extraction took it, R2) the next number
    is tried. rec["run_id"] is set to the claimed slot's id before its bytes are written, so a
    record's id always equals its filename (review round 2 R5). Returns the path."""
    d = Path(runs_dir) / "E015"
    d.mkdir(parents=True, exist_ok=True)
    n = 1
    while True:
        path = d / f"E015-r{n:04d}.json"
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            n += 1
            continue
        rec["run_id"] = f"E015-r{n:04d}"
        try:
            os.write(fd, (json.dumps(rec, indent=1) + "\n").encode("utf-8"))
            os.fsync(fd)
        finally:
            os.close(fd)
        return path


def host_free(value):
    """A recorded string without the owner's home directory (T34 review R9): the session path and
    DOSBox-X's `mount c <path>` echo on the shell screen name it. It becomes `~`; nothing else in
    the string changes, and a non-string is returned as it is."""
    home = str(Path.home())
    if isinstance(value, str) and len(home) > 1:
        return value.replace(home, "~")
    return value


def _jsonl(path):
    """The JSON objects of a JSONL file's well-formed lines, with their 1-based line numbers."""
    out = []
    if Path(path).is_file():
        for n, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
            try:
                out.append((n, json.loads(raw)))
            except json.JSONDecodeError:
                continue
    return out


def _utc(text):
    from datetime import datetime
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return None


def session_marks(session, meta):
    """The session's notes (notes.jsonl, runtime/human/note.py) and pauses (pauses.jsonl, the
    recorder), in time order: each {kind: note|pause|resume, line, utc, monotonic_s, ...}."""
    t0 = meta.get("monotonic_start_s")
    marks = [{"kind": "note", "line": n, "utc": x.get("utc"), "monotonic_s": x.get("monotonic_s"),
              "text": x.get("text", "")} for n, x in _jsonl(session / "notes.jsonl")]
    for n, x in _jsonl(session / "pauses.jsonl"):
        mono = x.get("monotonic_s")
        marks.append({"kind": x.get("event"), "line": n, "utc": x.get("utc"), "monotonic_s": mono,
                      "elapsed_s": x.get("elapsed_s") if x.get("elapsed_s") is not None else
                      (round(mono - t0, 3) if mono is not None and t0 is not None else None)})
    has_mono = t0 is not None and all(m["monotonic_s"] is not None for m in marks)
    marks.sort(key=(lambda m: m["monotonic_s"]) if has_mono else
               (lambda m: _utc(m["utc"] or "") or _utc("9999-12-31T00:00:00+00:00")))
    for m in marks:
        m["clock"] = "monotonic" if has_mono else "utc"
    return marks


def screen_time(entry, meta):
    """When a state's screen was taken: the start of its save-request window on the recorder's
    monotonic clock (meta's monotonic_start_s + request_s), else its staging UTC; None when
    neither is known."""
    t0 = meta.get("monotonic_start_s")
    if t0 is not None and entry.get("request_s") is not None:
        return {"monotonic": t0 + entry["request_s"], "utc": _utc(entry.get("utc") or "")}
    return {"monotonic": None, "utc": _utc(entry.get("utc") or "")}


def mark_before(mark, when):
    """Whether a note or pause precedes the screen taken at `when` (screen_time): on the monotonic
    clock both share, else on UTC. A state with no time places nothing before it."""
    if mark["clock"] == "monotonic" and when["monotonic"] is not None:
        return mark["monotonic_s"] < when["monotonic"]
    at = _utc(mark["utc"] or "")
    return at is not None and when["utc"] is not None and at < when["utc"]


def build_record(session, states, diffs, countries, runs_dir, machine, started, malformed, scripted_keys=False):
    """The run/1 document: one step per parsed state, the diffs after their later state, every
    file the pass read named with its sha256 (every file — R11 — and every country record
    address uses c * COUNTRY_SIZE, not (c-1) * COUNTRY_SIZE, R9)."""
    parsed = [s for s in states if s.get("error") is None]
    conf_path = session / "dosbox.conf"
    meta_path = session / "meta.json"
    meta = {}
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    commit = short_commit()
    rec = {
        "schema": "run/1",
        "run_id": None,  # set by claim_record to the slot it claims (R5)
        "experiment": "E015",
        "arm": "human-playthrough",
        "rep": 1,
        "code_commit": commit,
        "machine": machine,
        "artifact": {"set": driver.SET_ID, "variant": None},
        "runtime": {
            "driver": f"runtime/human/recorder.py@{commit}",
            "platform": f"python-{sys.version.split()[0]}/{machine}",
            "fingerprint": {"dosbox-x": meta.get("dosbox_x_version") or "unknown",
                            "extract_py_sha256": sha256_file(__file__)},
        },
        "interventions": [
            {"level": "I2",
             "what": "the recorder's watcher sent the host key F12+S directly to the game window "
                     "(xdotool key --window, never a global keystroke) every ~20 s of the sitting; "
                     "DOSBox-X wrote state.sav and the watcher staged a copy per snapshot "
                     "(a savestate written; neutrality not tested)"},
            {"level": "I1",
             "what": "each staged savestate's Vga and Memory components read (text screen and "
                     "guest memory), as the G1 driver reads savestates (F001 route A)"},
        ],
        "start_state": {
            "id": "first-savestate",
            "sha256": parsed[0]["sha256"] if parsed else "0" * 64,
            "restore": "no start state was restored: runtime/human/play.sh launched dosbox-x "
                       "windowed (config sha256 " + (meta.get("config_sha256") or
                       (sha256_file(conf_path) if conf_path.is_file() else "unknown")) + ") with "
                       "drive C: mounted from a per-session copy of the verified release set "
                       f"{driver.SET_ID}; GOAL booted under the player's own keys. The session's "
                       "earliest staged savestate is the earliest state on record.",
        },
        "seed": None,
        "actions": {
            "script": "experiments/E015-human-playthrough/extract.py",
            "sha256": sha256_file(__file__),
            "args": [host_free(str(session)), "--countries", ",".join(map(str, countries))],
        },
        "observations": [],
        "outputs": [],
        "started": started,
        "ended": driver.host_times()["utc"],
        "status": "completed",
    }
    obs = rec["observations"]
    step = 0

    def add(source, field, value, addr=None):
        item = {"step": step, "source": source, "field": field, "value": host_free(value)}
        if addr:
            item["addr"] = addr
        obs.append(item)

    add("log", "session folder (input; git-ignored: savestates and videos stay out of git)",
        str(session))
    for name, p in (("session index", session / "index.jsonl"), ("session meta", session / "meta.json"),
                    ("session dosbox config", conf_path)):
        if p.is_file():
            add("file", f"read {name}: {p.name} (bytes {p.stat().st_size})", sha256_file(p))
    if malformed:
        add("log", f"index.jsonl: {malformed} malformed line(s) skipped (valid-prefix recovery, R7)",
            str(malformed))
    def emit_diff(s):
        """The diff that ends at state s, for every parsed state — partial ones included (review
        round 2 R6). A comparison one side cannot make is rendered "unavailable", never "none"."""
        d = diffs.get(s["file"])
        if not d:
            return
        prev_file = d.get("prev_file")
        add("log", f"diff {prev_file} -> {s['file']}: screen changed",
            "yes" if d["screen_changed"] else "no")
        ch = d["state_changes"]
        add("log", f"diff {prev_file} -> {s['file']}: game state [A923] byte changes",
            "unavailable" if ch is None else
            "; ".join(f"{x['offset']}: {x['before']} -> {x['after']}" for x in ch) or "none")
        if not d.get("countries_compared"):
            add("log", f"diff {prev_file} -> {s['file']}: country squads and player records",
                "unavailable")
            return
        for c in sorted({x["country"] for x in d["squad_changes"]} | {x["country"] for x in d["record_changes"]}):
            sc = [x for x in d["squad_changes"] if x["country"] == c]
            rc = [x for x in d["record_changes"] if x["country"] == c]
            add("log", f"diff {prev_file} -> {s['file']}: country {c} squad changes (slot: "
                       f"before -> after)",
                "; ".join(f"slot {x['slot']}: {x['before']} -> {x['after']}" for x in sc) or "none")
            add("log", f"diff {prev_file} -> {s['file']}: country {c} player record changes "
                       f"(player: offset: before -> after)",
                "; ".join(_render_record_change(x) for x in rc) or "none")

    # T39b: the owner's coaching notes and DOSBox-X's pauses, each emitted between the two states
    # whose screens it falls between
    marks = session_marks(session, meta)
    for name in ("notes.jsonl", "pauses.jsonl"):
        if (session / name).is_file():
            add("file", f"read {name}", sha256_file(session / name))
    labels = [s["label"] for s in states]
    times = [screen_time(s["entry"], meta) for s in states]

    def emit_marks(i):
        """The marks before state i (all that remain when i == len(states)), between its
        predecessor and it."""
        while marks and (i == len(states) or mark_before(marks[0], times[i])):
            m = marks.pop(0)
            where = (f"between state {labels[i - 1] if i else '(start)'} and state "
                     f"{labels[i] if i < len(states) else '(end)'}")
            if m["kind"] == "note":
                add("log", f"note (notes.jsonl line {m['line']}, UTC {m['utc']}) {where}",
                    m["text"])
            else:
                add("log", f"{m['kind']} of DOSBox-X (pauses.jsonl line {m['line']}, UTC "
                           f"{m['utc']}, +{m['elapsed_s']}s) {where}", m["kind"])

    for i, s in enumerate(states):
        emit_marks(i)
        # rework round 2 R11: every file is hashed and named in the record, whether the parse
        # succeeded or not. The "unreadable" case has no bytes to hash; "sha256 mismatch" and
        # "not a savestate this reader parses" both have bytes and were silently dropped before.
        if s.get("bytes") is not None and s.get("sha256") is not None:
            add("file", f"read snapshot {s['file']} (bytes {s['bytes']})", s["sha256"])
        if s.get("error"):
            add("log", f"state {s['file']} skipped", s["error"])
            step += 1
            continue
        if s.get("memory_unavailable"):
            add("save", f"state {s['label']} (bytes {s['bytes']}, parsed)", s["sha256"])
            add("screen", f"state {s['label']}: text screen 80x25, chars+attributes (4000 bytes), sha256",
                s["screen_digest"])
            if s.get("program"):
                add("log", f"state {s['label']}: GOAL.EXE data segment located", s["program"])
            elif s.get("program_error"):
                add("log", f"state {s['label']}: GOAL.EXE data segment not found", s["program_error"])
            add("log", f"state {s['label']}: memory readings unavailable", s["memory_unavailable"])
            seen = rec.setdefault("_screens", {})
            if s["screen_digest"] not in seen:
                seen[s["screen_digest"]] = True
                add("ui-text", f"state {s['label']}: text screen rows 0-24, CP437 decoded, trailing "
                               f"blanks trimmed (digest {s['screen_digest']})", s["screen_text"])
            emit_diff(s)
            step += 1
            continue
        add("save", f"state {s['label']} (bytes {s['bytes']}, parsed)", s["sha256"])
        add("screen", f"state {s['label']}: text screen 80x25, chars+attributes (4000 bytes), sha256",
            s["screen_digest"])
        if s.get("program"):
            add("log", f"state {s['label']}: GOAL.EXE data segment located", s["program"])
        if s.get("state_tuple") is not None:
            add("memory", f"state {s['label']}: the game state, {GAME_RECORD_BYTES:#x} bytes at the "
                          f"far pointer DS:A923 -> {s['state_ptr']} (linear 0x{s['state_linear']:X}), hex",
                hexs(s["state_tuple"]), addr=f"0x{s['state_linear']:X}")
            for field, value in named_bytes(s):
                add("log", f"state {s['label']}: {field}", value)
        if s.get("arrays_unavailable"):
            add("log", f"state {s['label']}: country and player arrays unavailable",
                s["arrays_unavailable"])
        if s.get("check_problems") is not None:
            add("log", f"state {s['label']}: players.check problems (T15)",
                "; ".join(s["check_problems"]) or "none")
        seen = rec.setdefault("_screens", {})
        if s["screen_digest"] not in seen:
            seen[s["screen_digest"]] = True
            add("ui-text", f"state {s['label']}: text screen rows 0-24, CP437 decoded, trailing "
                           f"blanks trimmed (digest {s['screen_digest']})", s["screen_text"])
        for c, cc in s.get("countries", {}).items():
            add("memory", f"state {s['label']}: country record {c} ({players.COUNTRY_SIZE:#x} bytes "
                          f"at [A917]+c*{players.COUNTRY_SIZE:#x}={hex(cc['record_linear'])}), hex",
                hexs(cc["record"]), addr=f"0x{cc['record_linear']:X}")
            for n in sorted(cc["members"]):
                add("memory", f"state {s['label']}: country {c} squad player {n} record "
                              f"({players.PLAYER_SIZE:#x} bytes at [A91B]+n*{players.PLAYER_SIZE:#x}"
                              f"={hex(cc['members_base'] + n * players.PLAYER_SIZE)}), hex",
                    hexs(cc["members"][n]), addr=f"0x{cc['members_base'] + n * players.PLAYER_SIZE:X}")
        emit_diff(s)
        step += 1
    emit_marks(len(states))
    vpath = session / "video.mkv"
    if meta.get("video"):
        if vpath.is_file():
            add("file", f"read video {vpath.name} (bytes {vpath.stat().st_size})", sha256_file(vpath))
        else:
            add("log", "video named by the session meta but not present",
                json.dumps(meta["video"]))
    rec["decoded"] = [
        {"field": f"state {s['label']}: country {c} squad (player numbers)",
         "value": json.dumps(s["countries"][c]["squad"]),
         "via": "R012"}
        for s in states if s.get("error") is None and s.get("memory_unavailable") is None
        for c in s.get("countries", {})
    ]
    screens = {s["screen_digest"] for s in states if s.get("error") is None}
    partial = sum(1 for s in states if s.get("error") is None
                  and (s.get("memory_unavailable") or s.get("arrays_unavailable")))
    add("log", "summary",
        f"states: {len(parsed)}, screens: {len(screens)} unique, diffs: {len(diffs)}"
        + (f", skipped: {len(states) - len(parsed)}" if len(states) > len(parsed) else "")
        + (f", partial: {partial}" if partial else ""))
    rec.pop("_screens", None)
    if (session / "notes.jsonl").is_file() or (session / "pauses.jsonl").is_file():
        kinds = [m["kind"] for m in session_marks(session, meta)]
        add("log", "notes and pauses placed between states (T39b)",
            f"notes: {kinds.count('note')}, pauses: {kinds.count('pause')}, "
            f"resumes: {kinds.count('resume')}")
    screen_key_map = None
    if (session / "keys.jsonl").is_file():
        import keymap
        screen_key_map = keymap.read_session(session, states)
        rec["runtime"]["fingerprint"]["keymap_py_sha256"] = sha256_file(keymap.__file__)
        add("file", "read key log keys.jsonl", sha256_file(session / "keys.jsonl"))
        add("log", "key log presses (keys.jsonl lines whose event is press)",
            str(sum(1 for line in (session / "keys.jsonl").read_text().splitlines()
                    if line.strip() and json.loads(line).get("event") == "press")))
        if (session / "requests.jsonl").is_file():
            add("file", "read save requests requests.jsonl", sha256_file(session / "requests.jsonl"))
        add("log", "screen/key map summary", screen_key_map["summary"])
        add("log", "screen/key map (JSON)", json.dumps(screen_key_map, sort_keys=True))
        if scripted_keys:
            add("log", "scripted sitting key events (explicit opt-in; never for human sittings)",
                (session / "keys.jsonl").read_text())
    if not parsed:
        rec["status"] = "aborted: no savestate in the session parsed"
    out_path = claim_record(runs_dir, rec)
    if screen_key_map is not None:
        table_path = ROOT / "experiments" / "E015-human-playthrough" / f"{rec['run_id']}-keymap.md"
        # Tables follow the record's immutable id; fixture runs stay in their run folder.
        if Path(runs_dir).resolve() != (ROOT / "runs").resolve():
            table_path = out_path.with_suffix(".keymap.md")
        with open(table_path, "x", encoding="utf-8") as f:
            f.write(keymap.table(screen_key_map))
    return rec, out_path


def _render_record_change(x):
    """One diff entry for a squad member, as it appears in the per-country observation."""
    status = x["status"]
    if status == "added":
        return f"player {x['player']}: added ({x['after']})"
    if status == "removed":
        return f"player {x['player']}: removed ({x['before']})"
    return f"player {x['player']}: " + "; ".join(
        f"{y['offset']}: {y['before']} -> {y['after']}" for y in x["changes"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("session", type=Path, help="a session folder made by runtime/human/play.sh")
    ap.add_argument("--countries", default=DEFAULT_COUNTRIES,
                    help=f"comma-separated country numbers 1..{N_COUNTRIES} (default {DEFAULT_COUNTRIES})")
    ap.add_argument("--runs-dir", type=Path, default=ROOT / "runs")
    ap.add_argument("--machine", default="ubuntu-24-04-wsl2")
    ap.add_argument("--scripted-keys", action="store_true", help="include raw keys ONLY for a scripted acceptance sitting")
    a = ap.parse_args(argv)
    session = a.session.resolve()
    if not session.is_dir():
        raise SystemExit(f"{session}: no such session folder")
    countries = []
    for part in a.countries.split(","):
        part = part.strip()
        if not part:
            continue
        c = int(part)
        if not 1 <= c <= N_COUNTRIES:
            raise SystemExit(f"country {c}: countries with squads run 1..{N_COUNTRIES}")
        countries.append(c)
    started = driver.host_times()["utc"]
    t0 = time.monotonic()
    entries, malformed = read_index(session)
    if not entries:
        raise SystemExit(f"{session}: no staged savestates (no index.jsonl and no snapshots/)")
    states = [read_snapshot(session, e, countries) for e in entries]
    diffs = {}
    last = None
    for s in states:
        if s.get("error"):
            continue
        if last is not None:
            d = diff_states(last, s)
            d["prev_file"] = last["file"]
            diffs[s["file"]] = d
        last = s
    rec, out_path = build_record(session, states, diffs, countries, a.runs_dir, a.machine, started,
                                 malformed, scripted_keys=a.scripted_keys)
    parsed = [s for s in states if s.get("error") is None]
    screens = {s["screen_digest"] for s in parsed if s.get("screen_digest") is not None}
    partial = sum(1 for s in parsed if s.get("memory_unavailable") or s.get("arrays_unavailable"))
    print(f"states: {len(parsed)}, screens: {len(screens)} unique, diffs: {len(diffs)}"
          + (f", skipped: {len(states) - len(parsed)}" if len(states) > len(parsed) else "")
          + (f", partial: {partial}" if partial else ""))
    print(f"{out_path} ({time.monotonic() - t0:.1f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
