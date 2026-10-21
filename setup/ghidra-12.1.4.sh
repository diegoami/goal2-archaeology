#!/usr/bin/env bash
# [designed: owner, 2026-10-20] Installs, on demand, the two tools tools/static/decompile.sh needs
# (docs/environment.md "Ghidra"): Ghidra 12.1.4 and the Temurin JDK 21.0.12.1, from their official
# GitHub releases, each checked against its pinned sha256 (the digests the releases publish), into
# $TOOLS (default ~/tools): ghidra_12.1.4_PUBLIC and jdk-21.0.12.1+1, the paths decompile.sh looks
# for. No sudo. About 780 MB to download; run it only when a task regenerates the decompiled or
# named views (docs/process.md §13), not at every session start. Idempotent: an install that is
# already there is left as it is. Ends with `ready <ghidra> <jdk>`, or exits 1.
set -euo pipefail
TOOLS="${TOOLS:-$HOME/tools}"
GHIDRA_DIR="$TOOLS/ghidra_12.1.4_PUBLIC"
JDK_DIR="$TOOLS/jdk-21.0.12.1+1"
GHIDRA_URL=https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.1.4_build/ghidra_12.1.4_PUBLIC_20260921.zip
GHIDRA_SHA=ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db
JDK_URL=https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz
JDK_SHA=ce79869e1307ed8ee1e2baa86a412b1eb5b75d10a01006d788a6f968bcfaee94

mkdir -p "$TOOLS"
dl=$(mktemp -d)
trap 'rm -rf "$dl"' EXIT
fetch() {  # fetch <url> <sha256> <file>
  curl -sSfL --retry 3 -o "$dl/$3" "$1"
  echo "$2  $dl/$3" | sha256sum -c --quiet || { echo "sha256 mismatch for $3" >&2; exit 1; }
}

if [ ! -x "$JDK_DIR/bin/java" ]; then
  fetch "$JDK_URL" "$JDK_SHA" jdk.tar.gz
  tar -xzf "$dl/jdk.tar.gz" -C "$TOOLS"
fi
"$JDK_DIR/bin/java" -version 2>&1 | head -1 | grep -q '"21.0.12.1"' || { echo "$JDK_DIR is not JDK 21.0.12.1" >&2; exit 1; }

if [ ! -x "$GHIDRA_DIR/support/analyzeHeadless" ]; then
  command -v unzip >/dev/null || { echo "unzip is needed (apt-get install unzip)" >&2; exit 1; }
  fetch "$GHIDRA_URL" "$GHIDRA_SHA" ghidra.zip
  unzip -q "$dl/ghidra.zip" -d "$TOOLS"
fi
grep -q '^application.version=12.1.4$' "$GHIDRA_DIR/Ghidra/application.properties" \
  || { echo "$GHIDRA_DIR is not Ghidra 12.1.4" >&2; exit 1; }
echo "ready $GHIDRA_DIR $JDK_DIR"
