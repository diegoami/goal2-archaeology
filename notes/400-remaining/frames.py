"""Read-only T88 frame derivation. See seg_0791_20.asm and seg_214B_02.asm.

The native collector's diagnostic `takers` array used whole words for byte
parameters. The immutable raw arrays stay unchanged; derive the actual low bytes here.
"""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/driver')]
from original_match.image import Image
from emul.watched_match import cpu_state

def derive(raw):
    image=Image.from_savestate(raw);r=cpu_state(raw);m=image.memory
    ds=image.DS*16;ss=r['SS']*16;sp=r['ESP']&65535
    w=lambda a:int.from_bytes(m[a:a+2],'little')
    sw=lambda o:w(ss+o)
    # CF3A's read frame: 08DD pushes BP, saves old BP, and far-returns to CF3A.
    reads=[bp for bp in range(sp,65530) if sw(bp+2)==0xCF3A and sw(bp+4)==image.load+0x0791 and bp<sw(bp)<65530]
    chain=[]
    if r['CS']==0xF000:
        assert len(reads)==1,'must have exactly one live CF3A read frame'
        bp=reads[0];anchor='08DD far return 0791:CF3A'
    else:
        bp=r['EBP']&65535;anchor='saved CPU EBP in original delay'
    seen=set()
    while sp<=bp<65530 and bp not in seen:
        seen.add(bp);chain.append(dict(bp=bp,parent=sw(bp),return_offset=sw(bp+2)))
        if sw(bp+2)==0x6D74:break
        bp=sw(bp)
    assert chain and chain[-1]['return_offset']==0x6D74,'CC7B near caller absent from live chain'
    tbp=chain[-1]['bp'];role=m[ss+tbp+4];side=m[ss+tbp+6]
    assert role==2 and side in (0,1)
    if reads:
        assert chain[0]['bp']==reads[0] and sw(reads[0]+4)==image.load+0x0791
    else:
        assert r['CS']==image.load+0x214B and 0x1E2B<=r['EIP']<=0x1E8D
        assert [f['return_offset'] for f in chain[:3]]==[0xCC65,0xCED9,0x6D74]
        assert sw(chain[0]['bp']+4)==image.load+0x0791
    country=w(ds+0x9B34+2*side)
    far=lambda o:w(ds+o)+16*w(ds+o+2)
    names=far(0x9B68)+16*country
    name=bytes(m[names+1:names+1+m[names]]).decode('cp437')
    squad=far(0xA917)+191*country
    eleven=[w(squad+2*n) for n in range(11)]
    highlight=sw(tbp-5);pick=sw(tbp-7)
    assert 1<=highlight<=11 and eleven[highlight-1]==pick
    player=far(0xA91B)+20*pick
    manager=m[squad+0x2E];assert manager>=0x80
    cpu_segment=r['CS'] if r['CS']==0xF000 else (r['CS']-image.load)&65535
    return dict(cpu=f"{cpu_segment:04X}:{r['EIP']:04X}",ss=r['SS'],sp=sp,anchor=anchor,chain=chain,
                role=role,side=side,country=country,country_name=name,highlight=highlight,selection=pick,
                stored_pick=w(ds+0x9976+10*side+2*role),eleven=eleven,minute=w(ds+0x831F),
                manager_byte=manager,selected_status=m[player+0x10],selected_position=m[player+6],
                rng_main=w(ds+0x7B62),rng_aux=w(ds+0x7B64),build_problems=image.build_problems())
