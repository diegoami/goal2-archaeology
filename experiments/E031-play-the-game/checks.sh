#!/usr/bin/env bash
# Re-run every check the PR quotes and write out/checks.txt (checks.py does the work and fails
# closed: any check's non-zero exit makes this script exit non-zero). No game is run.
# Usage: bash experiments/E031-play-the-game/checks.sh
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
exec python3 experiments/E031-play-the-game/checks.py "$@"
