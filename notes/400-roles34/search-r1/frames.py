"""Read-only T131 frame derivation for a kept Core state, no goal2 import and no guest instruction executed.

Reads the memory and registers of a `.g2core` (goal2 `Core.save`, magic G2C1) or of a `.ucstate` (a zip of
memory.bin and registers.json) and derives the live CC7B choose_captain_or_taker frame the way
notes/400-remaining/frames.py does for a DOSBox state: role and side are BYTE arguments (their high bytes are
scratch), the highlight is the word at [bp-5], the current pick the word at [bp-7], and the stored pick the word
DS:9976 + 2*role + 10*side. The live BP chain is followed from the saved BP; BIOS-like zero frames are not game
frames.
"""
import json,zlib,zipfile,io
GOAL_DS_PARAGRAPH=0x2581      # static/goal-exe/README.md; goal2/engine/original_match/image.py
MAGIC=b'G2C1'
TEAMS=0x9B34                  # team 0's country DS:9B34, team 1's DS:9B36 (F029)
MINUTE=0x831F
SEEDS=(0x7B62,0x7B64)

def read_g2core(raw):
    assert raw[:4]==MAGIC
    n=int.from_bytes(raw[4:8],'little');meta=json.loads(raw[8:8+n]);body=zlib.decompress(raw[8+n:])
    return meta,body

def read_ucstate(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        memory=z.read('memory.bin');reg=json.loads(z.read('registers.json'))
    return dict(load=reg['load'],regs=reg['regs']),memory

def derive(memory,load,regs):
    """The live CC7B frame, or raises AssertionError naming what is missing."""
    ds=(load+GOAL_DS_PARAGRAPH)*16;ss=regs['SS']*16;sp=regs['ESP']&0xFFFF
    w=lambda a:int.from_bytes(memory[a:a+2],'little')
    sw=lambda o:w(ss+(o&0xFFFF))
    site='%04X:%04X'%((sw(sp+2)-load)&0xFFFF,sw(sp))       # where the original reads or polls, as the listing writes it
    bp=regs['EBP']&0xFFFF;chain=[]
    for _ in range(16):
        chain.append(dict(bp=bp,parent=sw(bp),return_offset=sw(bp+2),return_segment=(sw(bp+4)-load)&0xFFFF))
        if sw(bp+2)==0x6D74:break
        nxt=sw(bp)
        assert bp<nxt<0xFFF0,'the live BP chain ended before a frame returning to 6D74'
        bp=nxt
    assert chain[-1]['return_offset']==0x6D74,'CC7B near caller 6D74 absent from the live chain'
    tbp=chain[-1]['bp'];role=memory[ss+tbp+4];side=memory[ss+tbp+6]
    country=w(ds+TEAMS+2*side);other=w(ds+TEAMS+2*(1-side))
    far=lambda o:w(ds+o)+16*w(ds+o+2)
    squad=far(0xA917)+191*country
    eleven=[w(squad+2*n) for n in range(11)]
    highlight=sw(tbp-5);pick=sw(tbp-7)
    players=far(0xA91B)
    names=far(0x9B68)
    cname=lambda c:bytes(memory[names+16*c+1:names+16*c+1+memory[names+16*c]]).decode('cp437')
    return dict(site=site,cpu='%04X:%04X'%((regs['CS']-load)&0xFFFF if regs['CS']!=0xF000 else 0xF000,regs['EIP']&0xFFFF),
                ss=regs['SS'],sp=sp,chain=chain,role=role,side=side,country=country,country_name=cname(country),
                opponent=other,opponent_name=cname(other),highlight=highlight,pick=pick,
                stored_pick=w(ds+0x9976+10*side+2*role),eleven=eleven,
                pick_in_eleven=1<=highlight<=11 and eleven[highlight-1]==pick,
                pick_status=memory[players+20*pick+0x10] if pick<3061 else None,
                pick_position=memory[players+20*pick+6] if pick<3061 else None,
                manager_byte=memory[squad+0x2E],minute=w(ds+MINUTE),
                rng_main=w(ds+SEEDS[0]),rng_aux=w(ds+SEEDS[1]))
