#!/usr/bin/env bash
# Re-run every check the PR quotes, from the committed logs, and write the output to out/checks.txt
# (the one place the PR body and the README quote from). No game is run.
# Usage: bash experiments/E031-play-the-game/checks.sh
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
e=experiments/E031-play-the-game
{
  echo "commit $(git rev-parse --short HEAD) (worktree clean apart from this file: $(test -z "$(git status --porcelain -- "$e" docs ":!$e/out/checks.txt")" && echo yes || echo no)), $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo '$ python3 experiments/E031-play-the-game/verify_saves.py | tail -1'
  python3 $e/verify_saves.py 2>&1 | tail -1
  echo
  echo '$ python3 experiments/E031-play-the-game/progress.py g1 --md experiments/E031-play-the-game/out/g1/progress.md | tail -6'
  python3 $e/progress.py g1 --md $e/out/g1/progress.md | tail -6
  echo
  echo '$ python3 experiments/E031-play-the-game/claims.py'
  python3 $e/claims.py
  echo
  echo '$ python3 tools/check_links.py'
  python3 tools/check_links.py 2>&1 | tail -1
  echo
  echo '$ python3 -m unittest tests.test_agent_permissions tests.test_screens'
  python3 -m unittest tests.test_agent_permissions tests.test_screens 2>&1 | tail -3
} > $e/out/checks.txt
cat $e/out/checks.txt
