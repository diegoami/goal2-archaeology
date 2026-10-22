# T62 full suite in the cloud session (2026-10-21/22): triage of the 24 non-passes

Run: `full-suite-cloud-20261021.txt` (1608 tests, failures=5, errors=19, skipped=32, exit 1), on the merged T62 head.
No failure is in a port, engine or E036 module; `tests.test_port_motion` (44) passed there and in
`focused-checks-cloud-20261021.txt`. Every non-pass is of this cloud environment:

- 18 errors (test_human_record x3, test_known_sets, test_publish_evidence, test_register_artifact x6,
  test_validate_runs x8 minus overlap): `tools.ga.GaError: gh api repos/diegoami/game-archaeologist/... failed:
  GitHub access to this repo` -- the session's GitHub scope is goal2-archaeology only, so the pinned checker
  from game-archaeologist cannot be fetched.
- test_ga x2 (unreadable formats/tools directory is a named error): the suite runs as root (uid 0), for which
  chmod 000 does not make a directory unreadable.
- test_human_record.test_the_record_names_no_home_directory: asserts its work directory lies under $HOME;
  here the checkout is /home/user/goal2-archaeology and $HOME is /root.
- test_driver_terminate.test_launch_never_restores_into_a_dos_prompt_session: the title start state placed from
  the Drive checkpoint (T62's, saved with C: mounted under /home/diego) was refused; with the cloud session's
  own title state in .cache/states/driver it passes (`full-suite-cloud-20261021-retake-env-b.txt`).
- test_driver_keys.test_no_alt_is_held_and_f10_arrives_as_f10: dosbox-x exits -11 (SIGSEGV) during a savestate;
  reproduced identically on a clean clone of main 841f311 in the same session, so not this PR's.

CI (`checks`) is green on the PR head. Follow-up issue for the cloud gaps: see the PR's merge comment.
