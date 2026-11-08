# T128 write-order proof boundary

[confirmed: accepted source6bdf7bbed441b6e2c758949bae409963dfa6c175, port/prove.py step3; port/runtime.py Regs.store/flush] The established port proof compares ordered byte writes outside the original routine's measured dead stack frame. Python stack stores may coalesce and reorder transient dead-frame writes. This is not a promise to reproduce every x86 instruction write.

[confirmed: experiments/E040-route-fixture-writes/out/T128/order-boundary-diagnosis-v1.json] The unchanged accepted within-twenty primitive already fails the new raw write-list assertion: original first writes92FFE:2,92FFA:2,92FFC:2, while the port flushes92FFA:6. Both old and new primitive retain identical complete final1MiB/ALL16 and every helper-entry1MiB/ALL16. Caller fields93FF5/93FFF are outside the original measured frame. The failed raw-order calibration and baseline evidence remain unchanged.

[designed: main] Compare byte-expanded ordered writes outside exactly the ORIGINAL-measured lowest stack reached while writing through caller SP after return, using the existing Prover definition. Derive and record the interval per case; no fixed padding or enlarged exclusion. Assert that caller mark/index/scroll and pool/squad records are outside it. Preserve every original helper call and its complete input memory/register snapshots.

Compare ALL1MiB and ALL16 registers at final and helper-entry checkpoints, including every dead-stack byte: there is no memory-value mask. Retain all old within-twenty and C1F refusal assertions, gate/index/swap falsifiers, sealed-helper controls and both complete write traces. Only transient write ordering inside the established measured frame is outside the order comparison. Report this boundary precisely; do not claim instruction-by-instruction equality or weaken final/caller-visible effects.

## Bounded real-helper closure amendment

[confirmed: static/goal-exe/code/seg_0791_22.asm DDCB–DE24; named seg_0791_12.c:596–609] DE27 already dispatches the pool path to DDCB, but its port entry is missing. The real-helper T128 control failed honestly there. DDCB has no callees, a six-byte frame and ret2. It returns the manager's two game cursor/scroll words plus the pool-base table word minus2, with original16-bit arithmetic and exact scratch/stack effects.

[designed: main] Rescope T128 to include this small inseparable leaf in the same selection module and ABI proof layer. Add standalone original/PyPy DDCB controls and retain the failed real-helper calibration. No original-helper replay may stand in for the final sealed closure; no further missing primitive is absorbed without another main decision. Existing whole-memory/ALL16 and ordered-observation requirements remain.
