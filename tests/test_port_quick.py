"""T77 concrete listing-value quick-result branches and original stack calls."""
import inspect
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import port
from original_match.port import quick,rare
from tests.test_port_selection import Rig as BaseRig
from tests.test_port_update import PSEG,POFF,SQSEG,SQOFF,GSEG,GOFF

class Rig(BaseRig):
    def run(self,address,words=(),answer=None,variant=None):
        self.respond=answer
        entry=(quick.PORTS.entries | rare.PORTS.entries)[address]
        sp=self.mem.reg('sp')
        for i,value in enumerate([0x5678]+([0x0791] if entry.far else [])+list(words)):
            self.lin16(sp+2*i,value)
        return self._invoke(entry,variant)

    def _invoke(self,entry,variant=None):
        mem=self.mem;sp=mem.reg('sp');bp=mem.reg('bp');mem._entries.append((sp,entry.far))
        try:
            value=entry.fn(mem,variant)
            if inspect.isgenerator(value):
                gen=value;sent=None
                while True:
                    try:request=gen.send(sent)
                    except StopIteration as stop:value=stop.value;break
                    self.steps+=1
                    if self.steps>10000:raise AssertionError('taker routine did not terminate')
                    self.calls.append((request.target,request.args,request.ret_to,request.far))
                    oldsp=mem.reg('sp');oldbp=mem.reg('bp');oldcs=mem.reg('cs');stack=oldsp
                    for w in request.args+((int(request.ret_to.split(':')[0],16),) if request.far else ())+ (int(request.ret_to.split(':')[1],16),):
                        stack=(stack-2)&0xFFFF;self.lin16(stack,w)
                    mem.regs.update(sp=stack,cs=int(request.target.split(':')[0],16))
                    handled=self.respond(request,mem) if self.respond else None
                    if handled is None and request.target=='23E4:08DF':
                        from original_match.port.pilot import in_set
                        element,seg,off=request.args
                        present=in_set(mem,mem.addr(seg,off),element&255)
                        mem.regs['eflags']=(mem.reg('eflags')&~64) if present else (mem.reg('eflags')|64)
                        handled=1
                    if handled is None:
                        registries=[quick.PORTS,rare.PORTS]+[port._module_registry(n) for n in ('runtime',)]
                        callee=next((reg.entries[request.target] for reg in registries if request.target in reg.entries),None)
                        if callee is not None:self._invoke(callee)
                        else:mem.regs['ax']=0
                    else:mem.regs['ax']=handled&0xFFFF
                    mem.regs.update(sp=oldsp,bp=oldbp,cs=oldcs);sent=mem.reg('ax')
            if value is not None:mem.regs['ax']=int(value)&0xFFFF
            return value
        finally:
            mem._entries.pop();mem.regs.update(sp=sp,bp=bp)


class Quick(unittest.TestCase):
    def test_all_four_entries_are_real_bodies(self):
        self.assertEqual(set(quick.PORTS.entries),{'0791:D733','0791:D5C1','0791:B19D','1771:0BC4'})
        self.assertTrue(all(e.stub is None for e in quick.PORTS.entries.values()))

    def test_trial_goals_opponent_draw_first_and_three_strict_contests(self):
        for draws,want,n in [([5,5],0,4),([5,6,8,8],0,6),([5,6,8,9,10,10],0,8),([5,6,8,9,10,11],1,8)]:
            r=Rig()
            for i,v in enumerate([31,32,41,42,51,52,61,62]):r.ds16(0x9B45+2*i,v)
            values=iter(draws+[1,1]);bounds=[]
            def answer(q,mem):
                if q.target=='214B:06B1':
                    bounds.append(q.args[0]);self.assertLessEqual(len(bounds),n,'extra RNG draw after a failed contest');return next(values,1)
            r.run('0791:B19D',[1],answer)
            self.assertEqual(r.mem.ds16(0x9B3C),want)
            self.assertEqual(len(bounds),n)
            self.assertEqual(bounds[:2],[52,51])
            if len(draws)>2:self.assertEqual(bounds[2:4],[84,61])
            if len(draws)>4:self.assertEqual(bounds[4:6],[32,61])

    def test_zero_attempts_retains_score_without_rng(self):
        r=Rig();r.ds16(0x9B3C,0x0302);r.run('0791:B19D',[0])
        self.assertEqual(r.mem.ds16(0x9B3C),0x0302);self.assertEqual(r.calls,[])

    def test_signed_trial_compare_rejects_high_bit_draw(self):
        r=Rig();draws=iter([1,0xFFFF,1,1])
        r.run('0791:B19D',[1],lambda q,m:next(draws,1))
        self.assertEqual(r.mem.ds16(0x9B3C),0)

    def test_line_strength_zero_players_and_signed_home_eighth(self):
        for flag,want in [(0,8),(1,9)]:
            r=Rig();r.squad(7,[101]+[0]*10);r.player(101,6,0);r.ds8(0xD4E,0)
            def answer(q,mem):
                if q.target=='1771:0AA7':return 0
                if q.target=='1771:377E':return 8
            r.run('1771:0BC4',[flag,1,7],answer)
            self.assertEqual(r.mem.ds16(0x9B47),want)
            self.assertEqual([r.mem.ds16(x) for x in (0x9B4B,0x9B4F,0x9B53)],[0]*3)

    def test_line_strength_split_roles_and_tactic_shares(self):
        r=Rig();r.squad(7,[101]+[0]*10);r.player(101,6,3);r.player(101,0,7)
        r.ds8(0xD51,4);r.country(7,45,0x31)
        r.lin8(0x1771*16+0xBA4,0x62)
        def answer(q,mem):
            if q.target=='1771:0AA7':return 16
            if q.target=='1771:377E':return 9
        r.run('1771:0BC4',[0,0,7],answer)
        self.assertEqual([r.mem.ds16(x) for x in (0x9B45,0x9B49,0x9B4D,0x9B51)],[0,12,12,6])

    def test_quick_commit_is_one_goal_and_energy_signed_boundary(self):
        r=Rig();r.ds16(0x9B3C,0x0102);r.ds16(0x831B,5);r.ds16(0x831F,3)
        r.ds8(0xA8A,1);r.ds8(0xA8C,90);r.ds8(0xA6C,1)
        r.ds16(0x9B34,7);r.ds16(0x9B36,19);r.squad(7,[101]*20);r.squad(19,[102]*20)
        for slot in range(1,23):r.ds16(0x80E8+22*slot+13,100+slot)
        for w,e in [(101,2),(102,1),(103,0),(104,255),(105,127)]:r.player(w,14,e)
        def answer(q,mem):
            if q.target=='0791:B19D':r.ds16(0x9B3C,0x0304);return 0
            if q.target=='1771:0BC4':return 0
            if q.target=='214B:06B1':return 1 if q.args[0]==30 else 3
            if q.target=='1771:3216':return 0
            if q.target=='1771:3A82':return 1
            if q.target=='214B:06D0':return 0
            return 0
        r.run('0791:D733',answer=answer)
        self.assertEqual(r.mem.ds16(0x9B3C),0x0103)
        self.assertEqual(len(r.args('0791:6443')),1)
        self.assertEqual([r.mem.u8(PSEG*16+POFF+20*w+14) for w in range(101,106)],[1,1,0,255,126])
        score_writers=[at for off,size,v,at in r.writes if off==0x9B3C]
        self.assertIn(r.mem.lin('0791:D77B'),score_writers);self.assertIn(r.mem.lin('0791:DA58'),score_writers)
        self.assertEqual(len(r.args('0791:65FE')),1);self.assertEqual(r.args('0791:8062'),[])

    def test_quick_foul_unavailable_skips_coin_and_skill_draws(self):
        for unavailable in (1,2):
            r=Rig();checks=[]
            def answer(q,mem):
                if q.target=='214B:06B1':return 1
                if q.target=='0791:2956':checks.append(q.args);return int(len(checks)==unavailable)
                self.fail('unexpected call '+q.target)
            r.run('0791:D5C1',[0x2000],answer)
            self.assertEqual(len(checks),unavailable)

if __name__=='__main__':unittest.main()
