# The review brief's own sections

Every review brief carries these two sections, in full, after the numbered block of
`process.md` §5 (or, in the review profile, after the brief's numbered lines). The reviewer reads
the brief in another file, so paste them; never point to this one. Write "Blocking means" for the
task; paste the second section as it is. (L47, L49)

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
Tests and tools that need the network (GitHub, through gh; #236): the tests marked
@netskip.needs_pinned_tools in tests/test_validate_runs.py, test_register_artifact.py,
test_known_sets.py, test_publish_evidence.py and test_human_record.py, and the tools
tools/check_citations.py, verify_evidence.py, validate_runs.py, register_artifact.py (all through
tools/ga.py) and fetch_artifact.py. Each gh call retries a network failure once; offline those
tests skip and print "SKIPPED ... offline, needs the network: ...", and a tool fails with gh's
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
```
