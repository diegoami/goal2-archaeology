"""T120 (#427): the silent path's ports proved inside the route harness, on E040's states.

    python3 -B experiments/E040-route-fixture-writes/prove.py --ports silent                  # the proof, its record
    python3 -B experiments/E040-route-fixture-writes/prove.py --ports silent --variant silent.goal-plus-one   # caught?
    python3 -B experiments/E040-route-fixture-writes/prove.py --ports silent --cases E040-r0004 --no-record

`--ports M,...|all` and `--variant M.NAME` are as check.py takes them (runtime/original_match/check.py; the variant's
module is added if not named). Each case is one call of route_fixture 000E:6CA7 by T119a's harness,
`Route(image, record_writes=False)`, with the ports installed on its machine (port.install) and a `Prover` on it
(port/prove.py; T119c's ProvedRouteTests): every armed call of a ported routine runs as its port and then as the
original, and any difference raises ProofError. The key reads and polls are the harness's (route.py's policy, as
E040's runner gives it: runner.policy), answered once in the port's run and replayed to the original: the results
page's poll 6B84 and its delay loop's 6BF2 are answered the same way in both runs.

The cases [designed: T120]: every published state E040's runner names (runner.CASES; a state two run ids share runs
once, under the first), then two edits of E040-r0004's state (E006-r0004), each declared in the record as an input:
- `bb2f`: fixture 3 (the managed friendly 7 v 27, first byte 0xFE) made kind 0. route_fixture then calls
  prepare_unplayed_match 0791:BB2F for it (seg_000E_09.asm 6D79-6DA7: a managed side gives the gate 6C21 flag 0, which
  returns 1; 6E15: kind 0 is not in CS:6C87; 6ED8 `cmp byte ptr es:[di + 2], 0; jne` and 6EF9 `call far 0791:BB2F`).
  No published state reaches BB2F: none of their fixtures from the cursor to the managed one has kind 0 (the record
  lists them).
- `silent-kind-0`: fixture 1 (18 v 10, the next silent fixture, first byte 0xFF) made kind 0: the Done-when's own
  input. Its first byte is not 0xFE, so route_fixture tests the kind sets 695A and 697A (6DAE-6E04), finds neither,
  and calls 6970 at 7014: it does not reach BB2F (the record says so).

Each case runs in two passes when `silent` is installed with no variant: `four` (the modules as given), where
D47E and B602 run nested in 6970's proved calls, and `inner` (the same with silent's 000E:6970 left out, so the
original 6970 calls D47E and B602 and each call is proved on its own). A kit site at 0791:2648 (the set-up reseed)
counts its visits by the return addresses of A3DE and of A3DE's caller (frame words), so the record shows which of
D47E's, BB2F's (through A4A1) and E80D's calls reached it.

With `--variant`, the cases run in the `four` pass until the first ProofError: the falsifier is caught there (exit 0),
or never (exit 1). The record goes to out/T120/prove-<ports>[-<variant>]-<UTC time>.json, never overwritten; it is
refused while route.py, the port package or this file has uncommitted changes (the record names the commit), unless
--no-record."""
import argparse
import collections
import datetime
import hashlib
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = HERE / "out" / "T120"
DL = ROOT / ".cache" / "dl"
sys.path.insert(0, str(ROOT / "runtime"))
sys.path.insert(0, str(HERE))
import runner  # noqa: E402

SILENT = ("000E:6970", "0791:D47E", "0791:B602", "0791:BB2F")
RESEED = "0791:2648"
SCORE_PAGE, RESULTS = "000E:6A89", "000E:6B89"      # 6970's key read after the score page, its poll on the results list
EDITS = {
    "bb2f": ("E040-r0004", 3, 1, "fixture 3 (the managed friendly 7 v 27, first byte 0xFE) kind byte +2 := 0 "
                                 "(from 1): route_fixture calls 0791:BB2F for it at 6EF9"),
    "silent-kind-0": ("E040-r0004", 1, 1, "fixture 1 (18 v 10, the next silent fixture, first byte 0xFF) kind byte "
                                          "+2 := 0 (from 1): the Done-when's input; route_fixture sends it to 6970 "
                                          "(6DAE-7014), not BB2F"),
}
DIRTY_PATHS = ("runtime/original_match/route.py", "runtime/original_match/port", "runtime/original_match/machine.py",
               "runtime/original_match/match.py", "experiments/E040-route-fixture-writes/prove.py",
               "experiments/E040-route-fixture-writes/runner.py")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def cases():
    """[(name, run id, asset, what, edit or None)]: the published states, once each, then the edits."""
    out, seen = [], set()
    for case in runner.CASES:
        run_id, _, _, asset, what = case[:5]
        if asset in seen:
            continue
        seen.add(asset)
        out.append((run_id, run_id, asset, what, None))
    by_id = {c[1]: c for c in out}
    for name, (run_id, index, old, what) in EDITS.items():
        out.append((name, run_id, by_id[run_id][2], by_id[run_id][3], (index, old, what)))
    return out


def port_specs(ports, variant):
    """check.py's --ports and --variant: the specs, the module names, the variant."""
    from original_match import port
    names = [s for s in (ports or "").split(",") if s]
    if variant is not None:
        if "." not in variant:
            raise SystemExit(f"--variant {variant!r}: MODULE.NAME")
        names = [s for s in names if s != variant.split(".")[0]] + [variant]
    loaded = port.load(names)
    return loaded


def without_6970(loaded):
    """The same ports, silent's 000E:6970 left out (a copy of its registry)."""
    from original_match.port import Registry
    out = []
    for reg, variant in loaded:
        if reg.name == "silent":
            copy = Registry(reg.name, reg.doc)
            copy.variants = dict(reg.variants)
            copy.entries = {a: e for a, e in reg.entries.items() if a != "000E:6970"}
            reg = copy
        out.append((reg, variant))
    return out


def fixtures_ahead(image):
    """The fixtures from the cursor to the first with a managed side: index, first byte, kind, countries."""
    cur, end = image.fixture_index(), image.rd_far(0xA923, 0x28)
    base, managed = image.far(0xA92B), set(image.managed_countries())
    out = []
    for i in range(cur, end):
        fx = bytes(image.memory[base + 8 * (i - 1):base + 8 * i])
        a, b = int.from_bytes(fx[4:6], "little"), int.from_bytes(fx[6:8], "little")
        out.append({"index": i, "first_byte": fx[0], "kind": fx[2], "countries": [a, b],
                    "managed": a in managed or b in managed})
        if a in managed or b in managed:
            break
    return out


def run_pass(image_bytes, case, loaded, label):
    """One call of route_fixture with `loaded` installed and proved: what the record keeps of it."""
    from original_match import port, route as R
    from original_match.image import Image
    from original_match.port.prove import Prover, ProofError
    name, run_id, asset, what, edit = case
    image = Image.from_savestate(image_bytes)
    inputs = []
    if edit is not None:
        index, old, why = edit
        a = image.far(0xA92B) + 8 * (index - 1) + 2
        if image.memory[a] != old:
            raise SystemExit(f"{name}: fixture {index}'s kind byte is {image.memory[a]}, not {old}")
        image.memory[a] = 0
        inputs.append({"what": why, "linear": a, "old": f"{old:02x}", "new": "00"})
    ahead = fixtures_ahead(image)
    case_by_id = next(c for c in runner.CASES if c[0] == run_id)
    r = R.Route(image, keys=runner.policy(case_by_id), record_writes=False)
    installed = port.install(r.m, loaded)
    m = r.m
    reseeds = collections.Counter()

    def reseed(replay):
        if replay:
            return
        bp = m.reg("bp")                       # A3DE's BP at 2648's entry (A3DE: push bp; mov bp, sp; ...)
        bp2 = m.frame_word(bp, 0)
        reseeds[f"A3DE returning to {m.frame_word(bp, 2):04X}, its caller to {m.frame_word(bp2, 2):04X}"] += 1
    m.at(RESEED, reseed)
    prover = Prover(m, installed)
    t0 = time.time()
    status, error = "completed", None
    try:
        r.call()
    except ProofError as exc:
        status, error = "differs", str(exc)
    except Exception as exc:
        status, error = f"aborted: {type(exc).__name__}", str(exc)[:2000]
    summary = prover.summary()
    calls = dict(installed.calls)
    keys = collections.Counter(e[1] for e in r.record if e[0] == "key")
    accounted = {a: summary[a]["proved"] + summary[a]["nested"] == n for a, n in calls.items()}
    return {
        "case": name, "pass": label, "status": status, "error": error,
        "inputs": inputs, "fixtures_ahead": ahead,
        "ports": port.spec_names(loaded),
        "calls": {a: calls.get(a, 0) for a in sorted(calls)},
        "proof": {a: summary[a] for a in sorted(summary) if a in SILENT or summary[a]["proved"] or summary[a]["nested"]},
        "every_call_proved_or_nested": all(accounted.values()) and status == "completed",
        "before_armed": sum(v["before"] for v in summary.values()),
        "reseed_2648": dict(reseeds),
        "pages_6970": {"score_page_6A84": keys.get(SCORE_PAGE, 0), "results_list_6B84": keys.get(RESULTS, 0)},
        "key_visits": dict(sorted(keys.items())),
        "matches": [e[1] for e in r.record if e[0] == "match"],
        "returned": any(e[0] == "return" for e in r.record),
        "elapsed_s": round(time.time() - t0, 1),
    }


def verdict(passes, loaded):
    """The proof's problems ([] when it holds): every pass completed with each call proved or nested; in the `inner`
    pass D47E, B602 and BB2F each proved on its own; BB2F reached in `bb2f` only; every D47E call reached 2648."""
    problems = []
    names = {reg.name for reg, _ in loaded}
    for p in passes:
        tag = f"{p['case']}/{p['pass']}"
        if p["status"] != "completed":
            problems.append(f"{tag}: {p['status']}: {p['error']}")
            continue
        if not p["every_call_proved_or_nested"]:
            problems.append(f"{tag}: a call neither proved nor nested: {p['calls']} {p['proof']}")
        if p["before_armed"]:
            problems.append(f"{tag}: {p['before_armed']} calls before the proof was armed")
        if "silent" not in names:
            continue
        bb2f = p["calls"].get("0791:BB2F", 0)
        if (p["case"] == "bb2f") != (bb2f > 0):
            problems.append(f"{tag}: BB2F called {bb2f} times")
        if not p["inputs"] and any(f["kind"] == 0 for f in p["fixtures_ahead"]):
            problems.append(f"{tag}: a published state with a kind-0 fixture ahead: {p['fixtures_ahead']}")
        if p["pass"] == "inner":
            for a in ("0791:D47E", "0791:B602", "0791:BB2F"):
                if p["proof"][a]["proved"] != p["calls"].get(a, 0):
                    problems.append(f"{tag}: {a} proved {p['proof'][a]['proved']} of {p['calls'].get(a, 0)} calls")
        d47e = p["calls"].get("0791:D47E", 0)
        from_d47e = sum(n for k, n in p["reseed_2648"].items() if k.startswith("A3DE returning to D495"))
        if from_d47e != d47e:
            problems.append(f"{tag}: {d47e} calls of D47E, {from_d47e} visits of 2648 from D47E's A3DE")
    return problems


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ports", required=True, help="port modules (port/), as check.py: M,...|all")
    ap.add_argument("--variant", help="MODULE.NAME: one of a module's variants (a falsifier), which must be caught")
    ap.add_argument("--cases", help="comma-separated case names (run ids, bb2f, silent-kind-0); default: all")
    ap.add_argument("--no-record", action="store_true", help="write no record (a development run)")
    a = ap.parse_args(argv)
    loaded = port_specs(a.ports, a.variant)
    from original_match import port
    dirty = git("status", "--porcelain", "--", *DIRTY_PATHS)
    if dirty and not a.no_record:
        raise SystemExit(f"refused: uncommitted changes the record would not name:\n{dirty}")
    chosen = cases()
    if a.cases:
        want = a.cases.split(",")
        unknown = set(want) - {c[0] for c in chosen}
        if unknown:
            raise SystemExit(f"--cases: no case {sorted(unknown)}")
        chosen = [c for c in chosen if c[0] in want]
    started = datetime.datetime.now(datetime.timezone.utc)
    commit = git("rev-parse", "HEAD")                # the code that runs (DIRTY_PATHS clean, or --no-record)
    states, passes = {}, []
    caught = None
    names = {reg.name for reg, _ in loaded}
    for case in chosen:
        asset = case[2]
        path = DL / asset
        if not path.is_file():
            raise SystemExit(f"{asset} is absent: python3 -B experiments/E040-route-fixture-writes/runner.py --fetch")
        actual, want = sha256_file(path), runner.expected(asset)
        if actual != want:
            raise SystemExit(f"{asset}: sha256 {actual}, its evidence manifest says {want}")
        states[asset] = actual
        data = path.read_bytes()
        labels = [("four", loaded)]
        if a.variant is None and "silent" in names:
            labels.append(("inner", without_6970(loaded)))
        for label, specs in labels:
            p = run_pass(data, case, specs, label)
            passes.append(p)
            calls = " ".join(f"{k}={v}" for k, v in p["calls"].items() if k in SILENT)
            print(f"{case[0]:14} {label:5} {p['status']:9} {calls} 2648={sum(p['reseed_2648'].values())} "
                  f"pages={p['pages_6970']['score_page_6A84']}/{p['pages_6970']['results_list_6B84']} "
                  f"{p['elapsed_s']}s", flush=True)
            if p["status"] == "differs":
                print("  " + p["error"].splitlines()[0][:400], flush=True)
        if a.variant is not None and passes[-1]["status"] == "differs":
            caught = {"case": case[0], "error": passes[-1]["error"]}
            break
    if a.variant is not None:
        problems = [] if caught else [f"{a.variant} was not caught on {len(passes)} cases"]
        print(f"{a.variant}: " + (f"caught on {caught['case']}" if caught else "NOT caught"))
    else:
        problems = verdict(passes, loaded)
        totals = collections.Counter()
        proved = collections.Counter()
        for p in passes:
            for k in SILENT:
                if p["pass"] == "inner" or k == "000E:6970":
                    totals[k] += p["calls"].get(k, 0)
                    proved[k] += p["proof"].get(k, {}).get("proved", 0)
        for k in SILENT:
            print(f"{k}: {proved[k]} of {totals[k]} calls proved on their own")
        print("proof: " + ("holds" if not problems else "FAILS"))
        for line in problems:
            print("  " + line)
    if not a.no_record:
        OUT.mkdir(parents=True, exist_ok=True)
        stamp = started.strftime("%Y%m%dT%H%M%SZ")
        tag = a.ports.replace(",", "+") + (f"-{a.variant}" if a.variant else "")
        out = OUT / f"prove-{tag}-{stamp}.json"
        if out.exists():
            raise SystemExit(f"{out} exists: never overwritten")
        import unicorn
        record = {
            "schema": "e040-t120-prove/1", "task": "T120", "experiment": "E040",
            "command": "python3 -B experiments/E040-route-fixture-writes/prove.py " + " ".join(argv or sys.argv[1:]),
            "code_commit": commit, "ports": port.spec_names(loaded), "variant": a.variant,
            "runtime": {"unicorn": unicorn.__version__, "python": platform.python_version(),
                        "route.py": sha256_file(ROOT / "runtime/original_match/route.py"),
                        "silent.py": sha256_file(ROOT / "runtime/original_match/port/silent.py"),
                        "prove.py": sha256_file(Path(__file__))},
            "states": {k: {"sha256": v, "verified_against": "its evidence manifest (runner.expected)"}
                       for k, v in states.items()},
            "edits_declared": {name: {"case": run_id, "fixture": index, "kind_from": old, "kind_to": 0, "what": what}
                               for name, (run_id, index, old, what) in EDITS.items()},
            "bb2f_in_published_states": "none: no published case calls 0791:BB2F (calls per pass below), and no "
                                        "fixture from a published state's cursor to its managed one has kind 0 "
                                        "(fixtures_ahead)" if a.variant is None else None,
            "passes": passes, "caught": caught, "problems": problems,
            "started": stamp, "ended": datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        }
        out.write_text(json.dumps(record, indent=1) + "\n")
        print(f"record: {out.relative_to(ROOT)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
