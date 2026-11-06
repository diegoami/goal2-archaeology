"""T124e: actual stage-news calls, cursor lifetime and ordered page history."""
from tests.test_port_stages import _Calls, RET
from original_match import port
from original_match.port import Registry, stages as ST

RET.update({'000E:5DAF':'000E:5FA0','000E:5E6C':'000E:6199','000E:60CB':'000E:7152'})


def specs(variant=None,news_helpers=True):
    wanted={'000E:5DAF','000E:5E6C','000E:60CB','0791:DAF8','1771:55FC','1771:0947','214B:06B1','214B:0018','214B:003C','214B:007B','23E4:025D',
            '23E4:0644','23E4:062A','23E4:06B7','23E4:075A'}
    result=[]
    for reg,_ in port.load(['all']):
        sub=Registry(reg.name,reg.doc)
        for a,e in reg.entries.items():
            if a in wanted or (news_helpers and reg.name in ('news','route')):
                assert not e.stub;sub._add(e)
        if sub.entries:
            sub.variants=dict(reg.variants);result.append((sub,variant if reg.name=='stages' else None))
    return result


def manager_country(m):return m.read(m.far(ST.MANAGERS)+3*129,1)[0]


def parent_frame(m,rating=24,sacked=False):
    from original_match.match import SS_PARAGRAPH
    ss=m.seg(SS_PARAGRAPH)*16;parent=0x3F00
    m.write(ss+parent+6,manager_country(m).to_bytes(2,'little'))
    m.write(ss+parent-0x21,rating.to_bytes(2,'little'))
    if sacked:m.write(m.far(ST.GAME)+0x47+1,b'\1')


class StageNews(_Calls):
    def test_tour_helper_true_original_near_abi_and_no_duplicate_assistant_owner(self):
        self.assertEqual(ST.PORTS.entries['000E:5DAF'].ret,'ret 2')
        self.assertNotIn('0791:DAF8',ST.PORTS.entries)
        self.assertNotIn('1771:55FC',ST.PORTS.entries)
        m,p=self.call('000E:5DAF',(0x3F00,),specs=specs(),before=parent_frame)
        self.proved(p,'000E:5DAF')

    def test_failure_headline_keeps_manager_ownership_and_visits_tour_when_sacked(self):
        saved={}
        def before(m):
            parent_frame(m,sacked=True)
            saved['country']=manager_country(m);saved['tag']=m.read(m.far(ST.COUNTRIES)+191*saved['country']+46,1)
            m.wr(0x9B43,0x1234)
        m,p=self.call('000E:5E6C',(0x3F00,),specs=specs(),before=before)
        self.proved(p,'000E:5E6C')
        self.assertEqual(p.summary()['000E:5DAF']['nested'],1)
        self.assertEqual(m.read(m.far(ST.COUNTRIES)+191*saved['country']+46,1),saved['tag'])
        self.assertEqual(m.rd(0x9B43),0x1234)
