"""Offline integrity and live original-poll verification for exact-CPU research replays."""
import hashlib,json,subprocess,zipfile,zlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/driver')]
from original_match.image import Image
def sha(b):return hashlib.sha256(b).hexdigest()
def machine(path):
    with zipfile.ZipFile(path) as z:return z.read('memory.bin'),json.loads(z.read('registers.json'))
def target(path):
    mem,s=machine(path);r=s['regs'];load=s['load'];ss=r['SS']*16;ds=(load+0x2581)*16;sp=r['ESP']&65535
    im=Image(bytes.fromhex(s['memory_header'])+mem);assert not im.build_problems()
    w=lambda a:int.from_bytes(mem[a:a+2],'little');sw=lambda o:w(ss+o)
    site=f'{sw(sp+2)-load:04X}:{sw(sp):04X}';bp=r['EBP']&65535;chain=[]
    if (r['CS']-load,r['EIP'])==(0x214B,0x0723):
        assert site in ('0791:CC54','0791:CEDE')
        if site=='0791:CC54':
            assert sw(bp+2)==0xCED9;chain.append(dict(bp=bp,parent=sw(bp),near_return='CED9'));bp=sw(bp)
    else:assert (r['CS']-load,r['EIP'],site)==(0x214B,0x08DD,'0791:CF3A')
    assert sw(bp+2)==0x6D74;role=mem[ss+bp+4];side=mem[ss+bp+6];assert role in (3,4) and side in (0,1)
    chain.append(dict(bp=bp,parent=sw(bp),near_return='6D74'));wrapper=sw(bp);origin=sw(wrapper+2)
    assert origin=={3:0x6EEF,4:0x6F92}[role]
    assert sw(wrapper+4)&255=={3:10,4:11}[role] and sw(wrapper+6)&255==role and mem[ss+wrapper+8]==side
    far=lambda o:w(ds+o)+16*w(ds+o+2)
    country=w(ds+0x9B34+side*2);cs=far(0xA917)+191*country;xi=[w(cs+2*n) for n in range(11)]
    slot=sw(bp-5);pick=sw(bp-7);assert 1<=slot<=11 and xi[slot-1]==pick and mem[cs+46]>128
    return dict(cpu=f'{r["CS"]-load:04X}:{r["EIP"]:04X}',site=site,ss=r['SS'],sp=sp,chain=chain,wrapper_bp=wrapper,restart_caller=f'0791:{origin:04X}',role=role,side=side,country=country,highlight=slot,selection=pick,stored=w(ds+0x9976+10*side+2*role),eleven=xi,minute=w(ds+0x831F),rng_main=w(ds+0x7B62),rng_aux=w(ds+0x7B64))
def records():
    results={}
    for folder in sorted((ROOT/'notes/400-last').glob('uc-r*')):
        if not folder.is_dir():continue
        rec=json.loads((folder/'record.json').read_text());src=json.loads((folder/'source.json').read_text());code=(folder/'collector.py').read_bytes()
        assert sha(code)==rec['collector_sha256']==src['collector_sha256']
        assert subprocess.check_output(['git','show',rec['head']+':notes/400-last/collect_unicorn.py'],cwd=ROOT)==code
        assert sha((ROOT/rec['source']).read_bytes())==rec['source_sha256']
        assert rec['host_alias_roles']==[2,5] and rec['initial_import']['cpu_unchanged'] and rec['initial_import']['game_memory_unchanged']
        for name,digest in rec['runtime_files'].items():assert sha((ROOT/'.cache/400-nice-try/core-source'/name).read_bytes())==digest
        rows=[json.loads(l) for l in (folder/'steps.jsonl').read_text().splitlines()];assert len(rows)==rec['observations']
        for n,row in enumerate(rows,1):
            assert row['n']==n
            for key in ('core','machine'):
                item=row[key]
                if item:assert sha((ROOT/item['file']).read_bytes())==item['sha256']
            memory,meta=machine(ROOT/row['machine']['file']);assert meta['regs']==row['regs'] and meta['load']==row['load']
            assert not Image(bytes.fromhex(meta['memory_header'])+memory).build_problems()
        results[folder.name]=(rec,rows)
    return results
