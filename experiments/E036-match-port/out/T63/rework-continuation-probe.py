"""Trace two Python continuations during one real kit match without editing the port."""
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
OUT = Path("experiments/E036-match-port/out/T63/probe-continuation-cbbfb28.jsonl")
POSITIONING = ROOT / "runtime/original_match/port/positioning.py"
lines = POSITIONING.read_text().splitlines()
target_lines = {
    "1FDD_after_A920": next(i for i, line in enumerate(lines, 1) if line.strip() == "drop_words(mem, 1)"),
    "20E3_after_1FDD": next(i for i, line in enumerate(lines, 1) if line.strip() == 'f.w16(-4, k, "0791:21BE")'),
}
hits = {key: 0 for key in target_lines}


def local_trace(frame, event, _arg):
    if event == "line":
        for key, line in target_lines.items():
            if frame.f_lineno == line:
                hits[key] += 1
    return local_trace


def trace(frame, event, _arg):
    if event == "call" and frame.f_code.co_filename == str(POSITIONING):
        return local_trace
    return None


def main():
    assert not (ROOT / OUT).exists(), OUT
    spec = importlib.util.spec_from_file_location("t63_probe_family", ROOT / "experiments/E036-match-port/family.py")
    family = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(family)
    import heavy_slot
    heavy_slot.take("family", weight=1)
    sys.settrace(trace)
    try:
        status = family.main(["--family", "F40", "--only", "F40/e032-0101",
                              "--ports", "positioning", "--time-limit", "3000",
                              "--count", "0791:1FDD,0791:20E3", "--out", str(OUT)])
    finally:
        sys.settrace(None)
    records = [json.loads(line) for line in (ROOT / OUT).read_text().splitlines()]
    assert status == 0 and len(records) == 1 and records[0].get("error") is None, (status, records)
    assert all(hits.values()), hits
    print(json.dumps({"source": str(POSITIONING), "match": records[0]["id"],
                      "continuation_lines": target_lines, "hits": hits}, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
