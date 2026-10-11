#!/usr/bin/env bash
# Installs DOSBox-X 2024.03.01, the version this project is calibrated to (F001), beside the system
# package, for this project only (#117). Ubuntu 26.04's apt offers only 2026.01.02, whose
# savestates the readers cannot parse. This unpacks Ubuntu 24.04's packages (dpkg-deb -x, no
# install, no sudo) into ~/tools/dosbox-x-2024.03.01 and writes bin/dosbox-x, a wrapper that adds
# the bundle's lib/ (libFLAC.so.12, which 26.04 lacks) to LD_LIBRARY_PATH. runtime/driver/driver.py's
# dosbox_x() runs the wrapper when it exists. Idempotent: an installed bundle that reports
# 2024.03.01 is left as it is. Ends with `ready <path>`, or exits 1.
set -euo pipefail
DEST="$HOME/tools/dosbox-x-2024.03.01"
WANT=2024.03.01
POOL=http://archive.ubuntu.com/ubuntu/pool
# name, path in the pool, sha256 (downloaded and checked 2026-10-11, #117)
PKGS=(
  "dosbox-x_2024.03.01+dfsg-1build2_amd64.deb universe/d/dosbox-x 1a27eb70d26360a0b82145ab4d1035e2e02d8d844211985758d51f6c854f874b"
  "dosbox-x-data_2024.03.01+dfsg-1build2_all.deb universe/d/dosbox-x 48f393f48415d246236e4fa4288d0ef234e365bcf4656f38692f7a1add76867f"
  "libflac12t64_1.4.3+ds-2.1ubuntu2_amd64.deb main/f/flac f2396692573407b2fbc92cd83148342d4aec717d42d5e24ac64c471204a0b7a9"
)
version() { "$DEST/bin/dosbox-x" -version 2>&1 | sed -n 's/^DOSBox-X version \([0-9.]*\).*/\1/p' | head -1; }
if [ -x "$DEST/bin/dosbox-x" ] && [ "$(version)" = "$WANT" ]; then
  echo "ready $DEST/bin/dosbox-x"; exit 0
fi
dl=$(mktemp -d)
trap 'rm -rf "$dl"' EXIT
mkdir -p "$DEST/lib" "$DEST/bin"
for p in "${PKGS[@]}"; do
  read -r name dir sum <<<"$p"
  curl -sSf -o "$dl/$name" "$POOL/$dir/$name"
  echo "$sum  $dl/$name" | sha256sum -c --quiet
  if [[ $name == libflac* ]]; then
    dpkg-deb -x "$dl/$name" "$dl/flac"
    cp -a "$dl"/flac/usr/lib/x86_64-linux-gnu/libFLAC.so.12* "$DEST/lib/"
  else
    dpkg-deb -x "$dl/$name" "$DEST"
  fi
done
cat > "$DEST/bin/dosbox-x" <<'WRAP'
#!/bin/sh
# DOSBox-X 2024.03.01 for goal2-archaeology (setup/dosbox-x-2024.03.01.sh, #117): Ubuntu 24.04's
# package unpacked, with libFLAC 12 in ../lib. The system /usr/bin/dosbox-x stays for other projects.
here=$(dirname "$(readlink -f "$0")")/..
LD_LIBRARY_PATH="$here/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" exec "$here/usr/bin/dosbox-x" "$@"
WRAP
chmod +x "$DEST/bin/dosbox-x"
if LD_LIBRARY_PATH="$DEST/lib" ldd "$DEST/usr/bin/dosbox-x" | grep -q "not found"; then
  echo "missing libraries:"; LD_LIBRARY_PATH="$DEST/lib" ldd "$DEST/usr/bin/dosbox-x" | grep "not found"; exit 1
fi
[ "$(version)" = "$WANT" ] || { echo "the bundle reports $(version), not $WANT"; exit 1; }
echo "ready $DEST/bin/dosbox-x"
