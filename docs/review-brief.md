# The review brief's own sections

Every review brief carries these three sections, in full, after the numbered block of
`process.md` §5 (or, in the review profile, after the brief's numbered lines). The reviewer reads
the brief in another file, so paste them; never point to this one. Write "Blocking means" for the
task; paste the other two sections as they are. (L47, L49)

```text
## Blocking means

Any one is enough; a blocking finding means rework, never approve.
1. A Done-when line fails, or cannot be run as written.
2. What this task protects can be got past: <name it: the guard, check, permission, invariant,
   rule value or file this task exists to protect>. A bypass you proved is blocking, even when it
   looks like an edge case. Never "follow-up hardening" or "outside the threat model" unless the
   task says so; if it does, quote the line. (L47)
3. Behaviour the task forbids, or behaviour nobody asked for, inside a file the task requires. (L44)
4. <project-specific items: a constant with no evidence, a test that passes with the behaviour
   deleted, a status written into a document>
Not blocking: wording, style, and defects in code the PR did not change: file those as follow-ups.
When unsure, say how likely the problem is. Rate it blocking only if it is likely and would get
past what the task protects; otherwise it is a follow-up. (L53)
Tests and tools that need the network (GitHub, through gh; #236): the tests marked with
tests/netskip.py (needs_pinned_tools in tests/test_validate_runs.py, test_register_artifact.py,
test_known_sets.py, test_publish_evidence.py and test_human_record.py; needs_release, with an
empty cache, in test_fetch_artifact.py, test_known_sets.py and test_human_keys.py), and the tools
tools/check_citations.py, verify_evidence.py, validate_runs.py, register_artifact.py (all through
tools/ga.py), fetch_artifact.py and the human recorder's release download. Each of those gh calls
retries a network failure once; offline those tests skip and print "SKIPPED ... offline, needs the
network for ...", and a tool fails with gh's
message ("error connecting to api.github.com", "TLS handshake timeout"). That is your network, not
the PR: re-run the line when the network answers, and rate it blocking only if it fails online.
A skipped test proves nothing: never count one as a pass.

## Report every blocking finding in this one review

This review is your only pass before the author fixes. Do not stop at the first blocking
finding: finish reading the whole diff and the task file, check every Done-when line and
every item under "Blocking means", and report all blocking findings together.

- Before you write the verdict, make one last pass over the full diff for anything you have
  not yet rated, and say "Final pass done" as the last line before the verdict.
- Number the findings R1, R2, … in order of severity. A finding you held back because an
  earlier one was already blocking is a review defect: if two problems share a cause, list
  both and say so.
- Do not rely on a later round. The author fixes everything you list, and the next review
  checks those fixes and new code only, not anything you saw but did not report.
- If you ran out of time or context before covering the whole diff, say which files or
  sections you did not cover. Do not approve in that case.

Run mechanics: some suites in this repository take 7 minutes or more and print nothing meanwhile.
That is expected, not a hang. Run such a suite once, in one foreground call whose timeout is long
enough for it. Do not start it in the background and poll it, and do not kill it for being quiet:
the harness stops a review only after 25 minutes without activity, which one foreground call stays
well inside.

Scratch space: /tmp is a small RAM-backed disk shared with other projects, and it may be full (it
was at 100% on 2026-10-17 and a review died of ENOSPC after an hour). Put copies of main,
family-run outputs, suite logs and any other big file in your scratch folder under
~/goal2-review-tmp/ (the run's rules name it; TMPDIR, TMP and TEMP already point there; it is on the
real disk, its path has no dot element, and the script removes it when your review is read). Never
write them under /tmp. If a command fails with "No space left on device", say so in the review and
move its output to the scratch folder rather than retrying in /tmp.

## Rework rounds: what you re-run (the owner, 2026-10-18, #319)

The first review of a task or fix (the brief has no "This is review round" line) re-runs every
Done-when line, a full family run included. In a rework round (the brief says "This is review round"
2 or later, and names "Sample for this round") you re-run instead:
- the sample the brief names, in place of the full run of any Done-when line that runs the whole
  family or sweep;
- every unit test, every mutation check a Done-when line names, and the check of each finding of the
  earlier review;
- every other Done-when line, as in the first review.
You verify, and do not re-run, the committed full-family outputs: their sha256 against the
implementer's manifest, and the comparison tool (compare.py for the engine tasks) run on the
committed files. Account for each such line as `DW<k>: sampled <command> → <result>; hashes ok or
differ; compare <result>`.
If the sample differs from the committed output in any way, or a hash does not match, stop sampling:
run the full line and say so. A sample run that cannot be made is `DW<k>: not run`, never an approval.
```
