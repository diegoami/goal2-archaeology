---
name: run-task
description: Run tasks or fixes end to end. The user chooses who implements and who reviews, on which model (asked one question each); the reviewer is of another model family; the main session watches, merges and reports. Main session only.
---

# /run-task [T<nn> | #<issue> ...]

Read `docs/process.md` §3–§6 first. Given ids, run them in order; given none, take the first
`status:ready` task in `docs/tasks/README.md`. Report after each task; stop at any escalation.
For `#<issue>` of a bug labelled `fix`, the bug body replaces the task file, the branch is
`fix/<issue>-<slug>` (`--fix <issue>` in the scripts), and there is one review round.

0. **Check.** The issue is `status:ready` and every Merge-after task is merged. Run
   `gh issue list --label triage:needed --state open`; triage anything that names this task first.
   If `harness.json` has cutoffs for `breaks-play`, route those issues through Jev first (`/jev`
   step 4). Act on its confident ends and triage the middle yourself; exit 3 means triage it all.

   Run every Done-when line yourself: it must fail on `main` and pass on a mock fix (a scratch
   change, then discarded). A line that cannot is amended on `main` before dispatch (L45).

1. **Brief.** Write it to a temp file: the task file **pasted in full**, then `docs/process.md` §4's
   block, then (on rework) the review comment's URL. Never a pointer to the task file.

   **Watching background work** (CLAUDE.md "Choosing models" rules 8-13). Start every OpenCode
   run in the background with stdin from a file, never an inherited pipe. Arm ONE monitor that
   checks every 1-2 minutes: the session started (`opencode session list` in the run's directory,
   or the log's `session ses_... started` line) and the exit; progress (the log's size, the
   session's `updated` time, the worktree's changed files, new lines in `RUN-NOTES.md`, new commits
   on the branch); "possibly stuck" after ~10 minutes with no change; "unpushed" when a commit sits
   on the branch but not on origin for ~15 minutes (push it for the run, and record that); free
   memory, if short (then reviews and builds one at a time). For a Claude agent, the signal is its
   transcript file's size plus its worktree. Tell the user in plain language what each agent is
   doing: its step, its commits, its findings; never raw log lines or byte counts. On "possibly
   stuck": check the process is alive on its exact PID and read its newest session messages (below);
   a long build or test is not stuck. Dead, or silent for 20 minutes: stuck; stop it only if it is
   ours. Never wait with `while pgrep -f '<pattern>'` (it matches itself); wait on the PID with
   `while kill -0 <pid>`.

2. **Implement.** First ask the user ONE question (CLAUDE.md "Choosing models" rule 1): the main
   session or a subagent, and which model; show `/recommend`'s pick and pair as a suggestion only.
   Record the answer and the suggestion's reasons on the issue. Label `status:in-progress`.
   - The main session: it works in its own `git worktree` on the task's branch, keeps `RUN-NOTES.md`
     there (`docs/running-notes.md`), pushes after every commit and opens the PR.
   - OpenCode: `node tools/harness/implement.mjs --task T<nn> --slug <slug> --issue <n> --brief <file>
     --model <the user's model>` with `run_in_background`, watched (above).
     - Exit 0: a PR is open. Note the `implemented by:` line.
     - Exit 1: read the log it names and the run's final message (below). A run that stopped and
       reported a blocker gets an answer (fix the brief or the setup), never a retry on another model.
     - Exit 2 on a refused model (DeepSeek, an unknown name): tell the user.
     - Exit 3: OpenCode, the model's login or its provider does not answer. Tell the user and ask
       which model instead (rule 7); never re-route on your own.
     - Killed by our own idle or total limit: resume it, don't restart it:
       `implement.mjs ... --model <same> --session <ses_...> --total-timeout-sec <longer>` with a
       short "continue where you stopped" brief, in the kept worktree (rule 13).
   - A Claude agent: `Agent(subagent_type: "implementer", isolation: "worktree")` on the model the
     user named, with the brief. Read its final report in full before acting, and post its
     `RUN-NOTES.md` on the issue.
   - **Read before you retry (L55).** Before a retry, a re-route to another model, or calling a
     run a failure, read what it returned; never retry blind. An OpenCode exit 1 with an empty
     diff looks the same for an early end and for a run that stopped and reported a blocker, and
     the log's tail shows only the last tool output. Read the model's final message from the
     session record, read-only (never `auth.json` in that directory), with the `session ses_…` id
     from the run's log:
     ```bash
     python3 - <<'EOF'
     import sqlite3, json, os
     home = os.environ.get('HARNESS_OPENCODE_HOME') or os.path.expanduser('~/.local/share/harness-opencode')
     db = 'file:' + os.path.join(home, 'data', 'opencode', 'opencode.db') + '?mode=ro'   # the scripts' data directory
     c = sqlite3.connect(db, uri=True)
     sid = 'ses_...'   # the "session ses_..." line in the run's log
     parts = [json.loads(d) for (d,) in c.execute("select data from part where session_id=? order by time_created", (sid,))]
     texts = [p for p in parts if p.get('type') == 'text']
     print(texts[-1]['text'] if texts else 'no text part')
     EOF
     ```
     For a Claude agent, read its final report in full. A run that stopped and reported gets an
     answer to its report (amend the task, decide, or escalate), and the report is posted on the
     task's issue so it is kept.
   - The Claude agent's file (`.claude/agents/implementer.md`) carries
     §4's block and the run mechanics, and its hook refuses `git stash`, `git worktree`, a
     force-push and `gh pr merge`.

3. **Review.** First ask the user ONE question (rule 2): which external model reviews (never the
   implementer's family); show `/recommend?tier=...&exclude_family=<implementer's family>`'s pick as a
   suggestion only, and record the answer on the PR. One review per PR unless the user asks for more,
   run alone. Label `status:in-review`.
   - OpenCode: `node tools/harness/review.mjs --pr <pr> --brief <file> --reviewer <the user's model>
     --exclude <implemented by> --issue <n> --apply-label`, in the background. (`--hard`/`--sol`,
     which run harness.json's reviewer chains, are superseded: the user names the reviewer.) Name
     the PR's head in the brief only after the push has landed: take it from the local branch
     (`git rev-parse <branch>`). A brief whose block before the task file names another commit
     exits 2 before anything runs (L33).
     - Exit 0: posted and labelled.
     - Exit 3: no review came back, or OpenCode or its login is unavailable (read the run's final
       message first, as under step 2's *Read before you retry*). Nothing was posted: tell the
       user and ask which reviewer instead (rule 7).
     - Exit 4: a review was posted whole under a note (it may be cut off, its verdict is
       unreadable, its verdicts differ, or a finding follows its closing verdict), or an approve
       left a Done-when line unaccounted for or not run (L32). No label was applied. For a
       missing `DW` line, run a supplementary review of those lines alone, or send it to rework. Read it on the PR
       and decide: apply the label it supports, or escalate. Never pay for a second review just
       because the first was flagged.
   - A Claude reviewer, when the user names one: first `git fetch origin pull/<pr>/head`, since the
     reviewer has no GitHub credentials (#68); then `Agent(subagent_type: "reviewer", isolation:
     "worktree")` on the named model,
     with §5's brief filled in. The agent file carries the rest; its hook refuses every write. It
     **returns** its review: save its final message to a file, then post it with
     `node tools/harness/post-review.mjs --pr <pr> --brief <brief> --review <file>
     --by "claude (<model>)" --issue <n> --apply-label`. Its exits are review.mjs's, but 1 means no
     review was in the message: re-run the reviewer once, then escalate.
   - Architecture task: also `/code-review <pr>`, always with the number.

4. **Decide** on the label the reviewer applied.
   - `status:approved`:
     1. Wait for green CI.
     2. Re-run the check the approval rests on most (the Done-when line or the mutation that
        proves the task) on the PR's head yourself. A different result is rework, not a merge (L46).
     3. `gh pr merge <pr> --squash --delete-branch`, then label `status:merged`.
     4. File one `T<nn> follow-up` issue (`triage:needed`) for the non-blocking findings.
     5. Unblock the tasks whose Merge-after are now all merged.
     6. Remove the task's worktrees.
     7. Post §9's measurement comment on the PR.
     8. Report the merge, the findings, the follow-ups and what is ready next.
   - `status:rework`:
     1. Check that every finding names a file in `gh pr diff <pr> --name-only`. A review that
        does not reviewed the wrong tree: discard it, say so, and re-review.
     2. At `review-round:2` (at `review-round:1` for a fix), go to step 5.
        A reviewer that reports one blocking finding per round despite the brief's one-pass
        section (L49): after the second such round, stop. Request no further review until you
        have gone through the whole diff yourself for that class and fixed what you found, and
        recorded the pattern in the model-trials record. The review after that is the task's last
        before escalation (step 5).
     3. **The next round's implementer is the user's choice** (rule 1; L38's ladder is superseded).
        When the review was heavy (three or more blocking findings, or a repeated class), say so in
        the question. On a change of implementer, hand over: stop the current one if it is
        mid-round; save its unpushed work as a patch (`git add -N` new files, then
        `git diff > <patch>`); start the new one on the pushed branch with the task file pasted in
        full, every review so far (the current one pasted in full), the patch path "to weigh, never
        to apply blindly", and the instruction to fix the class of the findings, not each instance,
        then sweep its own code for the same class and list the sweep in the PR body. The round
        count does not reset, the reviewer stays of another family, and the Done-when is never
        weakened.
     4. Set the next round and return to step 1, with the full review's URL in the brief (and,
        after step 3, the hand-over's). The implementer script resumes the branch.

5. **Escalate** (`docs/process.md` §7): label `status:escalated`, comment the evidence on the issue,
   and bring the user the decision with options and a recommendation. Stop.
   A defect found in merged code outside the task is filed as a bug (`triage:needed`). If it
   blocks the task: a one-file mechanical fix may ride this PR, declared under Scope; otherwise
   label the task `status:blocked` and stop.

Never:
- merge without an approving review and green CI;
- weaken a Done-when;
- let the implementer's model family review its PR;
- relay part of a review;
- force-push or rewrite `main`.
