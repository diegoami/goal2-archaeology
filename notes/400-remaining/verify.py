#!/usr/bin/env python3
"""Verify immutable provenance, low-byte roles, live frames and private readbacks."""
import hashlib,json,subprocess
from pathlib import Path
from frames import ROOT,derive

def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    base=ROOT/'notes/400-remaining'
    inventory=json.loads((ROOT/'notes/390/inventory.json').read_text())['assets']
    n=0
    for folder in sorted(base.glob('native-r*')):
        rec=json.loads((folder/'record.json').read_text());source=json.loads((folder/'source.json').read_text())
        assert rec['status'] in ('stopped','bound-or-eof','aborted')
        assert source['head']==rec['head'] and source['collector_sha256']==rec['collector_sha256']
        collector=(folder/'collector.py').read_bytes();assert sha(collector)==rec['collector_sha256']
        assert subprocess.check_output(['git','show',rec['head']+':notes/400-remaining/collect.py'],cwd=ROOT)==collector
        original=rec.get('source','G4C.GL');digest=next(a['sha256'] for a in inventory if a['file']==original)
        assert rec['source_sha256']==digest==sha((ROOT/'.cache'/original).read_bytes())
        rows=[json.loads(line) for line in (folder/'steps.jsonl').read_text().splitlines()]
        assert len(rows)==rec['observations'];previous=None
        for idx,row in enumerate(rows,1):
            assert row['n']==idx and row['preceding']==previous
            assert sha((ROOT/row['file']).read_bytes())==row['sha256']
            assert not row['build_problems'];previous=row['sha256'];n+=1
        if 'resume' in rec:
            resume=rec['resume'];assert sha((ROOT/resume['file']).read_bytes())==resume['sha256']
            assert resume['verified_mounts']==[f"mount c {resume['game_dir']}",f"mount d {resume['workdir']}/dosclock"]
            assert (ROOT/'.cache/400-remaining'/folder.name/'preceding-driver-files/dosbox.conf').exists()
            old=(ROOT/'.cache/400-remaining'/folder.name/'preceding-driver-files/dosbox.conf').read_bytes()
            assert old==(folder/'preceding-dosbox.conf').read_bytes()
            assert [line for line in old.decode().splitlines() if line.startswith('mount ')]==resume['verified_mounts']
        else:
            assert any('Please enter name of saved game' in row['screen'] for row in rows)
            keys=[row['request']['keys'] for row in rows if isinstance(row['request'],dict) and 'keys' in row['request']]
            assert list(original[:-3].lower()) in keys
    delivery=json.loads((base/'delivery.json').read_text())
    assert delivery['covered']==['role2_corner','role2_space_CF3A','E022_E19F_nice_try']
    assert set(delivery['unavailable'])=={'role3_penalty','role4_free_kick','role5_goal_kick','E022_E062_no_player','EA09_EC60_vacancy'}
    rows=[json.loads(line) for line in (base/'native-r4/steps.jsonl').read_text().splitlines()]
    for item in delivery['inputs']:
        row=rows[item['step']-1];raw=(ROOT/row['file']).read_bytes()
        assert item['sha256']==row['sha256']==sha((ROOT/item['readback']).read_bytes())
        assert item['frame']==derive(raw)
        assert item['preceding_sha256']==row['preceding']
        assert item['preceding_sha256']==sha((ROOT/item['preceding_readback']).read_bytes())
    assert rows[87]['request']=={'keys':['space']}
    assert rows[88]['request']==rows[89]['request']=={'keys':['Return']}
    assert delivery['inputs'][1]['frame']['anchor']=='08DD far return 0791:CF3A'
    package=delivery['attempt_package']
    assert sha((ROOT/package['file']).read_bytes())==package['sha256']==sha((ROOT/package['readback']).read_bytes())
    from verify_core import check
    state=check(delivery['nice_try']);assert state==delivery['nice_try']['frame']
    print(f'PASS: {n} native observations / 4 native attempts + 17 core observations / 1 bounded attempt; corner, CF3A and E19F; all private readbacks verified; five cases remain unavailable')

if __name__=='__main__':main()
