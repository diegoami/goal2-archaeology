#!/usr/bin/env python3
"""Enumerate unresolved memory-API source sites; does not infer a site's record kind."""
import argparse
import ast
import collections
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'notes/engine-study/foundations'))
from check import pin,sha,write_new

OPS={'read','write','u8','u16','u32','w8','w16','w32','ds8','ds16','ds32','wds8','wds16','wds32'}
EXCLUDE={'__init__','mem','guest','prove'}


def build():
    groups=[];sources=[]
    for p in sorted((ROOT/'runtime/original_match/port').glob('*.py')):
        if p.stem in EXCLUDE:continue
        name=p.relative_to(ROOT).as_posix();sources.append(name)
        sites=collections.defaultdict(list)
        for n in ast.walk(ast.parse(p.read_text())):
            if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in OPS:
                sites[n.func.attr].append(n.lineno)
        groups.append({'file':name,'sites':{op:sorted(lines) for op,lines in sorted(sites.items())},
                       'site_count':sum(map(len,sites.values())),
                       'record_kind':'unresolved here: player/country/pitch/ball/table/stack/copy target requires caller and pointer provenance'})
    return pin({'task':'T96b-access-frontier','method':'Python AST calls at selected guest-memory/record APIs; includes non-player sites deliberately; not an alias/reachability proof',
                'operations':sorted(OPS),'excluded_machinery':sorted(EXCLUDE),'files':groups,
                'site_count':sum(g['site_count'] for g in groups),'analysis_sha256':sha(Path(__file__).read_bytes())},
               ['1771:3216'],sources)


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--check',action='store_true');a=ap.parse_args()
    path=ROOT/'notes/engine-study/T96/access-frontier-v1.json';data=build()
    if a.check:
        assert json.loads(path.read_text())==data,'memory API source frontier differs'
        print(f"PASS: {data['site_count']} explicit unresolved memory-API sites in {len(data['files'])} files; source hashes pinned")
    else:
        write_new(path,data);print(data['site_count'],len(data['files']))


if __name__=='__main__':main()
