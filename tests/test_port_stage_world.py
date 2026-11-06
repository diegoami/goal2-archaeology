"""T124d: world constructors on faithful original-produced group/aggregate/bracket inputs.

PRIMARY private inputs are fresh nativeCP4 original Route/Match/legal11 contexts.
CI without private captures derives separate DECLARED SYNTHETIC fixtures from
nativeE006 using original constructors/6970 AND actualouter8757 finalization.
No host-written scores/rankings/winnerflags; no oldunfinalizedB1v4 input reuse.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from tests.test_port_stages import _Calls,RET,_image,ROOT
from tests.test_port_stage_qualifying import qualifying_rng_port,word
from original_match.image import Image
from original_match.machine import MEM_SIZE
from original_match.port import stages as ST

RET.update({'1771:6FEB':'1771:711C','1771:7090':'1771:76E2','1771:71B2':'1771:76EB','1771:74BE':'1771:76F4'})
ENTRIES={'1771:6FEB':'ret 2','1771:7090':'ret','1771:71B2':'ret','1771:74BE':'ret'}
HERE=ROOT/'experiments/E040-route-fixture-writes/out/T124d'
_CACHES={}


def get_inputs(load=None):
    """Source-correct immutable images; fallback load matches the shared old test machine."""
    key=load
    if key in _CACHES:return _CACHES[key]
    file=HERE/'natural-inputs-v1.jsonl'
    if file.exists():
        rows=[json.loads(l) for l in file.read_text().splitlines()]
        if rows[-1]['status']=='completed':
            entries={};afters={}
            for r in rows:
                if r.get('status') in ('constructor-entry','constructed'):
                    cp=r['checkpoint'];data=(ROOT/cp['path']).read_bytes()
                    assert hashlib.sha256(data).hexdigest()==cp['sha256']
                    image=Image(data)
                    if load is not None and image.load!=load:break
                    (entries if r['status']=='constructor-entry' else afters)[r['phase']]=image
            else:
                if len(entries)==len(afters)==7:
                    _CACHES[key]=(entries,afters,'naturalCP4');return _CACHES[key]
    spec=importlib.util.spec_from_file_location('t124d_unit_reference',HERE/'reference.py')
    ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
    base=_image()
    assert load is None or base.load==load
    entries,afters,_=ref.make_inputs(base)
    _CACHES[key]=(entries,afters,'declared synthetic E006/original6970+actual8757');return _CACHES[key]


def move_manager(m,continent,count=1):
    """Consistent controlled move to non-winning qualifying slots; not a natural career change."""
    g=m.far(ST.GAME);countries=m.far(ST.COUNTRIES);mgr=m.far(ST.MANAGERS);table=m.far(ST.TABLES)
    old_count=m.read(g,1)[0]
    for manager in range(1,old_count+1):
        old=m.read(mgr+3*(128+manager),1)[0]
        if old:m.write(countries+191*old+46,bytes([old]))
    m.write(g,bytes([count]));m.write(g+1,bytes([1 if count else 0]))
    selected=[]
    for manager in range(1,count+1):
        country=m.word_at(table+continent*0x1C0+0x38+8*(manager+1)+0xC00)
        assert country and m.read(countries+191*country+44,1)[0]==continent
        m.write(countries+191*country+46,bytes([128+manager]));m.write(mgr+3*(128+manager),bytes([country]))
        selected.append(country)
    return selected


def playoff_mark_input(m):move_manager(m,4,2)
def playoff_constructor_input(m):move_manager(m,3,1)
def host_input(m):word(m,m.far(0xA978),6)


def world_falsifier_input(m,variant):
    entries,afters,_=get_inputs(m.load)
    if variant=='world-playoff-mark-dropped':image=afters['playoffs']
    elif variant=='world-host-bound-seven':image=entries['groups']
    elif variant=='world-third-place-opponent':image=entries['finals']
    else:raise AssertionError(variant)
    m.write(0,bytes(image.memory[:MEM_SIZE]))
    if variant=='world-playoff-mark-dropped':playoff_mark_input(m)
    elif variant=='world-host-bound-seven':host_input(m)


def win(m,n,loser=False):
    p=m.far(ST.FIXTURES)+8*(n-1);flag=m.read(p+3,1)[0]
    winner=m.word_at(p+(6 if flag==1 else 4))
    if not loser:return winner
    return m.word_at(p+(4 if flag==1 else 6))


class World(_Calls):
    @classmethod
    def setUpClass(cls):
        super().setUpClass();cls.base=cls.image
        cls.entries,cls.afters,cls.input_kind=get_inputs()

    def specs(self,variant=None):
        return ((ST.PORTS,variant),'runtime',qualifying_rng_port(),(ST.display_helpers(),None))

    def phase_call(self,target,phase,*,after=False,variant=None,before=None,args=()):
        old=self.image;self.image=(self.afters if after else self.entries)[phase]
        try:return self.call(target,args,specs=self.specs(variant),before=before)
        finally:self.image=old

    def test_world_entries_with_true_return_abis(self):
        self.assertEqual({a:ST.PORTS.entries[a].ret for a in ENTRIES},ENTRIES)

    def test_marking_matches_any_manager_continent_not_actual_participation(self):
        m,p=self.phase_call('1771:6FEB','playoffs',after=True,args=(0x3E80,),before=playoff_mark_input)
        self.proved(p,'1771:6FEB')
        n=m.word_at(m.far(ST.GAME)+0x28)-1;fx=m.far(ST.FIXTURES)+8*(n-1)
        self.assertEqual(m.read(fx,1)[0],254)
        for off in (4,6):self.assertLessEqual(m.read(m.far(ST.COUNTRIES)+191*m.word_at(fx+off)+46,1)[0],128)

    def test_zero_managers_skip_marking(self):
        m,p=self.phase_call('1771:6FEB','playoffs',after=True,args=(0x3E80,),before=lambda m:move_manager(m,4,0))
        self.proved(p,'1771:6FEB')
        fx=m.far(ST.FIXTURES)+8*(m.word_at(m.far(ST.GAME)+0x28)-2)
        self.assertEqual(m.read(fx,1)[0],255)

    def test_both_playoff_legs_full_eight_byte_aggregate_and_broad_marks(self):
        m,p=self.phase_call('1771:7090','playoffs',before=playoff_constructor_input)
        self.proved(p,'1771:7090');g=m.far(ST.GAME);start=m.word_at(g+0x2C)
        self.assertEqual(m.word_at(g+0x28),start+16)
        fx=m.far(ST.FIXTURES)
        for pair in range(8):
            first=fx+8*(start+2*pair-1);second=first+8;agg=fx+8*(2400+pair)
            self.assertEqual(hashlib.sha256(m.read(first,8)).digest(),hashlib.sha256(m.read(agg,8)).digest())
            self.assertEqual((m.word_at(first+4),m.word_at(first+6)),(m.word_at(second+6),m.word_at(second+4)))
            self.assertEqual(m.read(first,1)[0],254 if pair<4 else 255)
            self.assertEqual(m.read(second,1)[0],254 if pair<4 else 255)

    def test_groups_finalize_aggregate_winners_and_all320_friendlies_before48_finals(self):
        m,p=self.phase_call('1771:71B2','groups')
        self.proved(p,'1771:71B2');g=m.far(ST.GAME);end=m.word_at(g+0x28);start=end-368;fx=m.far(ST.FIXTURES)
        self.assertEqual([m.read(fx+8*(n-1)+2,1)[0] for n in range(start,start+320)],[1]*320)
        self.assertEqual([m.read(fx+8*(n-1)+2,1)[0] for n in range(start+320,end)],[7]*48)
        table=m.far(ST.TABLES);countries=[]
        for group in range(1,9):
            actual={m.word_at(table+group*0x38+0x14C8+8*(slot-1)) for slot in range(1,5)}
            expected={m.word_at(table+group*0x38+0xDC8),m.word_at(table+(9-group)*0x38+0xDD0),
                      m.word_at(table+group*0x38+0xF88),win(m,2400+group)}
            self.assertEqual(actual,expected);countries.extend(actual)
        self.assertEqual(len(set(countries)),32)

    def test_last16_save_start_and_reverse_runnerup_groups(self):
        m,p=self.phase_call('1771:74BE','last16');self.proved(p,'1771:74BE')
        g=m.far(ST.GAME);start=m.word_at(g+0x2A);self.assertEqual(m.word_at(g+0x28),start+8)
        for i in range(8):self.assertEqual(m.read(m.far(ST.FIXTURES)+8*(start+i-1)+2,1)[0],8)

    def test_quarters_and_semis_use_previous_winners(self):
        for phase,count,kind in (('quarters',4,200),('semis',2,201)):
            with self.subTest(phase=phase):
                m,p=self.phase_call('1771:74BE',phase);self.proved(p,'1771:74BE')
                end=m.word_at(m.far(ST.GAME)+0x28)
                self.assertEqual([m.read(m.far(ST.FIXTURES)+8*(n-1)+2,1)[0] for n in range(end-count,end)],[kind]*count)

    def test_third_place_losers_precede_final_winners(self):
        m,p=self.phase_call('1771:74BE','finals');self.proved(p,'1771:74BE')
        g=m.far(ST.GAME);start=m.word_at(g+0x2A);end=m.word_at(g+0x28);fx=m.far(ST.FIXTURES)
        third=fx+8*(end-3);final=third+8
        self.assertEqual(m.read(third+2,1)[0],202);self.assertEqual(m.read(final+2,1)[0],203)
        self.assertEqual({m.word_at(third+4),m.word_at(third+6)},{win(m,start+12,True),win(m,start+13,True)})
        self.assertEqual({m.word_at(final+4),m.word_at(final+6)},{win(m,start+12),win(m,start+13)})

    def test_three_required_falsifiers_are_caught(self):
        from original_match.port.prove import ProofError
        for variant,target,phase,after,before,args in (
           ('world-host-bound-seven','1771:71B2','groups',False,host_input,()),
           ('world-playoff-mark-dropped','1771:6FEB','playoffs',True,playoff_mark_input,(0x3E80,)),
           ('world-third-place-opponent','1771:74BE','finals',False,None,())):
            with self.subTest(variant=variant),self.assertRaises(ProofError):
                self.phase_call(target,phase,after=after,variant=variant,before=before,args=args)
