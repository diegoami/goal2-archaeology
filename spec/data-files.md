# Data files and saves

Written by the main session at promotion (docs/wide-pass.md, the wide pass of 2026-10-13): rows drafted from reviewed findings F001-F022 by read-only agents, statuses re-derived by the main session (`corroborated` only with two findings and both a behavioural and a static method in the Basis and Findings cells). The summary describes only `supported` and `corroborated` claims.

## Summary

(none)

## Claims

| ID | Claim | Status | Scope | Basis | Findings | Uncertainty | Next |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C-FILE-01 | F7 saves and play continues; F10 quits and saves if asked; F3 replays a saved goal; F4 loads a saved match summary; goals and match summaries can be saved and loaded; saving a goal needs the action replay on (INS toggles it). Save and reload only in the full registered version. | documented | S | doc (GOAL.HLP 75, 123-125, 222-227, 587-588); observed (F001) | [F001](../findings/F001-goal2-runs-unattended-under-dosbox-x.md) | `exact` for F7 and F10 (F001: one session each); F3, F4, INS never run | run-free: read `0791:0C65`, `0791:0A6B`, and the key handlers for F3/F4/INS in the named view; 2 h (help Q16.3, Q16.4) |
