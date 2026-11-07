"""T124f original-oracle ageing and explicit no-write deferred-year boundary.

Direct cases use the published E006 image and declared byte/word fixtures, never
optional private captures. Natural C/D actual70E6 contexts are separate immutable
harness proofs. Every original caller address and full near/far ABI is retained.
"""
import hashlib,unittest
from tests.test_port_stages import _Calls,RET
from original_match import port
from original_match.port import Registry,ageing as A
from original_match.port.engine import PortMachine
from original_match.machine import MEM_SIZE,REGS

ENTRIES={'1771:80DA':'ret','1771:7FDF':'ret 2','1771:7FB1':'ret 4','1771:7E4A':'ret 2',
 '1771:32EB':'retf 2','1771:7F40':'retf 2','1771:7E80':'ret 2','1771:96D3':'retf 8',
 '1771:3291':'ret 2','1771:0000':'retf'}
RET.update({'1771:80DA':'1771:826D','1771:7FDF':'1771:80FA','1771:7FB1':'1771:8015',
 '1771:7E4A':'1771:7FD1','1771:32EB':'1771:7E7A','1771:7F40':'1771:8099',
 '1771:7E80':'1771:80AE','1771:96D3':'1771:7EC3','1771:3291':'1771:975E','1771:0000':'1771:7F22'})


def specs(variant=None):
    wanted=set(A.PORTS.entries)|{'214B:06B1','1771:0B77','1771:10E7','1771:3431','1771:3558',
      '1771:2FFB','1771:33CD','23E4:08DF','214B:0C79','214B:0CA1'}
    result=[]
    for reg,_ in port.load(['all']):
        sub=Registry(reg.name,reg.doc)
        for address,e in reg.entries.items():
            if address in wanted:assert not e.stub;sub._add(e)
        if sub.entries:sub.variants=dict(reg.variants);result.append((sub,variant if reg.name=='ageing' else None))
    assert {a for reg,_ in result for a in reg.entries}==wanted
    return result


def pa(m,player,k=0):return m.rd(0xA91D)*16+((m.rd(0xA91B)+20*player+k)&65535)
def byte(m,player,k,value):m.write(pa(m,player,k),bytes([value&255]))
def word(m,address,value):m.write(address,(value&65535).to_bytes(2,'little'))
def field(m,player,k):return m.read(pa(m,player,k),1)[0]
def record(m,player,**fields):
    for k,v in fields.items():byte(m,player,int(k[1:],16),v)
def computer(m,country=1):m.write(m.far(0xA917)+191*country+46,bytes([country]))
def name_hash(m,player):return hashlib.sha256(m.read(m.far(0x9B6C)+11*player,11)).hexdigest()


def pool_setup(m,base=None,bias=0):
    countries=m.far(0xA917);country=m.read(m.far(0xA91F)+3*129,1)[0]
    squad={m.word_at(countries+191*country+2*i) for i in range(20)}
    oldbase=m.rd(0x6D1A);seg=m.rd(0xA929);off=m.rd(0xA927)
    candidates=[m.word_at(seg*16+((off+2*(oldbase+i))&65535)) for i in range(80)]
    players=list(dict.fromkeys(p for p in candidates if p and p not in squad))[:2]
    assert len(players)==2
    first,last=players;record(m,first,p1=250,p2=28,p3=200,p7=1,p11=9);record(m,last,p1=255,p2=28,p3=200,p7=1,p11=7)
    word(m,pa(m,first,8),0);word(m,pa(m,last,8),0)
    m.write(countries+191*country+46,b'\x81')
    chosen=oldbase if base is None else base;m.wr(0x6D1A,chosen);m.wr(0xA927,(off+bias)&65535)
    if chosen<=((chosen+79)&65535):
        for i in range(80):word(m,seg*16+(((off+bias)&65535)+2*((chosen+i)&65535)&65535),last if i==79 else first)
    return {'country':country,'first':first,'last':last,'seed':m.rd(0x7B62),'base':chosen}


class Entries(unittest.TestCase):
    def test_exact_ten_original_abis_no_wrapped_duplicate_owner(self):
        self.assertEqual({a:e.ret for a,e in A.PORTS.entries.items()},ENTRIES)
        self.assertNotIn('1771:110E7',A.PORTS.entries)
        self.assertNotIn('1771:10E7',A.PORTS.entries)
        self.assertNotIn('1771:3431',A.PORTS.entries)
        self.assertNotIn('1771:3558',A.PORTS.entries)


class Leaves(_Calls):
    def call_age(self,target,args,*,before=None,variant=None):return self.call(target,args,specs=specs(variant),before=before)

    def test_ability_peak_plateau_half_step_and_word_wrap(self):
        for age,peak,rating,ability,ax,dx in [(27,28,160,160,160,0),(28,28,160,160,160,31),
          (31,28,160,160,160,31),(32,28,160,150,150,0),(255,0,255,78,334,12)]:
            with self.subTest(age=age,peak=peak):
                m,p=self.call_age('1771:32EB',(1,),before=lambda m:record(m,1,p1=age,p2=peak,p3=rating))
                self.proved(p,'1771:32EB');self.assertEqual((field(m,1,4),m.reg('ax'),m.reg('dx')),(ability,ax,dx))

    def test_nonzero_age_zero_increments_and255_wraps(self):
        for age,want in [(0,1),(254,255),(255,0)]:
            with self.subTest(age=age):
                m,p=self.call_age('1771:7E4A',(1,),before=lambda m:record(m,1,p1=age,p2=28,p3=160))
                self.proved(p,'1771:7E4A');self.assertEqual(field(m,1,1),want)

    def test_literal_player_zero_skips_age_but_age_one_clears_scorer(self):
        def before(m):record(m,0,p1=255,p4=123,p11=9)
        m,p=self.call_age('1771:7E4A',(0,),before=before);self.proved(p,'1771:7E4A')
        self.assertEqual((field(m,0,1),field(m,0,4),field(m,0,0x11)),(255,123,9))
        m,p=self.call_age('1771:7FB1',(0,0x3E80),before=before);self.proved(p,'1771:7FB1')
        self.assertEqual((field(m,0,1),field(m,0,4),field(m,0,0x11)),(255,123,0))

    def test_nonzero_word_alias_of_player_zero_still_ages(self):
        m,p=self.call_age('1771:7E4A',(0x8000,),before=lambda m:record(m,0,p1=7,p2=28,p3=160))
        self.proved(p,'1771:7E4A');self.assertEqual(field(m,0,1),8)

    def test_peak_age_two_ordered_draws_keeper_and_outfield(self):
        for club in (0,1):
            with self.subTest(club=club):
                m,p=self.call_age('1771:3291',(1,),before=lambda m:record(m,1,p7=club))
                self.proved(p,'1771:3291');base=m.rd(0xE80+int(club==0),1)
                self.assertTrue(base-2<=field(m,1,2)<=base+2)
                self.assertEqual(p.summary()['214B:06B1']['nested'],2)
                self.assertEqual(m.reg('ax')&255,field(m,1,2))

    def test_initial_zero_address_far_function_uses_real_letter_table(self):
        m,p=self.call_age('1771:0000',())
        self.proved(p,'1771:0000');n=m.rd(0xC38,1)
        self.assertIn(m.reg('ax')&255,list(m.read(m.DS*16+0xC39,n)))
        self.assertEqual(p.summary()['214B:06B1']['nested'],1)

    def test_retirement_exact_limits_caps_words_and_club_position(self):
        for club,limit in [(1,30),(0,33)]:
            for age in (limit-1,limit,limit+1):
                for caps in (0,1,256):
                    with self.subTest(club=club,age=age,caps=caps):
                        def before(m):record(m,1,p1=age,p2=250,p6=1-club,p7=club);word(m,pa(m,1,8),caps)
                        m,p=self.call_age('1771:7F40',(1,),before=before);self.proved(p,'1771:7F40')
                        self.assertEqual(m.reg('ax')&255,int(age>limit and caps==0))

    def test_retirement_peak_plus_five_is_extended_word(self):
        def before(m):record(m,1,p1=255,p2=255,p7=1);word(m,pa(m,1,8),256)
        m,p=self.call_age('1771:7F40',(1,),before=before);self.proved(p,'1771:7F40')
        self.assertEqual((m.reg('ax'),m.reg('dx')),(0,260))

    def test_retirement_early_true_preserves_unsigned_mul_high_word(self):
        def before(m):record(m,0,p1=31,p2=28,p7=1);word(m,pa(m,0,8),0)
        m,p=self.call_age('1771:7F40',(0x8000,),before=before);self.proved(p,'1771:7F40')
        self.assertEqual((m.reg('ax'),m.reg('dx')),(1,10))

    def test_make_player_flags_and_full_argument_words_preserve_unowned_fields(self):
        for flag in (0,1):
            for club in (0,1):
                with self.subTest(flag=flag,club=club):
                    saved={}
                    def before(m):
                        computer(m);record(m,1,p0=1,p7=club,p10=9,p11=11)
                        word(m,pa(m,1,8),0x1234);word(m,pa(m,1,0xA),0x5678);saved['name']=name_hash(m,1)
                    m,p=self.call_age('1771:96D3',(1,1,0xCD00|club,0xAB00|flag),before=before)
                    self.proved(p,'1771:96D3')
                    self.assertEqual((field(m,1,0),field(m,1,7),field(m,1,6)),(1,club,club))
                    self.assertEqual((m.word_at(pa(m,1,8)),m.word_at(pa(m,1,0xA)),field(m,1,0x10),field(m,1,0x11)),(0x1234,0x5678,9,11))
                    self.assertEqual(m.word_at(pa(m,1,0x12)),0x7FFF);self.assertEqual(name_hash(m,1),saved['name'])
                    self.assertEqual(p.summary()['214B:06B1']['nested'],7+int(flag==0))

    def test_replacement_real_draws_resets_and_restores_current_position(self):
        saved={}
        def before(m):
            computer(m);record(m,1,p0=1,p6=9,p7=1,p10=9,p11=11)
            word(m,pa(m,1,8),0x1234);word(m,pa(m,1,0xA),0xABCD);saved['name']=name_hash(m,1)
        m,p=self.call_age('1771:7E80',(1,),before=before);self.proved(p,'1771:7E80')
        self.assertEqual((field(m,1,6),field(m,1,7),field(m,1,0x10),field(m,1,0x11)),(9,1,0,11))
        self.assertEqual((m.word_at(pa(m,1,8)),m.word_at(pa(m,1,0xA))),(0,0))
        self.assertEqual(name_hash(m,1),saved['name']);self.assertEqual(p.summary()['214B:06B1']['nested'],10)
        base=m.rd(0x110C,1);self.assertTrue(base-5<=field(m,1,1)<=base+5)

    def test_computer_duplicates_age_all20_before_any_retirement(self):
        def before(m):
            computer(m)
            for i in range(20):word(m,m.far(0xA917)+191+2*i,1)
            record(m,1,p0=1,p1=20,p2=28,p6=9,p7=1,p11=7);word(m,pa(m,1,8),0)
        m,p=self.call_age('1771:7FDF',(1,),before=before);self.proved(p,'1771:7FDF')
        for a,n in [('1771:7FB1',20),('1771:7F40',20),('1771:7E80',1)]:self.assertEqual(p.summary()[a]['nested'],n)
        self.assertEqual([m.word_at(m.far(0xA917)+191+2*i) for i in range(20)],[1]*20)
        self.assertEqual((field(m,1,6),field(m,1,0x11)),(9,0))

    def test_computer_zero_slots_are_not_omitted_from_retirement(self):
        def before(m):
            computer(m);computer(m,0)
            for i in range(20):word(m,m.far(0xA917)+191+2*i,0)
            record(m,0,p0=0,p1=255,p2=0,p6=2,p7=0,p11=9);word(m,pa(m,0,8),0)
        m,p=self.call_age('1771:7FDF',(1,),before=before);self.proved(p,'1771:7FDF')
        self.assertEqual(p.summary()['1771:7E4A']['nested'],20)
        self.assertEqual(p.summary()['1771:7F40']['nested'],20)
        self.assertEqual(p.summary()['1771:7E80']['nested'],1)
        self.assertEqual((field(m,0,6),field(m,0,0x11)),(2,0))

    def test_managed80_pool_duplicates_and_unsigned_wrap_gate(self):
        country=self.image.memory[self.image.far(0xA91F)+3*129]
        for base,bias,visits in [(None,0,80),(0x8000,0,80),(0x7FE0,0x40,80),(0xFFF0,0,0)]:
            with self.subTest(base=base,bias=bias):
                saved={}
                def before(m):saved.update(pool_setup(m,base,bias))
                m,p=self.call_age('1771:7FDF',(country,),before=before);self.proved(p,'1771:7FDF')
                self.assertEqual(p.summary()['1771:7FB1']['nested'],20+visits)
                self.assertEqual(p.summary()['1771:7F40']['nested'],0)
                self.assertEqual(p.summary()['1771:7E80']['nested'],0)
                self.assertEqual(m.rd(0x7B62),saved['seed'])
                self.assertEqual((field(m,saved['first'],1),field(m,saved['last'],1)),((250+79)&255,0) if visits else (250,255))
                self.assertEqual((field(m,saved['first'],0x11),field(m,saved['last'],0x11)),(0,0) if visits else (9,7))

    def test_in_season_body_ages_all128_without_year_or_country_housekeeping(self):
        for stage in (3,7):
            with self.subTest(stage=stage):
                saved={}
                def before(m):
                    g=m.far(0xA923);m.write(g+0x3C,bytes([stage]))
                    cp=m.far(0xA917);saved['countries']=hashlib.sha256(m.read(cp,129*191)).digest()
                    saved['game']=hashlib.sha256(m.read(g,0x10E)).digest()
                    saved['managed']=sum(m.read(cp+191*c+46,1)[0]>128 for c in range(1,129))
                m,p=self.call_age('1771:80DA',(),before=before);self.proved(p,'1771:80DA')
                self.assertEqual(p.summary()['1771:7FDF']['nested'],128)
                self.assertEqual(p.summary()['1771:7FB1']['nested'],2560+80*saved['managed'])
                self.assertEqual(hashlib.sha256(m.read(m.far(0xA917),129*191)).digest(),saved['countries'])
                self.assertEqual(hashlib.sha256(m.read(m.far(0xA923),0x10E)).digest(),saved['game'])

    def test_four_required_falsifiers_are_caught(self):
        from original_match.port.prove import ProofError
        def aged(m):record(m,1,p1=27,p2=28,p3=160)
        def retire(m):record(m,1,p1=31,p2=250,p7=1);word(m,pa(m,1,8),0)
        def replacement(m):computer(m);record(m,1,p0=1,p6=9,p7=1)
        country=self.image.memory[self.image.far(0xA91F)+3*129]
        for variant,target,args,before in [('age-increment-dropped','1771:7E4A',(1,),aged),
          ('retirement-threshold-plus-one','1771:7F40',(1,),retire),
          ('replacement-draw-dropped','1771:7E80',(1,),replacement),
          ('pool-scorer-write-dropped','1771:7FDF',(country,),pool_setup)]:
            with self.subTest(variant=variant),self.assertRaises(ProofError):self.call_age(target,args,before=before,variant=variant)


class DeferredBoundary(unittest.TestCase):
    def test_year_rollover_refuses_before_even_a_same_value_stack_write(self):
        from original_match.port.mem import PortError
        for stage in (2,5):
            with self.subTest(stage=stage):
                m=PortMachine(bytearray(MEM_SIZE),0)
                m.wr(0xA923,0x100);m.wr(0xA925,0x5000);m.write(0x50100+0x3C,bytes([stage]))
                for n,v in [('ss',0x7000),('sp',0x3000),('bp',0x3F00),('ds',m.DS),('cs',0x1771),('eip',0x80DA),('ax',0xCAFE)]:m.set_reg(n,v)
                word(m,0x73000,0x826D)
                port.install(m,[(A.PORTS,None)])
                writes=[];m.on_write(0,MEM_SIZE-1,lambda a,n,v:writes.append((a,n,v)))
                # Positive observer control: same-value writes still count.
                m.write_as(0x72FFE,2,m.word_at(0x72FFE),m.lin('1771:80DA'));self.assertTrue(writes);writes.clear()
                memory=m.read(0,MEM_SIZE);regs=[m.reg(n) for n in REGS]
                with self.assertRaisesRegex(PortError,'deferred year rollover.*stage '+str(stage)):
                    m.run(m.lin('1771:826D'),fresh=True)
                self.assertEqual(writes,[])
                self.assertEqual(hashlib.sha256(m.read(0,MEM_SIZE)).digest(),hashlib.sha256(memory).digest())
                self.assertEqual([m.reg(n) for n in REGS],regs)
