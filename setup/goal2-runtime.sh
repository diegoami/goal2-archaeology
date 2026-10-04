#!/usr/bin/env bash
# Checks the tools the GOAL2 runtime spike needs, unpacks the release `goal2-original` into
# .cache/goal2 (git-ignored) and verifies it against artifacts/known.json. Installs nothing.
# Ends with one line: `ready`, or `missing: <list>`.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 1
ROOT=$PWD
REPO=diegoami/goal2-archaeology
TAG=goal2-original
WANT_DOSBOX=2024.03.01
missing=()

need() { # need <command> <what>
  command -v "$1" >/dev/null 2>&1 || { missing+=("$2"); return 1; }
}

# dosbox-x, exact version (the task's runs-on pins it)
if need dosbox-x "dosbox-x@$WANT_DOSBOX (sudo apt install dosbox-x)"; then
  v=$(dosbox-x -version 2>&1 | sed -n 's/^DOSBox-X version \([0-9.]*\).*/\1/p' | head -1)
  echo "dosbox-x    $v ($(command -v dosbox-x))"
  [ "$v" = "$WANT_DOSBOX" ] || missing+=("dosbox-x $WANT_DOSBOX (found ${v:-unknown})")
fi

# display: Xvfb to run on, xdotool to type with
if need Xvfb "Xvfb (apt package xvfb)"; then
  echo "Xvfb        $(dpkg-query -W -f='${Version}' xvfb 2>/dev/null || echo present) ($(command -v Xvfb))"
fi
if need xdotool "xdotool"; then
  echo "xdotool     $(xdotool --version 2>&1 | head -1)"
fi

# python >= 3.11, standard library only
if need python3 "python3 >= 3.11"; then
  if python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)'; then
    echo "python3     $(python3 -c 'import platform; print(platform.python_version())')"
  else
    missing+=("python3 >= 3.11 (found $(python3 -c 'import platform; print(platform.python_version())'))")
  fi
fi

# gh, only needed to download the release when .cache/goal2 is not complete
python3 - "$ROOT" <<'PY' >/dev/null 2>&1
import hashlib, json, sys
root = sys.argv[1]
files = json.load(open(root + "/artifacts/known.json"))["sets"][0]["manifest"]["files"]
for f in files:
    if hashlib.sha256(open(root + "/.cache/goal2/" + f["path"], "rb").read()).hexdigest() != f["sha256"]:
        sys.exit(1)
PY
if [ $? -ne 0 ]; then
  if need gh "gh (to download release $TAG)"; then
    echo "release     downloading $TAG into .cache/goal2"
    mkdir -p .cache/goal2
    gh release download "$TAG" --repo "$REPO" -D .cache/goal2 --clobber >/dev/null 2>&1 \
      || missing+=("release $TAG (gh release download failed: is gh logged in with access to $REPO?)")
  fi
else
  echo "release     .cache/goal2 already matches artifacts/known.json"
fi

# verify the unpacked files against the registered set, byte for byte
if [ -d .cache/goal2 ]; then
  out=$(python3 - "$ROOT" <<'PY'
import hashlib, json, os, sys
root = sys.argv[1]
m = json.load(open(root + "/artifacts/known.json"))["sets"][0]["manifest"]
bad = []
for f in m["files"]:
    p = root + "/.cache/goal2/" + f["path"]
    if not os.path.isfile(p) or hashlib.sha256(open(p, "rb").read()).hexdigest() != f["sha256"]:
        bad.append(f["path"])
print("; ".join(bad) if bad else "OK %d files" % len(m["files"]))
PY
)
  case "$out" in
    OK*) echo "artifact    $out match set $(python3 -c "import json;print(json.load(open('artifacts/known.json'))['sets'][0]['manifest']['id'])")" ;;
    *) missing+=("release files that match artifacts/known.json: $out") ;;
  esac
else
  missing+=("release files in .cache/goal2")
fi

if [ ${#missing[@]} -eq 0 ]; then
  echo ready
else
  printf 'missing: %s' "${missing[0]}"; for m in "${missing[@]:1}"; do printf '; %s' "$m"; done; echo
  exit 1
fi
