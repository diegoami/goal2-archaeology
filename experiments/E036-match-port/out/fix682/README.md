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

Natural producer calibration original-friendly-v1.log stopped before completing its first arm:the producer called nonexistent Match.dump/timeout keyword. The actual API is Match.save()/Match.load(saved), which preserves saved timeout_s. Versioned proof-v2.py corrects only those calls and additionally asserts the retained60s timeout; no game/fidelity assertion was removed. The failed output remains immutable and is not a pass.

Actual proof batch:index-v1.json binds all four producer receipts to identical runtime/proof source hashes. Eight completed matches (legacy+opt-in, originalCPython+verifiedPyPy3.11, friendly+admittedknockout) check28stops/560currentrecords. Both checkpoints retain flag/payload/fullphysicalstate; friendly pause/half-time/immediate swap includeswithdrawnplayers, knockout visitsbothETintervals/shootout. At half-time11players havechangedenergy/performance versusinitialinput. Within each backend legacy/opt-in fullresult/fullphysicalmemory areEXACTLYequal; expected opt-in events are the exact legacy events with only independently readrecord additions. AllTrue/False snapshots match between original/port. Existing result/RNG/acceptedranges/display-profile event comparisons pass. Raw original/portfriendlyphysicalhashes differ, as recorded, so no fullcrossbackendphysicalequality is claimed there; knockoutfullphysicalhashes match. Existing onlyfull_time.screen_sha256 projection staysunchanged, rawall-eventhashes retained; no new mask/projection. PyPyunit6/6PASS0.054s; existingstoppedcontrols9/9PASS; links/JSON11672filesPASS. CI stillrequired beforemerge/adoption. Raw originalrecords remainprivate.
