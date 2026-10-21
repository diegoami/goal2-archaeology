#!/usr/bin/env bash
# [designed: owner, 2026-10-20] Prepare a fresh checkout, a cloud session included, to work on
# goal2-archaeology (docs/cloud.md). Safe to run again; each step skips what is already in place.
# It mirrors CI (.github/workflows/ci.yml): the same apt tools, Python requirements and artifacts,
# plus DOSBox-X 2024.03.01 from setup/dosbox-x-2024.03.01.sh when apt offers another version
# (F001: the readers parse only 2024.03.01's savestates, #117).
# Afterwards: source .cache/cloud.env
set -uo pipefail
cd "$(git rev-parse --show-toplevel)"
say() { printf '== %s\n' "$*"; }
mkdir -p .cache "$HOME/.local/bin"
export PATH="$HOME/tools/dosbox-x-2024.03.01/bin:$HOME/.local/bin:$PATH"
root=$([ "$(id -u)" = 0 ] && echo yes || echo no)

say "system tools: Xvfb, Xephyr, xinput, xdotool, ffmpeg, gh, and DOSBox-X's libraries"
if command -v apt-get >/dev/null && [ "$root" = yes ]; then
  apt-get update -qq >/dev/null 2>&1
  # The distribution's dosbox-x brings every runtime library DOSBox-X links against, whatever the
  # package names on this release; the 2024.03.01 bundle below then runs on them.
  apt-get install -y -qq --no-install-recommends xvfb xserver-xephyr xinput xdotool x11-utils ffmpeg \
    dosbox-x gh curl unzip binutils >/dev/null 2>&1 || echo "apt-get install failed for some tools"
else
  echo "skipped (not root or no apt-get): install xvfb xserver-xephyr xinput xdotool x11-utils ffmpeg dosbox-x"
fi

say "DOSBox-X 2024.03.01"
if [ "$(dosbox-x -version 2>&1 | sed -n 's/^DOSBox-X version \([0-9.]*\).*/\1/p' | head -1)" != 2024.03.01 ]; then
  bash setup/dosbox-x-2024.03.01.sh || echo "the DOSBox-X 2024.03.01 bundle could not be installed"
fi
dbx="$HOME/tools/dosbox-x-2024.03.01/usr/bin/dosbox-x"
if [ -x "$dbx" ]; then
  missing=$(LD_LIBRARY_PATH="$HOME/tools/dosbox-x-2024.03.01/lib" ldd "$dbx" 2>/dev/null | awk '/not found/ {print $1}' | tr '\n' ' ')
  [ -z "$missing" ] || echo "DOSBox-X libraries missing: $missing(install their packages; docs/cloud.md)"
fi
version=$(dosbox-x -version 2>&1 | sed -n 's/^DOSBox-X version \([0-9.]*\).*/\1/p' | head -1)
echo "DOSBox-X: ${version:-not runnable} ($(command -v dosbox-x || echo none))"

say "Python requirements (as CI)"
python3 -m pip install -q -r tools/static/requirements.txt -r runtime/emul/requirements.txt 2>/dev/null \
  || python3 -m pip install -q --break-system-packages -r tools/static/requirements.txt -r runtime/emul/requirements.txt \
  || echo "pip install failed"

say "the original game's artifact sets (public releases, verified by hash; CLAUDE.md rule 18)"
python3 tools/fetch_artifact.py goal2-67cf27d6 || echo "fetching goal2-67cf27d6 failed"
python3 tools/fetch_artifact.py goal2-a949da2f || echo "fetching goal2-a949da2f failed"
bash setup/goal2-runtime.sh || true

say "emulator probe: boot to the title screen, key, restore, read (runtime/driver/cycle.py --dry)"
# Proves DOSBox-X 2024.03.01, the display, the key transport and the savestate reader work together
# here, and that the title screen is byte for byte the one the published records saw (its digest is
# in runs/E001/E001-r0001.json). It writes no record.
title=$(python3 - 2>/dev/null <<'PY'
# The title start state (made once if missing; start states are never replaced, L207) and the
# screen digest stored in it, read with the project's own savestate reader.
import sys; sys.path.insert(0, "runtime/driver")
import driver, savestate
path = driver.STATES / "title.sav"
if not path.exists():
    driver.make_state("title")
print(savestate.Savestate(path.read_bytes()).screen().digest())
PY
)
if [ -z "$title" ]; then
  echo "emulator probe: FAILED to make or read the title state (python3 runtime/driver/driver.py make-state title)"
elif ! grep -q "$title" runs/E001/E001-r0001.json; then
  echo "emulator probe: FAILED: title screen $title differs from the published records (runs/E001)"
elif python3 runtime/driver/cycle.py --runs 2 --start-state title --dry 2>&1 | tail -1 | grep -q "2 of 2 cycles completed"; then
  echo "emulator probe: ok (title screen matches runs/E001; 2 of 2 cycles)"
else
  echo "emulator probe: FAILED (python3 runtime/driver/cycle.py --runs 2 --start-state title --dry shows why)"
fi

say "checkpoint from the owner's Drive (the non-git state of interrupted work; docs/cloud.md)"
# GOAL2_RCLONE_TOKEN: the whole JSON of rclone.conf's `token = {...}` (refresh_token included), the
# same secret goal2's cloud sessions use; the remote sees only the owner's goal2 folder.
DRIVE_FOLDER=12fgdrQUQB4pHdq0ibY-NP-aU8jgNaRzc
if [ -n "${GOAL2_RCLONE_TOKEN:-}" ]; then
  command -v rclone >/dev/null || { [ "$root" = yes ] && apt-get install -y -qq rclone >/dev/null 2>&1; }
  if ! printf '%s' "$GOAL2_RCLONE_TOKEN" | python3 -c "import json,sys; sys.exit(0 if json.load(sys.stdin).get('refresh_token') else 1)" 2>/dev/null; then
    echo "GOAL2_RCLONE_TOKEN is not the whole token JSON (with refresh_token); no Drive checkpoint pulled"
  elif rclone config create goal2drive drive scope=drive root_folder_id="$DRIVE_FOLDER" token="$GOAL2_RCLONE_TOKEN" \
         ${RCLONE_DRIVE_CLIENT_ID:+client_id="$RCLONE_DRIVE_CLIENT_ID"} \
         ${RCLONE_DRIVE_CLIENT_SECRET:+client_secret="$RCLONE_DRIVE_CLIENT_SECRET"} --non-interactive >/dev/null; then
    latest=$(rclone lsf --dirs-only goal2drive:goal2-archaeology 2>/dev/null | grep '^checkpoint-' | sort | tail -1)
    if [ -n "$latest" ]; then
      rclone copy "goal2drive:goal2-archaeology/$latest" .cache && echo "Drive checkpoint ${latest%/} copied into .cache/" \
        || echo "copying the Drive checkpoint ${latest%/} failed"
    else
      echo "no checkpoint-* folder under goal2drive:goal2-archaeology"
    fi
  else
    echo "could not create the goal2drive remote"
  fi
else
  echo "GOAL2_RCLONE_TOKEN is not set: no Drive checkpoint (fine when nothing was handed over)"
fi

say "GitHub"
gh api user --jq .login >/dev/null 2>&1 && echo "gh is logged in" || echo "gh is not logged in: set GH_TOKEN (docs/cloud.md)"

cat > .cache/cloud.env <<EOF
# written by tools/cloud_setup.sh
export PATH="\$HOME/tools/dosbox-x-2024.03.01/bin:\$HOME/.local/bin:\$PATH"
EOF
say "done: source .cache/cloud.env"
