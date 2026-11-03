"""E040 (T119b, #427): route_fixture's writes and draws, observed by the route harness, against the static write-set.

    python3 -B experiments/E040-route-fixture-writes/runner.py --run [RUN_ID ...]   # record the cases not yet recorded
    python3 -B experiments/E040-route-fixture-writes/runner.py --check              # the committed records vs the tables
    python3 -B experiments/E040-route-fixture-writes/runner.py --report             # also writes out/coverage.json

The protocol is README.md beside this file. `--run` needs unicorn and the published states (`.cache/dl`, fetched by
`--fetch`, each verified by its sha256); it runs one call of route_fixture 000E:6CA7 per case with the route harness
(runtime/original_match/route.py, T119a) and its default key policy, and writes runs/E040/<run id>.json (run/1).
`--check` needs neither: it reads the committed records and the static tables notes/427/writeset/*.json.

What the runner observes [designed: T119b; the sites from the raw listings, as check.py reads them]: a code hook at
every instruction of the scoped routines (the three tables' scopes) that is a basic block's leader, a store or call
site, or a call's return address. From these it keeps the stack of active scoped calls (pushed at a call site, popped
when its return address is reached with SP at or above the call's), and gives every write the harness records the
chain of scoped sites it happened in: its own site when the writing instruction is in a scoped routine, else the
innermost active call. The match (Match, tail=False) is the call at 000E:6F18; its write-back and its draws are
attributed to that call. The record keeps the observations, never a row of the tables: the check maps them.
"""
import argparse
import collections
import datetime
import hashlib
import importlib.util
import json
import platform
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNS = ROOT / "runs" / "E040"
OUT = HERE / "out"
DL = ROOT / ".cache" / "dl"
WRITESET = ROOT / "notes" / "427" / "writeset"
TABLES = ("writeset.json", "sack.json", "news.json")
CODE = ROOT / "static" / "goal-exe" / "code"
SCHEMA_NOTE = "e040/1"
ARTIFACT_SET = "goal2-67cf27d6"     # the states' GOAL.EXE (evidence/E006, E014, E015 manifests)

# The cases [designed: T119b; every state published, at the manager menu ("play next game") with the next managed
# fixture ahead of the cursor; calendars read from the states' memory, the screens from the run records named]:
LIMIT_ROUND_BYTE = ("aborted: GuestError: Match's set-up wrote what route_fixture had not left there: inputs "
                    "[{'what': 'fixture 22 := 16 v 3, kind 2'")
CASES = [
    # run id, arm, release, asset, what the run record of the state says (its sha256: its evidence manifest), the key
    # policy, and the status expected ("completed", or the harness limit the case meets: README.md, "Harness limits")
    ("E040-r0001", "e006-friendly", "E006", "e0afff6751747233-e006-1000-r0001.sav",
     "E006-r0001's state: manager menu, fixture 1 the managed friendly 27 v 7 (first byte 0xFE)", "default", "completed"),
    ("E040-r0002", "e006-friendly", "E006", "e548627d333fb1b8-e006-1001-r0002.sav",
     "E006-r0002's state: fixture 1 the managed friendly 9 v 7", "default", "completed"),
    ("E040-r0003", "e006-friendly", "E006", "cb78606bc5c54674-e006-1002-r0003.sav",
     "E006-r0003's state: seven silent friendlies, then the managed friendly 31 v 7 (fixture 8)", "default", "completed"),
    ("E040-r0004", "e006-friendly", "E006", "f8b22081eeb072e5-e006-1337-r0004.sav",
     "E006-r0004's state: two silent friendlies, then the managed friendly 7 v 27 (fixture 3)", "default", "completed"),
    ("E040-r0005", "e006-friendly", "E006", "3453dbc1663430b5-e006-2358-r0006.sav",
     "E006-r0006's state: three silent friendlies, then the managed friendly 7 v 22 (fixture 4)", "default", "completed"),
    ("E040-r0006", "e006-friendly", "E006", "c6b4796bbd02b1ab-e006-0000-r0007.sav",
     "E006-r0007's state: seven silent friendlies, then the managed friendly 13 v 7 (fixture 8)", "default", "completed"),
    ("E040-r0007", "e006-friendly", "E006", "b9f1fe3925f4b8b3-e006-1200-r0009.sav",
     "E006-r0009's state: five silent fixtures, then the managed friendly 8 v 7 (fixture 6)", "default", "completed"),
    ("E040-r0008", "e006-friendly", "E006", "5a4bd63023af6b7c-e006-1745-r0010.sav",
     "E006-r0010's state: eight silent fixtures, then the managed friendly 13 v 7 (fixture 9)", "default", "completed"),
    ("E040-r0009", "e015-friendly", "E015", "71eefbea6e9db696-snap-0026-20261011T141040Z.sav",
     "E015-r0007 state 26: manager menu (Italy, 16); silent fixtures 1-17 (7 with first byte 0xFE), the managed "
     "friendly 29 v 16 (fixture 18)", "default+tables", "completed"),
    ("E040-r0010", "e015-qualifier", "E015", "53b69d3dfb964e77-snap-0213-20261011T142027Z.sav",
     "E015-r0007 state 213: manager menu; silent friendlies 19-21, the managed qualifier 16 v 3 (fixture 22, kind 2)",
     "default", LIMIT_ROUND_BYTE),
    ("E040-r0011", "e015-qualifier", "E015", "46bbf5dabaaa9553-snap-0003-20261011T195415Z.sav",
     "E015-r0009 state 3: the same calendar position as r0010, another sitting (seed word 0)", "default",
     LIMIT_ROUND_BYTE),
    ("E040-r0012", "e014-stage3", "E014", "291d0eb3b0dcec34-e014-cal3-y1.sav",
     "E014-r0006's input (cal3-y1): stage 3, cursor 769 of 1345, country 7 managed", "default", "completed"),
]

# Far pointers to the records the writes are sorted into, with their allocated sizes (globals.tsv, F007, F011, F023;
# the game block's 0x10E bytes as the E015 records read it; the two text pages 4000 bytes, 80 x 25 x 2).
BLOCKS = (("game", 0xA923, 0x10E, None), ("countries", 0xA917, 0x603F, 0xBF), ("players", 0xA91B, 0xEF24, 0x14),
          ("managers", 0xA91F, 0x195, None), ("pool", 0xA927, 0x3C2, None), ("fixtures", 0xA92B, 0x4B48, 8),
          ("fixture_lists", 0xA92F, 0x2448, None), ("group_tables", 0xA933, 0x1C00, None),
          ("video", 0xA96A, 4000, None), ("backbuf", 0xA96E, 4000, None))
DS_SIZE = 0xAD10        # SS = load + 0x3052 = DS + 0xAD1 paragraphs: DS offsets from 0xAD10 are the stack segment's
STACK_SIZE = 0x4000

JUMPS = re.compile(r"^(j[a-z]+|loop[a-z]*|jcxz)$")
ENDS = {"ret", "retf", "iret", "jmp"}
LINE = re.compile(r"^([0-9A-F]{4})  ((?:[0-9A-F]{2} )+)\s*(.+)$")
LABEL = re.compile(r"^(?:loc|sub)_([0-9A-F]{4}):$")
SEAT_TEST, SEAT_DRAW = "000E:04A6", "000E:04B2"     # 045D: `cmp byte es:[di-0xA2], 7; jae` then 06B1(15)


def _check_module():
    spec = importlib.util.spec_from_file_location("t118_check", WRITESET / "check.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def tables():
    return {name: json.loads((WRITESET / name).read_text()) for name in TABLES}


def scope_routines(tabs=None):
    out = []
    for t in (tabs or tables()).values():
        out += [r for r in t["scope"] if r not in out]
    return out


def listing(routine, chk=None):
    """Every instruction of a routine in the raw listing: [(offset, length, mnemonic, operands, line)], and the label
    offsets."""
    chk = chk or _check_module()
    path, first, last = chk.listing_of(routine)
    insns, labels = [], set()
    for n, text in enumerate(path.read_text().splitlines()[first - 1:last], start=first):
        m = LABEL.match(text)
        if m:
            labels.add(int(m.group(1), 16))
            continue
        m = LINE.match(text)
        if not m:
            continue
        words = m.group(3).split()
        mnem = words[0]
        ops = " ".join(words[1:])
        if mnem in ("rep", "repe", "repne", "repz", "repnz", "lock") and len(words) > 1:
            mnem, ops = words[1], " ".join(words[2:])
        insns.append((int(m.group(1), 16), len(m.group(2).split()), mnem, ops, n))
    return insns, labels


def static_model(chk=None):
    """From the raw listings alone (no rows): per scoped routine its instructions, basic blocks, store and call sites
    (check.py's own `sites`), and each call's return address. Keys are 'SSSS:OOOO'."""
    chk = chk or _check_module()
    model = {"insn": {}, "leader": {}, "block": {}, "store": set(), "call": {}, "stackop": set(), "routine": {}}
    for routine in scope_routines():
        seg = routine[:4]
        insns, labels = listing(routine, chk)
        found = chk.sites(routine)
        leaders = {insns[0][0]} | labels
        for i, (off, length, mnem, ops, line) in enumerate(insns):
            if JUMPS.match(mnem) or mnem in ENDS:
                if i + 1 < len(insns):
                    leaders.add(insns[i + 1][0])
                t = re.search(r"0x([0-9a-f]+)$", ops)
                if t and "far" not in ops and "[" not in ops:
                    leaders.add(int(t.group(1), 16))
        block = None
        for i, (off, length, mnem, ops, line) in enumerate(insns):
            site = f"{seg}:{off:04X}"
            if off in leaders:
                block = site
                model["leader"][site] = routine
            model["insn"][site] = (routine, mnem, ops, line)
            model["block"][site] = block
            model["routine"][site] = routine
            kind = found.get(site, (None, None))[1]
            if kind == "store":
                model["store"].add(site)
            elif kind == "call":
                nxt = insns[i + 1][0] if i + 1 < len(insns) else off + length
                if nxt != off + length:
                    raise ValueError(f"{site}: the next instruction is at {nxt:04X}, not {off + length:04X}")
                model["call"][site] = f"{seg}:{nxt:04X}"
            elif mnem in ("push", "pushf", "enter", "int"):
                model["stackop"].add(site)
    return model


# -- running ---------------------------------------------------------------------------------------------------------
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch():
    """Download every case's state from its release into .cache/dl (skipped when present), and verify it."""
    DL.mkdir(parents=True, exist_ok=True)
    for run_id, arm, release, asset, what, *_ in CASES:
        path = DL / asset
        if not path.exists():
            subprocess.run(["gh", "release", "download", release, "--pattern", asset, "--dir", str(DL)],
                           cwd=ROOT, check=True)
        print(run_id, asset, "ok" if sha256(path) == expected(asset) else "HASH MISMATCH")


def expected(asset):
    """The sha256 the state's evidence manifest records (evidence/E<nnn>/*.manifest.json), by its asset name."""
    for path in sorted((ROOT / "evidence").glob("E0*/*.manifest.json")):
        for f in json.loads(path.read_text()).get("files", ()):
            if f.get("asset") == asset:
                return f["sha256"]
    raise ValueError(f"{asset}: no evidence manifest names it")


class Observer:
    """The code hooks on the route harness's machine: every hit of a hooked address, with the record's length then."""

    def __init__(self, route, model):
        self.r, self.model = route, model
        self.events = []
        m = route.m
        sites = set(model["leader"]) | model["store"] | set(model["call"]) | set(model["call"].values()) | {SEAT_TEST}
        self.lin = {}
        for site in sorted(sites):
            lin = m.lin(site)
            self.lin[lin] = site
            m.at_linear(lin, self._hit(site))

    def _hit(self, site):
        r, events = self.r, self.events
        m = r.m
        if site == SEAT_TEST:
            def probe(replay):
                if replay:
                    return
                di = (m.reg("di") - 0xA2) & 0xFFFF
                byte = m.read(m.reg("es") * 16 + di, 1)[0]
                events.append((len(r.record), site, m.reg("sp"), byte))
            return probe

        def hit(replay):
            if not replay:
                events.append((len(r.record), site, m.reg("sp"), None))
        return hit


# 6970's score page for a 0xFE fixture calls show_updated_group_tables 0791:E929, whose table screen reads a key
# through 214B:1560 from 1771:9022 or 91BE, or through 08DD at 1771:9562 (the finals' table) [confirmed: match.py
# TABLE_READS, TABLE_KEY, where Match answers Enter: "the competition's table, looked at: one pass"]. route.py's
# DEFAULT_KEYS does not name these sites; the cases that reach them answer them as Match does (README.md).
TABLE_SITES = ("214B:157C<1771:9022", "214B:157C<1771:91BE", "1771:9567")


def policy(case):
    from original_match import route as R
    keys = dict(R.DEFAULT_KEYS)
    if case[5] == "default+tables":
        keys.update({s: R.ENTER for s in TABLE_SITES})
    return keys


def regions_of(m):
    """[(name, start, size, stride)] of the blocks, from the far pointers in this state."""
    return [(name, m.far(ptr), size, stride) for name, ptr, size, stride in BLOCKS]


def classify(m, blocks, linear):
    ds, ss = m.DS * 16, m.seg(0x3052) * 16
    for name, start, size, stride in blocks:
        if start <= linear < start + size:
            off = linear - start
            if name == "game":
                return f"game:+{off:02X}"
            if stride:
                return f"{name}:+{off % stride:02X}"
            return name
    if ss <= linear < ss + STACK_SIZE:
        return "stack"
    if ds <= linear < ds + DS_SIZE:
        return f"ds:{linear - ds:04X}"
    return f"other:{linear:05X}"


def digest(route, observer, model, start_memory):
    """The observations of one call, from the harness's record and the hook hits, merged in time order."""
    m, rec, events = route.m, route.record, observer.events
    blocks = regions_of(m)
    seed_lin = {"7B62": m.DS * 16 + 0x7B62, "8336": m.DS * 16 + 0x8336}
    stack = []      # frames: [site, return site, sp, steps 7B62, steps 8336]
    visits, leaders = collections.Counter(), collections.Counter()
    seq = []        # the writeset-scope sites visited, in order (route_fixture, 6C21, 6970, 6685)
    first_scope = set(tables()["writeset.json"]["scope"])
    writes = collections.Counter()      # (outer chain site, writeset-level site, inner site, how, region) -> count
    kit_bytes = collections.Counter()   # (writeset-level site, inner site, why, region) -> bytes
    steps_hist = {"7B62": collections.defaultdict(collections.Counter), "8336": collections.defaultdict(collections.Counter)}
    draws = {"7B62": [], "8336": []}    # runs of [where, inner site, count]
    chain_ok = {"7B62": True, "8336": True}
    last_word = {k: int.from_bytes(start_memory[v:v + 2], "little") for k, v in seed_lin.items()}
    seat = collections.Counter()
    keys = collections.Counter()
    problems = []
    unmatched_returns = 0
    writeset_routines = first_scope

    def in_first(site):
        return model["routine"].get(site) in writeset_routines

    def chain(own=None):
        c = [f[0] for f in stack] + ([own] if own else [])
        return c

    def levels(c):
        """(outermost, the innermost writeset-scope site, innermost) of a chain."""
        if not c:
            return None, None, None
        ws = None
        for s in c:
            if in_first(s):
                ws = s
        return c[0], ws, c[-1]

    def visit(site, sp):
        visits[site] += 1
        if in_first(site):
            seq.append(site)

    def handle(site, sp, extra):
        if stack and stack[-1][1] == site and sp >= stack[-1][2]:
            f = stack.pop()
            steps_hist["7B62"][f[0]][f[3]] += 1
            steps_hist["8336"][f[0]][f[4]] += 1
        if site == SEAT_TEST:
            seat["lt7" if extra < 7 else "ge7"] += 1
            return
        if site in model["leader"]:
            leaders[site] += 1
        if site in model["store"] or site in model["call"]:
            visit(site, sp)
        if site in model["call"]:
            stack.append([site, model["call"][site], sp, 0, 0])

    def add_draw(name, where, inner):
        runs = draws[name]
        if runs and runs[-1][0] == where and runs[-1][1] == inner:
            runs[-1][2] += 1
        else:
            runs.append([where, inner, 1])

    ev = 0
    for i, e in enumerate(rec):
        while ev < len(events) and events[ev][0] <= i:
            _, site, sp, extra = events[ev]
            handle(site, sp, extra)
            ev += 1
        kind = e[0]
        if kind == "w":
            _, pc, linear, size, value = e
            site = _site_of(m, model, pc)
            if site is not None:
                if site in model["store"]:
                    how = "store"
                elif site in model["call"]:
                    how = "call-push"
                elif site in model["stackop"]:
                    how = "stack-op"
                else:
                    how = "unlisted"
                c = chain() if how == "call-push" and stack and stack[-1][0] == site else chain(site)
            else:
                how = "callee" if stack else "outside"
                c = chain()
            outer, ws, inner = levels(c)
            writes[(outer, ws, inner, how, classify(m, blocks, linear))] += 1
        elif kind == "k":
            _, why, linear, data = e
            if why.startswith("delay calibration") or why.startswith("the call of"):
                ws = inner = "harness"
            else:
                c = chain()
                _, ws, inner = levels(c)
            label = "match" if why == "match" else why.split(" ")[0]
            for j in range(len(data)):
                region = classify(m, blocks, linear + j)
                if label == "match" and region.startswith(("ds:", "other:")):
                    region = region.split(":")[0]       # the match's write-back: DS bytes counted together
                kit_bytes[(ws, inner, label, region)] += 1
        elif kind == "rng":
            _, name, old, new, pc, where = e
            if old != last_word[name]:
                chain_ok[name] = False
            last_word[name] = new
            inner = stack[-1][0] if stack else None
            if stack:
                stack[-1][3 if name == "7B62" else 4] += 1
            add_draw(name, where, inner)
        elif kind == "stop":
            visit(e[1], 0x3EC4)
            stack.append([e[1], model["call"][e[1]], 0x3EC4, 0, 0])
        elif kind == "resume":
            if stack and stack[-1][0] == "000E:6F18":
                f = stack.pop()
                steps_hist["7B62"][f[0]][f[3]] += 1
                steps_hist["8336"][f[0]][f[4]] += 1
            else:
                problems.append("resume without the 6F18 frame on top")
        elif kind == "key":
            _, site, how, key, source = e
            inner = stack[-1][0] if stack else None
            keys[(site, how, source, inner)] += 1
    while ev < len(events):
        _, site, sp, extra = events[ev]
        handle(site, sp, extra)
        ev += 1
    if stack:
        problems.append(f"frames still open at the return: {[f[0] for f in stack]}")
    return {
        "visits": dict(sorted(visits.items())),
        "leaders": dict(sorted(leaders.items())),
        "sequence": seq,
        "writes": [list(k) + [n] for k, n in sorted(writes.items(), key=lambda kv: [str(x) for x in kv[0]])],
        "kit_bytes": [list(k) + [n] for k, n in sorted(kit_bytes.items(), key=lambda kv: [str(x) for x in kv[0]])],
        "steps_per_visit": {name: {s: {str(k): v for k, v in sorted(h.items())} for s, h in sorted(hist.items())}
                            for name, hist in steps_hist.items()},
        "draws": draws,
        "draw_chain_ok": chain_ok,
        "seat_test": dict(seat),
        "keys": [list(k) + [n] for k, n in sorted(keys.items(), key=lambda kv: [str(x) for x in kv[0]])],
        "problems": problems,
    }


def _site_of(m, model, pc):
    """'SSSS:OOOO' of a linear pc in a scoped routine's segment, or None."""
    for seg in ("000E", "1771"):
        base = m.seg(int(seg, 16)) * 16
        if 0 <= pc - base < 0x10000:
            site = f"{seg}:{pc - base:04X}"
            if site in model["insn"]:
                return site
    return None


def fixture_facts(m, before, after, first, last):
    from original_match.image import FIXTURES_PTR, FIXTURE_SIZE, COUNTRIES_PTR, COUNTRY_SIZE
    fx, co = m.far(FIXTURES_PTR), m.far(COUNTRIES_PTR)
    out = []
    for n in range(first, last + 1):
        a = fx + FIXTURE_SIZE * (n - 1)
        b0, b1 = before[a:a + 8], after[a:a + 8]
        sides = [int.from_bytes(b0[4:6], "little"), int.from_bytes(b0[6:8], "little")]
        out.append({"index": n, "before": b0.hex(), "after": b1.hex(), "sides": sides,
                    "manager_byte_before": [before[co + COUNTRY_SIZE * c + 0x2E] for c in sides],
                    "manager_byte_after": [after[co + COUNTRY_SIZE * c + 0x2E] for c in sides]})
    return out


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def run_case(case, model):
    run_id, arm, release, asset, what = case[:5]
    from original_match import route as R
    from original_match.image import Image, GAME_PTR
    from original_match.machine import MEM_SIZE
    path = DL / asset
    digest_expected = expected(asset)
    actual = sha256(path)
    if actual != digest_expected:
        raise SystemExit(f"{asset}: sha256 {actual}, its manifest says {digest_expected}")
    started = datetime.datetime.now(datetime.timezone.utc)
    image = Image.from_savestate(path.read_bytes())
    r = R.Route(image, keys=policy(case))
    obs = Observer(r, model)
    m = r.m
    game = m.far(GAME_PTR)
    start = bytes(r.origin)
    head = {"cursor": m.word_at(game + 0x26), "count": m.word_at(game + 0x28), "season_word_38": m.word_at(game + 0x38),
            "year_word_3A": m.word_at(game + 0x3A), "stage_3C": m.read(game + 0x3C, 1)[0],
            "managers_0": m.read(game, 1)[0], "game_1": m.read(game + 1, 1)[0], "seed_7B62": m.rd(0x7B62),
            "seed_8336": m.rd(0x8336)}
    t0 = time.time()
    status = "completed"
    try:
        r.call()
    except Exception as exc:     # an aborted run is kept (README: stopping rule)
        status = f"aborted: {type(exc).__name__}: {str(exc).splitlines()[0][:300]}"
    elapsed = time.time() - t0
    end = bytes(m.read(0, MEM_SIZE))
    tail = {"cursor": m.word_at(game + 0x26), "seed_7B62": m.rd(0x7B62), "seed_8336": m.rd(0x8336)}
    d = digest(r, obs, model, start)
    counts = collections.Counter(e[0] for e in r.record)
    raw = hashlib.sha256()
    for e in r.record:
        raw.update(repr(e).encode())
    replay_ok = r.replay(r.origin) == end
    facts = fixture_facts(m, start, end, head["cursor"], max(head["cursor"], tail["cursor"] - 1))
    matches = [e[1] for e in r.record if e[0] == "match"]
    ended = datetime.datetime.now(datetime.timezone.utc)
    commit = git("rev-parse", "HEAD")
    obs_list = []

    def o(source, field, value):
        obs_list.append({"step": 0, "source": source, "field": field,
                         "value": value if isinstance(value, str) else json.dumps(value, separators=(",", ":"))})
    o("save", f"start state {asset} (sha256, verified against its evidence manifest)", actual)
    o("log", "e040 observation schema", SCHEMA_NOTE)
    o("log", "the case", what)
    o("memory", "game record and seeds at the start (cursor +0x26, count +0x28, +0x38, +0x3A, +0x3C, +0, +1, DS:7B62, "
      "DS:8336)", head)
    o("log", "the harness's inputs (Route.inputs)", r.inputs)
    o("log", "the harness's record: entries by kind, and the sha256 of their repr() in order",
      {"counts": dict(sorted(counts.items())), "sha256": raw.hexdigest()})
    o("log", "the record replayed over the start memory equals the memory the call left", "true" if replay_ok else "false")
    o("log", "the managed matches (Route.record 'match' entries)", matches)
    o("memory", "the fixtures from the start cursor to the last one run: bytes before and after, both sides' "
      "country +0x2E before and after", facts)
    o("memory", "game record and seeds at the end", tail)
    for key in ("visits", "leaders", "sequence", "writes", "kit_bytes", "steps_per_visit", "draws", "draw_chain_ok",
                "seat_test", "keys", "problems"):
        o("log", f"observed: {key}", d[key])
    o("log", "elapsed seconds of the call", f"{elapsed:.1f}")
    import unicorn
    record = {
        "schema": "run/1", "run_id": run_id, "experiment": "E040", "arm": arm,
        "rep": sum(1 for c in CASES[:CASES.index(case) + 1] if c[1] == arm),
        "code_commit": commit[:12], "machine": "wsl-ubuntu",
        "artifact": {"set": ARTIFACT_SET, "variant": None},
        "runtime": {"driver": f"runtime/original_match/route.py@{commit[:12]}",
                    "platform": f"python-{platform.python_version()}/{platform.system().lower()}",
                    "fingerprint": {"unicorn": unicorn.__version__, "python": platform.python_version(),
                                    "route.py": sha256(ROOT / "runtime/original_match/route.py"),
                                    "match.py": sha256(ROOT / "runtime/original_match/match.py"),
                                    "machine.py": sha256(ROOT / "runtime/original_match/machine.py")}},
        "interventions": [
            {"level": "I1", "what": "every write, RNG step and key visit recorded by the route harness (T119a), and code "
                                    "hooks at the scoped routines' leaders, store and call sites and return addresses"},
            {"level": "I3", "what": "the key policy route.DEFAULT_KEYS (a key at the first poll, Enter; N at the watch "
                                    "prompt)" + (", and Enter at the group-table reads " + ", ".join(TABLE_SITES) +
                                                 " (as Match answers them)" if case[5] == "default+tables" else "") +
                                    "; the managed match played by Match(tail=False) and written back"}],
        "start_state": {"id": asset, "sha256": actual,
                        "restore": "the Memory component of the published savestate loaded into a kit Machine "
                                   "(Image.from_savestate); route_fixture 000E:6CA7 called as play_round 70D1 calls it"},
        "seed": None,
        "actions": {"script": "experiments/E040-route-fixture-writes/runner.py", "sha256": sha256(Path(__file__)),
                    "args": ["--run", run_id]},
        "observations": obs_list, "outputs": [],
        "started": started.strftime("%Y-%m-%dT%H:%M:%SZ"), "ended": ended.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
    }
    return record


def do_run(ids):
    sys.path.insert(0, str(ROOT / "runtime"))
    dirty = git("status", "--porcelain", "--", "experiments/E040-route-fixture-writes/runner.py", "runtime/original_match",
                "notes/427/writeset")
    if dirty:
        raise SystemExit(f"refused: uncommitted changes the record would not name:\n{dirty}")
    model = static_model()
    RUNS.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        if ids and case[0] not in ids:
            continue
        path = RUNS / f"{case[0]}.json"
        if path.exists():
            print(case[0], "recorded already: kept")
            continue
        rec = run_case(case, model)
        path.write_text(json.dumps(rec, indent=1) + "\n")
        print(case[0], rec["status"], flush=True)


# -- the check -------------------------------------------------------------------------------------------------------
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--run", nargs="*", metavar="RUN_ID")
    p.add_argument("--fetch", action="store_true")
    p.add_argument("--check", action="store_true")
    p.add_argument("--report", action="store_true")
    a = p.parse_args(argv)
    if a.fetch:
        fetch()
    if a.run is not None:
        do_run(a.run)
    if a.check or a.report:
        from check_records import check_all
        return check_all(report=a.report)
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    sys.exit(main())
