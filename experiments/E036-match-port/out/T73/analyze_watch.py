"""T73: independent original-access constraints; never reads a candidate port run.

The result is an access-only candidate set, NOT a license to mask state-bearing
bytes. Every eventual mask range still needs the listing/semantic audit in notes.
All unobserved DS bytes, unknown owners and semantic kit reads/writes are excluded.
"""
import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[4]
E036 = ROOT / 'experiments/E036-match-port'
sys.path.insert(0, str(E036))
import compare, families, sizes
ROW = set(sizes.TASKS['T73'][3])


def spans(offsets):
    result=[]
    for off in sorted(offsets):
        if result and result[-1][1] == off:result[-1][1] = off+1
        else:result.append([off, off+1])
    return [[a,b-a] for a,b in result]


def analyze(reports):
    writers,readers,semantic,host_writes = defaultdict(set),defaultdict(set),defaultdict(set),set()
    observed=set(range(65536));seen=set()
    for report in reports:
        assert report['ports']==[] and report['excluded_ds_spans_are_unmaskable'] is True
        assert report['match'] not in seen
        seen.add(report['match'])
        observed &= {i for a,b in report['watched_ds_spans'] for i in range(a,b)}
        for access in report['guest_accesses']:
            assert access['kind'] in ('read','write') and type(access['count']) is int and access['count']>0
            into=writers if access['kind']=='write' else readers
            for off in range(access['ds_offset'],min(65536,access['ds_offset']+access['size'])):
                into[off].add(access['routine'])
        for access in report['kit_reads']:
            if access['category']=='semantic':
                for off in range(access['ds_offset'],min(65536,access['ds_offset']+access['size'])):
                    semantic[off].add(access['origin'])
            else:assert access['category']=='measurement'
        for access in report['kit_writes']:
            host_writes.update(range(access['ds_offset'],min(65536,access['ds_offset']+access['size'])))
    possible={off for off,owners in writers.items() if off in observed and owners and owners<=ROW
              and readers.get(off,set())<=ROW and not semantic.get(off) and off not in host_writes}
    facts=[]
    for start,length in spans(possible):
        facts.append({'ds_offset':start,'length':length,
                      'writers':sorted(set().union(*(writers[i] for i in range(start,start+length)))),
                      'readers':sorted(set().union(*(readers.get(i,set()) for i in range(start,start+length))))})
    return {'matches':sorted(seen),'observed_ds_spans':spans(observed),
            'unobserved_bytes_are_unmaskable':True,
            'access_only_candidate_ranges':facts,
            'candidate_bytes':len(possible),
            'warning':'Each range requires a separate static/semantic audit; state-bearing bytes remain protected.'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',required=True)
    ap.add_argument('--out',required=True)
    ap.add_argument('--require-all',action='store_true')
    a=ap.parse_args()
    root=Path(a.input)
    paths=sorted(root.rglob('*-accesses.json'))+sorted(root.rglob('*-accesses.json.gz'))
    reports=[];candidate={}
    declared=families.discover()
    specs={mid:sha for fam in declared.values() for mid,sha in fam.expected().items()}
    reference={mid:rec for fam in declared.values() for mid,rec in compare.load(ROOT/fam.reference).items()}
    for path in paths:
        text=gzip.decompress(path.read_bytes()).decode() if path.suffix=='.gz' else path.read_text()
        report=json.loads(text)
        name=path.name.removesuffix('.gz').removesuffix('-accesses.json')
        records=compare.load(path.with_name(name+'-record.jsonl'))
        assert set(records)=={report['match']}
        record=records[report['match']]
        assert 'ports' not in record and record['mask']==[]
        assert report['match'] not in candidate
        candidate.update(records);reports.append(report)
    if a.require_all:assert set(candidate)==set(specs), 'incomplete ALL watch'
    lines,ok=compare.check(reference,candidate,{mid:specs[mid] for mid in candidate},image_sha256=families.image_sha256())
    assert ok,'watch changed original behavior'
    result=analyze(reports)
    result['comparison_tail']=lines[-1]
    result['source_reports']=[str(p.resolve().relative_to(ROOT)) for p in paths]
    out=Path(a.out)
    with out.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(result['comparison_tail'])
    print(len(reports),'original matches;',result['candidate_bytes'],'access-only candidate bytes;',
          len(result['access_only_candidate_ranges']),'ranges (not yet approved masks)')


if __name__=='__main__':main()
