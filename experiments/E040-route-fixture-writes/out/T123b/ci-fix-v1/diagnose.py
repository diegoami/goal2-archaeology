"""Corroborate T117 CI failure without changing its historical receipt or runtime."""
import copy, hashlib, importlib.util, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5]
sys.path[:0] = [str(ROOT), str(ROOT / "runtime")]
from original_match import Match
spec = importlib.util.spec_from_file_location("t117", ROOT / "tests/test_port_overhead_t117.py")
t = importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
held = {}
original = Match.result

def capture(self):
    result = original(self)
    held["match"] = self
    held["result"] = result
    return result

Match.result = capture
sources = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted((ROOT / "runtime/original_match").rglob("*.py"))}
digest = lambda v: hashlib.sha256(json.dumps(v, sort_keys=True, default=repr).encode()).hexdigest()
try:
    t.Drive("test_e034_03_drive_equals_the_recorded_before_receipt").test_e034_03_drive_equals_the_recorded_before_receipt()
except AssertionError as error:
    failure = str(error)
else:
    raise AssertionError("unchanged T117 test should reproduce the CI failure")
result = held["result"]
before = json.loads(t.RECEIPT.read_text())
raw_digest = digest(result)
assert raw_digest == "f9579e4afae0d530a58b0c914c6a4401f418e0c2219e9b2f58b24a57d01f58ed", raw_digest
new_count = result["ports"]["calls"].pop("0791:DEA6")
assert new_count == 0, new_count
assert digest(result) == before["result_sha256"]
memory_digest = hashlib.sha256(held["match"].m.read(0, 0x110000)).hexdigest()
assert memory_digest == before["memory_sha256"]
assert sources == {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted((ROOT / "runtime/original_match").rglob("*.py"))}
receipt = dict(head=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
               python=sys.version, unchanged_test_failure=failure, events_golden_assertions_passed=True,
               raw_result_sha256=raw_digest, removed_only={"0791:DEA6":new_count},
               normalized_result_sha256=digest(result), expected_result_sha256=before["result_sha256"],
               memory_sha256=memory_digest, expected_memory_sha256=before["memory_sha256"],
               runtime_source_sha256=sources, runtime_sources_unchanged=True,
               original_receipt_sha256=hashlib.sha256(t.RECEIPT.read_bytes()).hexdigest())
with Path(sys.argv[1]).open("x") as f: json.dump(receipt,f,indent=2)
print("Original test red; only zero-call DEA6 metadata removed; complete result/events/memory golden unchanged.")
