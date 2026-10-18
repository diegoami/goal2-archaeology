"""Compare the records of a scratch log with the T57 reference, match by match (compare.differences)."""
import sys
sys.path.insert(0, "experiments/E036-match-port")
import compare
import records

ref = compare.load("experiments/E036-match-port/out/T57/reference.jsonl")
for r in records.read_log(sys.argv[1]):
    a = ref[r["id"]]
    why = compare.completed(r)
    d = compare.differences(a, r) if not why else []
    print(r["id"], "NOT COMPLETED " + why if why else ("identical" if not d else "DIFFER " + compare.describe(d)),
          r.get("port_calls"), r["counts"])
