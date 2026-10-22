#!/usr/bin/env bash
# The collector of .github/workflows/family-run.yml (#361), run from the repository root on the dispatched branch:
# joins the shard logs in SHARDS_DIR (default shards/) with shards.py collect, writes a manifest, commits all of it to
# experiments/E036-match-port/out/$TASK/<dir>/ and pushes to $GITHUB_REF_NAME.
#
# <dir> is "$NAME-$GITHUB_RUN_ID" for a run's first attempt (the T64 and T69 runs' folders) and
# "$NAME-$GITHUB_RUN_ID-attempt-$GITHUB_RUN_ATTEMPT" for a re-run of the same run: each attempt writes a folder of its
# own, so a re-run never adds a path the first attempt committed (#364: "Re-run all jobs" kept the run id, and the
# second collector's rebase stopped on an add/add conflict in manifest.json).
#
# Environment: TASK, NAME, FAMILY, ONLY (may be empty), INPUTS (JSON), GITHUB_RUN_ID, GITHUB_RUN_ATTEMPT,
# GITHUB_WORKFLOW, GITHUB_REF_NAME, GITHUB_SHA, GITHUB_SERVER_URL, GITHUB_REPOSITORY; RETRY_SLEEP (seconds, default
# 10: a push lost to a concurrent one waits RETRY_SLEEP x attempt before the next of five).
# Exit status: 0 when the commit is pushed and the join was complete; 2 when it is pushed but shards.py refused the join
# (a match missing or twice: the shards are committed all the same, and the job fails); 1 when five pushes failed or
# the folder already exists.
set -u
shards_dir=${SHARDS_DIR:-shards}
dir="$NAME-$GITHUB_RUN_ID"
[ "$GITHUB_RUN_ATTEMPT" != 1 ] && dir="$dir-attempt-$GITHUB_RUN_ATTEMPT"
dest="experiments/E036-match-port/out/$TASK/$dir"
if [ -e "$dest" ]; then
  echo "$dest exists: a folder is never written twice" >&2
  exit 1
fi
mkdir -p "$dest"
cp "$shards_dir"/* "$dest/"
args=(collect --family "$FAMILY" --out "$dest/$NAME.jsonl")
[ -n "$ONLY" ] && args+=(--only "$ONLY")
python3 -B experiments/E036-match-port/shards.py "${args[@]}" "$dest"/shard-*.jsonl > "$dest/collect.txt" 2>&1
joined=$?
echo "exit $joined" >> "$dest/collect.txt"
cat "$dest/collect.txt"
python3 - "$dest/manifest.json" <<'PY'
import json, os, sys
json.dump({"run_id": os.environ["GITHUB_RUN_ID"], "run_attempt": os.environ["GITHUB_RUN_ATTEMPT"],
           "workflow": os.environ["GITHUB_WORKFLOW"], "ref": os.environ["GITHUB_REF_NAME"],
           "sha": os.environ["GITHUB_SHA"], "inputs": json.loads(os.environ["INPUTS"]),
           "run_url": f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{os.environ['GITHUB_RUN_ID']}"},
          open(sys.argv[1], "w"), indent=1)
PY
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add "$dest"
git commit -q -m "$TASK: $NAME, E036 family run $GITHUB_RUN_ID attempt $GITHUB_RUN_ATTEMPT on Actions (#361)"
for i in 1 2 3 4 5; do
  if git pull -q --rebase origin "$GITHUB_REF_NAME"; then
    git push -q origin "HEAD:$GITHUB_REF_NAME" && { [ $joined = 0 ] && exit 0; exit 2; }
  else
    git rebase --abort 2>/dev/null       # a stopped rebase is undone, so the next try starts from the commit again
  fi
  sleep $((i * ${RETRY_SLEEP:-10}))
done
exit 1
