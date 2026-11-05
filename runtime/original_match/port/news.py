"""T122a–c: shared post-match news primitives and result text.

[confirmed: F012/F025/F039; upstream7032ce40; named/seg_000E_01..04.c,
then code/seg_000E_01.asm 03C4-0A52, _02.asm 0A53-0CCC/11D9-1F4C, _03.asm 1F4D-2013,
_04.asm 2E1F-2E93, _05.asm 3A5E-3AF0/4045-408A,
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

PORTS = Registry('news', 'shared news formatting, waits, ratings and result text (T122a–c)')
PORTS.variant('crowd-draw-dropped', '045D: omit the conditional third RNG draw at04B2')
PORTS.variant('centering-width-minus-one', '03C4: center to width minus one')
PORTS.variant('result-draw-dropped', '11D9: omit a direct result-column RNG draw')
PORTS.variant('result-text-inverted', '11D9 at1213: exchange winning and non-winning text branches')
PORTS.variant('secondary-draw-dropped', '26F2: omit one direct result-column RNG draw')
PORTS.variant('secondary-text-byte-flipped', '26F2 at274D: flip one country-name buffer byte')
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


def _result_call(mem, r, variant, target, words, ret, far):
    """11D9's arguments have already been pushed in listing order.

    Consume only the callee's declared words. Hidden string-result pointers stay
    below SP, exactly as their Pascal producers' ret/retf leaves them.
    """
    values = [pop(mem, r) for _ in range(words)]
    if variant == "result-draw-dropped" and target == "214B:06B1":
        r.ax = 1
        return r
    r.store(stack=True)
    from .guest import call
    yield call(target, *reversed(values), ret_to=f'000E:{ret:04X}', far=far)
    return Regs(mem, resumed=True)


@PORTS.port('000E:11D9', ret='ret 2')
def result_column(mem, variant):
    """T122b [confirmed: F039; code/seg_000E_02.asm11D9-1F4C].

    Structured transcription of the listing's acyclic branches, with shared
    suffixes factored into private generator regions named by listing offset.
    There is no instruction decoder or runtime dispatch/listing dependency.
    Each statement's comment is its original offset. Signed branches, temporary
    Pascal strings, caller frames and the real call return addresses stay exact.
    """
    r = Regs(mem)
    r.enter(0x308)
    r = yield from _result_at_11e0(mem, r, variant)
    return _end(r)


def _result_at_11e0(mem, r, variant):
    r.di = ss16(mem, r, r.bp + 4)  # 11E0
    r.es, r.di = ss16(mem, r, r.di + 4 + 2), ss16(mem, r, r.di + 4)  # 11E3
    r.local16(-4, r.di)  # 11E7
    r.local16(-2, r.es)  # 11EA
    r.di = ss16(mem, r, r.bp + 4)  # 11ED
    r.ax = ss16(mem, r, r.di + 8)  # 11F0
    r.dx = 0xbf  # 11F4
    mul(r, r.dx)  # 11F7
    r.es, r.di = mem.ds16((0xa917 + 2) & M16), mem.ds16((0xa917) & M16)  # 11F9
    r.di += r.ax  # 11FD
    r.local16(-8, r.di)  # 11FF
    r.local16(-6, r.es)  # 1202
    r.es, r.di = ss16(mem, r, r.bp - 4 + 2), ss16(mem, r, r.bp - 4)  # 1205
    r.al = mem.u8(mem.addr(r.es, r.di + 3))  # 1208
    r.di = ss16(mem, r, r.bp + 4)  # 120C
    _left, _right = r.al, ss8(mem, r, r.di - 1)  # 120F
    if (_left == _right) != (variant == "result-text-inverted"):  # 1213
        r.es, r.di = ss16(mem, r, r.bp - 4 + 2), ss16(mem, r, r.bp - 4)  # 1218
        r.al = mem.u8(mem.addr(r.es, r.di + 2))  # 121B
        _left, _right = r.al, 0xcb  # 121F
        if _left != _right:  # 1221
            _left, _right = r.al, 0x67  # 1249
            if _left != _right:  # 124B
                _left, _right = r.al, 0xc9  # 1262
                if _left != _right:  # 1264
                    _left, _right = r.al, 0x65  # 127B
                    if _left != _right:  # 127D
                        _left, _right = r.al, 0xc8  # 12B6
                        if _left != _right:  # 12B8
                            _left, _right = r.al, 8  # 12CF
                            if _left != _right:  # 12D1
                                r.di = ss16(mem, r, r.bp + 4)  # 12EF
                                r.es, r.di = ss16(mem, r, r.di + 4 + 2), ss16(mem, r, r.di + 4)  # 12F2
                                r.push(r.es)  # 12F6
                                r.push(r.di)  # 12F7
                                r = yield from _result_call(mem, r, variant, '1771:5C60', 2, 0x12FD, far=True)  # 12F8
                                _left, _right = r.ax, 3  # 12FD
                                if _left >= _right:  # 1300
                                    return (yield from _result_at_131f(mem, r, variant))
                                else:
                                    r.di = ss16(mem, r, r.bp + 4)  # 1302
                                    r.al = ss8(mem, r, r.di - 1)  # 1305
                                    cbw(r)  # 1309
                                    r.dx = 0xa  # 130A
                                    mul(r, r.dx)  # 130D
                                    r.di = r.ax  # 130F
                                    _left, _right = mem.ds8((r.di + 0x7b86) & M16), 0  # 1311
                                    if _left <= _right:  # 1316
                                        return (yield from _result_at_131f(mem, r, variant))
                                    else:
                                        r.push(r.bp)  # 1318
                                        r = yield from _result_call(mem, r, variant, '000E:0C3A', 1, 0x131C, far=False)  # 1319
                            else:
                                r.di = r.bp - 0x108  # 12D3
                                r.push(r.ss)  # 12D7
                                r.push(r.di)  # 12D8
                                r.push(ss16(mem, r, r.bp + 4))  # 12D9
                                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x12DF, far=False)  # 12DC
                                r.di = 0xd35  # 12DF
                                r.push(mem.seg(0xE))  # 12E2
                                r.push(r.di)  # 12E3
                                r.di = 0xd0a  # 12E4
                                r.push(mem.seg(0xE))  # 12E7
                                r.push(r.di)  # 12E8
                                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x12EC, far=False)  # 12E9
                        else:
                            r.di = 0xd28  # 12BA
                            r.push(mem.seg(0xE))  # 12BD
                            r.push(r.di)  # 12BE
                            r.di = 0xd0a  # 12BF
                            r.push(mem.seg(0xE))  # 12C2
                            r.push(r.di)  # 12C3
                            r.di = 0xd0a  # 12C4
                            r.push(mem.seg(0xE))  # 12C7
                            r.push(r.di)  # 12C8
                            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x12CC, far=False)  # 12C9
                    else:
                        r.di = r.bp - 0x108  # 127F
                        r.push(r.ss)  # 1283
                        r.push(r.di)  # 1284
                        r.push(ss16(mem, r, r.bp + 4))  # 1285
                        r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x128B, far=False)  # 1288
                        r.di = 0xd23  # 128B
                        r.push(mem.seg(0xE))  # 128E
                        r.push(r.di)  # 128F
                        r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x1295, far=True)  # 1290
                        r.di = r.bp - 0x208  # 1295
                        r.push(r.ss)  # 1299
                        r.push(r.di)  # 129A
                        r.push(ss16(mem, r, r.bp + 4))  # 129B
                        r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x12A1, far=False)  # 129E
                        r.di = 0xd26  # 12A1
                        r.push(mem.seg(0xE))  # 12A4
                        r.push(r.di)  # 12A5
                        r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x12AB, far=True)  # 12A6
                        r.di = 0xd0a  # 12AB
                        r.push(mem.seg(0xE))  # 12AE
                        r.push(r.di)  # 12AF
                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x12B3, far=False)  # 12B0
                else:
                    r.di = 0xd0b  # 1266
                    r.push(mem.seg(0xE))  # 1269
                    r.push(r.di)  # 126A
                    r.di = 0xd0b  # 126B
                    r.push(mem.seg(0xE))  # 126E
                    r.push(r.di)  # 126F
                    r.di = 0xd17  # 1270
                    r.push(mem.seg(0xE))  # 1273
                    r.push(r.di)  # 1274
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1278, far=False)  # 1275
            else:
                r.di = 0xcf4  # 124D
                r.push(mem.seg(0xE))  # 1250
                r.push(r.di)  # 1251
                r.di = 0xcff  # 1252
                r.push(mem.seg(0xE))  # 1255
                r.push(r.di)  # 1256
                r.di = 0xd0a  # 1257
                r.push(mem.seg(0xE))  # 125A
                r.push(r.di)  # 125B
                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x125F, far=False)  # 125C
        else:
            r.di = 0xccf  # 1223
            r.push(mem.seg(0xE))  # 1226
            r.push(r.di)  # 1227
            r.di = r.bp - 0x108  # 1228
            r.push(r.ss)  # 122C
            r.push(r.di)  # 122D
            r.push(ss16(mem, r, r.bp + 4))  # 122E
            r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x1234, far=False)  # 1231
            r.di = 0xce0  # 1234
            r.push(mem.seg(0xE))  # 1237
            r.push(r.di)  # 1238
            r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x123E, far=True)  # 1239
            r.di = 0xce4  # 123E
            r.push(mem.seg(0xE))  # 1241
            r.push(r.di)  # 1242
            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1246, far=False)  # 1243
        return (yield from _result_at_19c9(mem, r, variant))
    else:
        r.es, r.di = ss16(mem, r, r.bp - 4 + 2), ss16(mem, r, r.bp - 4)  # 19CC
        r.al = mem.u8(mem.addr(r.es, r.di + 2))  # 19CF
        _left, _right = r.al, 0xcb  # 19D3
        if _left != _right:  # 19D5
            _left, _right = r.al, 0x67  # 19EC
            if _left != _right:  # 19EE
                _left, _right = r.al, 0xc9  # 1A16
                if _left == _right:  # 1A18
                    return (yield from _result_at_1a22(mem, r, variant))
                else:
                    _left, _right = r.al, 0xc8  # 1A1A
                    if _left == _right:  # 1A1C
                        return (yield from _result_at_1a22(mem, r, variant))
                    else:
                        _left, _right = r.al, 8  # 1A1E
                        if _left != _right:  # 1A20
                            _left, _right = r.al, 0x65  # 1A37
                            if _left != _right:  # 1A39
                                r.di = ss16(mem, r, r.bp + 4)  # 1A57
                                r.es, r.di = ss16(mem, r, r.di + 4 + 2), ss16(mem, r, r.di + 4)  # 1A5A
                                r.push(r.es)  # 1A5E
                                r.push(r.di)  # 1A5F
                                r = yield from _result_call(mem, r, variant, '1771:5C60', 2, 0x1A65, far=True)  # 1A60
                                _left, _right = r.ax, 0  # 1A65
                                if _left == _right:  # 1A67
                                    r.push(ss16(mem, r, r.bp + 4))  # 1A6C
                                    r = yield from _result_call(mem, r, variant, '000E:09DB', 1, 0x1A72, far=False)  # 1A6F
                                    _left, _right = r.al, 0  # 1A72
                                    if _left == _right:  # 1A74
                                        r.push(ss16(mem, r, r.bp + 4))  # 1AC0
                                        r = yield from _result_call(mem, r, variant, '000E:0A53', 1, 0x1AC6, far=False)  # 1AC3
                                        _left, _right = r.al, 0  # 1AC6
                                        if _left == _right:  # 1AC8
                                            r.ax = 2  # 1B13
                                            r.push(r.ax)  # 1B16
                                            r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x1B1C, far=True)  # 1B17
                                            _left, _right = r.ax, 1  # 1B1C
                                            if _left != _right:  # 1B1F
                                                _left, _right = r.ax, 2  # 1B3C
                                                if _left != _right:  # 1B3F
                                                    pass
                                                else:
                                                    r.di = r.bp - 0x108  # 1B41
                                                    r.push(r.ss)  # 1B45
                                                    r.push(r.di)  # 1B46
                                                    r.push(ss16(mem, r, r.bp + 4))  # 1B47
                                                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1B4D, far=False)  # 1B4A
                                                    r.di = 0x1048  # 1B4D
                                                    r.push(mem.seg(0xE))  # 1B50
                                                    r.push(r.di)  # 1B51
                                                    r.di = 0xd0a  # 1B52
                                                    r.push(mem.seg(0xE))  # 1B55
                                                    r.push(r.di)  # 1B56
                                                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1B5A, far=False)  # 1B57
                                            else:
                                                r.di = r.bp - 0x108  # 1B21
                                                r.push(r.ss)  # 1B25
                                                r.push(r.di)  # 1B26
                                                r.push(ss16(mem, r, r.bp + 4))  # 1B27
                                                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1B2D, far=False)  # 1B2A
                                                r.di = 0x1040  # 1B2D
                                                r.push(mem.seg(0xE))  # 1B30
                                                r.push(r.di)  # 1B31
                                                r.di = 0xd0a  # 1B32
                                                r.push(mem.seg(0xE))  # 1B35
                                                r.push(r.di)  # 1B36
                                                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1B3A, far=False)  # 1B37
                                        else:
                                            r.ax = 2  # 1ACA
                                            r.push(r.ax)  # 1ACD
                                            r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x1AD3, far=True)  # 1ACE
                                            _left, _right = r.ax, 1  # 1AD3
                                            if _left != _right:  # 1AD6
                                                _left, _right = r.ax, 2  # 1AF3
                                                if _left != _right:  # 1AF6
                                                    pass
                                                else:
                                                    r.di = r.bp - 0x108  # 1AF8
                                                    r.push(r.ss)  # 1AFC
                                                    r.push(r.di)  # 1AFD
                                                    r.push(ss16(mem, r, r.bp + 4))  # 1AFE
                                                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1B04, far=False)  # 1B01
                                                    r.di = 0x1038  # 1B04
                                                    r.push(mem.seg(0xE))  # 1B07
                                                    r.push(r.di)  # 1B08
                                                    r.di = 0xd0a  # 1B09
                                                    r.push(mem.seg(0xE))  # 1B0C
                                                    r.push(r.di)  # 1B0D
                                                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1B11, far=False)  # 1B0E
                                            else:
                                                r.di = r.bp - 0x108  # 1AD8
                                                r.push(r.ss)  # 1ADC
                                                r.push(r.di)  # 1ADD
                                                r.push(ss16(mem, r, r.bp + 4))  # 1ADE
                                                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1AE4, far=False)  # 1AE1
                                                r.di = 0xdd0  # 1AE4
                                                r.push(mem.seg(0xE))  # 1AE7
                                                r.push(r.di)  # 1AE8
                                                r.di = 0xd0a  # 1AE9
                                                r.push(mem.seg(0xE))  # 1AEC
                                                r.push(r.di)  # 1AED
                                                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1AF1, far=False)  # 1AEE
                                            return (yield from _result_at_1b11(mem, r, variant))
                                    else:
                                        r.ax = 2  # 1A76
                                        r.push(r.ax)  # 1A79
                                        r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x1A7F, far=True)  # 1A7A
                                        _left, _right = r.ax, 1  # 1A7F
                                        if _left != _right:  # 1A82
                                            _left, _right = r.ax, 2  # 1A9F
                                            if _left != _right:  # 1AA2
                                                pass
                                            else:
                                                r.di = 0x102a  # 1AA4
                                                r.push(mem.seg(0xE))  # 1AA7
                                                r.push(r.di)  # 1AA8
                                                r.di = r.bp - 0x108  # 1AA9
                                                r.push(r.ss)  # 1AAD
                                                r.push(r.di)  # 1AAE
                                                r.push(ss16(mem, r, r.bp + 4))  # 1AAF
                                                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1AB5, far=False)  # 1AB2
                                                r.di = 0xd0a  # 1AB5
                                                r.push(mem.seg(0xE))  # 1AB8
                                                r.push(r.di)  # 1AB9
                                                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1ABD, far=False)  # 1ABA
                                        else:
                                            r.di = r.bp - 0x108  # 1A84
                                            r.push(r.ss)  # 1A88
                                            r.push(r.di)  # 1A89
                                            r.push(ss16(mem, r, r.bp + 4))  # 1A8A
                                            r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1A90, far=False)  # 1A8D
                                            r.di = 0xd97  # 1A90
                                            r.push(mem.seg(0xE))  # 1A93
                                            r.push(r.di)  # 1A94
                                            r.di = 0xd9f  # 1A95
                                            r.push(mem.seg(0xE))  # 1A98
                                            r.push(r.di)  # 1A99
                                            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1A9D, far=False)  # 1A9A
                                        return (yield from _result_at_1abd(mem, r, variant))
                                    return (yield from _result_at_1b5a(mem, r, variant))
                                else:
                                    r.di = ss16(mem, r, r.bp + 4)  # 1B5D
                                    r.es, r.di = ss16(mem, r, r.di + 4 + 2), ss16(mem, r, r.di + 4)  # 1B60
                                    r.push(r.es)  # 1B64
                                    r.push(r.di)  # 1B65
                                    r = yield from _result_call(mem, r, variant, '1771:5C60', 2, 0x1B6B, far=True)  # 1B66
                                    _left, _right = r.ax, 3  # 1B6B
                                    if _left >= _right:  # 1B6E
                                        return (yield from _result_at_1b8d(mem, r, variant))
                                    else:
                                        r.di = ss16(mem, r, r.bp + 4)  # 1B70
                                        r.al = ss8(mem, r, r.di - 1)  # 1B73
                                        cbw(r)  # 1B77
                                        r.dx = 0xa  # 1B78
                                        mul(r, r.dx)  # 1B7B
                                        r.di = r.ax  # 1B7D
                                        _left, _right = mem.ds8((r.di + 0x7b86) & M16), 0  # 1B7F
                                        if _left <= _right:  # 1B84
                                            return (yield from _result_at_1b8d(mem, r, variant))
                                        else:
                                            r.push(r.bp)  # 1B86
                                            r = yield from _result_call(mem, r, variant, '000E:0C3A', 1, 0x1B8A, far=False)  # 1B87
                            else:
                                r.di = r.bp - 0x108  # 1A3B
                                r.push(r.ss)  # 1A3F
                                r.push(r.di)  # 1A40
                                r.push(ss16(mem, r, r.bp + 4))  # 1A41
                                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1A47, far=False)  # 1A44
                                r.di = 0x1021  # 1A47
                                r.push(mem.seg(0xE))  # 1A4A
                                r.push(r.di)  # 1A4B
                                r.di = 0xd0a  # 1A4C
                                r.push(mem.seg(0xE))  # 1A4F
                                r.push(r.di)  # 1A50
                                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1A54, far=False)  # 1A51
                        else:
                            return (yield from _result_at_1a22(mem, r, variant))
            else:
                r.di = 0xff3  # 19F0
                r.push(mem.seg(0xE))  # 19F3
                r.push(r.di)  # 19F4
                r.di = 0xfff  # 19F5
                r.push(mem.seg(0xE))  # 19F8
                r.push(r.di)  # 19F9
                r.di = r.bp - 0x108  # 19FA
                r.push(r.ss)  # 19FE
                r.push(r.di)  # 19FF
                r.push(ss16(mem, r, r.bp + 4))  # 1A00
                r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x1A06, far=False)  # 1A03
                r.di = 0xd26  # 1A06
                r.push(mem.seg(0xE))  # 1A09
                r.push(r.di)  # 1A0A
                r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x1A10, far=True)  # 1A0B
                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1A13, far=False)  # 1A10
        else:
            r.di = 0xfdb  # 19D7
            r.push(mem.seg(0xE))  # 19DA
            r.push(r.di)  # 19DB
            r.di = 0xfe3  # 19DC
            r.push(mem.seg(0xE))  # 19DF
            r.push(r.di)  # 19E0
            r.di = 0xfeb  # 19E1
            r.push(mem.seg(0xE))  # 19E4
            r.push(r.di)  # 19E5
            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x19E9, far=False)  # 19E6
    return r


def _result_at_131f(mem, r, variant):
    r.di = ss16(mem, r, r.bp + 4)  # 131F
    r.es, r.di = ss16(mem, r, r.di + 4 + 2), ss16(mem, r, r.di + 4)  # 1322
    r.push(r.es)  # 1326
    r.push(r.di)  # 1327
    r = yield from _result_call(mem, r, variant, '1771:5C60', 2, 0x132D, far=True)  # 1328
    _left, _right = r.ax, 0  # 132D
    if _left != _right:  # 132F
        r.di = ss16(mem, r, r.bp + 4)  # 1372
        r.es, r.di = ss16(mem, r, r.di + 4 + 2), ss16(mem, r, r.di + 4)  # 1375
        r.push(r.es)  # 1379
        r.push(r.di)  # 137A
        r.di = ss16(mem, r, r.bp + 4)  # 137B
        r.al = ss8(mem, r, r.di - 1)  # 137E
        r.push(r.ax)  # 1382
        r = yield from _result_call(mem, r, variant, '0791:B71C', 3, 0x1388, far=True)  # 1383
        _left, _right = r.ax, 0xff01  # 1388
        if s16(_left) < s16(_right):  # 138B
            return (yield from _result_at_13dc(mem, r, variant))
        else:
            _left, _right = r.ax, 0xfffb  # 138D
            if s16(_left) > s16(_right):  # 1390
                return (yield from _result_at_13dc(mem, r, variant))
            else:
                r.ax = 2  # 1392
                r.push(r.ax)  # 1395
                r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x139B, far=True)  # 1396
                _left, _right = r.ax, 1  # 139B
                if _left != _right:  # 139E
                    _left, _right = r.ax, 2  # 13BB
                    if _left != _right:  # 13BE
                        pass
                    else:
                        r.di = r.bp - 0x108  # 13C0
                        r.push(r.ss)  # 13C4
                        r.push(r.di)  # 13C5
                        r.push(ss16(mem, r, r.bp + 4))  # 13C6
                        r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x13CC, far=False)  # 13C9
                        r.di = 0xd7e  # 13CC
                        r.push(mem.seg(0xE))  # 13CF
                        r.push(r.di)  # 13D0
                        r.di = 0xd0a  # 13D1
                        r.push(mem.seg(0xE))  # 13D4
                        r.push(r.di)  # 13D5
                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x13D9, far=False)  # 13D6
                else:
                    r.di = r.bp - 0x108  # 13A0
                    r.push(r.ss)  # 13A4
                    r.push(r.di)  # 13A5
                    r.push(ss16(mem, r, r.bp + 4))  # 13A6
                    r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x13AC, far=False)  # 13A9
                    r.di = 0xd73  # 13AC
                    r.push(mem.seg(0xE))  # 13AF
                    r.push(r.di)  # 13B0
                    r.di = 0xd0a  # 13B1
                    r.push(mem.seg(0xE))  # 13B4
                    r.push(r.di)  # 13B5
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x13B9, far=False)  # 13B6
                return (yield from _result_at_13d9(mem, r, variant))
    else:
        r.push(ss16(mem, r, r.bp + 4))  # 1331
        r = yield from _result_call(mem, r, variant, '000E:09DB', 1, 0x1337, far=False)  # 1334
        _left, _right = r.al, 0  # 1337
        if _left == _right:  # 1339
            r.di = r.bp - 0x108  # 1356
            r.push(r.ss)  # 135A
            r.push(r.di)  # 135B
            r.push(ss16(mem, r, r.bp + 4))  # 135C
            r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1362, far=False)  # 135F
            r.di = 0xd57  # 1362
            r.push(mem.seg(0xE))  # 1365
            r.push(r.di)  # 1366
            r.di = 0xd62  # 1367
            r.push(mem.seg(0xE))  # 136A
            r.push(r.di)  # 136B
            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x136F, far=False)  # 136C
        else:
            r.di = r.bp - 0x108  # 133B
            r.push(r.ss)  # 133F
            r.push(r.di)  # 1340
            r.push(ss16(mem, r, r.bp + 4))  # 1341
            r = yield from _result_call(mem, r, variant, '000E:0B0A', 1, 0x1347, far=False)  # 1344
            r.di = 0xd40  # 1347
            r.push(mem.seg(0xE))  # 134A
            r.push(r.di)  # 134B
            r.di = 0xd4b  # 134C
            r.push(mem.seg(0xE))  # 134F
            r.push(r.di)  # 1350
            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1354, far=False)  # 1351
        return (yield from _result_at_136f(mem, r, variant))
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_136f(mem, r, variant):
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_13d9(mem, r, variant):
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_13dc(mem, r, variant):
    _left, _right = r.ax, 0xfffc  # 13DC
    if s16(_left) < s16(_right):  # 13DF
        return (yield from _result_at_1450(mem, r, variant))
    else:
        _left, _right = r.ax, 0xfffe  # 13E1
        if s16(_left) > s16(_right):  # 13E4
            return (yield from _result_at_1450(mem, r, variant))
        else:
            r.ax = 3  # 13E6
            r.push(r.ax)  # 13E9
            r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x13EF, far=True)  # 13EA
            _left, _right = r.ax, 1  # 13EF
            if _left != _right:  # 13F2
                _left, _right = r.ax, 2  # 140F
                if _left != _right:  # 1412
                    _left, _right = r.ax, 3  # 142F
                    if _left != _right:  # 1432
                        pass
                    else:
                        r.di = r.bp - 0x108  # 1434
                        r.push(r.ss)  # 1438
                        r.push(r.di)  # 1439
                        r.push(ss16(mem, r, r.bp + 4))  # 143A
                        r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1440, far=False)  # 143D
                        r.di = 0xda8  # 1440
                        r.push(mem.seg(0xE))  # 1443
                        r.push(r.di)  # 1444
                        r.di = 0xd0a  # 1445
                        r.push(mem.seg(0xE))  # 1448
                        r.push(r.di)  # 1449
                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x144D, far=False)  # 144A
                else:
                    r.di = r.bp - 0x108  # 1414
                    r.push(r.ss)  # 1418
                    r.push(r.di)  # 1419
                    r.push(ss16(mem, r, r.bp + 4))  # 141A
                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1420, far=False)  # 141D
                    r.di = 0xd97  # 1420
                    r.push(mem.seg(0xE))  # 1423
                    r.push(r.di)  # 1424
                    r.di = 0xd9f  # 1425
                    r.push(mem.seg(0xE))  # 1428
                    r.push(r.di)  # 1429
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x142D, far=False)  # 142A
            else:
                r.di = r.bp - 0x108  # 13F4
                r.push(r.ss)  # 13F8
                r.push(r.di)  # 13F9
                r.push(ss16(mem, r, r.bp + 4))  # 13FA
                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1400, far=False)  # 13FD
                r.di = 0xd8b  # 1400
                r.push(mem.seg(0xE))  # 1403
                r.push(r.di)  # 1404
                r.di = 0xd0a  # 1405
                r.push(mem.seg(0xE))  # 1408
                r.push(r.di)  # 1409
                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x140D, far=False)  # 140A
            return (yield from _result_at_144d(mem, r, variant))
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_144d(mem, r, variant):
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_1450(mem, r, variant):
    _left, _right = r.ax, 0xffff  # 1450
    if _left == _right:  # 1453
        r.ax = 3  # 1458
        r.push(r.ax)  # 145B
        r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x1461, far=True)  # 145C
        _left, _right = r.ax, 1  # 1461
        if _left != _right:  # 1464
            _left, _right = r.ax, 2  # 1496
            if _left != _right:  # 1499
                _left, _right = r.ax, 3  # 14B6
                if _left != _right:  # 14B9
                    pass
                else:
                    r.di = r.bp - 0x108  # 14BB
                    r.push(r.ss)  # 14BF
                    r.push(r.di)  # 14C0
                    r.push(ss16(mem, r, r.bp + 4))  # 14C1
                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x14C7, far=False)  # 14C4
                    r.di = 0xdd9  # 14C7
                    r.push(mem.seg(0xE))  # 14CA
                    r.push(r.di)  # 14CB
                    r.di = 0xd0a  # 14CC
                    r.push(mem.seg(0xE))  # 14CF
                    r.push(r.di)  # 14D0
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x14D4, far=False)  # 14D1
            else:
                r.di = r.bp - 0x108  # 149B
                r.push(r.ss)  # 149F
                r.push(r.di)  # 14A0
                r.push(ss16(mem, r, r.bp + 4))  # 14A1
                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x14A7, far=False)  # 14A4
                r.di = 0xdd0  # 14A7
                r.push(mem.seg(0xE))  # 14AA
                r.push(r.di)  # 14AB
                r.di = 0xd0a  # 14AC
                r.push(mem.seg(0xE))  # 14AF
                r.push(r.di)  # 14B0
                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x14B4, far=False)  # 14B1
        else:
            r.di = 0xdb6  # 1466
            r.push(mem.seg(0xE))  # 1469
            r.push(r.di)  # 146A
            r.di = 0xdc0  # 146B
            r.push(mem.seg(0xE))  # 146E
            r.push(r.di)  # 146F
            r.di = r.bp - 0x208  # 1470
            r.push(r.ss)  # 1474
            r.push(r.di)  # 1475
            r.di = 0xdcc  # 1476
            r.push(mem.seg(0xE))  # 1479
            r.push(r.di)  # 147A
            r = yield from _result_call(mem, r, variant, '23E4:062A', 2, 0x1480, far=True)  # 147B
            r.di = r.bp - 0x108  # 1480
            r.push(r.ss)  # 1484
            r.push(r.di)  # 1485
            r.push(ss16(mem, r, r.bp + 4))  # 1486
            r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x148C, far=False)  # 1489
            r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x1491, far=True)  # 148C
            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1494, far=False)  # 1491
        return (yield from _result_at_14d4(mem, r, variant))
    else:
        _left, _right = r.ax, 0  # 14D7
        if _left == _right:  # 14DA
            r.di = ss16(mem, r, r.bp + 4)  # 14DF
            r.es, r.di = ss16(mem, r, r.di + 4 + 2), ss16(mem, r, r.di + 4)  # 14E2
            r.push(r.es)  # 14E6
            r.push(r.di)  # 14E7
            r = yield from _result_call(mem, r, variant, '1771:5C60', 2, 0x14ED, far=True)  # 14E8
            _left, _right = r.ax, 1  # 14ED
            if _left == _right:  # 14F0
                r.ax = 4  # 14F5
                r.push(r.ax)  # 14F8
                r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x14FE, far=True)  # 14F9
                _left, _right = r.ax, 1  # 14FE
                if _left != _right:  # 1501
                    _left, _right = r.ax, 2  # 151E
                    if _left != _right:  # 1521
                        _left, _right = r.ax, 3  # 1548
                        if _left != _right:  # 154B
                            _left, _right = r.ax, 4  # 157D
                            if _left != _right:  # 1580
                                pass
                            else:
                                r.di = 0xe20  # 1582
                                r.push(mem.seg(0xE))  # 1585
                                r.push(r.di)  # 1586
                                r.di = 0xe2a  # 1587
                                r.push(mem.seg(0xE))  # 158A
                                r.push(r.di)  # 158B
                                r.di = 0xd0a  # 158C
                                r.push(mem.seg(0xE))  # 158F
                                r.push(r.di)  # 1590
                                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1594, far=False)  # 1591
                        else:
                            r.di = 0xe08  # 154D
                            r.push(mem.seg(0xE))  # 1550
                            r.push(r.di)  # 1551
                            r.di = r.bp - 0x208  # 1552
                            r.push(r.ss)  # 1556
                            r.push(r.di)  # 1557
                            r.di = 0xe1a  # 1558
                            r.push(mem.seg(0xE))  # 155B
                            r.push(r.di)  # 155C
                            r = yield from _result_call(mem, r, variant, '23E4:062A', 2, 0x1562, far=True)  # 155D
                            r.di = r.bp - 0x108  # 1562
                            r.push(r.ss)  # 1566
                            r.push(r.di)  # 1567
                            r.push(ss16(mem, r, r.bp + 4))  # 1568
                            r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x156E, far=False)  # 156B
                            r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x1573, far=True)  # 156E
                            r.di = 0xd0a  # 1573
                            r.push(mem.seg(0xE))  # 1576
                            r.push(r.di)  # 1577
                            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x157B, far=False)  # 1578
                    else:
                        r.di = r.bp - 0x108  # 1523
                        r.push(r.ss)  # 1527
                        r.push(r.di)  # 1528
                        r.push(ss16(mem, r, r.bp + 4))  # 1529
                        r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x152F, far=False)  # 152C
                        r.di = 0xdf6  # 152F
                        r.push(mem.seg(0xE))  # 1532
                        r.push(r.di)  # 1533
                        r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x1539, far=True)  # 1534
                        r.di = 0xdfa  # 1539
                        r.push(mem.seg(0xE))  # 153C
                        r.push(r.di)  # 153D
                        r.di = 0xd0a  # 153E
                        r.push(mem.seg(0xE))  # 1541
                        r.push(r.di)  # 1542
                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1546, far=False)  # 1543
                else:
                    r.di = r.bp - 0x108  # 1503
                    r.push(r.ss)  # 1507
                    r.push(r.di)  # 1508
                    r.push(ss16(mem, r, r.bp + 4))  # 1509
                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x150F, far=False)  # 150C
                    r.di = 0xde6  # 150F
                    r.push(mem.seg(0xE))  # 1512
                    r.push(r.di)  # 1513
                    r.di = 0xdf1  # 1514
                    r.push(mem.seg(0xE))  # 1517
                    r.push(r.di)  # 1518
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x151C, far=False)  # 1519
                return (yield from _result_at_1594(mem, r, variant))
            else:
                r.ax = 4  # 1597
                r.push(r.ax)  # 159A
                r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x15A0, far=True)  # 159B
                _left, _right = r.ax, 1  # 15A0
                if _left != _right:  # 15A3
                    _left, _right = r.ax, 2  # 15C0
                    if _left != _right:  # 15C3
                        _left, _right = r.ax, 3  # 15E0
                        if _left != _right:  # 15E3
                            _left, _right = r.ax, 4  # 1600
                            if _left != _right:  # 1603
                                pass
                            else:
                                r.di = r.bp - 0x108  # 1605
                                r.push(r.ss)  # 1609
                                r.push(r.di)  # 160A
                                r.push(ss16(mem, r, r.bp + 4))  # 160B
                                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1611, far=False)  # 160E
                                r.di = 0xe71  # 1611
                                r.push(mem.seg(0xE))  # 1614
                                r.push(r.di)  # 1615
                                r.di = 0xe7e  # 1616
                                r.push(mem.seg(0xE))  # 1619
                                r.push(r.di)  # 161A
                                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x161E, far=False)  # 161B
                        else:
                            r.di = r.bp - 0x108  # 15E5
                            r.push(r.ss)  # 15E9
                            r.push(r.di)  # 15EA
                            r.push(ss16(mem, r, r.bp + 4))  # 15EB
                            r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x15F1, far=False)  # 15EE
                            r.di = 0xe61  # 15F1
                            r.push(mem.seg(0xE))  # 15F4
                            r.push(r.di)  # 15F5
                            r.di = 0xe68  # 15F6
                            r.push(mem.seg(0xE))  # 15F9
                            r.push(r.di)  # 15FA
                            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x15FE, far=False)  # 15FB
                    else:
                        r.di = r.bp - 0x108  # 15C5
                        r.push(r.ss)  # 15C9
                        r.push(r.di)  # 15CA
                        r.push(ss16(mem, r, r.bp + 4))  # 15CB
                        r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x15D1, far=False)  # 15CE
                        r.di = 0xe4b  # 15D1
                        r.push(mem.seg(0xE))  # 15D4
                        r.push(r.di)  # 15D5
                        r.di = 0xe57  # 15D6
                        r.push(mem.seg(0xE))  # 15D9
                        r.push(r.di)  # 15DA
                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x15DE, far=False)  # 15DB
                else:
                    r.di = 0xe35  # 15A5
                    r.push(mem.seg(0xE))  # 15A8
                    r.push(r.di)  # 15A9
                    r.di = 0xe41  # 15AA
                    r.push(mem.seg(0xE))  # 15AD
                    r.push(r.di)  # 15AE
                    r.di = r.bp - 0x108  # 15AF
                    r.push(r.ss)  # 15B3
                    r.push(r.di)  # 15B4
                    r.push(ss16(mem, r, r.bp + 4))  # 15B5
                    r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x15BB, far=False)  # 15B8
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x15BE, far=False)  # 15BB
            return (yield from _result_at_161e(mem, r, variant))
        else:
            _left, _right = r.ax, 1  # 1621
            if _left == _right:  # 1624
                r.ax = 5  # 1629
                r.push(r.ax)  # 162C
                r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x1632, far=True)  # 162D
                _left, _right = r.ax, 1  # 1632
                if _left != _right:  # 1635
                    _left, _right = r.ax, 2  # 1653
                    if _left != _right:  # 1656
                        _left, _right = r.ax, 3  # 1673
                        if _left != _right:  # 1676
                            _left, _right = r.ax, 4  # 16A8
                            if _left != _right:  # 16AB
                                _left, _right = r.ax, 5  # 16C8
                                if _left != _right:  # 16CB
                                    pass
                                else:
                                    r.di = 0xeb6  # 16CD
                                    r.push(mem.seg(0xE))  # 16D0
                                    r.push(r.di)  # 16D1
                                    r.di = 0xec1  # 16D2
                                    r.push(mem.seg(0xE))  # 16D5
                                    r.push(r.di)  # 16D6
                                    r.di = r.bp - 0x108  # 16D7
                                    r.push(r.ss)  # 16DB
                                    r.push(r.di)  # 16DC
                                    r.push(ss16(mem, r, r.bp + 4))  # 16DD
                                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x16E3, far=False)  # 16E0
                                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x16E6, far=False)  # 16E3
                            else:
                                r.di = r.bp - 0x108  # 16AD
                                r.push(r.ss)  # 16B1
                                r.push(r.di)  # 16B2
                                r.push(ss16(mem, r, r.bp + 4))  # 16B3
                                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x16B9, far=False)  # 16B6
                                r.di = 0xea6  # 16B9
                                r.push(mem.seg(0xE))  # 16BC
                                r.push(r.di)  # 16BD
                                r.di = 0xd0a  # 16BE
                                r.push(mem.seg(0xE))  # 16C1
                                r.push(r.di)  # 16C2
                                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x16C6, far=False)  # 16C3
                        else:
                            r.di = 0xe9d  # 1678
                            r.push(mem.seg(0xE))  # 167B
                            r.push(r.di)  # 167C
                            r.di = 0xdc0  # 167D
                            r.push(mem.seg(0xE))  # 1680
                            r.push(r.di)  # 1681
                            r.di = r.bp - 0x208  # 1682
                            r.push(r.ss)  # 1686
                            r.push(r.di)  # 1687
                            r.di = 0xdcc  # 1688
                            r.push(mem.seg(0xE))  # 168B
                            r.push(r.di)  # 168C
                            r = yield from _result_call(mem, r, variant, '23E4:062A', 2, 0x1692, far=True)  # 168D
                            r.di = r.bp - 0x108  # 1692
                            r.push(r.ss)  # 1696
                            r.push(r.di)  # 1697
                            r.push(ss16(mem, r, r.bp + 4))  # 1698
                            r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x169E, far=False)  # 169B
                            r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x16A3, far=True)  # 169E
                            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x16A6, far=False)  # 16A3
                    else:
                        r.di = r.bp - 0x108  # 1658
                        r.push(r.ss)  # 165C
                        r.push(r.di)  # 165D
                        r.push(ss16(mem, r, r.bp + 4))  # 165E
                        r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x1664, far=False)  # 1661
                        r.di = 0xe92  # 1664
                        r.push(mem.seg(0xE))  # 1667
                        r.push(r.di)  # 1668
                        r.di = 0xd0a  # 1669
                        r.push(mem.seg(0xE))  # 166C
                        r.push(r.di)  # 166D
                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1671, far=False)  # 166E
                else:
                    r.di = r.bp - 0x108  # 1637
                    r.push(r.ss)  # 163B
                    r.push(r.di)  # 163C
                    r.push(ss16(mem, r, r.bp + 4))  # 163D
                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1643, far=False)  # 1640
                    r.di = 0xe85  # 1643
                    r.push(mem.seg(0xE))  # 1646
                    r.push(r.di)  # 1647
                    r.di = 0xd0a  # 1648
                    r.push(mem.seg(0xE))  # 164B
                    r.push(r.di)  # 164C
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1650, far=False)  # 164D
                return (yield from _result_at_16e6(mem, r, variant))
            else:
                _left, _right = r.ax, 2  # 16E9
                if _left == _right:  # 16EC
                    r.ax = 4  # 16F1
                    r.push(r.ax)  # 16F4
                    r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x16FA, far=True)  # 16F5
                    _left, _right = r.ax, 1  # 16FA
                    if _left != _right:  # 16FD
                        _left, _right = r.ax, 2  # 171A
                        if _left != _right:  # 171D
                            _left, _right = r.ax, 3  # 173A
                            if _left != _right:  # 173D
                                _left, _right = r.ax, 4  # 175A
                                if _left != _right:  # 175D
                                    pass
                                else:
                                    r.di = r.bp - 0x108  # 175F
                                    r.push(r.ss)  # 1763
                                    r.push(r.di)  # 1764
                                    r.push(ss16(mem, r, r.bp + 4))  # 1765
                                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x176B, far=False)  # 1768
                                    r.di = 0xef7  # 176B
                                    r.push(mem.seg(0xE))  # 176E
                                    r.push(r.di)  # 176F
                                    r.di = 0xd0a  # 1770
                                    r.push(mem.seg(0xE))  # 1773
                                    r.push(r.di)  # 1774
                                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1778, far=False)  # 1775
                            else:
                                r.di = r.bp - 0x108  # 173F
                                r.push(r.ss)  # 1743
                                r.push(r.di)  # 1744
                                r.push(ss16(mem, r, r.bp + 4))  # 1745
                                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x174B, far=False)  # 1748
                                r.di = 0xeed  # 174B
                                r.push(mem.seg(0xE))  # 174E
                                r.push(r.di)  # 174F
                                r.di = 0xd0a  # 1750
                                r.push(mem.seg(0xE))  # 1753
                                r.push(r.di)  # 1754
                                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1758, far=False)  # 1755
                        else:
                            r.di = r.bp - 0x108  # 171F
                            r.push(r.ss)  # 1723
                            r.push(r.di)  # 1724
                            r.push(ss16(mem, r, r.bp + 4))  # 1725
                            r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x172B, far=False)  # 1728
                            r.di = 0xede  # 172B
                            r.push(mem.seg(0xE))  # 172E
                            r.push(r.di)  # 172F
                            r.di = 0xd0a  # 1730
                            r.push(mem.seg(0xE))  # 1733
                            r.push(r.di)  # 1734
                            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1738, far=False)  # 1735
                    else:
                        r.di = r.bp - 0x108  # 16FF
                        r.push(r.ss)  # 1703
                        r.push(r.di)  # 1704
                        r.push(ss16(mem, r, r.bp + 4))  # 1705
                        r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x170B, far=False)  # 1708
                        r.di = 0xecb  # 170B
                        r.push(mem.seg(0xE))  # 170E
                        r.push(r.di)  # 170F
                        r.di = 0xed9  # 1710
                        r.push(mem.seg(0xE))  # 1713
                        r.push(r.di)  # 1714
                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1718, far=False)  # 1715
                    return (yield from _result_at_1778(mem, r, variant))
                else:
                    _left, _right = r.ax, 3  # 177B
                    if _left == _right:  # 177E
                        r.ax = 5  # 1783
                        r.push(r.ax)  # 1786
                        r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x178C, far=True)  # 1787
                        _left, _right = r.ax, 1  # 178C
                        if _left != _right:  # 178F
                            _left, _right = r.ax, 2  # 17AD
                            if _left != _right:  # 17B0
                                _left, _right = r.ax, 3  # 17E2
                                if _left != _right:  # 17E5
                                    _left, _right = r.ax, 4  # 1802
                                    if _left != _right:  # 1805
                                        _left, _right = r.ax, 5  # 1822
                                        if _left != _right:  # 1825
                                            pass
                                        else:
                                            r.di = r.bp - 0x108  # 1827
                                            r.push(r.ss)  # 182B
                                            r.push(r.di)  # 182C
                                            r.push(ss16(mem, r, r.bp + 4))  # 182D
                                            r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1833, far=False)  # 1830
                                            r.di = 0xf46  # 1833
                                            r.push(mem.seg(0xE))  # 1836
                                            r.push(r.di)  # 1837
                                            r.di = 0xd0a  # 1838
                                            r.push(mem.seg(0xE))  # 183B
                                            r.push(r.di)  # 183C
                                            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1840, far=False)  # 183D
                                    else:
                                        r.di = r.bp - 0x108  # 1807
                                        r.push(r.ss)  # 180B
                                        r.push(r.di)  # 180C
                                        r.push(ss16(mem, r, r.bp + 4))  # 180D
                                        r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1813, far=False)  # 1810
                                        r.di = 0xf3d  # 1813
                                        r.push(mem.seg(0xE))  # 1816
                                        r.push(r.di)  # 1817
                                        r.di = 0xd0a  # 1818
                                        r.push(mem.seg(0xE))  # 181B
                                        r.push(r.di)  # 181C
                                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1820, far=False)  # 181D
                                else:
                                    r.di = 0xf26  # 17E7
                                    r.push(mem.seg(0xE))  # 17EA
                                    r.push(r.di)  # 17EB
                                    r.di = 0xf33  # 17EC
                                    r.push(mem.seg(0xE))  # 17EF
                                    r.push(r.di)  # 17F0
                                    r.di = r.bp - 0x108  # 17F1
                                    r.push(r.ss)  # 17F5
                                    r.push(r.di)  # 17F6
                                    r.push(ss16(mem, r, r.bp + 4))  # 17F7
                                    r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x17FD, far=False)  # 17FA
                                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1800, far=False)  # 17FD
                            else:
                                r.di = 0xf13  # 17B2
                                r.push(mem.seg(0xE))  # 17B5
                                r.push(r.di)  # 17B6
                                r.di = r.bp - 0x208  # 17B7
                                r.push(r.ss)  # 17BB
                                r.push(r.di)  # 17BC
                                r.di = 0xf21  # 17BD
                                r.push(mem.seg(0xE))  # 17C0
                                r.push(r.di)  # 17C1
                                r = yield from _result_call(mem, r, variant, '23E4:062A', 2, 0x17C7, far=True)  # 17C2
                                r.di = r.bp - 0x108  # 17C7
                                r.push(r.ss)  # 17CB
                                r.push(r.di)  # 17CC
                                r.push(ss16(mem, r, r.bp + 4))  # 17CD
                                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x17D3, far=False)  # 17D0
                                r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x17D8, far=True)  # 17D3
                                r.di = 0xd0a  # 17D8
                                r.push(mem.seg(0xE))  # 17DB
                                r.push(r.di)  # 17DC
                                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x17E0, far=False)  # 17DD
                        else:
                            r.di = r.bp - 0x108  # 1791
                            r.push(r.ss)  # 1795
                            r.push(r.di)  # 1796
                            r.push(ss16(mem, r, r.bp + 4))  # 1797
                            r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x179D, far=False)  # 179A
                            r.di = 0xf06  # 179D
                            r.push(mem.seg(0xE))  # 17A0
                            r.push(r.di)  # 17A1
                            r.di = 0xd0a  # 17A2
                            r.push(mem.seg(0xE))  # 17A5
                            r.push(r.di)  # 17A6
                            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x17AA, far=False)  # 17A7
                        return (yield from _result_at_1840(mem, r, variant))
                    else:
                        _left, _right = r.ax, 4  # 1843
                        if s16(_left) >= s16(_right):  # 1846
                            _left, _right = r.ax, 6  # 184B
                            if s16(_left) <= s16(_right):  # 184E
                                r.ax = 5  # 1853
                                r.push(r.ax)  # 1856
                                r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x185C, far=True)  # 1857
                                _left, _right = r.ax, 1  # 185C
                                if _left != _right:  # 185F
                                    _left, _right = r.ax, 2  # 1883
                                    if _left != _right:  # 1886
                                        _left, _right = r.ax, 3  # 18A3
                                        if _left != _right:  # 18A6
                                            _left, _right = r.ax, 4  # 18C3
                                            if _left != _right:  # 18C6
                                                _left, _right = r.ax, 5  # 18DC
                                                if _left != _right:  # 18DF
                                                    pass
                                                else:
                                                    r.di = 0xf89  # 18E1
                                                    r.push(mem.seg(0xE))  # 18E4
                                                    r.push(r.di)  # 18E5
                                                    r.di = 0xf9a  # 18E6
                                                    r.push(mem.seg(0xE))  # 18E9
                                                    r.push(r.di)  # 18EA
                                                    r.di = 0xd0a  # 18EB
                                                    r.push(mem.seg(0xE))  # 18EE
                                                    r.push(r.di)  # 18EF
                                                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x18F3, far=False)  # 18F0
                                            else:
                                                r.di = 0xf78  # 18C8
                                                r.push(mem.seg(0xE))  # 18CB
                                                r.push(r.di)  # 18CC
                                                r.di = 0xd0a  # 18CD
                                                r.push(mem.seg(0xE))  # 18D0
                                                r.push(r.di)  # 18D1
                                                r.di = 0xd0a  # 18D2
                                                r.push(mem.seg(0xE))  # 18D5
                                                r.push(r.di)  # 18D6
                                                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x18DA, far=False)  # 18D7
                                        else:
                                            r.di = r.bp - 0x108  # 18A8
                                            r.push(r.ss)  # 18AC
                                            r.push(r.di)  # 18AD
                                            r.push(ss16(mem, r, r.bp + 4))  # 18AE
                                            r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x18B4, far=False)  # 18B1
                                            r.di = 0xf70  # 18B4
                                            r.push(mem.seg(0xE))  # 18B7
                                            r.push(r.di)  # 18B8
                                            r.di = 0xd0a  # 18B9
                                            r.push(mem.seg(0xE))  # 18BC
                                            r.push(r.di)  # 18BD
                                            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x18C1, far=False)  # 18BE
                                    else:
                                        r.di = r.bp - 0x108  # 1888
                                        r.push(r.ss)  # 188C
                                        r.push(r.di)  # 188D
                                        r.push(ss16(mem, r, r.bp + 4))  # 188E
                                        r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1894, far=False)  # 1891
                                        r.di = 0xf5f  # 1894
                                        r.push(mem.seg(0xE))  # 1897
                                        r.push(r.di)  # 1898
                                        r.di = 0xd0a  # 1899
                                        r.push(mem.seg(0xE))  # 189C
                                        r.push(r.di)  # 189D
                                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x18A1, far=False)  # 189E
                                else:
                                    r.di = r.bp - 0x108  # 1861
                                    r.push(r.ss)  # 1865
                                    r.push(r.di)  # 1866
                                    r.push(ss16(mem, r, r.bp + 4))  # 1867
                                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x186D, far=False)  # 186A
                                    r.di = 0xf57  # 186D
                                    r.push(mem.seg(0xE))  # 1870
                                    r.push(r.di)  # 1871
                                    r.di = r.bp - 0x208  # 1872
                                    r.push(r.ss)  # 1876
                                    r.push(r.di)  # 1877
                                    r.push(ss16(mem, r, r.bp + 4))  # 1878
                                    r = yield from _result_call(mem, r, variant, '000E:0B0A', 1, 0x187E, far=False)  # 187B
                                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1881, far=False)  # 187E
                                return (yield from _result_at_18f3(mem, r, variant))
                            else:
                                return (yield from _result_at_18f6(mem, r, variant))
                        else:
                            return (yield from _result_at_18f6(mem, r, variant))
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_14d4(mem, r, variant):
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_1594(mem, r, variant):
    return (yield from _result_at_161e(mem, r, variant))
    return r


def _result_at_161e(mem, r, variant):
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_16e6(mem, r, variant):
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_1778(mem, r, variant):
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_1840(mem, r, variant):
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_18f3(mem, r, variant):
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_18f6(mem, r, variant):
    _left, _right = r.ax, 7  # 18F6
    if s16(_left) >= s16(_right):  # 18F9
        _left, _right = r.ax, 0xff  # 18FE
        if s16(_left) <= s16(_right):  # 1901
            r.di = ss16(mem, r, r.bp + 4)  # 1906
            r.al = ss8(mem, r, r.di - 1)  # 1909
            cbw(r)  # 190D
            r.es, r.di = ss16(mem, r, r.bp - 4 + 2), ss16(mem, r, r.bp - 4)  # 190E
            r.di += r.ax  # 1911
            _left, _right = mem.u8(mem.addr(r.es, r.di)), 5  # 1913
            if _left <= _right:  # 1917
                r = yield from _result_call(mem, r, variant, '214B:06FA', 0, 0x1991, far=True)  # 198C
                _left, _right = r.al, 0  # 1991
                if _left == _right:  # 1993
                    r.di = r.bp - 0x108  # 19B0
                    r.push(r.ss)  # 19B4
                    r.push(r.di)  # 19B5
                    r.push(ss16(mem, r, r.bp + 4))  # 19B6
                    r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x19BC, far=False)  # 19B9
                    r.di = 0xfcc  # 19BC
                    r.push(mem.seg(0xE))  # 19BF
                    r.push(r.di)  # 19C0
                    r.di = 0xd0a  # 19C1
                    r.push(mem.seg(0xE))  # 19C4
                    r.push(r.di)  # 19C5
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x19C9, far=False)  # 19C6
                else:
                    r.di = r.bp - 0x108  # 1995
                    r.push(r.ss)  # 1999
                    r.push(r.di)  # 199A
                    r.push(ss16(mem, r, r.bp + 4))  # 199B
                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x19A1, far=False)  # 199E
                    r.di = 0xfc2  # 19A1
                    r.push(mem.seg(0xE))  # 19A4
                    r.push(r.di)  # 19A5
                    r.di = 0xd0a  # 19A6
                    r.push(mem.seg(0xE))  # 19A9
                    r.push(r.di)  # 19AA
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x19AE, far=False)  # 19AB
            else:
                r = yield from _result_call(mem, r, variant, '214B:06FA', 0, 0x191E, far=True)  # 1919
                _left, _right = r.al, 0  # 191E
                if _left == _right:  # 1920
                    r.di = 0xfb5  # 1978
                    r.push(mem.seg(0xE))  # 197B
                    r.push(r.di)  # 197C
                    r.di = 0xd0a  # 197D
                    r.push(mem.seg(0xE))  # 1980
                    r.push(r.di)  # 1981
                    r.di = 0xd0a  # 1982
                    r.push(mem.seg(0xE))  # 1985
                    r.push(r.di)  # 1986
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x198A, far=False)  # 1987
                else:
                    r.di = r.bp - 0x108  # 1922
                    r.push(r.ss)  # 1926
                    r.push(r.di)  # 1927
                    r.di = ss16(mem, r, r.bp + 4)  # 1928
                    r.al = ss8(mem, r, r.di - 1)  # 192B
                    cbw(r)  # 192F
                    r.es, r.di = ss16(mem, r, r.bp - 4 + 2), ss16(mem, r, r.bp - 4)  # 1930
                    r.di += r.ax  # 1933
                    r.al = mem.u8(mem.addr(r.es, r.di))  # 1935
                    r.ah = 0  # 1938
                    r.dx = 0  # 193A
                    r.push(r.dx)  # 193C
                    r.push(r.ax)  # 193D
                    r = yield from _result_call(mem, r, variant, '214B:09DA', 2, 0x1943, far=True)  # 193E
                    r.di = 0xfa7  # 1943
                    r.push(mem.seg(0xE))  # 1946
                    r.push(r.di)  # 1947
                    r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x194D, far=True)  # 1948
                    r.di = r.bp - 0x308  # 194D
                    r.push(r.ss)  # 1951
                    r.push(r.di)  # 1952
                    r.di = 0xe1a  # 1953
                    r.push(mem.seg(0xE))  # 1956
                    r.push(r.di)  # 1957
                    r = yield from _result_call(mem, r, variant, '23E4:062A', 2, 0x195D, far=True)  # 1958
                    r.di = r.bp - 0x208  # 195D
                    r.push(r.ss)  # 1961
                    r.push(r.di)  # 1962
                    r.push(ss16(mem, r, r.bp + 4))  # 1963
                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1969, far=False)  # 1966
                    r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x196E, far=True)  # 1969
                    r.di = 0xd0a  # 196E
                    r.push(mem.seg(0xE))  # 1971
                    r.push(r.di)  # 1972
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1976, far=False)  # 1973
                return (yield from _result_at_198a(mem, r, variant))
        else:
            pass
    else:
        pass
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_198a(mem, r, variant):
    return (yield from _result_at_19c9(mem, r, variant))
    return r


def _result_at_19c9(mem, r, variant):
    yield from ()
    return r


def _result_at_1a22(mem, r, variant):
    r.di = 0x1009  # 1A22
    r.push(mem.seg(0xE))  # 1A25
    r.push(r.di)  # 1A26
    r.di = 0x1013  # 1A27
    r.push(mem.seg(0xE))  # 1A2A
    r.push(r.di)  # 1A2B
    r.di = 0xd0a  # 1A2C
    r.push(mem.seg(0xE))  # 1A2F
    r.push(r.di)  # 1A30
    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1A34, far=False)  # 1A31
    return r


def _result_at_1abd(mem, r, variant):
    return (yield from _result_at_1b5a(mem, r, variant))
    return r


def _result_at_1b11(mem, r, variant):
    return (yield from _result_at_1b5a(mem, r, variant))
    return r


def _result_at_1b5a(mem, r, variant):
    yield from ()
    return r


def _result_at_1b8d(mem, r, variant):
    r.push(ss16(mem, r, r.bp + 4))  # 1B8D
    r = yield from _result_call(mem, r, variant, '000E:0B77', 1, 0x1B93, far=False)  # 1B90
    _left, _right = r.ax, 0xfffa  # 1B93
    if _left != _right:  # 1B96
        _left, _right = r.ax, 0xfff9  # 1BE7
        if _left != _right:  # 1BEA
            _left, _right = r.ax, 0xfff6  # 1C08
            if s16(_left) < s16(_right):  # 1C0B
                return (yield from _result_at_1c2e(mem, r, variant))
            else:
                _left, _right = r.ax, 0xfff8  # 1C0D
                if s16(_left) > s16(_right):  # 1C10
                    return (yield from _result_at_1c2e(mem, r, variant))
                else:
                    r.di = 0x1096  # 1C12
                    r.push(mem.seg(0xE))  # 1C15
                    r.push(r.di)  # 1C16
                    r.di = 0x10a3  # 1C17
                    r.push(mem.seg(0xE))  # 1C1A
                    r.push(r.di)  # 1C1B
                    r.di = r.bp - 0x108  # 1C1C
                    r.push(r.ss)  # 1C20
                    r.push(r.di)  # 1C21
                    r.push(ss16(mem, r, r.bp + 4))  # 1C22
                    r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x1C28, far=False)  # 1C25
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1C2B, far=False)  # 1C28
        else:
            r.di = r.bp - 0x108  # 1BEC
            r.push(r.ss)  # 1BF0
            r.push(r.di)  # 1BF1
            r.push(ss16(mem, r, r.bp + 4))  # 1BF2
            r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x1BF8, far=False)  # 1BF5
            r.di = 0x1082  # 1BF8
            r.push(mem.seg(0xE))  # 1BFB
            r.push(r.di)  # 1BFC
            r.di = 0x108c  # 1BFD
            r.push(mem.seg(0xE))  # 1C00
            r.push(r.di)  # 1C01
            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1C05, far=False)  # 1C02
    else:
        r.es, r.di = ss16(mem, r, r.bp - 8 + 2), ss16(mem, r, r.bp - 8)  # 1B98
        _left, _right = mem.u8(mem.addr(r.es, r.di + 0xb8)), 3  # 1B9B
        if _left <= _right:  # 1BA1
            r.di = r.bp - 0x108  # 1BCB
            r.push(r.ss)  # 1BCF
            r.push(r.di)  # 1BD0
            r.push(ss16(mem, r, r.bp + 4))  # 1BD1
            r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x1BD7, far=False)  # 1BD4
            r.di = 0x1069  # 1BD7
            r.push(mem.seg(0xE))  # 1BDA
            r.push(r.di)  # 1BDB
            r.di = 0x1075  # 1BDC
            r.push(mem.seg(0xE))  # 1BDF
            r.push(r.di)  # 1BE0
            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1BE4, far=False)  # 1BE1
        else:
            r.di = r.bp - 0x108  # 1BA3
            r.push(r.ss)  # 1BA7
            r.push(r.di)  # 1BA8
            r.es, r.di = ss16(mem, r, r.bp - 8 + 2), ss16(mem, r, r.bp - 8)  # 1BA9
            r.al = mem.u8(mem.addr(r.es, r.di + 0xb8))  # 1BAC
            r.ah = 0  # 1BB1
            r.dx = 0  # 1BB3
            r.push(r.dx)  # 1BB5
            r.push(r.ax)  # 1BB6
            r = yield from _result_call(mem, r, variant, '214B:09DA', 2, 0x1BBC, far=True)  # 1BB7
            r.di = 0x1055  # 1BBC
            r.push(mem.seg(0xE))  # 1BBF
            r.push(r.di)  # 1BC0
            r.di = 0x105b  # 1BC1
            r.push(mem.seg(0xE))  # 1BC4
            r.push(r.di)  # 1BC5
            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1BC9, far=False)  # 1BC6
        return (yield from _result_at_1be4(mem, r, variant))
    return r


def _result_at_1be4(mem, r, variant):
    yield from ()
    return r


def _result_at_1c2e(mem, r, variant):
    _left, _right = r.ax, 0xff01  # 1C2E
    if s16(_left) < s16(_right):  # 1C31
        return (yield from _result_at_1c5e(mem, r, variant))
    else:
        _left, _right = r.ax, 0xfff5  # 1C33
        if s16(_left) > s16(_right):  # 1C36
            return (yield from _result_at_1c5e(mem, r, variant))
        else:
            r.di = 0x10af  # 1C38
            r.push(mem.seg(0xE))  # 1C3B
            r.push(r.di)  # 1C3C
            r.di = r.bp - 0x108  # 1C3D
            r.push(r.ss)  # 1C41
            r.push(r.di)  # 1C42
            r.push(ss16(mem, r, r.bp + 4))  # 1C43
            r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x1C49, far=False)  # 1C46
            r.di = 0x10b7  # 1C49
            r.push(mem.seg(0xE))  # 1C4C
            r.push(r.di)  # 1C4D
            r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x1C53, far=True)  # 1C4E
            r.di = 0x10bc  # 1C53
            r.push(mem.seg(0xE))  # 1C56
            r.push(r.di)  # 1C57
            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1C5B, far=False)  # 1C58
    return r


def _result_at_1c5e(mem, r, variant):
    r.di = ss16(mem, r, r.bp + 4)  # 1C5E
    r.es, r.di = ss16(mem, r, r.di + 4 + 2), ss16(mem, r, r.di + 4)  # 1C61
    r.push(r.es)  # 1C65
    r.push(r.di)  # 1C66
    r = yield from _result_call(mem, r, variant, '1771:5C60', 2, 0x1C6C, far=True)  # 1C67
    _left, _right = r.ax, 3  # 1C6C
    if _left < _right:  # 1C6F
        r.push(ss16(mem, r, r.bp + 4))  # 1C74
        r = yield from _result_call(mem, r, variant, '000E:09DB', 1, 0x1C7A, far=False)  # 1C77
        _left, _right = r.al, 0  # 1C7A
        if _left != _right:  # 1C7C
            r.ax = 4  # 1C81
            r.push(r.ax)  # 1C84
            r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x1C8A, far=True)  # 1C85
            _left, _right = r.ax, 1  # 1C8A
            if _left != _right:  # 1C8D
                _left, _right = r.ax, 2  # 1CAA
                if _left != _right:  # 1CAD
                    _left, _right = r.ax, 3  # 1CC3
                    if _left != _right:  # 1CC6
                        _left, _right = r.ax, 4  # 1CE3
                        if _left != _right:  # 1CE6
                            pass
                        else:
                            r.di = 0x10ff  # 1CE8
                            r.push(mem.seg(0xE))  # 1CEB
                            r.push(r.di)  # 1CEC
                            r.di = r.bp - 0x108  # 1CED
                            r.push(r.ss)  # 1CF1
                            r.push(r.di)  # 1CF2
                            r.push(ss16(mem, r, r.bp + 4))  # 1CF3
                            r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1CF9, far=False)  # 1CF6
                            r.di = 0xd0a  # 1CF9
                            r.push(mem.seg(0xE))  # 1CFC
                            r.push(r.di)  # 1CFD
                            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1D01, far=False)  # 1CFE
                    else:
                        r.di = r.bp - 0x108  # 1CC8
                        r.push(r.ss)  # 1CCC
                        r.push(r.di)  # 1CCD
                        r.push(ss16(mem, r, r.bp + 4))  # 1CCE
                        r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x1CD4, far=False)  # 1CD1
                        r.di = 0x10f0  # 1CD4
                        r.push(mem.seg(0xE))  # 1CD7
                        r.push(r.di)  # 1CD8
                        r.di = 0xd0a  # 1CD9
                        r.push(mem.seg(0xE))  # 1CDC
                        r.push(r.di)  # 1CDD
                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1CE1, far=False)  # 1CDE
                else:
                    r.di = 0x10e2  # 1CAF
                    r.push(mem.seg(0xE))  # 1CB2
                    r.push(r.di)  # 1CB3
                    r.di = 0xd0a  # 1CB4
                    r.push(mem.seg(0xE))  # 1CB7
                    r.push(r.di)  # 1CB8
                    r.di = 0xd0a  # 1CB9
                    r.push(mem.seg(0xE))  # 1CBC
                    r.push(r.di)  # 1CBD
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1CC1, far=False)  # 1CBE
            else:
                r.di = 0x10cb  # 1C8F
                r.push(mem.seg(0xE))  # 1C92
                r.push(r.di)  # 1C93
                r.di = 0x10d7  # 1C94
                r.push(mem.seg(0xE))  # 1C97
                r.push(r.di)  # 1C98
                r.di = r.bp - 0x108  # 1C99
                r.push(r.ss)  # 1C9D
                r.push(r.di)  # 1C9E
                r.push(ss16(mem, r, r.bp + 4))  # 1C9F
                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1CA5, far=False)  # 1CA2
                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1CA8, far=False)  # 1CA5
            return (yield from _result_at_1d01(mem, r, variant))
        else:
            r.push(ss16(mem, r, r.bp + 4))  # 1D04
            r = yield from _result_call(mem, r, variant, '000E:0A53', 1, 0x1D0A, far=False)  # 1D07
            _left, _right = r.al, 0  # 1D0A
            if _left != _right:  # 1D0C
                r.ax = 4  # 1D11
                r.push(r.ax)  # 1D14
                r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x1D1A, far=True)  # 1D15
                _left, _right = r.ax, 1  # 1D1A
                if _left != _right:  # 1D1D
                    _left, _right = r.ax, 2  # 1D3A
                    if _left != _right:  # 1D3D
                        _left, _right = r.ax, 3  # 1D5A
                        if _left != _right:  # 1D5D
                            _left, _right = r.ax, 4  # 1D7A
                            if _left != _right:  # 1D7D
                                pass
                            else:
                                r.di = r.bp - 0x108  # 1D7F
                                r.push(r.ss)  # 1D83
                                r.push(r.di)  # 1D84
                                r.push(ss16(mem, r, r.bp + 4))  # 1D85
                                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1D8B, far=False)  # 1D88
                                r.di = 0x1140  # 1D8B
                                r.push(mem.seg(0xE))  # 1D8E
                                r.push(r.di)  # 1D8F
                                r.di = 0xd0a  # 1D90
                                r.push(mem.seg(0xE))  # 1D93
                                r.push(r.di)  # 1D94
                                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1D98, far=False)  # 1D95
                        else:
                            r.di = 0x112f  # 1D5F
                            r.push(mem.seg(0xE))  # 1D62
                            r.push(r.di)  # 1D63
                            r.di = r.bp - 0x108  # 1D64
                            r.push(r.ss)  # 1D68
                            r.push(r.di)  # 1D69
                            r.push(ss16(mem, r, r.bp + 4))  # 1D6A
                            r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1D70, far=False)  # 1D6D
                            r.di = 0xd0a  # 1D70
                            r.push(mem.seg(0xE))  # 1D73
                            r.push(r.di)  # 1D74
                            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1D78, far=False)  # 1D75
                    else:
                        r.di = r.bp - 0x108  # 1D3F
                        r.push(r.ss)  # 1D43
                        r.push(r.di)  # 1D44
                        r.push(ss16(mem, r, r.bp + 4))  # 1D45
                        r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1D4B, far=False)  # 1D48
                        r.di = 0x1124  # 1D4B
                        r.push(mem.seg(0xE))  # 1D4E
                        r.push(r.di)  # 1D4F
                        r.di = 0xd0a  # 1D50
                        r.push(mem.seg(0xE))  # 1D53
                        r.push(r.di)  # 1D54
                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1D58, far=False)  # 1D55
                else:
                    r.di = 0x110d  # 1D1F
                    r.push(mem.seg(0xE))  # 1D22
                    r.push(r.di)  # 1D23
                    r.di = 0x1115  # 1D24
                    r.push(mem.seg(0xE))  # 1D27
                    r.push(r.di)  # 1D28
                    r.di = r.bp - 0x108  # 1D29
                    r.push(r.ss)  # 1D2D
                    r.push(r.di)  # 1D2E
                    r.push(ss16(mem, r, r.bp + 4))  # 1D2F
                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1D35, far=False)  # 1D32
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1D38, far=False)  # 1D35
                return (yield from _result_at_1d98(mem, r, variant))
            else:
                r.ax = 3  # 1D9A
                r.push(r.ax)  # 1D9D
                r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x1DA3, far=True)  # 1D9E
                _left, _right = r.ax, 1  # 1DA3
                if _left != _right:  # 1DA6
                    _left, _right = r.ax, 2  # 1DC3
                    if _left != _right:  # 1DC6
                        _left, _right = r.ax, 3  # 1DE3
                        if _left != _right:  # 1DE6
                            pass
                        else:
                            r.di = r.bp - 0x108  # 1DE8
                            r.push(r.ss)  # 1DEC
                            r.push(r.di)  # 1DED
                            r.push(ss16(mem, r, r.bp + 4))  # 1DEE
                            r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1DF4, far=False)  # 1DF1
                            r.di = 0x1170  # 1DF4
                            r.push(mem.seg(0xE))  # 1DF7
                            r.push(r.di)  # 1DF8
                            r.di = 0x117b  # 1DF9
                            r.push(mem.seg(0xE))  # 1DFC
                            r.push(r.di)  # 1DFD
                            r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1E01, far=False)  # 1DFE
                    else:
                        r.di = r.bp - 0x108  # 1DC8
                        r.push(r.ss)  # 1DCC
                        r.push(r.di)  # 1DCD
                        r.push(ss16(mem, r, r.bp + 4))  # 1DCE
                        r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1DD4, far=False)  # 1DD1
                        r.di = 0x1165  # 1DD4
                        r.push(mem.seg(0xE))  # 1DD7
                        r.push(r.di)  # 1DD8
                        r.di = 0xd0a  # 1DD9
                        r.push(mem.seg(0xE))  # 1DDC
                        r.push(r.di)  # 1DDD
                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1DE1, far=False)  # 1DDE
                else:
                    r.di = 0x114f  # 1DA8
                    r.push(mem.seg(0xE))  # 1DAB
                    r.push(r.di)  # 1DAC
                    r.di = r.bp - 0x108  # 1DAD
                    r.push(r.ss)  # 1DB1
                    r.push(r.di)  # 1DB2
                    r.push(ss16(mem, r, r.bp + 4))  # 1DB3
                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1DB9, far=False)  # 1DB6
                    r.di = 0x1155  # 1DB9
                    r.push(mem.seg(0xE))  # 1DBC
                    r.push(r.di)  # 1DBD
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1DC1, far=False)  # 1DBE
        return (yield from _result_at_1e01(mem, r, variant))
    else:
        r.push(ss16(mem, r, r.bp + 4))  # 1E04
        r = yield from _result_call(mem, r, variant, '000E:09DB', 1, 0x1E0A, far=False)  # 1E07
        _left, _right = r.al, 0  # 1E0A
        if _left == _right:  # 1E0C
            r.push(ss16(mem, r, r.bp + 4))  # 1E58
            r = yield from _result_call(mem, r, variant, '000E:0A53', 1, 0x1E5E, far=False)  # 1E5B
            _left, _right = r.al, 0  # 1E5E
            if _left == _right:  # 1E60
                r.ax = 2  # 1EC8
                r.push(r.ax)  # 1ECB
                r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x1ED1, far=True)  # 1ECC
                _left, _right = r.ax, 1  # 1ED1
                if _left != _right:  # 1ED4
                    _left, _right = r.ax, 2  # 1F0D
                    if _left != _right:  # 1F10
                        pass
                    else:
                        r.di = r.bp - 0x108  # 1F12
                        r.push(r.ss)  # 1F16
                        r.push(r.di)  # 1F17
                        r.push(ss16(mem, r, r.bp + 4))  # 1F18
                        r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1F1E, far=False)  # 1F1B
                        r.di = 0x11cf  # 1F1E
                        r.push(mem.seg(0xE))  # 1F21
                        r.push(r.di)  # 1F22
                        r.di = r.bp - 0x308  # 1F23
                        r.push(r.ss)  # 1F27
                        r.push(r.di)  # 1F28
                        r.di = 0xdcc  # 1F29
                        r.push(mem.seg(0xE))  # 1F2C
                        r.push(r.di)  # 1F2D
                        r = yield from _result_call(mem, r, variant, '23E4:062A', 2, 0x1F33, far=True)  # 1F2E
                        r.di = r.bp - 0x208  # 1F33
                        r.push(r.ss)  # 1F37
                        r.push(r.di)  # 1F38
                        r.push(ss16(mem, r, r.bp + 4))  # 1F39
                        r = yield from _result_call(mem, r, variant, '000E:0B0A', 1, 0x1F3F, far=False)  # 1F3C
                        r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x1F44, far=True)  # 1F3F
                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1F47, far=False)  # 1F44
                else:
                    r.di = r.bp - 0x108  # 1ED6
                    r.push(r.ss)  # 1EDA
                    r.push(r.di)  # 1EDB
                    r.push(ss16(mem, r, r.bp + 4))  # 1EDC
                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1EE2, far=False)  # 1EDF
                    r.di = 0x11c6  # 1EE2
                    r.push(mem.seg(0xE))  # 1EE5
                    r.push(r.di)  # 1EE6
                    r.di = r.bp - 0x308  # 1EE7
                    r.push(r.ss)  # 1EEB
                    r.push(r.di)  # 1EEC
                    r.di = 0xdcc  # 1EED
                    r.push(mem.seg(0xE))  # 1EF0
                    r.push(r.di)  # 1EF1
                    r = yield from _result_call(mem, r, variant, '23E4:062A', 2, 0x1EF7, far=True)  # 1EF2
                    r.di = r.bp - 0x208  # 1EF7
                    r.push(r.ss)  # 1EFB
                    r.push(r.di)  # 1EFC
                    r.push(ss16(mem, r, r.bp + 4))  # 1EFD
                    r = yield from _result_call(mem, r, variant, '000E:0B0A', 1, 0x1F03, far=False)  # 1F00
                    r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x1F08, far=True)  # 1F03
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1F0B, far=False)  # 1F08
            else:
                r.ax = 2  # 1E62
                r.push(r.ax)  # 1E65
                r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x1E6B, far=True)  # 1E66
                _left, _right = r.ax, 1  # 1E6B
                if _left != _right:  # 1E6E
                    _left, _right = r.ax, 2  # 1EA7
                    if _left != _right:  # 1EAA
                        pass
                    else:
                        r.di = 0x11b6  # 1EAC
                        r.push(mem.seg(0xE))  # 1EAF
                        r.push(r.di)  # 1EB0
                        r.di = r.bp - 0x108  # 1EB1
                        r.push(r.ss)  # 1EB5
                        r.push(r.di)  # 1EB6
                        r.push(ss16(mem, r, r.bp + 4))  # 1EB7
                        r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x1EBD, far=False)  # 1EBA
                        r.di = 0xd0a  # 1EBD
                        r.push(mem.seg(0xE))  # 1EC0
                        r.push(r.di)  # 1EC1
                        r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1EC5, far=False)  # 1EC2
                else:
                    r.di = r.bp - 0x108  # 1E70
                    r.push(r.ss)  # 1E74
                    r.push(r.di)  # 1E75
                    r.push(ss16(mem, r, r.bp + 4))  # 1E76
                    r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1E7C, far=False)  # 1E79
                    r.di = 0x11a6  # 1E7C
                    r.push(mem.seg(0xE))  # 1E7F
                    r.push(r.di)  # 1E80
                    r.di = r.bp - 0x308  # 1E81
                    r.push(r.ss)  # 1E85
                    r.push(r.di)  # 1E86
                    r.di = 0x11b2  # 1E87
                    r.push(mem.seg(0xE))  # 1E8A
                    r.push(r.di)  # 1E8B
                    r = yield from _result_call(mem, r, variant, '23E4:062A', 2, 0x1E91, far=True)  # 1E8C
                    r.di = r.bp - 0x208  # 1E91
                    r.push(r.ss)  # 1E95
                    r.push(r.di)  # 1E96
                    r.push(ss16(mem, r, r.bp + 4))  # 1E97
                    r = yield from _result_call(mem, r, variant, '000E:0B0A', 1, 0x1E9D, far=False)  # 1E9A
                    r = yield from _result_call(mem, r, variant, '23E4:06B7', 2, 0x1EA2, far=True)  # 1E9D
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1EA5, far=False)  # 1EA2
                return (yield from _result_at_1ec5(mem, r, variant))
        else:
            r.ax = 2  # 1E0E
            r.push(r.ax)  # 1E11
            r = yield from _result_call(mem, r, variant, '214B:06B1', 1, 0x1E17, far=True)  # 1E12
            _left, _right = r.ax, 1  # 1E17
            if _left != _right:  # 1E1A
                _left, _right = r.ax, 2  # 1E3E
                if _left != _right:  # 1E41
                    pass
                else:
                    r.di = 0x118f  # 1E43
                    r.push(mem.seg(0xE))  # 1E46
                    r.push(r.di)  # 1E47
                    r.di = 0x119b  # 1E48
                    r.push(mem.seg(0xE))  # 1E4B
                    r.push(r.di)  # 1E4C
                    r.di = 0xd0a  # 1E4D
                    r.push(mem.seg(0xE))  # 1E50
                    r.push(r.di)  # 1E51
                    r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1E55, far=False)  # 1E52
            else:
                r.di = r.bp - 0x108  # 1E1C
                r.push(r.ss)  # 1E20
                r.push(r.di)  # 1E21
                r.push(ss16(mem, r, r.bp + 4))  # 1E22
                r = yield from _result_call(mem, r, variant, '000E:0B4D', 1, 0x1E28, far=False)  # 1E25
                r.di = 0x1182  # 1E28
                r.push(mem.seg(0xE))  # 1E2B
                r.push(r.di)  # 1E2C
                r.di = r.bp - 0x208  # 1E2D
                r.push(r.ss)  # 1E31
                r.push(r.di)  # 1E32
                r.push(ss16(mem, r, r.bp + 4))  # 1E33
                r = yield from _result_call(mem, r, variant, '000E:0ACB', 1, 0x1E39, far=False)  # 1E36
                r = yield from _result_call(mem, r, variant, '000E:062F', 6, 0x1E3C, far=False)  # 1E39
            return (yield from _result_at_1e55(mem, r, variant))
    return r


def _result_at_1d01(mem, r, variant):
    return (yield from _result_at_1e01(mem, r, variant))
    return r


def _result_at_1d98(mem, r, variant):
    return (yield from _result_at_1e01(mem, r, variant))
    return r


def _result_at_1e01(mem, r, variant):
    yield from ()
    return r


def _result_at_1e55(mem, r, variant):
    yield from ()
    return r


def _result_at_1ec5(mem, r, variant):
    yield from ()
    return r


# T122c [confirmed: F039; code/seg_000E_03.asm 2071-2389/26F2-2E1E].
# The two real recommendation loops are explicit below. Only their acyclic
# bodies/tails and the secondary column's acyclic branches are factored.
def _secondary_call(mem, r, variant, target, words, ret, far):
    if variant == 'secondary-draw-dropped' and target == '214B:06B1' and 0x26F2 < ret < 0x2E1F:
        for _ in range(words):
            pop(mem, r)
        r.ax = 1
        return r
    r = yield from _result_call(mem, r, variant, target, words, ret, far)
    if variant == 'secondary-text-byte-flipped' and ret == 0x274D:
        off, seg = ss16(mem, r, r.sp), ss16(mem, r, r.sp + 2)
        p = mem.addr(seg, off)
        if mem.u8(p):
            mem.w8(p + 1, mem.u8(p + 1) ^ 1, '000E:274D')
    return r


@PORTS.port('000E:2071', ret='ret 2')
def recommend_pool_player(mem, variant):
    """Original 20-slot minimum and 80-slot pool maximum, with strict ties.

    Both candidate improvements make the original second strength call.
    Pool candidates have no additional availability check in this caller.
    """
    r = Regs(mem)
    r.enter(0x312)
    r.di = ss16(mem, r, r.bp + 4)  # 2078
    r.di = ss16(mem, r, r.di + 4)  # 207B
    r.ax = ss16(mem, r, r.di + 8)  # 207F
    r.dx = 0xbf  # 2083
    mul(r, r.dx)  # 2086
    r.es, r.di = mem.ds16((0xa917 + 2) & M16), mem.ds16((0xa917) & M16)  # 2088
    r.di = r.di + r.ax  # 208C
    r.local16(-0xd, r.di)  # 208E
    r.local16(-0xb, r.es)  # 2091
    r.ax = 0xe  # 2094
    r.push(r.ax)  # 2097
    r = yield from _secondary_call(mem, r, variant, '214B:06B1', 1, 0x209D, far=True)  # 2098
    r.ax = r.ax - 1  # 209D
    mem.wds8(0x22, r.al, '000E:209E')  # 209E
    r.local8(-1, 0)  # 20A1
    r.es, r.di = ss16(mem, r, r.bp - 0xd + 2), ss16(mem, r, r.bp - 0xd)  # 20A5
    r.al = mem.u8(mem.addr(r.es, r.di + 0x2e))  # 20A8
    r.ah = 0  # 20AC
    r.ax = r.ax - 0x80  # 20AE
    r.es, r.di = mem.ds16((0xa923 + 2) & M16), mem.ds16((0xa923) & M16)  # 20B1
    r.di = r.di + r.ax  # 20B5
    _left, _right = mem.u8(mem.addr(r.es, r.di + 0x13)), 0  # 20B7
    if _left == _right:  # 20BC
        r.local16(-3, 0xffff)  # 20C1
        r.local16(-5, 1)  # 20C6
        while True:  # 20D0; back edge 2158 -> 20CD
            r = yield from _secondary_squad_20d0(mem, r, variant)
            _left, _right = ss16(mem, r, r.bp - 5), 0x14  # 2152
            if _left == _right:  # 2156
                break
            r.local16(-5, ss16(mem, r, r.bp - 5) + 1)  # 20CD
        _left, _right = ss16(mem, r, r.bp - 3), 0xffff  # 215B
        if _left < _right:  # 215F
            r.es, r.di = ss16(mem, r, r.bp - 0xd + 2), ss16(mem, r, r.bp - 0xd)  # 2164
            r.al = mem.u8(mem.addr(r.es, r.di + 0x2e))  # 2167
            r.ah = 0  # 216B
            r.ax = r.ax - 0x80  # 216D
            r.di = r.ax  # 2170
            r.di = r.di << 1  # 2172
            r.ax = mem.ds16((r.di + 0x6d18) & M16)  # 2174
            r.ax = r.ax + 0x4f  # 2178
            r.local16(-0xf, r.ax)  # 217B
            r.es, r.di = ss16(mem, r, r.bp - 0xd + 2), ss16(mem, r, r.bp - 0xd)  # 217E
            r.al = mem.u8(mem.addr(r.es, r.di + 0x2e))  # 2181
            r.ah = 0  # 2185
            r.ax = r.ax - 0x80  # 2187
            r.di = r.ax  # 218A
            r.di = r.di << 1  # 218C
            r.ax = mem.ds16((r.di + 0x6d18) & M16)  # 218E
            _left, _right = r.ax, ss16(mem, r, r.bp - 0xf)  # 2192
            if _left <= _right:  # 2195 (JA skips the pool loop)
                r.local16(-5, r.ax)  # 2197
                while True:  # 219F; back edge 2210 -> 219C
                    r = yield from _secondary_pool_219f(mem, r, variant)
                    r.ax = ss16(mem, r, r.bp - 5)  # 220A
                    _left, _right = r.ax, ss16(mem, r, r.bp - 0xf)  # 220D
                    if _left == _right:  # 2210
                        break
                    r.local16(-5, ss16(mem, r, r.bp - 5) + 1)  # 219C
            r.ax = ss16(mem, r, r.bp - 7)  # 2212
            r.dx = 0x14  # 2215
            mul(r, r.dx)  # 2218
            r.es, r.di = mem.ds16((0xa91b + 2) & M16), mem.ds16((0xa91b) & M16)  # 221A
            r.di = r.di + r.ax  # 221E
            r.local16(-0x11, r.di)  # 2220
            r.local16(-0xf, r.es)  # 2223
            r.push(ss16(mem, r, r.bp - 7))  # 2226
            r = yield from _secondary_call(mem, r, variant, '1771:377E', 1, 0x222E, far=True)  # 2229
            _left, _right = r.ax, ss16(mem, r, r.bp - 3)  # 222E
            if _left < _right:  # 2231
                r.ax = 0xa  # 2236
                r.push(r.ax)  # 2239
                r = yield from _secondary_call(mem, r, variant, '214B:06B1', 1, 0x223F, far=True)  # 223A
                r = yield from _secondary_recommend_223f(mem, r, variant)
    r.al = ss8(mem, r, r.bp - 1)  # 2381
    return _end(r, value=True)


def _secondary_squad_20d0(mem, r, variant):
    r.ax = ss16(mem, r, r.bp - 5)  # 20D0
    r.ax = r.ax << 1  # 20D3
    r.es, r.di = ss16(mem, r, r.bp - 0xd + 2), ss16(mem, r, r.bp - 0xd)  # 20D5
    r.di = r.di + r.ax  # 20D8
    r.ax = mem.u16(mem.addr(r.es, r.di - 2))  # 20DA
    r.dx = 0x14  # 20DE
    mul(r, r.dx)  # 20E1
    r.es, r.di = mem.ds16((0xa91b + 2) & M16), mem.ds16((0xa91b) & M16)  # 20E3
    r.di = r.di + r.ax  # 20E7
    r.local16(-0x11, r.di)  # 20E9
    r.local16(-0xf, r.es)  # 20EC
    r.es, r.di = ss16(mem, r, r.bp - 0x11 + 2), ss16(mem, r, r.bp - 0x11)  # 20EF
    r.al = mem.u8(mem.addr(r.es, r.di + 6))  # 20F2
    _left, _right = r.al, mem.ds8((0x22) & M16)  # 20F6
    if _left != _right:  # 20FA
        pass
    else:
        r.ax = ss16(mem, r, r.bp - 5)  # 20FC
        r.ax = r.ax << 1  # 20FF
        r.es, r.di = ss16(mem, r, r.bp - 0xd + 2), ss16(mem, r, r.bp - 0xd)  # 2101
        r.di = r.di + r.ax  # 2104
        r.push(mem.u16(mem.addr(r.es, r.di - 2)))  # 2106
        r = yield from _secondary_call(mem, r, variant, '1771:3216', 1, 0x210F, far=True)  # 210A
        _left, _right = r.al, 0  # 210F
        if _left != _right:  # 2111
            pass
        else:
            r.ax = ss16(mem, r, r.bp - 5)  # 2113
            r.ax = r.ax << 1  # 2116
            r.es, r.di = ss16(mem, r, r.bp - 0xd + 2), ss16(mem, r, r.bp - 0xd)  # 2118
            r.di = r.di + r.ax  # 211B
            r.push(mem.u16(mem.addr(r.es, r.di - 2)))  # 211D
            r = yield from _secondary_call(mem, r, variant, '1771:377E', 1, 0x2126, far=True)  # 2121
            _left, _right = r.ax, ss16(mem, r, r.bp - 3)  # 2126
            if _left >= _right:  # 2129
                pass
            else:
                r.ax = ss16(mem, r, r.bp - 5)  # 212B
                r.ax = r.ax << 1  # 212E
                r.es, r.di = ss16(mem, r, r.bp - 0xd + 2), ss16(mem, r, r.bp - 0xd)  # 2130
                r.di = r.di + r.ax  # 2133
                r.push(mem.u16(mem.addr(r.es, r.di - 2)))  # 2135
                r = yield from _secondary_call(mem, r, variant, '1771:377E', 1, 0x213E, far=True)  # 2139
                r.local16(-3, r.ax)  # 213E
                r.ax = ss16(mem, r, r.bp - 5)  # 2141
                r.ax = r.ax << 1  # 2144
                r.es, r.di = ss16(mem, r, r.bp - 0xd + 2), ss16(mem, r, r.bp - 0xd)  # 2146
                r.di = r.di + r.ax  # 2149
                r.ax = mem.u16(mem.addr(r.es, r.di - 2))  # 214B
                r.local16(-7, r.ax)  # 214F
    return r


def _secondary_pool_219f(mem, r, variant):
    r.ax = ss16(mem, r, r.bp - 5)  # 219F
    r.ax = r.ax << 1  # 21A2
    r.es, r.di = mem.ds16((0xa927 + 2) & M16), mem.ds16((0xa927) & M16)  # 21A4
    r.di = r.di + r.ax  # 21A8
    r.ax = mem.u16(mem.addr(r.es, r.di))  # 21AA
    r.dx = 0x14  # 21AD
    mul(r, r.dx)  # 21B0
    r.es, r.di = mem.ds16((0xa91b + 2) & M16), mem.ds16((0xa91b) & M16)  # 21B2
    r.di = r.di + r.ax  # 21B6
    r.local16(-0x13, r.di)  # 21B8
    r.local16(-0x11, r.es)  # 21BB
    r.es, r.di = ss16(mem, r, r.bp - 0x13 + 2), ss16(mem, r, r.bp - 0x13)  # 21BE
    r.al = mem.u8(mem.addr(r.es, r.di + 7))  # 21C1
    _left, _right = r.al, mem.ds8((0x22) & M16)  # 21C5
    if _left != _right:  # 21C9
        pass
    else:
        r.ax = ss16(mem, r, r.bp - 5)  # 21CB
        r.ax = r.ax << 1  # 21CE
        r.es, r.di = mem.ds16((0xa927 + 2) & M16), mem.ds16((0xa927) & M16)  # 21D0
        r.di = r.di + r.ax  # 21D4
        r.push(mem.u16(mem.addr(r.es, r.di)))  # 21D6
        r = yield from _secondary_call(mem, r, variant, '1771:377E', 1, 0x21DE, far=True)  # 21D9
        _left, _right = r.ax, ss16(mem, r, r.bp - 3)  # 21DE
        if _left <= _right:  # 21E1
            pass
        else:
            r.ax = ss16(mem, r, r.bp - 5)  # 21E3
            r.ax = r.ax << 1  # 21E6
            r.es, r.di = mem.ds16((0xa927 + 2) & M16), mem.ds16((0xa927) & M16)  # 21E8
            r.di = r.di + r.ax  # 21EC
            r.push(mem.u16(mem.addr(r.es, r.di)))  # 21EE
            r = yield from _secondary_call(mem, r, variant, '1771:377E', 1, 0x21F6, far=True)  # 21F1
            r.local16(-3, r.ax)  # 21F6
            r.ax = ss16(mem, r, r.bp - 5)  # 21F9
            r.ax = r.ax << 1  # 21FC
            r.es, r.di = mem.ds16((0xa927 + 2) & M16), mem.ds16((0xa927) & M16)  # 21FE
            r.di = r.di + r.ax  # 2202
            r.ax = mem.u16(mem.addr(r.es, r.di))  # 2204
            r.local16(-9, r.ax)  # 2207
    return r


def _secondary_recommend_223f(mem, r, variant):
    r.local16(-3, r.ax)  # 223F
    r.ax = ss16(mem, r, r.bp - 3)  # 2242
    _left, _right = r.ax, 1  # 2245
    if _left < _right:  # 2248
        return (yield from _secondary_recommend_228c(mem, r, variant))
    else:
        _left, _right = r.ax, 5  # 224A
        if _left > _right:  # 224D
            return (yield from _secondary_recommend_228c(mem, r, variant))
        else:
            r.di = ss16(mem, r, r.bp - 3)  # 224F
            r.cx = (r.cx & 0xff00) | ((4) & 255)  # 2252
            r.di = r.di << (r.cx & 255)  # 2254
            r.di = r.di + 0x14  # 2256
            r.push(mem.DS)  # 225A
            r.push(r.di)  # 225B
            r.di = r.bp - 0x111  # 225C
            r.push(r.ss)  # 2260
            r.push(r.di)  # 2261
            r.push(ss16(mem, r, r.bp - 9))  # 2262
            r = yield from _secondary_call(mem, r, variant, '1771:2E93', 1, 0x226A, far=True)  # 2265
            r.di = 0x2014  # 226A
            r.push(mem.seg(0xE))  # 226D
            r.push(r.di)  # 226E
            r = yield from _secondary_call(mem, r, variant, '23E4:06B7', 2, 0x2274, far=True)  # 226F
            r.al = mem.ds8((0x22) & M16)  # 2274
            r.ah = 0  # 2277
            r.dx = 0x13  # 2279
            mul(r, r.dx)  # 227C
            r.di = r.ax  # 227E
            r.di = r.di + 0x69b6  # 2280
            r.push(mem.DS)  # 2284
            r.push(r.di)  # 2285
            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2289, far=False)  # 2286
    return (yield from _secondary_recommend_237d(mem, r, variant))
    return r


def _secondary_recommend_228c(mem, r, variant):
    _left, _right = r.ax, 6  # 228C
    if _left != _right:  # 228F
        _left, _right = r.ax, 7  # 22D7
        if _left != _right:  # 22DA
            _left, _right = r.ax, 8  # 230C
            if _left != _right:  # 230F
                _left, _right = r.ax, 9  # 233B
                if _left != _right:  # 233E
                    _left, _right = r.ax, 0xa  # 235D
                    if _left != _right:  # 2360
                        pass
                    else:
                        r.di = r.bp - 0x111  # 2362
                        r.push(r.ss)  # 2366
                        r.push(r.di)  # 2367
                        r.push(ss16(mem, r, r.bp - 9))  # 2368
                        r = yield from _secondary_call(mem, r, variant, '1771:2E93', 1, 0x2370, far=True)  # 236B
                        r.di = 0x205c  # 2370
                        r.push(mem.seg(0xE))  # 2373
                        r.push(r.di)  # 2374
                        r.di = 0x2065  # 2375
                        r.push(mem.seg(0xE))  # 2378
                        r.push(r.di)  # 2379
                        r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x237D, far=False)  # 237A
                else:
                    r.di = r.bp - 0x111  # 2340
                    r.push(r.ss)  # 2344
                    r.push(r.di)  # 2345
                    r.push(ss16(mem, r, r.bp - 9))  # 2346
                    r = yield from _secondary_call(mem, r, variant, '1771:2E93', 1, 0x234E, far=True)  # 2349
                    r.di = 0x204c  # 234E
                    r.push(mem.seg(0xE))  # 2351
                    r.push(r.di)  # 2352
                    r.di = 0x2055  # 2353
                    r.push(mem.seg(0xE))  # 2356
                    r.push(r.di)  # 2357
                    r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x235B, far=False)  # 2358
            else:
                r.al = mem.ds8((0x22) & M16)  # 2311
                r.ah = 0  # 2314
                r.dx = 0x13  # 2316
                mul(r, r.dx)  # 2319
                r.di = r.ax  # 231B
                r.di = r.di + 0x69b6  # 231D
                r.push(mem.DS)  # 2321
                r.push(r.di)  # 2322
                r.di = r.bp - 0x111  # 2323
                r.push(r.ss)  # 2327
                r.push(r.di)  # 2328
                r.push(ss16(mem, r, r.bp - 7))  # 2329
                r = yield from _secondary_call(mem, r, variant, '1771:2E93', 1, 0x2331, far=True)  # 232C
                r.di = 0x2042  # 2331
                r.push(mem.seg(0xE))  # 2334
                r.push(r.di)  # 2335
                r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2339, far=False)  # 2336
        else:
            r.di = r.bp - 0x111  # 22DC
            r.push(r.ss)  # 22E0
            r.push(r.di)  # 22E1
            r.push(ss16(mem, r, r.bp - 9))  # 22E2
            r = yield from _secondary_call(mem, r, variant, '1771:2E93', 1, 0x22EA, far=True)  # 22E5
            r.di = 0x202d  # 22EA
            r.push(mem.seg(0xE))  # 22ED
            r.push(r.di)  # 22EE
            r = yield from _secondary_call(mem, r, variant, '23E4:06B7', 2, 0x22F4, far=True)  # 22EF
            r.di = 0x2031  # 22F4
            r.push(mem.seg(0xE))  # 22F7
            r.push(r.di)  # 22F8
            r.di = r.bp - 0x211  # 22F9
            r.push(r.ss)  # 22FD
            r.push(r.di)  # 22FE
            r.push(ss16(mem, r, r.bp - 7))  # 22FF
            r = yield from _secondary_call(mem, r, variant, '1771:2E93', 1, 0x2307, far=True)  # 2302
            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x230A, far=False)  # 2307
    else:
        r.di = 0x2018  # 2291
        r.push(mem.seg(0xE))  # 2294
        r.push(r.di)  # 2295
        r.di = r.bp - 0x111  # 2296
        r.push(r.ss)  # 229A
        r.push(r.di)  # 229B
        r.push(ss16(mem, r, r.bp - 7))  # 229C
        r = yield from _secondary_call(mem, r, variant, '1771:2E93', 1, 0x22A4, far=True)  # 229F
        r.di = 0x2023  # 22A4
        r.push(mem.seg(0xE))  # 22A7
        r.push(r.di)  # 22A8
        r = yield from _secondary_call(mem, r, variant, '23E4:06B7', 2, 0x22AE, far=True)  # 22A9
        r.di = r.bp - 0x311  # 22AE
        r.push(r.ss)  # 22B2
        r.push(r.di)  # 22B3
        r.di = 0x2028  # 22B4
        r.push(mem.seg(0xE))  # 22B7
        r.push(r.di)  # 22B8
        r = yield from _secondary_call(mem, r, variant, '23E4:062A', 2, 0x22BE, far=True)  # 22B9
        r.di = r.bp - 0x211  # 22BE
        r.push(r.ss)  # 22C2
        r.push(r.di)  # 22C3
        r.push(ss16(mem, r, r.bp - 9))  # 22C4
        r = yield from _secondary_call(mem, r, variant, '1771:2E93', 1, 0x22CC, far=True)  # 22C7
        r = yield from _secondary_call(mem, r, variant, '23E4:06B7', 2, 0x22D1, far=True)  # 22CC
        r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x22D4, far=False)  # 22D1
    return (yield from _secondary_recommend_237d(mem, r, variant))
    return r


def _secondary_recommend_237d(mem, r, variant):
    yield from ()
    r.local8(-1, 1)  # 237D
    return r


@PORTS.port('000E:26F2', ret='ret 2')
def secondary_result_column(mem, variant):
    """Original right-column branch tree; recommendation 2071 remains a real call."""
    r = Regs(mem)
    r.enter(0x308)
    r = yield from _secondary_column_26f9(mem, r, variant)
    return _end(r)


def _secondary_column_26f9(mem, r, variant):
    r.di = ss16(mem, r, r.bp + 4)  # 26F9
    r.es, r.di = ss16(mem, r, r.di + 4 + 2), ss16(mem, r, r.di + 4)  # 26FC
    r.local16(-4, r.di)  # 2700
    r.local16(-2, r.es)  # 2703
    r.di = ss16(mem, r, r.bp + 4)  # 2706
    r.ax = ss16(mem, r, r.di + 8)  # 2709
    r.dx = 0xbf  # 270D
    mul(r, r.dx)  # 2710
    r.es, r.di = mem.ds16((0xa917 + 2) & M16), mem.ds16((0xa917) & M16)  # 2712
    r.di = r.di + r.ax  # 2716
    r.local16(-8, r.di)  # 2718
    r.local16(-6, r.es)  # 271B
    r.es, r.di = ss16(mem, r, r.bp - 4 + 2), ss16(mem, r, r.bp - 4)  # 271E
    r.al = mem.u8(mem.addr(r.es, r.di + 3))  # 2721
    r.di = ss16(mem, r, r.bp + 4)  # 2725
    _left, _right = r.al, ss8(mem, r, r.di - 1)  # 2728
    if _left == _right:  # 272C
        r.es, r.di = ss16(mem, r, r.bp - 4 + 2), ss16(mem, r, r.bp - 4)  # 2731
        r.al = mem.u8(mem.addr(r.es, r.di + 2))  # 2734
        _left, _right = r.al, 0xcb  # 2738
        if _left != _right:  # 273A
            _left, _right = r.al, 0x67  # 2774
            if _left != _right:  # 2776
                _left, _right = r.al, 0xc9  # 2794
                if _left == _right:  # 2796
                    return (yield from _secondary_column_279c(mem, r, variant))
                else:
                    _left, _right = r.al, 0x65  # 2798
                    if _left != _right:  # 279A
                        r.push(r.bp)  # 27C9
                        r = yield from _secondary_call(mem, r, variant, '000E:2071', 1, 0x27CD, far=False)  # 27CA
                        _left, _right = r.al, 0  # 27CD
                        if _left == _right:  # 27CF
                            r.es, r.di = ss16(mem, r, r.bp - 8 + 2), ss16(mem, r, r.bp - 8)  # 27D4
                            r.al = mem.u8(mem.addr(r.es, r.di + 0xac))  # 27D7
                            _left, _right = r.al, 1  # 27DC
                            if _left == _right:  # 27DE
                                r.ax = 4  # 27E3
                                r.push(r.ax)  # 27E6
                                r = yield from _secondary_call(mem, r, variant, '214B:06B1', 1, 0x27EC, far=True)  # 27E7
                                _left, _right = r.ax, 1  # 27EC
                                if _left != _right:  # 27EF
                                    _left, _right = r.ax, 2  # 280C
                                    if _left != _right:  # 280F
                                        _left, _right = r.ax, 3  # 2836
                                        if _left != _right:  # 2839
                                            _left, _right = r.ax, 4  # 2860
                                            if _left != _right:  # 2863
                                                pass
                                            else:
                                                r.di = r.bp - 0x108  # 2865
                                                r.push(r.ss)  # 2869
                                                r.push(r.di)  # 286A
                                                r.push(ss16(mem, r, r.bp + 4))  # 286B
                                                r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2871, far=False)  # 286E
                                                r.di = 0x240b  # 2871
                                                r.push(mem.seg(0xE))  # 2874
                                                r.push(r.di)  # 2875
                                                r.di = 0x2415  # 2876
                                                r.push(mem.seg(0xE))  # 2879
                                                r.push(r.di)  # 287A
                                                r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x287E, far=False)  # 287B
                                        else:
                                            r.di = 0x23ff  # 283B
                                            r.push(mem.seg(0xE))  # 283E
                                            r.push(r.di)  # 283F
                                            r.di = r.bp - 0x108  # 2840
                                            r.push(r.ss)  # 2844
                                            r.push(r.di)  # 2845
                                            r.push(ss16(mem, r, r.bp + 4))  # 2846
                                            r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x284C, far=False)  # 2849
                                            r.di = 0x23fc  # 284C
                                            r.push(mem.seg(0xE))  # 284F
                                            r.push(r.di)  # 2850
                                            r = yield from _secondary_call(mem, r, variant, '23E4:06B7', 2, 0x2856, far=True)  # 2851
                                            r.di = 0x23fe  # 2856
                                            r.push(mem.seg(0xE))  # 2859
                                            r.push(r.di)  # 285A
                                            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x285E, far=False)  # 285B
                                    else:
                                        r.di = 0x23ee  # 2811
                                        r.push(mem.seg(0xE))  # 2814
                                        r.push(r.di)  # 2815
                                        r.di = r.bp - 0x108  # 2816
                                        r.push(r.ss)  # 281A
                                        r.push(r.di)  # 281B
                                        r.push(ss16(mem, r, r.bp + 4))  # 281C
                                        r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2822, far=False)  # 281F
                                        r.di = 0x23fc  # 2822
                                        r.push(mem.seg(0xE))  # 2825
                                        r.push(r.di)  # 2826
                                        r = yield from _secondary_call(mem, r, variant, '23E4:06B7', 2, 0x282C, far=True)  # 2827
                                        r.di = 0x23fe  # 282C
                                        r.push(mem.seg(0xE))  # 282F
                                        r.push(r.di)  # 2830
                                        r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2834, far=False)  # 2831
                                else:
                                    r.di = 0x23d4  # 27F1
                                    r.push(mem.seg(0xE))  # 27F4
                                    r.push(r.di)  # 27F5
                                    r.di = 0x23e4  # 27F6
                                    r.push(mem.seg(0xE))  # 27F9
                                    r.push(r.di)  # 27FA
                                    r.di = r.bp - 0x108  # 27FB
                                    r.push(r.ss)  # 27FF
                                    r.push(r.di)  # 2800
                                    r.push(ss16(mem, r, r.bp + 4))  # 2801
                                    r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2807, far=False)  # 2804
                                    r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x280A, far=False)  # 2807
                                return (yield from _secondary_column_287e(mem, r, variant))
                            else:
                                _left, _right = r.al, 2  # 2881
                                if _left != _right:  # 2883
                                    _left, _right = r.al, 3  # 28BE
                                    if _left != _right:  # 28C0
                                        _left, _right = r.al, 4  # 28DE
                                        if _left != _right:  # 28E0
                                            _left, _right = r.al, 5  # 28FE
                                            if _left != _right:  # 2900
                                                _left, _right = r.al, 6  # 291E
                                                if _left != _right:  # 2920
                                                    _left, _right = r.al, 7  # 293E
                                                    if _left != _right:  # 2940
                                                        r.ax = 0x10  # 295E
                                                        r.push(r.ax)  # 2961
                                                        r = yield from _secondary_call(mem, r, variant, '214B:06B1', 1, 0x2967, far=True)  # 2962
                                                        _left, _right = r.ax, 1  # 2967
                                                        if _left != _right:  # 296A
                                                            _left, _right = r.ax, 2  # 2988
                                                            if _left != _right:  # 298B
                                                                _left, _right = r.ax, 3  # 29A9
                                                                if _left != _right:  # 29AC
                                                                    _left, _right = r.ax, 4  # 29CA
                                                                    if _left != _right:  # 29CD
                                                                        _left, _right = r.ax, 5  # 29EB
                                                                        if _left != _right:  # 29EE
                                                                            _left, _right = r.ax, 6  # 2A0C
                                                                            if _left != _right:  # 2A0F
                                                                                _left, _right = r.ax, 7  # 2A2D
                                                                                if s16(_left) < s16(_right):  # 2A30
                                                                                    return (yield from _secondary_column_2a6a(mem, r, variant))
                                                                                else:
                                                                                    _left, _right = r.ax, 9  # 2A32
                                                                                    if s16(_left) > s16(_right):  # 2A35
                                                                                        return (yield from _secondary_column_2a6a(mem, r, variant))
                                                                                    else:
                                                                                        r.di = r.bp - 0x108  # 2A37
                                                                                        r.push(r.ss)  # 2A3B
                                                                                        r.push(r.di)  # 2A3C
                                                                                        r.es, r.di = ss16(mem, r, r.bp - 8 + 2), ss16(mem, r, r.bp - 8)  # 2A3D
                                                                                        r.al = mem.u8(mem.addr(r.es, r.di + 0xac))  # 2A40
                                                                                        r.ah = 0  # 2A45
                                                                                        r.dx = 0  # 2A47
                                                                                        r.push(r.dx)  # 2A49
                                                                                        r.push(r.ax)  # 2A4A
                                                                                        r = yield from _secondary_call(mem, r, variant, '214B:09DA', 2, 0x2A50, far=True)  # 2A4B
                                                                                        r.di = 0x2500  # 2A50
                                                                                        r.push(mem.seg(0xE))  # 2A53
                                                                                        r.push(r.di)  # 2A54
                                                                                        r = yield from _secondary_call(mem, r, variant, '23E4:06B7', 2, 0x2A5A, far=True)  # 2A55
                                                                                        r.di = 0x2506  # 2A5A
                                                                                        r.push(mem.seg(0xE))  # 2A5D
                                                                                        r.push(r.di)  # 2A5E
                                                                                        r.di = 0x23fe  # 2A5F
                                                                                        r.push(mem.seg(0xE))  # 2A62
                                                                                        r.push(r.di)  # 2A63
                                                                                        r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2A67, far=False)  # 2A64
                                                                            else:
                                                                                r.di = 0x24f4  # 2A11
                                                                                r.push(mem.seg(0xE))  # 2A14
                                                                                r.push(r.di)  # 2A15
                                                                                r.di = r.bp - 0x108  # 2A16
                                                                                r.push(r.ss)  # 2A1A
                                                                                r.push(r.di)  # 2A1B
                                                                                r.push(ss16(mem, r, r.bp + 4))  # 2A1C
                                                                                r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2A22, far=False)  # 2A1F
                                                                                r.di = 0x23fe  # 2A22
                                                                                r.push(mem.seg(0xE))  # 2A25
                                                                                r.push(r.di)  # 2A26
                                                                                r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2A2A, far=False)  # 2A27
                                                                        else:
                                                                            r.di = r.bp - 0x108  # 29F0
                                                                            r.push(r.ss)  # 29F4
                                                                            r.push(r.di)  # 29F5
                                                                            r.push(ss16(mem, r, r.bp + 4))  # 29F6
                                                                            r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x29FC, far=False)  # 29F9
                                                                            r.di = 0x24dd  # 29FC
                                                                            r.push(mem.seg(0xE))  # 29FF
                                                                            r.push(r.di)  # 2A00
                                                                            r.di = 0x24e9  # 2A01
                                                                            r.push(mem.seg(0xE))  # 2A04
                                                                            r.push(r.di)  # 2A05
                                                                            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2A09, far=False)  # 2A06
                                                                    else:
                                                                        r.di = 0x2439  # 29CF
                                                                        r.push(mem.seg(0xE))  # 29D2
                                                                        r.push(r.di)  # 29D3
                                                                        r.di = r.bp - 0x108  # 29D4
                                                                        r.push(r.ss)  # 29D8
                                                                        r.push(r.di)  # 29D9
                                                                        r.push(ss16(mem, r, r.bp + 4))  # 29DA
                                                                        r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x29E0, far=False)  # 29DD
                                                                        r.di = 0x23fe  # 29E0
                                                                        r.push(mem.seg(0xE))  # 29E3
                                                                        r.push(r.di)  # 29E4
                                                                        r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x29E8, far=False)  # 29E5
                                                                else:
                                                                    r.di = r.bp - 0x108  # 29AE
                                                                    r.push(r.ss)  # 29B2
                                                                    r.push(r.di)  # 29B3
                                                                    r.push(ss16(mem, r, r.bp + 4))  # 29B4
                                                                    r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x29BA, far=False)  # 29B7
                                                                    r.di = 0x24d2  # 29BA
                                                                    r.push(mem.seg(0xE))  # 29BD
                                                                    r.push(r.di)  # 29BE
                                                                    r.di = 0x23fe  # 29BF
                                                                    r.push(mem.seg(0xE))  # 29C2
                                                                    r.push(r.di)  # 29C3
                                                                    r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x29C7, far=False)  # 29C4
                                                            else:
                                                                r.di = 0x24b6  # 298D
                                                                r.push(mem.seg(0xE))  # 2990
                                                                r.push(r.di)  # 2991
                                                                r.di = r.bp - 0x108  # 2992
                                                                r.push(r.ss)  # 2996
                                                                r.push(r.di)  # 2997
                                                                r.push(ss16(mem, r, r.bp + 4))  # 2998
                                                                r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x299E, far=False)  # 299B
                                                                r.di = 0x24c0  # 299E
                                                                r.push(mem.seg(0xE))  # 29A1
                                                                r.push(r.di)  # 29A2
                                                                r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x29A6, far=False)  # 29A3
                                                        else:
                                                            r.di = r.bp - 0x108  # 296C
                                                            r.push(r.ss)  # 2970
                                                            r.push(r.di)  # 2971
                                                            r.push(ss16(mem, r, r.bp + 4))  # 2972
                                                            r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2978, far=False)  # 2975
                                                            r.di = 0x24a0  # 2978
                                                            r.push(mem.seg(0xE))  # 297B
                                                            r.push(r.di)  # 297C
                                                            r.di = 0x24ae  # 297D
                                                            r.push(mem.seg(0xE))  # 2980
                                                            r.push(r.di)  # 2981
                                                            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2985, far=False)  # 2982
                                                    else:
                                                        r.di = r.bp - 0x108  # 2942
                                                        r.push(r.ss)  # 2946
                                                        r.push(r.di)  # 2947
                                                        r.push(ss16(mem, r, r.bp + 4))  # 2948
                                                        r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x294E, far=False)  # 294B
                                                        r.di = 0x248a  # 294E
                                                        r.push(mem.seg(0xE))  # 2951
                                                        r.push(r.di)  # 2952
                                                        r.di = 0x249a  # 2953
                                                        r.push(mem.seg(0xE))  # 2956
                                                        r.push(r.di)  # 2957
                                                        r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x295B, far=False)  # 2958
                                                else:
                                                    r.di = r.bp - 0x108  # 2922
                                                    r.push(r.ss)  # 2926
                                                    r.push(r.di)  # 2927
                                                    r.push(ss16(mem, r, r.bp + 4))  # 2928
                                                    r = yield from _secondary_call(mem, r, variant, '000E:0B4D', 1, 0x292E, far=False)  # 292B
                                                    r.di = 0x2479  # 292E
                                                    r.push(mem.seg(0xE))  # 2931
                                                    r.push(r.di)  # 2932
                                                    r.di = 0x23fe  # 2933
                                                    r.push(mem.seg(0xE))  # 2936
                                                    r.push(r.di)  # 2937
                                                    r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x293B, far=False)  # 2938
                                            else:
                                                r.di = r.bp - 0x108  # 2902
                                                r.push(r.ss)  # 2906
                                                r.push(r.di)  # 2907
                                                r.push(ss16(mem, r, r.bp + 4))  # 2908
                                                r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x290E, far=False)  # 290B
                                                r.di = 0x245e  # 290E
                                                r.push(mem.seg(0xE))  # 2911
                                                r.push(r.di)  # 2912
                                                r.di = 0x246c  # 2913
                                                r.push(mem.seg(0xE))  # 2916
                                                r.push(r.di)  # 2917
                                                r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x291B, far=False)  # 2918
                                        else:
                                            r.di = 0x2444  # 28E2
                                            r.push(mem.seg(0xE))  # 28E5
                                            r.push(r.di)  # 28E6
                                            r.di = 0x2457  # 28E7
                                            r.push(mem.seg(0xE))  # 28EA
                                            r.push(r.di)  # 28EB
                                            r.di = r.bp - 0x108  # 28EC
                                            r.push(r.ss)  # 28F0
                                            r.push(r.di)  # 28F1
                                            r.push(ss16(mem, r, r.bp + 4))  # 28F2
                                            r = yield from _secondary_call(mem, r, variant, '000E:0B4D', 1, 0x28F8, far=False)  # 28F5
                                            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x28FB, far=False)  # 28F8
                                    else:
                                        r.di = 0x2439  # 28C2
                                        r.push(mem.seg(0xE))  # 28C5
                                        r.push(r.di)  # 28C6
                                        r.di = r.bp - 0x108  # 28C7
                                        r.push(r.ss)  # 28CB
                                        r.push(r.di)  # 28CC
                                        r.push(ss16(mem, r, r.bp + 4))  # 28CD
                                        r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x28D3, far=False)  # 28D0
                                        r.di = 0x23fe  # 28D3
                                        r.push(mem.seg(0xE))  # 28D6
                                        r.push(r.di)  # 28D7
                                        r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x28DB, far=False)  # 28D8
                                else:
                                    r = yield from _secondary_call(mem, r, variant, '214B:06FA', 0, 0x288A, far=True)  # 2885
                                    _left, _right = r.al, 0  # 288A
                                    if _left == _right:  # 288C
                                        r.di = 0x242b  # 28A9
                                        r.push(mem.seg(0xE))  # 28AC
                                        r.push(r.di)  # 28AD
                                        r.di = 0x23fe  # 28AE
                                        r.push(mem.seg(0xE))  # 28B1
                                        r.push(r.di)  # 28B2
                                        r.di = 0x23fe  # 28B3
                                        r.push(mem.seg(0xE))  # 28B6
                                        r.push(r.di)  # 28B7
                                        r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x28BB, far=False)  # 28B8
                                    else:
                                        r.di = 0x2423  # 288E
                                        r.push(mem.seg(0xE))  # 2891
                                        r.push(r.di)  # 2892
                                        r.di = r.bp - 0x108  # 2893
                                        r.push(r.ss)  # 2897
                                        r.push(r.di)  # 2898
                                        r.push(ss16(mem, r, r.bp + 4))  # 2899
                                        r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x289F, far=False)  # 289C
                                        r.di = 0x23fe  # 289F
                                        r.push(mem.seg(0xE))  # 28A2
                                        r.push(r.di)  # 28A3
                                        r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x28A7, far=False)  # 28A4
                                    return (yield from _secondary_column_28bb(mem, r, variant))
                        else:
                            pass
                    else:
                        return (yield from _secondary_column_279c(mem, r, variant))
            else:
                r.di = r.bp - 0x108  # 2778
                r.push(r.ss)  # 277C
                r.push(r.di)  # 277D
                r.push(ss16(mem, r, r.bp + 4))  # 277E
                r = yield from _secondary_call(mem, r, variant, '000E:0B4D', 1, 0x2784, far=False)  # 2781
                r.di = 0x23a1  # 2784
                r.push(mem.seg(0xE))  # 2787
                r.push(r.di)  # 2788
                r.di = 0x23b3  # 2789
                r.push(mem.seg(0xE))  # 278C
                r.push(r.di)  # 278D
                r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2791, far=False)  # 278E
        else:
            r.di = 0x238a  # 273C
            r.push(mem.seg(0xE))  # 273F
            r.push(r.di)  # 2740
            r.di = r.bp - 0x108  # 2741
            r.push(r.ss)  # 2745
            r.push(r.di)  # 2746
            r.push(ss16(mem, r, r.bp + 4))  # 2747
            r = yield from _secondary_call(mem, r, variant, '000E:0B4D', 1, 0x274D, far=False)  # 274A
            r.di = r.bp - 0x308  # 274D
            r.push(r.ss)  # 2751
            r.push(r.di)  # 2752
            r.di = 0x239c  # 2753
            r.push(mem.seg(0xE))  # 2756
            r.push(r.di)  # 2757
            r = yield from _secondary_call(mem, r, variant, '23E4:062A', 2, 0x275D, far=True)  # 2758
            r.di = r.bp - 0x208  # 275D
            r.push(r.ss)  # 2761
            r.push(r.di)  # 2762
            r.push(ss16(mem, r, r.bp + 4))  # 2763
            r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2769, far=False)  # 2766
            r = yield from _secondary_call(mem, r, variant, '23E4:06B7', 2, 0x276E, far=True)  # 2769
            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2771, far=False)  # 276E
        return (yield from _secondary_column_2af2(mem, r, variant))
    else:
        r.push(ss16(mem, r, r.bp + 4))  # 2AF5
        r = yield from _secondary_call(mem, r, variant, '000E:0B77', 1, 0x2AFB, far=False)  # 2AF8
        _left, _right = r.ax, 0xfff6  # 2AFB
        if s16(_left) >= s16(_right):  # 2AFE
            r.push(r.bp)  # 2B26
            r = yield from _secondary_call(mem, r, variant, '000E:2071', 1, 0x2B2A, far=False)  # 2B27
            _left, _right = r.al, 0  # 2B2A
            if _left == _right:  # 2B2C
                r.di = ss16(mem, r, r.bp + 4)  # 2B31
                r.es, r.di = ss16(mem, r, r.di + 4 + 2), ss16(mem, r, r.di + 4)  # 2B34
                r.push(r.es)  # 2B38
                r.push(r.di)  # 2B39
                r = yield from _secondary_call(mem, r, variant, '1771:5C60', 2, 0x2B3F, far=True)  # 2B3A
                _left, _right = r.ax, 1  # 2B3F
                if _left > _right:  # 2B42
                    r.ax = 6  # 2B47
                    r.push(r.ax)  # 2B4A
                    r = yield from _secondary_call(mem, r, variant, '214B:06B1', 1, 0x2B50, far=True)  # 2B4B
                    _left, _right = r.ax, 1  # 2B50
                    if _left != _right:  # 2B53
                        _left, _right = r.ax, 2  # 2B71
                        if _left != _right:  # 2B74
                            _left, _right = r.ax, 3  # 2B91
                            if _left != _right:  # 2B94
                                _left, _right = r.ax, 4  # 2BB1
                                if _left != _right:  # 2BB4
                                    _left, _right = r.ax, 5  # 2BD8
                                    if _left != _right:  # 2BDB
                                        _left, _right = r.ax, 6  # 2BF1
                                        if _left != _right:  # 2BF4
                                            pass
                                        else:
                                            r.di = r.bp - 0x108  # 2BF6
                                            r.push(r.ss)  # 2BFA
                                            r.push(r.di)  # 2BFB
                                            r.push(ss16(mem, r, r.bp + 4))  # 2BFC
                                            r = yield from _secondary_call(mem, r, variant, '000E:0B4D', 1, 0x2C02, far=False)  # 2BFF
                                            r.di = 0x25e2  # 2C02
                                            r.push(mem.seg(0xE))  # 2C05
                                            r.push(r.di)  # 2C06
                                            r.di = 0x25f2  # 2C07
                                            r.push(mem.seg(0xE))  # 2C0A
                                            r.push(r.di)  # 2C0B
                                            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2C0F, far=False)  # 2C0C
                                    else:
                                        r.di = 0x25c3  # 2BDD
                                        r.push(mem.seg(0xE))  # 2BE0
                                        r.push(r.di)  # 2BE1
                                        r.di = 0x25d1  # 2BE2
                                        r.push(mem.seg(0xE))  # 2BE5
                                        r.push(r.di)  # 2BE6
                                        r.di = 0x23fe  # 2BE7
                                        r.push(mem.seg(0xE))  # 2BEA
                                        r.push(r.di)  # 2BEB
                                        r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2BEF, far=False)  # 2BEC
                                else:
                                    r.di = r.bp - 0x108  # 2BB6
                                    r.push(r.ss)  # 2BBA
                                    r.push(r.di)  # 2BBB
                                    r.push(ss16(mem, r, r.bp + 4))  # 2BBC
                                    r = yield from _secondary_call(mem, r, variant, '000E:0B4D', 1, 0x2BC2, far=False)  # 2BBF
                                    r.di = 0x25b4  # 2BC2
                                    r.push(mem.seg(0xE))  # 2BC5
                                    r.push(r.di)  # 2BC6
                                    r.di = r.bp - 0x208  # 2BC7
                                    r.push(r.ss)  # 2BCB
                                    r.push(r.di)  # 2BCC
                                    r.push(ss16(mem, r, r.bp + 4))  # 2BCD
                                    r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2BD3, far=False)  # 2BD0
                                    r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2BD6, far=False)  # 2BD3
                            else:
                                r.di = 0x259c  # 2B96
                                r.push(mem.seg(0xE))  # 2B99
                                r.push(r.di)  # 2B9A
                                r.di = 0x25ad  # 2B9B
                                r.push(mem.seg(0xE))  # 2B9E
                                r.push(r.di)  # 2B9F
                                r.di = r.bp - 0x108  # 2BA0
                                r.push(r.ss)  # 2BA4
                                r.push(r.di)  # 2BA5
                                r.push(ss16(mem, r, r.bp + 4))  # 2BA6
                                r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2BAC, far=False)  # 2BA9
                                r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2BAF, far=False)  # 2BAC
                        else:
                            r.di = r.bp - 0x108  # 2B76
                            r.push(r.ss)  # 2B7A
                            r.push(r.di)  # 2B7B
                            r.push(ss16(mem, r, r.bp + 4))  # 2B7C
                            r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2B82, far=False)  # 2B7F
                            r.di = 0x2579  # 2B82
                            r.push(mem.seg(0xE))  # 2B85
                            r.push(r.di)  # 2B86
                            r.di = 0x2589  # 2B87
                            r.push(mem.seg(0xE))  # 2B8A
                            r.push(r.di)  # 2B8B
                            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2B8F, far=False)  # 2B8C
                    else:
                        r.di = r.bp - 0x108  # 2B55
                        r.push(r.ss)  # 2B59
                        r.push(r.di)  # 2B5A
                        r.push(ss16(mem, r, r.bp + 4))  # 2B5B
                        r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2B61, far=False)  # 2B5E
                        r.di = 0x2565  # 2B61
                        r.push(mem.seg(0xE))  # 2B64
                        r.push(r.di)  # 2B65
                        r.di = 0x2572  # 2B66
                        r.push(mem.seg(0xE))  # 2B69
                        r.push(r.di)  # 2B6A
                        r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2B6E, far=False)  # 2B6B
                    return (yield from _secondary_column_2c0f(mem, r, variant))
                else:
                    r.di = ss16(mem, r, r.bp + 4)  # 2C12
                    r.al = ss8(mem, r, r.di - 1)  # 2C15
                    cbw(r)  # 2C19
                    r.dx = 0xa  # 2C1A
                    mul(r, r.dx)  # 2C1D
                    r.di = r.ax  # 2C1F
                    r.al = mem.ds8((r.di + 0x7b7e) & M16)  # 2C21
                    r.ah = 0  # 2C25
                    r.cx = r.ax  # 2C27
                    r.di = ss16(mem, r, r.bp + 4)  # 2C29
                    r.al = ss8(mem, r, r.di - 1)  # 2C2C
                    cbw(r)  # 2C30
                    r.dx = 0xa  # 2C31
                    mul(r, r.dx)  # 2C34
                    r.di = r.ax  # 2C36
                    r.al = mem.ds8((r.di + 0x7b81) & M16)  # 2C38
                    r.ah = 0  # 2C3C
                    r.ax = r.ax + r.cx  # 2C3E
                    _left, _right = r.ax, 8  # 2C40
                    if s16(_left) >= s16(_right):  # 2C43
                        r.di = ss16(mem, r, r.bp + 4)  # 2CAF
                        r.al = ss8(mem, r, r.di - 1)  # 2CB2
                        cbw(r)  # 2CB6
                        r.dx = 0xa  # 2CB7
                        mul(r, r.dx)  # 2CBA
                        r.di = r.ax  # 2CBC
                        r.dx = (r.dx & 0xff00) | ((mem.ds8((r.di + 0x7b83) & M16)) & 255)  # 2CBE
                        r.di = ss16(mem, r, r.bp + 4)  # 2CC2
                        _left, _right = ss8(mem, r, r.di - 1), 0  # 2CC5
                        if _left == _right:  # 2CCA
                            r.al = 1  # 2CD0
                        else:
                            r.al = 0  # 2CCC
                        return (yield from _secondary_column_2cd2(mem, r, variant))
                    else:
                        r.ax = 3  # 2C45
                        r.push(r.ax)  # 2C48
                        r = yield from _secondary_call(mem, r, variant, '214B:06B1', 1, 0x2C4E, far=True)  # 2C49
                        _left, _right = r.ax, 1  # 2C4E
                        if _left != _right:  # 2C51
                            _left, _right = r.ax, 2  # 2C6E
                            if _left != _right:  # 2C71
                                _left, _right = r.ax, 3  # 2C8E
                                if _left != _right:  # 2C91
                                    pass
                                else:
                                    r.di = r.bp - 0x108  # 2C93
                                    r.push(r.ss)  # 2C97
                                    r.push(r.di)  # 2C98
                                    r.push(ss16(mem, r, r.bp + 4))  # 2C99
                                    r = yield from _secondary_call(mem, r, variant, '000E:0B4D', 1, 0x2C9F, far=False)  # 2C9C
                                    r.di = 0x262b  # 2C9F
                                    r.push(mem.seg(0xE))  # 2CA2
                                    r.push(r.di)  # 2CA3
                                    r.di = 0x2639  # 2CA4
                                    r.push(mem.seg(0xE))  # 2CA7
                                    r.push(r.di)  # 2CA8
                                    r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2CAC, far=False)  # 2CA9
                            else:
                                r.di = r.bp - 0x108  # 2C73
                                r.push(r.ss)  # 2C77
                                r.push(r.di)  # 2C78
                                r.push(ss16(mem, r, r.bp + 4))  # 2C79
                                r = yield from _secondary_call(mem, r, variant, '000E:0B4D', 1, 0x2C7F, far=False)  # 2C7C
                                r.di = 0x2617  # 2C7F
                                r.push(mem.seg(0xE))  # 2C82
                                r.push(r.di)  # 2C83
                                r.di = 0x2621  # 2C84
                                r.push(mem.seg(0xE))  # 2C87
                                r.push(r.di)  # 2C88
                                r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2C8C, far=False)  # 2C89
                        else:
                            r.di = r.bp - 0x108  # 2C53
                            r.push(r.ss)  # 2C57
                            r.push(r.di)  # 2C58
                            r.push(ss16(mem, r, r.bp + 4))  # 2C59
                            r = yield from _secondary_call(mem, r, variant, '000E:0B4D', 1, 0x2C5F, far=False)  # 2C5C
                            r.di = 0x2600  # 2C5F
                            r.push(mem.seg(0xE))  # 2C62
                            r.push(r.di)  # 2C63
                            r.di = 0x2608  # 2C64
                            r.push(mem.seg(0xE))  # 2C67
                            r.push(r.di)  # 2C68
                            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2C6C, far=False)  # 2C69
                        return (yield from _secondary_column_2cac(mem, r, variant))
            else:
                pass
        else:
            r.di = 0x2552  # 2B00
            r.push(mem.seg(0xE))  # 2B03
            r.push(r.di)  # 2B04
            r.di = r.bp - 0x108  # 2B05
            r.push(r.ss)  # 2B09
            r.push(r.di)  # 2B0A
            r.push(ss16(mem, r, r.bp + 4))  # 2B0B
            r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2B11, far=False)  # 2B0E
            r.di = 0x2563  # 2B11
            r.push(mem.seg(0xE))  # 2B14
            r.push(r.di)  # 2B15
            r = yield from _secondary_call(mem, r, variant, '23E4:06B7', 2, 0x2B1B, far=True)  # 2B16
            r.di = 0x23fe  # 2B1B
            r.push(mem.seg(0xE))  # 2B1E
            r.push(r.di)  # 2B1F
            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2B23, far=False)  # 2B20
    return r


def _secondary_column_279c(mem, r, variant):
    r.di = r.bp - 0x108  # 279C
    r.push(r.ss)  # 27A0
    r.push(r.di)  # 27A1
    r.push(ss16(mem, r, r.bp + 4))  # 27A2
    r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x27A8, far=False)  # 27A5
    r.di = 0x23c0  # 27A8
    r.push(mem.seg(0xE))  # 27AB
    r.push(r.di)  # 27AC
    r = yield from _secondary_call(mem, r, variant, '23E4:06B7', 2, 0x27B2, far=True)  # 27AD
    r.di = r.bp - 0x208  # 27B2
    r.push(r.ss)  # 27B6
    r.push(r.di)  # 27B7
    r.push(ss16(mem, r, r.bp + 4))  # 27B8
    r = yield from _secondary_call(mem, r, variant, '000E:0B4D', 1, 0x27BE, far=False)  # 27BB
    r.di = 0x23c7  # 27BE
    r.push(mem.seg(0xE))  # 27C1
    r.push(r.di)  # 27C2
    r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x27C6, far=False)  # 27C3
    return (yield from _secondary_column_2af2(mem, r, variant))
    return r


def _secondary_column_287e(mem, r, variant):
    return (yield from _secondary_column_2af2(mem, r, variant))
    return r


def _secondary_column_28bb(mem, r, variant):
    return (yield from _secondary_column_2af2(mem, r, variant))
    return r


def _secondary_column_2a6a(mem, r, variant):
    _left, _right = r.ax, 0xa  # 2A6A
    if s16(_left) < s16(_right):  # 2A6D
        return (yield from _secondary_column_2aa6(mem, r, variant))
    else:
        _left, _right = r.ax, 0xd  # 2A6F
        if s16(_left) > s16(_right):  # 2A72
            return (yield from _secondary_column_2aa6(mem, r, variant))
        else:
            r.di = r.bp - 0x108  # 2A74
            r.push(r.ss)  # 2A78
            r.push(r.di)  # 2A79
            r.es, r.di = ss16(mem, r, r.bp - 8 + 2), ss16(mem, r, r.bp - 8)  # 2A7A
            r.al = mem.u8(mem.addr(r.es, r.di + 0xac))  # 2A7D
            r.ah = 0  # 2A82
            r.dx = 0  # 2A84
            r.push(r.dx)  # 2A86
            r.push(r.ax)  # 2A87
            r = yield from _secondary_call(mem, r, variant, '214B:09DA', 2, 0x2A8D, far=True)  # 2A88
            r.di = 0x2517  # 2A8D
            r.push(mem.seg(0xE))  # 2A90
            r.push(r.di)  # 2A91
            r = yield from _secondary_call(mem, r, variant, '23E4:06B7', 2, 0x2A97, far=True)  # 2A92
            r.di = 0x2524  # 2A97
            r.push(mem.seg(0xE))  # 2A9A
            r.push(r.di)  # 2A9B
            r.di = 0x2530  # 2A9C
            r.push(mem.seg(0xE))  # 2A9F
            r.push(r.di)  # 2AA0
            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2AA4, far=False)  # 2AA1
    return (yield from _secondary_column_2af2(mem, r, variant))
    return r


def _secondary_column_2aa6(mem, r, variant):
    r.di = r.bp - 0x108  # 2AA6
    r.push(r.ss)  # 2AAA
    r.push(r.di)  # 2AAB
    r.es, r.di = ss16(mem, r, r.bp - 8 + 2), ss16(mem, r, r.bp - 8)  # 2AAC
    r.al = mem.u8(mem.addr(r.es, r.di + 0xac))  # 2AAF
    r.ah = 0  # 2AB4
    r.dx = 0  # 2AB6
    r.push(r.dx)  # 2AB8
    r.push(r.ax)  # 2AB9
    r = yield from _secondary_call(mem, r, variant, '214B:09DA', 2, 0x2ABF, far=True)  # 2ABA
    r.di = 0x2537  # 2ABF
    r.push(mem.seg(0xE))  # 2AC2
    r.push(r.di)  # 2AC3
    r = yield from _secondary_call(mem, r, variant, '23E4:06B7', 2, 0x2AC9, far=True)  # 2AC4
    r.di = r.bp - 0x308  # 2AC9
    r.push(r.ss)  # 2ACD
    r.push(r.di)  # 2ACE
    r.di = 0x2547  # 2ACF
    r.push(mem.seg(0xE))  # 2AD2
    r.push(r.di)  # 2AD3
    r = yield from _secondary_call(mem, r, variant, '23E4:062A', 2, 0x2AD9, far=True)  # 2AD4
    r.di = r.bp - 0x208  # 2AD9
    r.push(r.ss)  # 2ADD
    r.push(r.di)  # 2ADE
    r.push(ss16(mem, r, r.bp + 4))  # 2ADF
    r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2AE5, far=False)  # 2AE2
    r = yield from _secondary_call(mem, r, variant, '23E4:06B7', 2, 0x2AEA, far=True)  # 2AE5
    r.di = 0x23fe  # 2AEA
    r.push(mem.seg(0xE))  # 2AED
    r.push(r.di)  # 2AEE
    r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2AF2, far=False)  # 2AEF
    return (yield from _secondary_column_2af2(mem, r, variant))
    return r


def _secondary_column_2af2(mem, r, variant):
    yield from ()
    return r


def _secondary_column_2c0f(mem, r, variant):
    yield from ()
    return r


def _secondary_column_2cac(mem, r, variant):
    yield from ()
    return r


def _secondary_column_2cd2(mem, r, variant):
    cbw(r)  # 2CD2
    r.es, r.di = ss16(mem, r, r.bp - 4 + 2), ss16(mem, r, r.bp - 4)  # 2CD3
    r.di = r.di + r.ax  # 2CD6
    r.al = mem.u8(mem.addr(r.es, r.di))  # 2CD8
    _left, _right = r.al, (r.dx & 255)  # 2CDB
    if _left <= _right:  # 2CDD
        r.ax = 6  # 2D49
        r.push(r.ax)  # 2D4C
        r = yield from _secondary_call(mem, r, variant, '214B:06B1', 1, 0x2D52, far=True)  # 2D4D
        _left, _right = r.ax, 1  # 2D52
        if _left != _right:  # 2D55
            _left, _right = r.ax, 2  # 2D73
            if _left != _right:  # 2D76
                _left, _right = r.ax, 3  # 2D94
                if _left != _right:  # 2D97
                    _left, _right = r.ax, 4  # 2DB4
                    if _left != _right:  # 2DB7
                        _left, _right = r.ax, 5  # 2DDB
                        if _left != _right:  # 2DDE
                            _left, _right = r.ax, 6  # 2DFB
                            if _left != _right:  # 2DFE
                                pass
                            else:
                                r.di = 0x26dc  # 2E00
                                r.push(mem.seg(0xE))  # 2E03
                                r.push(r.di)  # 2E04
                                r.di = 0x26e7  # 2E05
                                r.push(mem.seg(0xE))  # 2E08
                                r.push(r.di)  # 2E09
                                r.di = r.bp - 0x108  # 2E0A
                                r.push(r.ss)  # 2E0E
                                r.push(r.di)  # 2E0F
                                r.push(ss16(mem, r, r.bp + 4))  # 2E10
                                r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2E16, far=False)  # 2E13
                                r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2E19, far=False)  # 2E16
                        else:
                            r.di = 0x26c2  # 2DE0
                            r.push(mem.seg(0xE))  # 2DE3
                            r.push(r.di)  # 2DE4
                            r.di = 0x26d4  # 2DE5
                            r.push(mem.seg(0xE))  # 2DE8
                            r.push(r.di)  # 2DE9
                            r.di = r.bp - 0x108  # 2DEA
                            r.push(r.ss)  # 2DEE
                            r.push(r.di)  # 2DEF
                            r.push(ss16(mem, r, r.bp + 4))  # 2DF0
                            r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2DF6, far=False)  # 2DF3
                            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2DF9, far=False)  # 2DF6
                    else:
                        r.di = r.bp - 0x108  # 2DB9
                        r.push(r.ss)  # 2DBD
                        r.push(r.di)  # 2DBE
                        r.push(ss16(mem, r, r.bp + 4))  # 2DBF
                        r = yield from _secondary_call(mem, r, variant, '000E:0B4D', 1, 0x2DC5, far=False)  # 2DC2
                        r.di = 0x26b3  # 2DC5
                        r.push(mem.seg(0xE))  # 2DC8
                        r.push(r.di)  # 2DC9
                        r.di = r.bp - 0x208  # 2DCA
                        r.push(r.ss)  # 2DCE
                        r.push(r.di)  # 2DCF
                        r.push(ss16(mem, r, r.bp + 4))  # 2DD0
                        r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2DD6, far=False)  # 2DD3
                        r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2DD9, far=False)  # 2DD6
                else:
                    r.di = 0x26a8  # 2D99
                    r.push(mem.seg(0xE))  # 2D9C
                    r.push(r.di)  # 2D9D
                    r.di = 0x23e4  # 2D9E
                    r.push(mem.seg(0xE))  # 2DA1
                    r.push(r.di)  # 2DA2
                    r.di = r.bp - 0x108  # 2DA3
                    r.push(r.ss)  # 2DA7
                    r.push(r.di)  # 2DA8
                    r.push(ss16(mem, r, r.bp + 4))  # 2DA9
                    r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2DAF, far=False)  # 2DAC
                    r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2DB2, far=False)  # 2DAF
            else:
                r.di = 0x2694  # 2D78
                r.push(mem.seg(0xE))  # 2D7B
                r.push(r.di)  # 2D7C
                r.di = r.bp - 0x108  # 2D7D
                r.push(r.ss)  # 2D81
                r.push(r.di)  # 2D82
                r.push(ss16(mem, r, r.bp + 4))  # 2D83
                r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2D89, far=False)  # 2D86
                r.di = 0x23fe  # 2D89
                r.push(mem.seg(0xE))  # 2D8C
                r.push(r.di)  # 2D8D
                r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2D91, far=False)  # 2D8E
        else:
            r.di = 0x2683  # 2D57
            r.push(mem.seg(0xE))  # 2D5A
            r.push(r.di)  # 2D5B
            r.di = r.bp - 0x108  # 2D5C
            r.push(r.ss)  # 2D60
            r.push(r.di)  # 2D61
            r.push(ss16(mem, r, r.bp + 4))  # 2D62
            r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2D68, far=False)  # 2D65
            r.di = 0x23fe  # 2D68
            r.push(mem.seg(0xE))  # 2D6B
            r.push(r.di)  # 2D6C
            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2D70, far=False)  # 2D6D
    else:
        r.ax = 3  # 2CDF
        r.push(r.ax)  # 2CE2
        r = yield from _secondary_call(mem, r, variant, '214B:06B1', 1, 0x2CE8, far=True)  # 2CE3
        _left, _right = r.ax, 1  # 2CE8
        if _left != _right:  # 2CEB
            _left, _right = r.ax, 2  # 2D08
            if _left != _right:  # 2D0B
                _left, _right = r.ax, 3  # 2D28
                if _left != _right:  # 2D2B
                    pass
                else:
                    r.di = 0x2662  # 2D2D
                    r.push(mem.seg(0xE))  # 2D30
                    r.push(r.di)  # 2D31
                    r.di = 0x2673  # 2D32
                    r.push(mem.seg(0xE))  # 2D35
                    r.push(r.di)  # 2D36
                    r.di = r.bp - 0x108  # 2D37
                    r.push(r.ss)  # 2D3B
                    r.push(r.di)  # 2D3C
                    r.push(ss16(mem, r, r.bp + 4))  # 2D3D
                    r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2D43, far=False)  # 2D40
                    r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2D46, far=False)  # 2D43
            else:
                r.di = 0x2651  # 2D0D
                r.push(mem.seg(0xE))  # 2D10
                r.push(r.di)  # 2D11
                r.di = r.bp - 0x108  # 2D12
                r.push(r.ss)  # 2D16
                r.push(r.di)  # 2D17
                r.push(ss16(mem, r, r.bp + 4))  # 2D18
                r = yield from _secondary_call(mem, r, variant, '000E:0ACB', 1, 0x2D1E, far=False)  # 2D1B
                r.di = 0x23fe  # 2D1E
                r.push(mem.seg(0xE))  # 2D21
                r.push(r.di)  # 2D22
                r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2D26, far=False)  # 2D23
        else:
            r.di = r.bp - 0x108  # 2CED
            r.push(r.ss)  # 2CF1
            r.push(r.di)  # 2CF2
            r.push(ss16(mem, r, r.bp + 4))  # 2CF3
            r = yield from _secondary_call(mem, r, variant, '000E:0B4D', 1, 0x2CF9, far=False)  # 2CF6
            r.di = 0x263f  # 2CF9
            r.push(mem.seg(0xE))  # 2CFC
            r.push(r.di)  # 2CFD
            r.di = 0x23fe  # 2CFE
            r.push(mem.seg(0xE))  # 2D01
            r.push(r.di)  # 2D02
            r = yield from _secondary_call(mem, r, variant, '000E:075F', 6, 0x2D06, far=False)  # 2D03
        return (yield from _secondary_column_2d46(mem, r, variant))
    return r


def _secondary_column_2d46(mem, r, variant):
    yield from ()
    return r
