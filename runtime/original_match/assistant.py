"""The original assistant's copied-state operation (T125).

``recommend(state, tables, key=13)`` accepts original_match.state/2 and loaded
port.tables.Tables. It returns a dict containing the copied ``state``, original
``allowed``/``refusal`` (None, 'finals', or 'tour'), current ``manager`` and
``country``, ordered ``squad`` (20 words), ``pool`` (80 words from DS:6D18 +
2*manager, with 16-bit addressing), ``next_fixture`` (DS:9B43), ``calls`` and
``keys``. The input state and tables are never changed. No EXE or Unicorn is
read. The operation follows original DC7E in the SELECT TEAM context, outside
a match: the current manager byte is [DS:A923]+1, not a caller-selected country.
The caller supplies the SELECT TEAM preparation: DS:0C1E/0C1F clear and the
incoming squad/pool order. This API starts at DC7E, without E44F's setup, its
52CC sort or the manager menu; it promises no parity for that earlier UI path.

DBFA's real message and draw/key subtree runs on PortMachine on refusals. The
key argument acknowledges its message; it does not choose an eleven. The
operation can update DS:9B43 and message/screen/stack bytes even on refusal;
refusal preserves squad/pool selection and player records. Wrapped pool-base
stress preserves DC7E's unsigned base+79 behavior; it is not a normal career.
"""
from . import port
from .image import Image
from .machine import MEM_SIZE
from .port.engine import PortMachine


def _ports():
    """Use existing real implementations only; an unported closure fails closed."""
    for reg,variant in port.load(['all']):
        real=port.Registry(reg.name,reg.doc)
        for entry in reg.entries.values():
            if entry.stub is None:real._add(entry)
        yield real,variant


class _Keys:
    def __init__(self,m,key):self.m,self.value,self.log=m,key,[]
    def key(self,site):
        self.log.append(['read',site,self.value])
        self.m.wr(0xA976,self.value|(self.value<<8))
        self.m.set_reg('ax',(self.m.reg('ax')&0xFF00)|self.value)
        return self.value
    def keypressed(self,site):
        self.log.append(['poll',site,True]);return True


def recommend(state,tables,*,key=13):
    """Run original DC7E on a copy; see the module doc for all input/output fields."""
    if type(key) is not int or not 0<=key<=255:raise ValueError('key must be a byte')
    image=Image.from_state(state,tables)
    m=PortMachine(image.memory,image.load);keys=_Keys(m,key)
    inst=port.install(m,list(_ports()),keys=keys)
    game=m.far(0xA923);manager=m.read(game+1,1)[0]
    country=m.read(m.far(0xA91F)+3*(manager+0x80),1)[0]
    result={'allowed':True,'refusal':None,'manager':manager,'country':country}
    def message(replay):
        # 1765 argument0 is a far string, argument2 the original byte boolean.
        flag=m.stack_word(8)&255
        if flag:
            caller=m.where(m.stack_word(2),m.stack_word(0))
            result.update(allowed=False,refusal={'0791:DC3D':'finals','0791:DC68':'tour'}[caller])
    m.at('214B:1765',message)
    ss=m.seg(0x3052);sp=0x3000
    m.far_call('0791:DC7E',(),'0791:E788',ss,sp)
    m.write(ss*16+sp,(0xE788).to_bytes(2,'little'))
    m.set_reg('bp',0x3456)
    m.run(m.lin('0791:E788'),fresh=True)
    if m.frames or m.reg('sp')!=sp+2:raise RuntimeError('assistant did not return with its original near ABI')
    image.memory[:MEM_SIZE]=m.read(0,MEM_SIZE)
    squad=m.far(0xA917)+country*191
    pool_off=m.rd(0xA927);pool_seg=m.rd(0xA929)
    base=m.rd(0x6D18+2*manager)
    result.update(state=image.state(tables),squad=[m.word_at(squad+2*i) for i in range(20)],
                  pool=[m.word_at(pool_seg*16+((pool_off+2*((base+i)&65535))&65535)) for i in range(80)],
                  next_fixture=m.rd(0x9B43),calls={k:v for k,v in inst.calls.items() if v},keys=keys.log)
    return result
