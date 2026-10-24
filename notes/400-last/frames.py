"""Read-only original penalty/free-kick frames, F030/6D4E/6ECF/6F3E."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'runtime/driver')]
from original_match.image import Image
from emul.watched_match import cpu_state
def derive(raw):
    im=Image.from_savestate(raw);m=im.memory;r=cpu_state(raw);ds=im.DS*16;ss=r['SS']*16;sp=r['ESP']&65535
    w=lambda a:int.from_bytes(m[a:a+2],'little');sw=lambda a:w(ss+a)
    if r['CS']==0xF000:
        reads=[b for b in range(sp,min(sp+0x200,65530)) if sw(b+2)==0xCF3A and sw(b+4)==im.load+0x0791 and b<sw(b)<65530]
        assert len(reads)==1;bp=reads[0];site='0791:CF3A';anchor='live08DD frame in current BIOS read'
    else:
        assert r['CS']==im.load+0x214B and 0x1E09<=r['EIP']<0x1E85
        bp=r['EBP']&65535;site='CC2E delay before CC4F/CC54';anchor='saved CPU BP'
    chain=[];seen=set()
    while sp<=bp<65530 and bp not in seen:
        seen.add(bp);chain.append(dict(bp=bp,parent=sw(bp),return_offset=sw(bp+2)))
        if sw(bp+2)==0x6D74:break
        bp=sw(bp)
    assert chain[-1]['return_offset']==0x6D74
    if site!='0791:CF3A':
        assert [c['return_offset'] for c in chain[:3]]==[0xCC65,0xCED9,0x6D74]
        assert sw(chain[0]['bp']+4)==im.load+0x0791
    tbp=chain[-1]['bp'];role=m[ss+tbp+4];side=m[ss+tbp+6];assert role in (3,4) and side in (0,1)
    wrapper=sw(tbp);origin=sw(wrapper+2)
    assert origin=={3:0x6EEF,4:0x6F92}[role]
    assert (sw(wrapper+4)&255)=={3:10,4:11}[role] and (sw(wrapper+6)&255)==role and m[ss+wrapper+8]==side
    country=w(ds+0x9B34+2*side);far=lambda o:w(ds+o)+16*w(ds+o+2)
    name=far(0x9B68)+16*country;squad=far(0xA917)+191*country
    xi=[w(squad+2*n) for n in range(11)];slot=sw(tbp-5);pick=sw(tbp-7)
    assert 1<=slot<=11 and xi[slot-1]==pick and m[squad+0x2E]>0x80
    p=far(0xA91B)+20*pick;seg=r['CS'] if r['CS']==0xF000 else r['CS']-im.load
    return dict(cpu=f'{seg:04X}:{r["EIP"]:04X}',site=site,ss=r['SS'],sp=sp,anchor=anchor,chain=chain,role=role,side=side,
                restart_caller=f'0791:{origin:04X}',wrapper_bp=wrapper,
                country=country,country_name=bytes(m[name+1:name+1+m[name]]).decode('cp437'),highlight=slot,selection=pick,
                stored=w(ds+0x9976+10*side+2*role),eleven=xi,selected_status=m[p+0x10],selected_position=m[p+6],
                minute=w(ds+0x831F),rng_main=w(ds+0x7B62),rng_aux=w(ds+0x7B64),build_problems=im.build_problems())
