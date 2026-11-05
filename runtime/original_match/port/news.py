"""T122a: shared post-match news primitives.

[confirmed: F012/F025/F039; upstream7032ce40; named/seg_000E_01..04.c,
then code/seg_000E_01.asm 03C4-0A52, _02.asm 0A53-0CCC/1F4D-2013,
_03.asm 2E1F-2E93, _05.asm 3A5E-3AF0/4045-408A,
_06.asm 47E6-48D6]. Original calls, hidden string result pointers,
caller frames, returned AX/DX and draw order are retained. Other news
routines remain original until their own T122 slice.
"""
from . import Registry
from .contests import ss8, ss16, pop
from .geometry import cbw, mul
from .mem import s16
from .restarts import _end
from .runtime import Regs
from .setup import farg, rb, rw, w8
from .silent import _ds_far, country_of, save_ptr
from .route import near, far

PORTS = Registry('news', 'shared news formatting, waits, ratings and text helpers (T122a)')
PORTS.variant('crowd-draw-dropped', '045D: omit the conditional third RNG draw at04B2')
PORTS.variant('centering-width-minus-one', '03C4: center to width minus one')
M16 = 0xffff


def copy_string(mem, r, src, dest, limit, ret):
    r.es, r.di = src
    r.di = dest[1]
    r.ax = limit
    return (yield from far(mem, r, '23E4:0644', *src, *dest, r.ax, ret=ret))


def local_texts(mem, r, copies):
    for arg, local, ret in copies:
        src = farg(mem, r, arg)
        r = yield from copy_string(mem, r, src, (r.ss, (r.bp+local)&M16), 0x14, ret)
    return r


def heading(mem, r, row, seg, off, ret, set_ax=True):
    if set_ax:
        r.ax = row
    r.di = off
    return (yield from near(mem, r, 0x070B, row, seg, off, ret=ret))


@PORTS.port('000E:03C4', ret='ret 6')
def center_text(mem, variant):
    r=Regs(mem); r.enter(0x152)
    text=(r.bp-0x51)&M16; tmp=(r.bp-0x151)&M16
    src=farg(mem,r,6)
    r=yield from copy_string(mem,r,src,(r.ss,text),0x50,0x03DE)
    width=ss16(mem,r,r.bp+4)-int(variant=='centering-width-minus-one')
    while True:
        r.al=ss8(mem,r,text); r.ah=0
        if r.ax>=width: break
        # String producers leave their hidden result pointer below SP.
        r.di=tmp; r.push(r.ss); r.push(tmp); r.di=0x03C2
        r=yield from far(mem,r,'23E4:062A',mem.seg(0xE),r.di,ret=0x03F8)
        r.di=text
        r=yield from far(mem,r,'23E4:06B7',r.ss,text,ret=0x0402)
        off,seg=pop(mem,r),pop(mem,r)
        r=yield from copy_string(mem,r,(seg,off),(r.ss,text),0x50,0x0410)
        r.al=ss8(mem,r,text); r.ah=0
        if r.ax<width:
            r.di=tmp; r.push(r.ss); r.push(tmp); r.di=text
            r=yield from far(mem,r,'23E4:062A',r.ss,text,ret=0x042A)
            r.di=0x03C2
            r=yield from far(mem,r,'23E4:06B7',mem.seg(0xE),r.di,ret=0x0434)
            off,seg=pop(mem,r),pop(mem,r)
            r=yield from copy_string(mem,r,(seg,off),(r.ss,text),0x50,0x0442)
    dest=farg(mem,r,0xA)
    r=yield from copy_string(mem,r,(r.ss,text),dest,0x50,0x0457)
    return _end(r)


@PORTS.port('000E:045D', ret='ret 4')
def crowd_animation(mem, variant):
    r=Regs(mem); r.enter(8)
    for outer in range(1,51):
        r.local16(-2,outer)
        for inner in range(1,11):
            r.local16(-4,inner)
            r.ax=5
            r=yield from far(mem,r,'214B:06B1',r.ax,ret=0x0480)
            row=r.ax; r.local16(-6,row)
            r.ax=0x50
            r=yield from far(mem,r,'214B:06B1',r.ax,ret=0x048C)
            col=r.ax; r.local16(-8,col)
            r.ax=col<<1; r.cx=r.ax; r.ax=row; r.dx=0xA0; mul(r,r.dx)
            _ds_far(mem,r,0xA96A); r.di+=r.ax+r.cx
            if rb(mem,r,-0xA2)<7:
                if variant=='crowd-draw-dropped':
                    r.ax=1
                else:
                    r.ax=0xF
                    r=yield from far(mem,r,'214B:06B1',r.ax,ret=0x04B7)
                value=r.al; r.bx=(r.bx&0xff00)|value
                r.ax=col<<1; r.cx=r.ax; r.ax=row; r.dx=0xA0; mul(r,r.dx)
                _ds_far(mem,r,0xA96A); r.di+=r.ax+r.cx
                w8(mem,r,-0xA1,value,'000E:04D0')
        r.ax=ss16(mem,r,r.bp+6)<<1
        r=yield from far(mem,r,'214B:1E09',r.ax,ret=0x04E6)
    return _end(r)


@PORTS.port('000E:04F5', ret='ret 4')
def play_tune_part(mem, variant):
    r=Regs(mem); r.enter(2)
    r.al=ss8(mem,r,r.bp+6)
    mem.wds8(0x7968,r.al,'000E:04FE')
    r=yield from far(mem,r,'214B:1E75',ret=0x0506)
    for note in range(1,17):
        r.local16(-2,note)
        r=yield from far(mem,r,'214B:0723',ret=0x0515)
        if r.al: return _end(r)
        r.ax=3; r.push(r.ax); r.di=note<<1
        r.al=mem.ds8(r.di); r.ah=0; r.push(r.ax)
        r.di=note<<1; r.al=mem.ds8(r.di+1); r.ah=0
        second=pop(mem,r); mode=pop(mem,r)
        r=yield from far(mem,r,'214B:1EF1',mode,second,r.ax,ret=0x053C)
        r.di=note<<1; r.al=mem.ds8(r.di+1); r.ah=0
        r=yield from near(mem,r,0x045D,r.ax,ss16(mem,r,r.bp+4),ret=0x054E)
    r=yield from far(mem,r,'214B:1E8D',ret=0x0559)
    return _end(r)


@PORTS.port('000E:0572', ret='ret 2')
def news_celebration(mem, variant):
    r=Regs(mem); r.enter()
    r.di=0xA96A
    r=yield from far(mem,r,'214B:0329',mem.DS,0x5B94,mem.DS,r.di,ret=0x0584)
    parent=ss16(mem,r,r.bp+4); r.di=parent
    if ss8(mem,r,parent+6):
        r.al=0xF; colour=r.ax; r.di=0x055F; r.al=3; row=r.ax; r.al=0x20; col=r.ax; r.di=0xA96A
        r=yield from far(mem,r,'214B:02C8',colour,mem.seg(0xE),0x055F,row,col,mem.DS,r.di,ret=0x05A6)
    else:
        mem.wds16(0x7966,1,'000E:05A8'); r.ax=0
        r=yield from near(mem,r,0x04F5,r.ax,r.bp,ret=0x05B5)
        r.di=parent
        if ss8(mem,r,parent+4):
            r.ax=4
            r=yield from near(mem,r,0x04F5,r.ax,r.bp,ret=0x05C7)
            _ds_far(mem,r,0xA923)
            if rb(mem,r,0x40):
                r.ax=8
                r=yield from near(mem,r,0x04F5,r.ax,r.bp,ret=0x05DA)
        r=yield from far(mem,r,'214B:1E8D',ret=0x05DF)
    while True:
        r.ax=2
        r=yield from near(mem,r,0x045D,r.ax,r.bp,ret=0x05E7)
        r=yield from far(mem,r,'214B:0723',ret=0x05EC)
        if r.al: break
    return _end(r)


@PORTS.port('000E:0868', ret='ret 0xa')
def manager_quote(mem, variant):
    r=Regs(mem); r.enter(0x2A)
    r=yield from local_texts(mem,r,((8,-0x15,0x0881),(4,-0x2A,0x0894)))
    r.ax=3; r=yield from far(mem,r,'214B:06B1',r.ax,ret=0x089D)
    if r.ax in (1,2,3):
        off,ret={1:(0x083B,0x08AD),2:(0x084B,0x08BF),3:(0x0858,0x08D1)}[r.ax]
        r=yield from heading(mem,r,ss16(mem,r,r.bp+0xC),mem.seg(0xE),off,ret,set_ax=False)
    r=yield from heading(mem,r,ss16(mem,r,r.bp+0xC)+1,r.ss,(r.bp-0x15)&M16,0x08DE)
    if ss8(mem,r,r.bp-0x2A):
        r=yield from heading(mem,r,ss16(mem,r,r.bp+0xC)+2,r.ss,(r.bp-0x2A)&M16,0x08F3)
    return _end(r)


def parent_country(mem,r):
    r.di=ss16(mem,r,r.bp+4); r.ax=ss16(mem,r,r.di+8)
    return country_of(mem,r,r.ax)


def parent_fixture(mem,r,other=False):
    parent=ss16(mem,r,r.bp+4); side=ss8(mem,r,parent-1)
    r.al=int(side==0) if other else side; cbw(r); r.ax<<=1
    r.di=parent
    r.es,r.di=ss16(mem,r,parent+6),ss16(mem,r,parent+4)
    r.di+=r.ax
    return rw(mem,r,4)


@PORTS.port('000E:08F9', ret='ret 2')
def player_name(mem, variant):
    r=Regs(mem); r.enter(4)
    country=parent_country(mem,r); save_ptr(r,-4)
    parent=ss16(mem,r,r.bp+4); r.di=parent; r.ax=ss16(mem,r,parent-6)<<1
    r.es,r.di=country; r.di+=r.ax; r.ax=rw(mem,r,-2); r.dx=0xB; mul(r,r.dx)
    _ds_far(mem,r,0x9B6C); r.di+=r.ax; src=r.es,r.di
    dest=farg(mem,r,6); r=yield from copy_string(mem,r,src,dest,0xF,0x0944)
    return _end(r)


@PORTS.port('000E:094A', ret='ret 2')
def sent_off_name(mem, variant):
    r=Regs(mem); r.enter(6)
    country=parent_country(mem,r); save_ptr(r,-6)
    farg(mem,r,6); w8(mem,r,0,0,'000E:096B')
    for slot in range(1,21):
        r.local16(-2,slot); r.ax=6; r.push(r.ax)
        r.ax=slot<<1; r.es,r.di=country; r.di+=r.ax; word=rw(mem,r,-2)
        r.ax=word; r.dx=0x14; mul(r,r.dx); _ds_far(mem,r,0xA91B); r.di+=r.ax
        r.al=rb(mem,r,0x10); r.ah=0; bit=pop(mem,r)
        r=yield from far(mem,r,'214B:0C57',bit,r.ax,ret=0x09A2)
        if r.al:
            r.ax=slot<<1; r.es,r.di=country; r.di+=r.ax; r.ax=rw(mem,r,-2)
            r.dx=0xB; mul(r,r.dx); _ds_far(mem,r,0x9B6C); r.di+=r.ax; src=r.es,r.di
            dest=farg(mem,r,6); r=yield from copy_string(mem,r,src,dest,0xF,0x09CF)
    return _end(r)


@PORTS.port('000E:09DB', ret='ret 2')
def opponent_outclassed(mem, variant):
    r=Regs(mem); r.enter(2)
    parent=ss16(mem,r,r.bp+4); r.di=parent; r.al=int(ss8(mem,r,parent-1)==1); r.ah=0; r.push(r.ax)
    country=parent_fixture(mem,r,True)
    r=yield from far(mem,r,'1771:10E7',country,ret=0x0A19)
    r.ax+=2; r.dx=pop(mem,r); r.ax-=r.dx; r.push(r.ax)
    country=parent_fixture(mem,r)
    r=yield from far(mem,r,'1771:10E7',country,ret=0x0A3C)
    r.dx=pop(mem,r); r.al=int(s16(r.ax)>s16(r.dx)); r.local8(-1,r.al)
    return _end(r,value=True)


@PORTS.port('000E:0A53', ret='ret 2')
def own_side_competitive(mem, variant):
    r=Regs(mem); r.enter(2)
    country=parent_fixture(mem,r,True)
    r=yield from far(mem,r,'1771:10E7',country,ret=0x0A7E); r.push(r.ax)
    country=parent_fixture(mem,r)
    r=yield from far(mem,r,'1771:10E7',country,ret=0x0A9B)
    r.ax+=2; r.dx=r.ax; r.di=ss16(mem,r,r.bp+4)
    r.al=int(ss8(mem,r,r.di-1)==1); r.ah=0; r.ax+=r.dx; r.dx=pop(mem,r)
    r.al=int(s16(r.ax)>s16(r.dx)); r.local8(-1,r.al)
    return _end(r,value=True)


@PORTS.port('000E:0ACB', ret='ret 2')
def manager_name(mem, variant):
    r=Regs(mem); r.enter(0x100)
    r.di=(r.bp-0x100)&M16; r.push(r.ss); r.push(r.di)
    parent_country(mem,r); r.al=rb(mem,r,0x2E); r.ah=0
    r=yield from far(mem,r,'1771:0947',r.ax,ret=0x0AF6)
    src=(pop(mem,r),pop(mem,r)); dest=farg(mem,r,6)
    r=yield from copy_string(mem,r,(src[1],src[0]),dest,0xF,0x0B04)
    return _end(r)


def country_name(mem, other):
    r=Regs(mem); r.enter()
    if other: r.ax=parent_fixture(mem,r,True)
    else: r.di=ss16(mem,r,r.bp+4); r.ax=ss16(mem,r,r.di+8)
    r.cx=(r.cx&0xff00)|4; r.ax<<=4; _ds_far(mem,r,0x9B68); r.di+=r.ax
    src=r.es,r.di; dest=farg(mem,r,6)
    r=yield from copy_string(mem,r,src,dest,0xF,0x0B47 if other else 0x0B71)
    return _end(r)


@PORTS.port('000E:0B0A', ret='ret 2')
def opponent_name(mem, variant): return (yield from country_name(mem,True))


@PORTS.port('000E:0B4D', ret='ret 2')
def own_name(mem, variant): return (yield from country_name(mem,False))


@PORTS.port('000E:0B77', ret='ret 2')
def manager_sack_score(mem, variant):
    r=Regs(mem); r.enter(6)
    country=parent_country(mem,r); save_ptr(r,-6)
    _ds_far(mem,r,0xA923)
    eligible=rw(mem,r,0x38)>=2
    if eligible:
        parent=ss16(mem,r,r.bp+4); r.di=parent
        r.es,r.di=ss16(mem,r,parent+6),ss16(mem,r,parent+4)
        eligible=rb(mem,r,2)!=1
    if eligible:
        r=yield from far(mem,r,'1771:59D8',ret=0x0BB3)
        if r.al:
            r.es,r.di=country; r.al=rb(mem,r,0x2E); r.ah=0; r.ax-=0x80
            _ds_far(mem,r,0xA923); r.di+=r.ax
            eligible=rb(mem,r,1)==0
        if eligible:
            r.es,r.di=country; eligible=rb(mem,r,0xBE)==0
    if eligible:
        r.es,r.di=country; r.al=rb(mem,r,0x2E); r.ah=0; r.dx=3; mul(r,r.dx)
        _ds_far(mem,r,0xA91F); r.di+=r.ax; r.al=rb(mem,r,2); cbw(r)
    else: r.ax=0
    r.local16(-2,r.ax)
    return _end(r,value=True)


@PORTS.port('000E:0C3A', ret='ret 2')
def red_card_headline(mem, variant):
    r=Regs(mem); r.enter(0x200); r.ax=3
    r=yield from far(mem,r,'214B:06B1',r.ax,ret=0x0C4A)
    choice=r.ax
    if choice in (1,2,3):
        first={1:0x0C07,2:0x0C17,3:0x0C2D}[choice]; r.di=first; r.push(mem.seg(0xE)); r.push(first)
        if choice==2:
            r.di=(r.bp-0x200)&M16; r.push(r.ss); r.push(r.di); r.di=0x0C27
            r=yield from far(mem,r,'23E4:062A',mem.seg(0xE),r.di,ret=0x0C88)
        r.di=(r.bp-0x100)&M16; r.push(r.ss); r.push(r.di)
        parent=ss16(mem,r,r.bp+4); r.di=parent
        r=yield from near(mem,r,0x094A,ss16(mem,r,parent+4),ret={1:0x0C64,2:0x0C98,3:0x0CC1}[choice])
        if choice==2:
            off,seg=pop(mem,r),pop(mem,r)
            r=yield from far(mem,r,'23E4:06B7',seg,off,ret=0x0C9D)
        off,seg=pop(mem,r),pop(mem,r); firstoff,firstseg=pop(mem,r),pop(mem,r)
        r.di=0x0C0E if choice==1 else 0x0C2C
        r=yield from near(mem,r,0x062F,firstseg,firstoff,seg,off,mem.seg(0xE),r.di,
                          ret={1:0x0C6C,2:0x0CA5,3:0x0CC9}[choice])
    return _end(r)


@PORTS.port('000E:1F4D', ret='ret 2')
def own_stats_ahead(mem, variant):
    r=Regs(mem); r.enter(2)
    parent=ss16(mem,r,r.bp+4); side=ss8(mem,r,parent-1); other=int(side==0)
    def stat(k,off): return mem.ds8((cbw_value(k)*10+off)&M16)
    r.bx=stat(side,0x7B83); r.cx=stat(other,0x7B82); r.ax=stat(other,0x7B7E)+r.cx+r.bx; r.push(r.ax)
    r.bx=stat(other,0x7B83); r.cx=stat(side,0x7B82)
    r.ax=side; cbw(r); r.dx=10; mul(r,r.dx); r.di=r.ax
    r.al=mem.ds8(r.di+0x7B7E); r.ah=0; r.ax+=r.cx+r.bx; r.dx=pop(mem,r)
    r.al=int(s16(r.ax)>s16(r.dx)); r.local8(-1,r.al)
    return _end(r,value=True)


def cbw_value(value): return value if value<128 else value-256


@PORTS.port('000E:2E1F', ret='ret 0xe')
def result_headings(mem, variant):
    r=Regs(mem); r.enter(0x40)
    r=yield from local_texts(mem,r,((0xE,-0x15,0x2E38),(0xA,-0x2A,0x2E4B),(6,-0x3F,0x2E5E)))
    for row,local,ret in ((1,-0x15,0x2E6A),(2,-0x2A,0x2E7C),(3,-0x3F,0x2E8E)):
        if row==1 or ss8(mem,r,r.bp+local):
            r=yield from heading(mem,r,row,r.ss,(r.bp+local)&M16,ret)
    return _end(r)


@PORTS.port('000E:3A5E', ret='ret 6')
def fan_quote(mem, variant):
    r=Regs(mem); r.enter(0x116)
    r=yield from local_texts(mem,r,((6,-0x15,0x3A78),))
    r.ax=2; r=yield from far(mem,r,'214B:06B1',r.ax,ret=0x3A81)
    if r.ax in (1,2,3):
        off,ret={1:(0x3A32,0x3A92),2:(0x3A3C,0x3AA5),3:(0x3A4C,0x3AB8)}[r.ax]
        r=yield from heading(mem,r,6,mem.seg(0xE),off,ret)
    r.ax=7; r.push(r.ax); r.di=(r.bp-0x115)&M16; r.push(r.ss); r.push(r.di); r.di=0x3A5C
    r=yield from far(mem,r,'23E4:062A',mem.seg(0xE),r.di,ret=0x3ACC)
    r.di=(r.bp-0x15)&M16
    r=yield from far(mem,r,'23E4:06B7',r.ss,r.di,ret=0x3AD6)
    r.di=0x3A5C
    r=yield from far(mem,r,'23E4:06B7',mem.seg(0xE),r.di,ret=0x3AE0)
    off,seg,row=pop(mem,r),pop(mem,r),pop(mem,r)
    r=yield from near(mem,r,0x070B,row,seg,off,ret=0x3AE3)
    r.di=ss16(mem,r,r.bp+4); r.flush(); mem.w8(mem.addr(r.ss,r.di-1),1,'000E:3AE6')
    return _end(r)


@PORTS.port('000E:4045', ret='ret 0xa')
def manager_quote_at_parent_row(mem, variant):
    r=Regs(mem); r.enter(0x2A)
    r=yield from local_texts(mem,r,((0xA,-0x15,0x405E),(6,-0x2A,0x4071)))
    parent=ss16(mem,r,r.bp+4); r.di=parent; row=ss16(mem,r,parent+6)
    r.di=(r.bp-0x2A)&M16
    r=yield from near(mem,r,0x0868,row,r.ss,(r.bp-0x15)&M16,r.ss,r.di,ret=0x4085)
    return _end(r)


@PORTS.port('000E:47E6', ret='ret 0xa')
def board_quote(mem, variant):
    r=Regs(mem); r.enter(0x2A)
    r=yield from local_texts(mem,r,((0xA,-0x15,0x47FF),(6,-0x2A,0x4812)))
    r=yield from far(mem,r,'214B:06FA',ret=0x4817)
    if r.al in (0,1):
        off,ret=(0x47BC,0x4827) if r.al==0 else (0x47D1,0x4839)
        r=yield from heading(mem,r,10,mem.seg(0xE),off,ret)
    r=yield from heading(mem,r,11,r.ss,(r.bp-0x15)&M16,0x4845)
    if ss8(mem,r,r.bp-0x2A):
        r=yield from heading(mem,r,12,r.ss,(r.bp-0x2A)&M16,0x4857)
    r.di=ss16(mem,r,r.bp+4); r.flush(); mem.w8(mem.addr(r.ss,r.di-1),1,'000E:485A')
    return _end(r)


@PORTS.port('000E:4865', ret='ret 2')
def excessive_fouls(mem, variant):
    r=Regs(mem); r.enter(2)
    for off,limit in ((0x7B84,10),(0x7B86,1),(0x7B85,2)):
        r.di=ss16(mem,r,r.bp+4); r.di=ss16(mem,r,r.di+4); r.di=ss16(mem,r,r.di+4)
        r.al=ss8(mem,r,r.di-1); cbw(r); r.dx=10; mul(r,r.dx); r.di=r.ax
        if mem.ds8((r.di+off)&M16)>limit:
            r.al=1; break
    else: r.al=0
    r.local8(-1,r.al)
    return _end(r,value=True)
