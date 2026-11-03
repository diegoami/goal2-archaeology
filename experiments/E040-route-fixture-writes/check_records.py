"""E040 (T119b, #427): the committed run records against the static write-set (README.md, "The check").

Called by `runner.py --check` (and `--report`, which also writes out/coverage.json). It needs no emulator and no
state: the records under runs/E040/, the tables notes/427/writeset/*.json and the raw listings static/goal-exe/code/.
"""
import collections
import json
import re
from pathlib import Path

import runner as E

CURSOR_ROWS = {"000E:7000", "000E:6A9B", "000E:6C17"}       # game +0x26 += 1 (writeset.json, phase cursor)
RUN_MATCH, UNPLAYED, SILENT = "000E:6F18", "000E:6EF9", "000E:7014"
CONFIDENCE = ("000E:6F80", "000E:6F86")                      # B71C, B6CC: both sides when bp-4 = 1 and kind != 1
NEWS_CALL, UPDATE = "000E:6FD8", "000E:6FF8"                 # 4E0E per managed side; B7FA
SACK_ENTRY = "000E:01FA"                                     # unmanage_country (sack.json)
# F039's order of route_fixture's phases in one call (writeset.json phases, consecutive repeats folded): the
# managers' flags, then per fixture the routing (and the gate), then either the played path (run_match or the
# unplayed set-up; for kind != 0 the confidence term when it applies, the news, the player update), the cursor and
# the tables, or the silent path 6970 (its cursor inside); after either, 6685 when it applies; the loop head's
# tables at the round's end [derived: F039 "One call", "The played path's order", "The silent path"].
ORDER = re.compile(r"^pre-match(,route(,watch-prompt(,route)?)*"
                   r"(,(unplayed|run_match(,confidence)?,news,player_update),cursor,group_tables"
                   r"|,silent,cursor(,silent)?)(,6685)?)*(,group_tables)?$")
# What a row's class lets a write reach (README.md, "The check", rule 2); `None` is any region.
STORE_REGIONS = {"frame": {"stack"}, "game": {"game"}, "countries": {"countries"}, "players": {"players"},
                 "managers": {"managers"}, "fixtures": {"fixtures"}, "screen": {"video", "backbuf"}}
CALL_REGIONS = {"frame": set(), "pure": set(), "rng": {"ds:7B62"}, "screen": {"video", "backbuf"},
                "prompt": {"ds:A976", "ds:A977"}, "game": {"game"}, "port-owned": None}
# The text routines 214B:0205 and 02C8 store their attribute argument in the CRT unit's TextAttr DS:AAB2, which
# 01A3 and 026D then write with [likely: static/goal-exe/annotations/routines.tsv 214B:0205, 214B:02C8]: a
# display variable of the screen class, which news.json's screen rows do not name (README.md, rule 2).
CALL_REGIONS["screen"] = CALL_REGIONS["screen"] | {"ds:AAB2"}
NAMED = re.compile(r"DS:([0-9A-F]{4})")


def rows_by_site(tabs):
    out = {}
    for name, t in tabs.items():
        for r in t["rows"]:
            out[r["site"]] = dict(r, table=name)
    return out


def observations(rec):
    out = {}
    for o in rec["observations"]:
        out[o["field"]] = o["value"]
    obs = {}
    for field, value in out.items():
        if field.startswith("observed: "):
            obs[field[len("observed: "):]] = json.loads(value)
        elif field.startswith("the fixtures from"):
            obs["fixtures"] = json.loads(value)
        elif field.startswith("the managed matches"):
            obs["matches"] = json.loads(value)
        elif field.startswith("game record and seeds at the start"):
            obs["head"] = json.loads(value)
        elif field.startswith("game record and seeds at the end"):
            obs["tail"] = json.loads(value)
        elif field.startswith("the record replayed"):
            obs["replay"] = value
        elif field.startswith("start state"):
            obs["sha256"] = value
        elif field == "e040 observation schema":
            obs["schema"] = value
    return obs


def family(region):
    if region.startswith("ds:") or region.startswith("other:"):
        return region
    return region.split(":")[0]


def allowed(row, how, region):
    """Whether a write the record attributes to `row` (its innermost site) may reach `region`."""
    fam = family(region)
    named = {f"ds:{x}" for x in NAMED.findall(row["target"])}
    cls = row["class"]
    if how in ("call-push", "stack-op"):
        return fam == "stack"
    if how == "store":
        return fam in STORE_REGIONS.get(cls, set()) or fam in named
    # a write inside the callee of a call row: the callee's own frame is the stack below the call; the class says
    # what else it may reach
    if fam == "stack":
        return True
    if cls == "subtree":
        return not row["callee"] in SCOPED
    regions = CALL_REGIONS.get(cls, set())
    return regions is None or fam in regions or fam in named


SCOPED = set()


def segments(seq):
    out, cur = [], []
    for s in seq:
        cur.append(s)
        if s in CURSOR_ROWS:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def check_record(rec, rows, model, tabs):
    p = []
    rid = rec["run_id"]
    case = next((c for c in E.CASES if c[0] == rid), None)
    if case is None:
        return [f"{rid}: not a case of runner.CASES"], {}
    expect = case[6]
    if expect != "completed":
        # a case the harness cannot run (README.md, "Harness limits"): its record must abort with that limit
        ok = rec["status"].startswith(expect) and rec["start_state"]["sha256"] == E.expected(case[3])
        return ([] if ok else [f"{rid}: {rec['status']}, the case expects {expect}"]), {}
    if rec["status"] != "completed":
        return [f"{rid}: {rec['status']}"], {}
    obs = observations(rec)
    asset = case[3]
    if rec["start_state"]["id"] != asset or obs.get("sha256") != E.expected(asset) or \
            rec["start_state"]["sha256"] != E.expected(asset):
        p.append(f"{rid}: the start state is not {asset} with its manifest's sha256")
    if obs.get("schema") != E.SCHEMA_NOTE:
        p.append(f"{rid}: observation schema {obs.get('schema')}")
    if obs.get("replay") != "true":
        p.append(f"{rid}: the record replayed does not give the memory the call left")
    p += [f"{rid}: {x}" for x in obs["problems"]]
    for name, ok in obs["draw_chain_ok"].items():
        if not ok:
            p.append(f"{rid}: the steps of {name} do not chain")

    # rule 1-3: every write attributed, in a row its class admits, in its phase
    for outer, ws, inner, how, region, n in obs["writes"]:
        where = f"{rid}: {n} write(s) {how} at {inner} (route level {ws}) to {region}"
        if how in ("unlisted", "outside"):
            p.append(f"{where}: no row")
            continue
        if how == "stack-op":
            if family(region) != "stack":
                p.append(f"{where}: a push off the stack")
            continue
        row = rows.get(inner)
        if row is None:
            p.append(f"{where}: {inner} is no row")
            continue
        if not allowed(row, how, region):
            p.append(f"{where}: class {row['class']} ({row['table']}) does not reach it")
        wrow = rows.get(ws)
        if wrow is None or wrow["table"] != "writeset.json":
            p.append(f"{where}: no route_fixture row above it")
            continue
        if row["table"] != "writeset.json":
            ok = wrow["class"] == "subtree" and (wrow["phase"] == "news" if row["table"] == "sack.json"
                                                 else wrow["phase"] in ("news", "6685"))
            if not ok or row["phase"] != "news":
                p.append(f"{where}: a {row['table']} row (phase {row['phase']}) under {ws} (phase {wrow['phase']})")
    for ws, inner, why, region, n in obs["kit_bytes"]:
        where = f"{rid}: {n} harness byte(s) '{why}' under {inner} to {region}"
        if inner == "harness":
            continue
        row = rows.get(inner)
        if row is None:
            p.append(f"{where}: no row")
        elif why == "match":
            if inner != RUN_MATCH:
                p.append(f"{where}: the match's write-back outside 6F18")
        elif not allowed(row, "callee", region):
            p.append(f"{where}: class {row['class']} does not reach it")

    # rule 4: the order of phases
    phases = []
    for s in obs["sequence"]:
        ph = rows[s]["phase"] if s in rows else None
        if ph and (not phases or phases[-1] != ph):
            phases.append(ph)
    if not ORDER.match(",".join(phases)):
        p.append(f"{rid}: phase order {','.join(phases)} is not F039's")

    # rule 5: reach. Every row in a block whose leader ran is visited as often as the leader; none elsewhere.
    visits, leaders = obs["visits"], obs["leaders"]
    for site, row in rows.items():
        block = model["block"].get(site)
        n_leader = leaders.get(block, 0)
        n = visits.get(site, 0)
        if n != n_leader:
            p.append(f"{rid}: row {site} visited {n} times, its block {block} entered {n_leader} times")

    # rule 6: draws. An rng row draws one step per visit; a row that is neither rng, port-owned nor an unscoped
    # subtree draws none; 8336 never steps outside port-owned or unscoped-subtree rows.
    for name, hist in obs["steps_per_visit"].items():
        for site, h in hist.items():
            row = rows.get(site)
            if row is None:
                p.append(f"{rid}: {name} steps under {site}, no row")
                continue
            free = row["class"] in ("port-owned",) or (row["class"] == "subtree" and row["callee"] not in SCOPED)
            if row["class"] == "rng" and name == "7B62":
                if set(h) != {"1"}:
                    p.append(f"{rid}: rng row {site} drew {h} (steps: visits) of {name}")
            elif not free and set(h) != {"0"}:
                p.append(f"{rid}: {row['class']} row {site} stepped {name}: {h}")
    for name, runs in obs["draws"].items():
        for where, inner, n in runs:
            if inner is None:
                p.append(f"{rid}: {n} {name} steps outside any scoped call")
            elif where == "match" and inner != RUN_MATCH:
                p.append(f"{rid}: the match's {name} steps under {inner}")

    # rule 7: 045D's seat test: the colour draw 04B2 follows exactly the tests that found a byte below 7
    seat = obs["seat_test"]
    if visits.get(E.SEAT_DRAW, 0) != seat.get("lt7", 0) or \
            seat.get("lt7", 0) + seat.get("ge7", 0) != visits.get("000E:047B", 0):
        p.append(f"{rid}: 045D's seat test {seat} against 04B2 {visits.get(E.SEAT_DRAW, 0)} and 047B "
                 f"{visits.get('000E:047B', 0)}")

    # rule 8: the fixtures' paths
    segs = segments(obs["sequence"])
    facts = obs["fixtures"]
    cov = {"run": rid, "arm": rec["arm"], "fixtures": [], "managed": None}
    if len([s for s in segs if set(s) & CURSOR_ROWS]) != len(facts):
        p.append(f"{rid}: {len(segs)} segments for {len(facts)} fixtures")
    for seg, f in zip(segs, facts):
        b = bytes.fromhex(f["before"])
        a = bytes.fromhex(f["after"])
        kind, first = b[2], b[0]
        managed = [mb >= 0x80 for mb in f["manager_byte_before"]]
        tag = f"{rid}: fixture {f['index']} (kind {kind}, first byte {first:02X})"
        c = collections.Counter(seg)
        entry = {"index": f["index"], "kind": kind, "first": first, "managed": any(managed)}
        if any(managed):
            if kind == 0:
                if not c[UNPLAYED]:
                    p.append(f"{tag}: managed kind 0 without 0791:BB2F")
            else:
                if c[RUN_MATCH] != 1 or c[SILENT]:
                    p.append(f"{tag}: managed but run_match {c[RUN_MATCH]}, silent {c[SILENT]}")
                want = 0 if kind == 1 else 2
                for s in CONFIDENCE:
                    if c[s] != want:
                        p.append(f"{tag}: {s} visited {c[s]} times, F039 says {want}")
                if c[NEWS_CALL] != sum(managed):
                    p.append(f"{tag}: 4E0E called {c[NEWS_CALL]} times for {sum(managed)} managed side(s)")
                if c[UPDATE] != 1:
                    p.append(f"{tag}: B7FA called {c[UPDATE]} times")
            s = 1 if managed[1] else 0
            result = "win" if a[3] == s else "draw" if a[3] == 2 else "loss"
            entry.update(result=result, goals=[a[0], a[1]], side=s, confidence=c[CONFIDENCE[0]])
            cov["managed"] = entry
            p += check_headline(rid, tag, result, a, rows, visits)
            if leaders.get(SACK_ENTRY, 0) and not (obs["head"]["season_word_38"] >= 2 and kind != 1):
                p.append(f"{tag}: the sack ran where 0B77 returns 0")
        else:
            if not c[SILENT] or c[RUN_MATCH]:
                p.append(f"{tag}: unmanaged but silent {c[SILENT]}, run_match {c[RUN_MATCH]}")
            fe = c["000E:6A84"] == 1 and c["000E:6A93"] == 1
            if (first == 0xFE) != fe:
                p.append(f"{tag}: first byte {first:02X} but the score page's key {c['000E:6A84']}, E929 "
                         f"{c['000E:6A93']}")
        entry["path"] = "silent" if c[SILENT] else "unplayed" if c[UNPLAYED] else "played"
        entry["gate"] = sum(c[x] for x in ("000E:6DA7", "000E:6DC6", "000E:6E0B"))
        entry["watch_prompt"] = c.get("000E:6C6C", 0)
        cov["fixtures"].append(entry)
    keyset = {k[0] for k in obs["keys"]}
    cov["key_sites"] = sorted(keyset)
    cov["crowd_animation_calls"] = leaders.get("000E:045D", 0)
    cov["draws_route_7B62"] = sum(n for w, _, n in obs["draws"]["7B62"] if w == "route")
    cov["draws_match_7B62"] = sum(n for w, _, n in obs["draws"]["7B62"] if w == "match")
    cov["sack"] = leaders.get(SACK_ENTRY, 0)
    cov["6685"] = visits.get("000E:7063", 0)
    cov["visited_rows"] = sorted(s for s in rows if visits.get(s, 0))
    return p, cov


def check_headline(rid, tag, result, a, rows, visits):
    """319B's result paths (sack.json conditions): a row conditioned on a win, a draw or a defeat is visited only
    when the managed side's result is that."""
    p = []
    for site, row in rows.items():
        if row["table"] != "sack.json" or not visits.get(site):
            continue
        cond = row["condition"]
        need = ("win" if cond.startswith("side s won") or cond.startswith("fixture +3 = s") else
                "draw" if cond.startswith("a draw") else "loss" if cond.startswith("side s lost") else None)
        if need and need != result:
            p.append(f"{tag}: {site} ({cond}) visited on a {result}")
    return p


def check_all(report=False):
    tabs = E.tables()
    rows = rows_by_site(tabs)
    SCOPED.update(E.scope_routines(tabs))
    model = E.static_model()
    problems, covs = [], []
    for case in E.CASES:
        path = E.RUNS / f"{case[0]}.json"
        if not path.exists():
            problems.append(f"{case[0]}: no record")
            continue
        p, cov = check_record(json.loads(path.read_text()), rows, model, tabs)
        problems += p
        if cov:
            covs.append(cov)
    for path in sorted(E.RUNS.glob("*.json")):
        if not any(path.stem == c[0] for c in E.CASES):
            problems.append(f"{path.name}: a record of no case")
    visited = set().union(*[set(c["visited_rows"]) for c in covs]) if covs else set()
    by_table = {name: {"rows": len(t["rows"]), "visited": sum(1 for r in t["rows"] if r["site"] in visited)}
                for name, t in tabs.items()}
    summary = {
        "records": len(covs),
        "managed": [dict(c["managed"], run=c["run"]) for c in covs if c["managed"]],
        "silent_fixtures": sum(1 for c in covs for f in c["fixtures"] if f["path"] == "silent"),
        "silent_fe": sum(1 for c in covs for f in c["fixtures"] if f["path"] == "silent" and f["first"] == 0xFE),
        "watch_prompts": sum(f["watch_prompt"] for c in covs for f in c["fixtures"]),
        "crowd_animation_calls": sum(c["crowd_animation_calls"] for c in covs),
        "sack": sum(c["sack"] for c in covs), "6685": sum(c["6685"] for c in covs),
        "unplayed": sum(1 for c in covs for f in c["fixtures"] if f["path"] == "unplayed"),
        "rows": by_table,
        "rows_not_visited": {name: sorted(r["site"] for r in t["rows"] if r["site"] not in visited)
                             for name, t in tabs.items()},
    }
    for line in problems:
        print(line)
    m = summary["managed"]
    print(f"E040: {summary['records']} records; managed {[(x['run'], x['kind'], x['result']) for x in m]}; "
          f"silent fixtures {summary['silent_fixtures']} ({summary['silent_fe']} with 0xFE); watch prompts "
          f"{summary['watch_prompts']}; crowd animation calls {summary['crowd_animation_calls']}; sack "
          f"{summary['sack']}; 6685 {summary['6685']}; unplayed {summary['unplayed']}")
    print("rows visited: " + "; ".join(f"{n} {v['visited']}/{v['rows']}" for n, v in by_table.items()))
    if report:
        E.OUT.mkdir(parents=True, exist_ok=True)
        (E.OUT / "coverage.json").write_text(json.dumps({"summary": summary, "records": covs}, indent=1) + "\n")
        print(f"wrote {(E.OUT / 'coverage.json').relative_to(E.ROOT)}")
    print(f"E040 check: {'ok' if not problems else f'{len(problems)} problem(s)'}")
    return 1 if problems else 0
