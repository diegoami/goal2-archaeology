# T128 historical zero-counter compatibility

[confirmed: test_port_overhead_t117.py; port/__init__.py counter initialization; Match.result] Results include every installed port entry, including unused zero counters. Adding DDCB changes historical telemetry shape, not the old scenario's execution. The T117 control already asserts zero and removes other later entries before comparing its fixed historical digest.

[confirmed: T128 targeted diagnostic] On unchanged97f, raw result digest cdaae0a21eef40534ee0f4c301bea48edb09544b1291f4068a980879eb2df107 differs only by DDCB=0. Removing ONLY that metadata in a copy restores immutable b08217dfc263e5406fe960e6a31dbae42770deb94f81b6ef339f2e1fac0eb289. All831 events match; full0x110000 memory matches f308151e71b9c2559734d46c10b1b8890f2b1497fc59fa26cbffb6d83d7daaa6. The failed general run remains failed and retained.

[designed: main] Add DDCB to the existing T117 zero-entry compatibility list, asserting its counter is exactly zero before removing it from a COPY. Keep every fixed historical result/event/memory hash and timing limit; do not modify production telemetry or historical receipts. Any nonzero/new nonmetadata difference is a failure.

T127's accepted-default comparison also hashes a historical port result. Once T127 is genuinely accepted, integrate its test with the pool branch: conditionally assert/remove only an added zero DDCB counter before the historical comparison, preserving the original accepted data/digest and all other fields. Missing DDCB on the older registry is unchanged; nonzero DDCB cannot be normalized. Prove these cases with focused controls and repeat the combined actual default/controlled profiles. No game outcome rebaseline, broad ports omission or weaker physical-state oracle is allowed.

For one coherent final CI cycle, T128 acceptance now follows T127 integration. T128's primitive work remains complete independently; its local T117 correction can proceed while waiting. Hold its next PR push until accepted T127 is normally merged and both compatibility guards/proofs are final. Full suites remain in CI; no running batch may be cancelled.

T129p must apply the same narrow explicit-zero rule for its new E2E6 telemetry entry while preserving all historical gameplay/event/memory hashes.
