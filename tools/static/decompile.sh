#!/bin/sh
# Decompile the released GOAL.EXE with Ghidra into pseudo-C per routine (T18).
#
#   bash tools/static/decompile.sh <released GOAL.EXE> <output directory>
#   bash tools/static/decompile.sh --annotations <annotations directory> <released GOAL.EXE> <output directory>
#
# The second form (T20) writes the named view, static/goal-exe/named/: before decompiling it applies
# the annotations (tools/static/ghidra/GoalAnnotate.java, after tools/static/check_annotations.py
# passes) and writes with tools/static/named.py. The first form never reads the annotations.
#
# Unpacks GOAL.EXE with tools/static/unlzexe.py and checks the unpacked sha256, imports it with
# Ghidra's MZ loader (x86 real mode) in a throw-away project, places each listing segment at a
# 64K-aligned Ghidra segment and makes one function per routine of static/goal-exe/routines.tsv
# (tools/static/ghidra/GoalSetup.java), runs Ghidra's default auto-analysis, decompiles every
# function (tools/static/ghidra/GoalDecompile.java) and writes the files of
# static/goal-exe/decompiled/ into the output directory (tools/static/decompiled.py), byte for byte.
#
# Needs Ghidra 12.1.4 (GHIDRA_HOME, else ~/tools/ghidra_12.1.4_PUBLIC) and a JDK 21 (JAVA_HOME, else
# ~/tools/jdk-21*), python3 >= 3.11. One Ghidra instance,
# two CPUs (the machine is shared). KEEP_WORK=1 keeps the work directory (Ghidra's log, raw output).
set -eu
annotations=
if [ "${1:-}" = --annotations ] && [ $# -eq 4 ]; then
  annotations=$(cd "$2" && pwd)
  shift 2
fi
if [ $# -ne 2 ]; then
  echo "usage: $0 [--annotations <annotations directory>] <released GOAL.EXE> <output directory>" >&2
  exit 2
fi
exe=$1
out=$2
root=$(cd "$(dirname "$0")/../.." && pwd)
crash_reports=$(find "$root" -type f -name 'hs_err_pid*.log' -print)
if [ -n "$crash_reports" ]; then
  echo "decompile.sh: refusing to run while JVM crash reports remain in the worktree:" >&2
  printf '%s\n' "$crash_reports" >&2
  echo "Review the reports before retrying; report JVM crashes to Adoptium: https://github.com/adoptium/adoptium-support/issues" >&2
  exit 1
fi
if [ -n "$annotations" ]; then
  python3 "$root/tools/static/check_annotations.py" --annotations "$annotations" > /dev/null
fi

GHIDRA_VERSION=12.1.4
JDK_MAJOR=21
UNPACKED_SHA256=6fd8c5ef995358ff8e5e47d60de61dccd7bdf8e73f2f584018fcfe4c8c713188
TIMEOUT_PER_FUNCTION=600

# docs/environment.md: the installs live under ~/tools unless GHIDRA_HOME / JAVA_HOME say otherwise
GHIDRA_HOME=${GHIDRA_HOME:-$HOME/tools/ghidra_${GHIDRA_VERSION}_PUBLIC}
if [ -z "${JAVA_HOME:-}" ]; then
  JAVA_HOME=$(ls -d "$HOME"/tools/jdk-"$JDK_MAJOR"* 2>/dev/null | sort | tail -1)
fi
if [ ! -x "$GHIDRA_HOME/support/analyzeHeadless" ] || [ ! -x "${JAVA_HOME:-/nonexistent}/bin/java" ]; then
  echo "decompile.sh: set GHIDRA_HOME to Ghidra $GHIDRA_VERSION and JAVA_HOME to a JDK $JDK_MAJOR" >&2
  exit 1
fi
props="$GHIDRA_HOME/Ghidra/application.properties"
ghidra_version=$(sed -n 's/^application.version=//p' "$props")
ghidra_revision=$(sed -n 's/^application.revision.ghidra=//p' "$props")
if [ "$ghidra_version" != "$GHIDRA_VERSION" ]; then
  echo "decompile.sh: Ghidra $GHIDRA_VERSION needed, $GHIDRA_HOME is '$ghidra_version'" >&2
  exit 1
fi
java_version=$("$JAVA_HOME/bin/java" -version 2>&1 | sed -n '1s/.*version "\([^"]*\)".*/\1/p')
case "$java_version" in
  "$JDK_MAJOR".*|"$JDK_MAJOR") ;;
  *) echo "decompile.sh: JDK $JDK_MAJOR needed, $JAVA_HOME is '$java_version'" >&2; exit 1 ;;
esac
export JAVA_HOME

work=$(mktemp -d)
annotate=
if [ -n "$annotations" ]; then
  annotate="-postScript GoalAnnotate.java $work/segmap.tsv $annotations"
fi
if [ "${KEEP_WORK:-0}" = 1 ]; then
  echo "decompile.sh: work directory $work" >&2
else
  trap 'rm -rf "$work"' EXIT
fi

python3 "$root/tools/static/unlzexe.py" "$exe" "$work/goal.exe" > /dev/null
sha=$(sha256sum "$work/goal.exe" | cut -d' ' -f1)
if [ "$sha" != "$UNPACKED_SHA256" ]; then
  echo "decompile.sh: unpacked sha256 $sha, expected $UNPACKED_SHA256" >&2
  exit 1
fi

mkdir "$work/project"
if ! "$GHIDRA_HOME/support/analyzeHeadless" "$work/project" goal \
    -import "$work/goal.exe" -loader MzLoader -processor 'x86:LE:16:Real Mode' \
    -scriptPath "$root/tools/static/ghidra" \
    -preScript GoalSetup.java "$root/static/goal-exe/routines.tsv" "$work/segmap.tsv" \
    $annotate \
    -postScript GoalDecompile.java "$work/segmap.tsv" "$work/raw.txt" "$TIMEOUT_PER_FUNCTION" \
    -deleteProject -max-cpu 2 > "$work/ghidra.log" 2>&1 \
  || grep -q 'SCRIPT ERROR' "$work/ghidra.log" || [ ! -s "$work/raw.txt" ]; then
  tail -30 "$work/ghidra.log" >&2
  echo "decompile.sh: Ghidra failed (log above)" >&2
  exit 1
fi
# GoalDecompile.java retries (with a fresh decompiler) only after "process died" and only before the
# last attempt (ATTEMPTS = 3); any other failed attempt ends that function's tries (fix #57).
grep 'GOALRETRY' "$work/ghidra.log" | sed -E -e 's/ \(GhidraScript\).*//' -e 't clear' -e ':clear' -e '/GOALRETRY .* attempt [12]: .*process died/ s/.*> GOALRETRY /decompile.sh: decompiler failed, retrying with a fresh one: /' -e 't' -e 's/.*> GOALRETRY /decompile.sh: decompiler failed, not retrying: /' >&2 || true
grep -E 'GOALSETUP|GOALANNOTATE|GOALDECOMPILE' "$work/ghidra.log" | sed 's/.*> //; s/ (GhidraScript).*//' > "$work/summary.txt"

writer=decompiled.py
extra=
if [ -n "$annotations" ]; then
  writer=named.py
  extra="--annotations $annotations"
fi
# shellcheck disable=SC2086 # $extra is empty or two words without spaces
python3 "$root/tools/static/$writer" $extra \
  --raw "$work/raw.txt" --segmap "$work/segmap.tsv" --summary "$work/summary.txt" \
  --routines "$root/static/goal-exe/routines.tsv" \
  --ghidra "$ghidra_version (revision $ghidra_revision)" --jdk "$java_version" \
  --out "$out"
