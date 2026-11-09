#!/usr/bin/env python3
"""Zip every private raw state of every T131 attempt, the pinned Core source and the run logs into one package.

Paths inside are relative to the repository root, so `unzip -n <zip> -d .` restores `.cache/400-roles34/...`. The delivered
t131-named copies and the original-byte inputs (the date-call savestate, GOAL.DAT: already on the owner's Drive) are not in it.
"""
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];CACHE=ROOT/'.cache/400-roles34'
OUT=CACHE/'delivery/t131-all-attempts-private.zip'
def main():
    OUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(CACHE.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts or p.parts[len(CACHE.parts):][0] in ('delivery','readback'):continue
            if p.name in ('e039-r0005-date-call.sav','GOAL.DAT'):continue
            z.write(p,str(p.relative_to(ROOT)))
    print(OUT,OUT.stat().st_size)
if __name__=='__main__':main()
