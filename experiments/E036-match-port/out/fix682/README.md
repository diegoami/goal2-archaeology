# Live-player-record API controls

Source baseline46e0043e; issue682 is the bounded contract. Pure coordinator/API/checkpoint
controls are synthetic and do not claim original/PyPy live-match proof. before-v1.log is
the initial5case reproduction. before-v2.log adds checkpoint flag controls:6tests,
13assertion failures(including subtests)/2errors. The legacy/default packet control passes.

after-v1.log is an edit-guard calibration:the guarded patch refused an ambiguous match
before writing production source, so it reran unchanged baseline and is NOT a pass.
after-v2.log exposed a test invocation error:the existing _checkpoint_state API returns
(n,state,engine), not(state,n,engine). Corrected calls keep all payload/flag assertions.
after-v3.log:6/6PASS0.007s; stopped-controls-v1.log:existing9/9PASS. No old game assertion,
seed, profile or mask changed. Natural proof/checkpoint/fidelity/CI acceptance remains
required before this API can merge. No raw original records or owner saves are published.
