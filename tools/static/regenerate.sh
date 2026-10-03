#!/bin/sh
# Rebuild everything under static/ from the released original files, byte for byte:
#   static/goal-exe/  the listing of the unpacked GOAL.EXE (tools/static/listing.py)
#   static/goal-dat/  the block table and the checks on GOAL.DAT (tools/static/goaldat.py)
# Needs python3 >= 3.11 and network access to PyPI (capstone, pinned) and to the private
# release on the first run. The originals and the unpacked executable stay in .cache/ and scratch/
# (both git-ignored). Run from anywhere; then `git diff --exit-code static/` must be clean.
set -eu
root=$(cd "$(dirname "$0")/../.." && pwd)
cd "$root"
if [ ! -f .cache/goal2/GOAL.EXE ] || [ ! -f .cache/goal2/GOAL.DAT ]; then
  gh release download goal2-original --repo diegoami/goal2-archaeology -D .cache/goal2 --clobber
fi
[ -x scratch/venv/bin/python ] || python3 -m venv scratch/venv
scratch/venv/bin/pip install -q -r tools/static/requirements.txt
python3 tools/static/unlzexe.py .cache/goal2/GOAL.EXE scratch/goal.exe
scratch/venv/bin/python tools/static/listing.py .cache/goal2/GOAL.EXE static/goal-exe
python3 tools/static/goaldat.py .cache/goal2/GOAL.DAT static/goal-dat
