"""Read-only verification of the actual E19F stop, including UnknownScreen capture."""
import hashlib,json,subprocess,zipfile,zlib
from pathlib import Path
from frames import ROOT,Image
def sha(b):return hashlib.sha256(b).hexdigest()

def unpack_core(raw):
    assert raw[:4]==b'G2C1';n=int.from_bytes(raw[4:8],'little')
    meta=json.loads(raw[8:8+n]);memory=zlib.decompress(raw[8+n:])
    return meta,memory

def check(delivery):
    folder=ROOT/'notes/400-remaining/core-r1';rec=json.loads((folder/'record.json').read_text())
    assert rec['status']=='aborted' and 'UnknownScreen' in rec['error']
    assert rec['elapsed_s']<rec['bound_s']==120
    assert sha((folder/'collector.py').read_bytes())==rec['collector_sha256']
    assert subprocess.check_output(['git','show',rec['head']+':notes/400-remaining/collect_core.py'],cwd=ROOT)==(folder/'collector.py').read_bytes()
    for path,digest in rec['core_files'].items():
        assert sha((ROOT/'.cache/400-nice-try/core-source'/path).read_bytes())==digest
    source=ROOT/'.cache/400-nice-try/source.g2core';assert sha(source.read_bytes())==rec['source_sha256']
    rows=[json.loads(line) for line in (folder/'steps.jsonl').read_text().splitlines()]
    assert len(rows)==rec['observations']==17
    for row in rows:
        for key in ('core','machine'):
            item=row[key]
            if item:assert sha((ROOT/item['file']).read_bytes())==item['sha256']
    assert rec['keys']==[32,171]+[177]*10+[13,177,13]
    pre=rows[-2];last=rows[-1]
    assert pre['core']==rec['pre_second_enter'] and last['request']=={'key':13,'error':True}
    assert last['site']=='214B:098A' and last['kind'] is None and 'Nice try' in last['text']
    raw=(ROOT/pre['core']['file']).read_bytes();meta,mem=unpack_core(raw)
    with zipfile.ZipFile(ROOT/last['machine']['file']) as z:
        after=z.read('memory.bin');snap=json.loads(z.read('registers.json'))
    image=Image(bytes.fromhex(meta['header'])+after);assert not image.build_problems()
    r=snap['regs'];ds=image.DS*16;ss=r['SS']*16;sp=r['ESP']&65535
    w=lambda a:int.from_bytes(after[a:a+2],'little');sw=lambda o:w(ss+o)
    assert (r['CS']-image.load,r['EIP'])==(0x214B,0x08DD)
    assert (sw(sp),sw(sp+2)-image.load)==(0x098A,0x214B)
    bp=r['EBP'];returns=[]
    for ret,seg in ((0x054E,0x214B),(0x1793,0x214B),(0xE19F,0x0791)):
        assert (sw(bp+2),sw(bp+4)-image.load)==(ret,seg)
        returns.append(dict(bp=bp,parent=sw(bp),return_to=f'{seg:04X}:{ret:04X}'));bp=sw(bp)
    assert sw(bp+2)==0xE693  # E022 near return to E44F's caller.
    parent=sw(bp);assert sw(bp+4)==parent and sw(parent+6)==rec['country']==7
    far=lambda o:w(ds+o)+16*w(ds+o+2)
    squad=far(0xA917)+7*191;players=far(0xA91B)
    assert w(squad+20)==125 and w(squad+22)==132
    assert after[players+20*125+0x10]==32 and after[players+20*132+0x10]==0
    assert after[players+20*132+0x0E]>0
    # Refusal preserves the squad and substitution budget; only original menu/keyboard activity ran.
    assert mem[squad:squad+40]==after[squad:squad+40]
    assert mem[ds+0x9B3A:ds+0x9B3C]==after[ds+0x9B3A:ds+0x9B3C]
    for item in (delivery['before'],delivery['at_warning'],delivery['package']):
        assert sha((ROOT/item['file']).read_bytes())==item['sha256']==sha((ROOT/item['readback']).read_bytes())
    assert delivery['source_sha256']==rec['source_sha256']
    return dict(site=last['site'],cpu='214B:08DD',frames=returns,country=7,outgoing=125,outgoing_slot=11,outgoing_status=32,incoming=132,incoming_slot=12,incoming_status=0,incoming_energy=after[players+20*132+0x0E],eleven=[w(squad+2*i) for i in range(11)],subs_left=list(after[ds+0x9B3A:ds+0x9B3C]),minute=w(ds+0x831F))
