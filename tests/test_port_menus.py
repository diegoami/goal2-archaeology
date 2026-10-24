"""T74: listing boundary branches, key-service ABI, and actual IVT/IRET calls."""
import inspect
import signal
import sys
import unittest
from pathlib import Path
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
from original_match import port
from original_match.port import menus
from original_match.port.mem import PlainMem
from tests.test_port_update import Rig as BaseRig, PSEG, POFF, SQSEG, SQOFF


class KeysMem(PlainMem):
    def _key(self,site):
        self.key_sites.append(site)
        value=self.keys.pop(0)
        self.wds8(0xA976,value,'214B:0947')
        self.wds8(0xA977,value,'214B:097C')
        return value

    def _keypressed(self,site):
        self.poll_sites.append(site)
        return self.waiting


class Rig(BaseRig):
    def __init__(self):
        super().__init__()
        old=self.mem
        self.mem=KeysMem(old.memory,regs=old.regs)
        self.mem.listeners=old.listeners
        self.mem.keys=[];self.mem.key_sites=[];self.mem.poll_sites=[];self.mem.waiting=False
        self.mem.regs.update(cs=0x1771)
        self.respond=None
        self.calls=[]
        self.steps=0

    def run(self,address,words=(),answer=None,variant=None):
        self.respond=answer
        entry=menus.PORTS.entries[address]
        sp=self.mem.reg('sp')
        layout=[0x5678]+([0x0791] if entry.far else [])+list(words)
        for i,value in enumerate(layout):self.lin16(sp+2*i,value)
        return self._invoke(entry,variant)

    def _invoke(self,entry,variant=None):
        mem=self.mem;sp=mem.reg('sp');bp=mem.reg('bp')
        mem._entries.append((sp,entry.far))
        try:
            value=entry.fn(mem,variant)
            if inspect.isgenerator(value):
                gen=value;sent=None
                while True:
                    try:request=gen.send(sent)
                    except StopIteration as stop:value=stop.value;break
                    self.steps+=1
                    if self.steps>1000:raise AssertionError('menu did not terminate within1000 calls')
                    self.calls.append((request.target,request.args,request.ret_to,request.far))
                    oldsp=mem.reg('sp');oldbp=mem.reg('bp');oldcs=mem.reg('cs')
                    stack=oldsp
                    for word in request.args+((int(request.ret_to.split(':')[0],16),) if request.far else ())+ (int(request.ret_to.split(':')[1],16),):
                        stack=(stack-2)&0xFFFF;self.lin16(stack,word)
                    mem.regs.update(sp=stack,cs=int(request.target.split(':')[0],16))
                    handled=self.respond(request,mem) if self.respond else None
                    if handled is None and request.target=='23E4:08DF':
                        from original_match.port.pilot import in_set
                        element,seg,off=request.args
                        present=in_set(mem,mem.addr(seg,off),element&255)
                        mem.regs['eflags']=(mem.reg('eflags')&~0x40) if present else (mem.reg('eflags')|0x40)
                        handled=1<<(element&7)
                    if handled is None:
                        registry=menus.PORTS if request.target in menus.PORTS.entries else port._module_registry('runtime')
                        callee=registry.entries.get(request.target)
                        if callee is None:callee=port._module_registry('pilot').entries.get(request.target)
                        if callee is not None:self._invoke(callee)
                        else:mem.regs['ax']=0
                    else:mem.regs['ax']=handled&0xFFFF
                    mem.regs.update(sp=oldsp,bp=oldbp,cs=oldcs)
                    sent=mem.reg('ax')
            if value is not None:mem.regs['ax']=int(value)&0xFFFF
            return value
        finally:
            mem._entries.pop();mem.regs.update(sp=sp,bp=bp)


class Menus(unittest.TestCase):
    def setUp(self):
        def expired(*args):raise AssertionError('menu did not terminate within10seconds')
        signal.signal(signal.SIGALRM,expired);signal.alarm(10)

    def tearDown(self):signal.alarm(0)

    def test_all27_listing_returns(self):
        expected={'0791:9372':'ret','0791:92FC':'ret 2','0791:ED8A':'ret 2','0791:7FCF':'ret 4',
                  '1771:1981':'retf 2','1771:4859':'retf 6','1771:4925':'ret 4','1771:4952':'retf 2',
                  '1771:49B8':'ret 2','1771:4B61':'retf 4','214B:04F8':'retf 4','214B:0566':'retf 4',
                  '214B:0723':'retf','214B:08DD':'retf','214B:0983':'retf','214B:0993':'retf 2',
                  '214B:09A7':'retf 4','214B:13F6':'retf 6','214B:1452':'retf 6','214B:14AC':'retf 6',
                  '214B:1507':'retf 6','214B:1560':'retf 6','214B:158E':'ret 6','214B:15B1':'retf 12',
                  '214B:1765':'retf 6','235C:0000':'retf 6','235C:000B':'retf 6'}
        self.assertEqual({a:e.ret for a,e in menus.PORTS.entries.items()},expected)
        self.assertTrue(all(e.stub is None for e in menus.PORTS.entries.values()))
        for address,entry in menus.PORTS.entries.items():
            self.assertEqual(entry.return_stack_delta,-2 if address=='235C:0000' else 0)

    def test_key_pressed_service_preserves_frame_and_high_ax(self):
        for waiting in (False,True):
            r=Rig();r.mem.waiting=waiting;r.mem.regs['ax']=0xA5FF
            before=bytes(r.mem.memory[0x2F00:0x3000])
            r.run('214B:0723')
            self.assertEqual(r.mem.reg('ax'),0xA500+waiting)
            self.assertEqual(r.mem.poll_sites,['0791:5678'])
            self.assertEqual(bytes(r.mem.memory[0x2F00:0x3000]),before)

    def test_key_read_service_and_pushed_key_are_distinct_paths(self):
        r=Rig();r.mem.keys=[0xAF];r.mem.regs['ax']=0xCAFE
        r.run('214B:08DD')
        self.assertEqual((r.mem.ds8(0xA976),r.mem.ds8(0xA977),r.mem.reg('ax')),(0xAF,0xAF,0xCAFE))
        self.assertEqual(r.mem.key_sites,['0791:5678'])
        p=Rig();p.ds8(0x79AE,1);p.ds8(0xA976,0xB1);p.mem.regs['ax']=0xCAFE
        p.run('214B:08DD')
        self.assertEqual((p.mem.ds8(0x79AE),p.mem.ds8(0xA977),p.mem.reg('ax')),(0,0xB1,0xCAB1))
        self.assertEqual(p.mem.key_sites,[])
        self.assertEqual(p.u16(0x2FFE),0x1234)

    def test_pushback_and_wait_clear(self):
        r=Rig();r.run('214B:0993',[0x52]);self.assertEqual((r.mem.ds8(0x79AE),r.mem.ds8(0xA976)),(1,0x52))
        r.mem.keys=[];r.run('214B:0983')
        self.assertEqual((r.mem.ds8(0x79AE),r.mem.ds8(0xA976),r.mem.ds8(0xA977)),(0,0,0x52))

    def test_byte_and_word_clamp_boundaries(self):
        # Home/page-up, End/page-down, arrows at both limits, ignored key.
        cases=[(0xAB,5,1),(0xAD,5,1),(0xB0,5,9),(0xB2,5,9),
               (0xAC,1,1),(0xAC,5,4),(0xB1,9,9),(0xB1,5,6),(0x1B,5,5)]
        for address,word in [('214B:13F6',False),('214B:14AC',True)]:
            for key,start,want in cases:
                with self.subTest(address=address,key=key,start=start):
                    r=Rig();r.ds8(0xA976,key);r.lin16(0x42000,start)
                    r.run(address,[9,0,0x4200])
                    self.assertEqual(r.u16(0x42000),want)
            # Word comparisons are unsigned; the byte path truncates only stores.
            r=Rig();r.ds8(0xA976,0xB0);r.run(address,[0x0102,0,0x4200])
            self.assertEqual(r.u16(0x42000),0x0102 if word else 2)

    def test_wrap_up_down_and_delegated_keys(self):
        for address in ('214B:1452','214B:1507'):
            for key,start,want in [(0xAC,1,9),(0xAC,5,4),(0xB1,9,1),(0xB1,5,6),(0xAB,5,1),(0xB0,5,9),(0x1B,5,5)]:
                with self.subTest(address=address,key=key,start=start):
                    r=Rig();r.ds8(0xA976,key);r.lin16(0x42000,start)
                    r.run(address,[9,0,0x4200]);self.assertEqual(r.u16(0x42000),want)

    def test_position_next_wraps13_to0_and_clears_key(self):
        for start,want in [(0,1),(1,2),(12,13),(13,0),(255,0)]:
            r=Rig();r.lin8(0x42000,start)
            r.run('1771:4925',[0,0x4200])
            self.assertEqual(r.mem.u8(0x42000),want)
            self.assertEqual(r.mem.ds8(0xA976),0)
            self.assertIn(('214B:1452','1771:4941'),r.targets())

    def test_position_club_reset_and_zero_player(self):
        for word in (0,5):
            r=Rig();r.ds8(0xA976,ord('C'));r.player(5,6,8);r.player(5,7,3)
            r.ds8(0xC1F,1);r.ds8(0xC1E,1)
            r.run('1771:4952',[word])
            self.assertEqual(r.mem.u8(PSEG*16+POFF+0x14*5+6),3 if word else 8)
            self.assertEqual(r.mem.ds8(0x9B55),int(bool(word)))
            self.assertEqual(bool(r.args('1771:3EF8')),bool(word))

    def test_position_rotation_and_no_refresh_flags(self):
        r=Rig();r.ds8(0xA976,ord('R'));r.player(5,6,13)
        r.run('1771:4952',[5]);self.assertEqual(r.mem.u8(PSEG*16+POFF+0x14*5+6),0)
        self.assertEqual(r.mem.ds8(0x9B55),0);self.assertFalse(r.args('1771:3EF8'))

    def test_zero_player_own_tactics_and_name_edit_do_nothing(self):
        for address,words in [('1771:4B61',[1,0]),('1771:4859',[2,8,0])]:
            r=Rig();r.run(address,words);self.assertFalse(r.calls)

    def test_message_if_flag_returns_low_byte_and_only_shows_when_set(self):
        for value in (0,1,0xFF):
            r=Rig();r.lin8(0x42000,3);r.mem.memory[0x42001:0x42004]=b'abc'
            def respond(q,mem):
                return 0 if q.target=='214B:04F8' else None
            r.run('214B:1765',[0,0x4200,value],answer=respond)
            self.assertEqual(r.mem.reg('ax')&255,value)
            self.assertEqual(bool(r.args('214B:04F8')),bool(value))
            self.assertEqual(r.mem.read(0x2FFE-0x52,4),b'\x03abc')

    def test_quick_result_guards_and_deferred_notice(self):
        for field,value in [(0x9A3E,1),(0x831B,0),(0x8326,1),(0x0C21,1)]:
            r=Rig();r.ds16(0x831B,20);r.ds8(0x8325,1)
            (r.ds16 if field==0x831B else r.ds8)(field,value)
            r.run('0791:92FC',[0x1234])
            self.assertFalse(r.calls)
        for field in (0x8325,0x0C20,0x7C37,0x9B55):
            r=Rig();r.ds16(0x831B,20);r.ds8(0x8325,1)
            r.ds8(field,0 if field==0x8325 else 1)
            r.run('0791:92FC',[0x1234])
            self.assertEqual(r.mem.ds8(0x7C38),1)
            self.assertEqual(r.mem.ds8(0x9A3E),0)
            self.assertEqual(len(r.args('214B:0329')),1)
            r.calls=[];r.run('0791:92FC',[0x1234])
            self.assertFalse(r.calls)  # already deferred: do not unpack twice

    def test_quick_result_commits_flags_and_calls_board_with_zero_low_byte(self):
        r=Rig();r.ds16(0x831B,20);r.ds8(0x8325,1);r.ds8(0x7C38,1);r.mem.regs['ax']=0xABCD
        r.run('0791:92FC',[0x1234])
        self.assertEqual([r.mem.ds8(k) for k in (0x9A3E,0x9A3F,0x7C38)],[1,1,0])
        self.assertEqual(r.args('0791:0106'),[(0xAB00,)])

    def test_poll_speed_arrows_clamp_at_zero_and_five(self):
        for key,speed,want in [(0xAE,2,3),(0xAE,5,5),(0xAF,2,1),(0xAF,0,0)]:
            with self.subTest(key=key,speed=speed):
                r=Rig();r.mem.waiting=True;r.mem.keys=[key]
                address=r.mem.ds_far(0xA923)+0x3F;r.lin8(address,speed)
                r.run('0791:9372')
                self.assertEqual(r.mem.u8(address),want)
                self.assertEqual(r.mem.key_sites,['0791:93D3'])
                self.assertEqual(r.mem.poll_sites,['0791:93C2'])

    def test_poll_dispatches_board_menu_sound_help_and_pitch(self):
        expected={0x20:'0791:1A04',0x0D:'0791:ED8A',0x1B:'0791:ED8A',
                  0xA7:'214B:1E5A',0x9F:'16D6:0945',0xAC:'214B:1D6F',0xB1:'214B:1D6F'}
        for key,target in expected.items():
            with self.subTest(key=key):
                r=Rig();r.mem.waiting=True;r.mem.keys=[key]
                def respond(q,mem):
                    return 0 if q.target in ('0791:ED8A','0791:1A04','16D6:0945','0791:0691') else None
                r.run('0791:9372',answer=respond)
                self.assertTrue(r.args(target) or any(t==target for t,_,_,_ in r.calls))
        r=Rig();r.mem.waiting=True;r.mem.keys=[0x9F];r.ds8(0x9A3E,1)
        r.run('0791:9372');self.assertFalse(any(t=='16D6:0945' for t,_,_,_ in r.calls))

    def test_poll_queued_quick_and_idle_deferred_call_use_parent_bp(self):
        for waiting in (False,True):
            r=Rig();r.mem.waiting=waiting;r.mem.keys=[ord('R')] if waiting else []
            r.ds8(0x7C38,1)
            r.run('0791:9372')
            self.assertEqual(r.args('0791:92FC'),[(0x2FFE,)])

    def test_team_tactics_toggles_selected_element_and_refreshes_marking(self):
        for element in (4,8):
            r=Rig();r.ds16(0xD8E,1);r.ds8(0x6BC0,element);r.ds8(0xC1E,1)
            keys=iter([13,27])
            def respond(q,mem):
                if q.target=='1771:0B77':return 1
                if q.target=='214B:1560':r.ds8(0xA976,next(keys));return 0
                return None
            r.run('1771:1981',[7],answer=respond)
            self.assertEqual(r.mem.u8(SQSEG*16+SQOFF+0xBF*7+0x2D),1<<(element-1))
            self.assertEqual(r.mem.ds8(0xC1A),1)
            self.assertEqual(len(r.args('1771:3EF8')),2 if element==8 else 0)

    def test_team_tactics_view_only_for_computer_or_locked_game(self):
        for managed,locked in [(0,0),(1,1)]:
            r=Rig();r.ds8(0xC20,locked);r.ds16(0xD8E,1);r.ds8(0x6BC0,4)
            def respond(q,mem):
                if q.target=='1771:0B77':return managed
                if q.target=='214B:1560':r.ds8(0xA976,13);return 0
                return None
            r.run('1771:1981',[7],answer=respond)
            self.assertFalse(r.args('214B:0CF4'));self.assertEqual(r.mem.ds8(0xC1A),0)
            self.assertEqual(len(r.args('214B:1560')),1)

    def test_own_tactic_three_states_and_return_to_team_value(self):
        for original,team,want in [(0,0,0x10),(0x10,0,0x11),(0x11,0,0),(0x11,1,1)]:
            with self.subTest(original=original,team=team):
                r=Rig();r.player(5,0,7);r.player(5,6,3);r.player(5,15,original)
                r.country(7,0x2D,team);r.ds16(0xF38,1);r.ds8(0xC1F,1)
                keys=iter([13,27])
                def respond(q,mem):
                    if q.target=='214B:1560':r.ds8(0xA976,next(keys));return 0
                    return None
                r.run('1771:4B61',[1,5],answer=respond)
                self.assertEqual(r.mem.u8(PSEG*16+POFF+0x14*5+15),want)
                self.assertEqual(r.mem.ds8(0x9B55),1)

    def test_own_tactics_marking_visibility_and_row5_dispatch(self):
        cases=[(0,3,1,0,False),(1,1,1,0,False),(1,3,0,0,False),(1,3,1,1,False),(1,3,1,0,True)]
        for setup,position,allowed,unavailable,can in cases:
            with self.subTest(setup=setup,position=position,allowed=allowed,unavailable=unavailable):
                r=Rig();r.player(5,0,7);r.player(5,6,position);r.ds8(0xC1E,setup);r.ds16(0xF38,5)
                keys=iter([13,27] if can else [27])
                def respond(q,mem):
                    if q.target=='1771:3216':return unavailable
                    if q.target=='214B:1560':r.ds8(0xA976,next(keys));return 0
                    if q.target=='1771:49B8':return 0
                    return None
                r.run('1771:4B61',[allowed,5],answer=respond)
                self.assertEqual(r.mem.ds16(0xF38),5 if can else 1)
                self.assertEqual(bool(r.args('1771:49B8')),can)
                self.assertTrue(all(a[-1]==(5 if can else 4) for a in r.args('214B:1560')))

    def test_marking_cycle_default_opponent_wrap_and_skip_unavailable(self):
        cases=[(0,0,0x40,0),(0x40,0,0x40,202),(0x40,211,0,0),(0x40,202,0x40,204)]
        for status,oldmark,wantstatus,wantmark in cases:
            with self.subTest(status=status,oldmark=oldmark):
                r=Rig();r.player(5,0,7);r.player(5,6,3);r.player(5,16,status)
                r.ds16(0x9B34,7);r.ds16(0x9B36,19);r.squad(19,list(range(201,212)))
                r.lin16(0x2008,5);r.ds16(0x9A44,oldmark)
                def respond(q,mem):
                    if q.target=='1771:3A82':return 3
                    if q.target=='1771:3216':return int(q.args[0]==203)
                    return None
                r.run('1771:49B8',[0x2000],answer=respond)
                self.assertEqual(r.mem.u8(PSEG*16+POFF+0x14*5+16),wantstatus)
                self.assertEqual(r.mem.ds16(0x9A44),wantmark)
                self.assertEqual(len(r.args('1771:3EF8')),1)

    def test_marking_goalkeeper_clears_flag_without_touching_word(self):
        r=Rig();r.player(5,0,19);r.player(5,6,1);r.player(5,16,0x41)
        r.ds16(0x9B34,7);r.ds16(0x9B36,19);r.lin16(0x2008,5);r.ds16(0x9A6C,777)
        def respond(q,mem):return 3 if q.target=='1771:3A82' else None
        r.run('1771:49B8',[0x2000],answer=respond)
        self.assertEqual(r.mem.u8(PSEG*16+POFF+0x14*5+16),1)
        self.assertEqual(r.mem.ds16(0x9A6C),777)

    def menu_rig(self,script,item=10,valid=(1,),used=1,change=False,locked=0,member=False):
        r=Rig();r.ds16(0x9B34,7);r.ds16(0x9B36,19);r.ds8(0xAC2,item);r.ds8(0xAC3,5)
        r.ds8(0xAC4,2);r.ds8(0xAC5,7);r.ds8(0x7920,255);r.ds8(0x7921,1)
        r.ds8(0xC1F,used);r.ds8(0xC21,locked)
        commands=iter(script);validity=iter(valid);r.menu_highlights=[]
        def respond(q,mem):
            if q.target=='1771:0B77':return int(q.args[0]==7)
            if q.target=='214B:1560':
                pointer=q.args[0]*16+q.args[1];r.menu_highlights.append(mem.u16(pointer))
                key,newitem=next(commands);r.ds8(0xA976,key)
                if newitem is not None:r.lin16(pointer,newitem)
                return 0
            if q.target=='23E4:08DF' and q.ret_to=='0791:EF07':
                mem.regs['eflags']=(mem.reg('eflags')&~0x40) if member else (mem.reg('eflags')|0x40)
                return 0
            if q.target=='1771:1981':
                if change:r.country(q.args[0],0x2D,8)
                return 0
            if q.target=='0791:EA09':return next(validity)
            if q.target=='214B:1765':return locked
            # Drawings and other rows remain declared guest calls in this unit.
            if q.target in ('0791:A75D','0791:E949','0791:E929','0791:0106','214B:0329','214B:02C8','214B:13C5'):
                return 0
            return None
        return r,respond

    def test_team_menu_tactics_refresh_changed_and_unchanged(self):
        for change in (False,True):
            r,respond=self.menu_rig([(13,None),(13,10)],item=6,change=change)
            r.run('0791:ED8A',[1],answer=respond)
            self.assertEqual(r.mem.ds8(0x9B55),int(change))
            self.assertEqual(r.args('1771:1981'),[(7,)])
            self.assertEqual(r.mem.ds8(0xC1F),1)
            self.assertEqual(len(r.args('0791:230C')),2)

    def test_team_menu_submenu_routes_board_tables_and_space(self):
        for item,target in [(2,'0791:E949'),(7,'0791:E949'),(4,'0791:0106'),(9,'0791:0106'),(3,'0791:E929'),(8,'0791:E929')]:
            r,respond=self.menu_rig([(13,None),(13,10)],item=item)
            r.run('0791:ED8A',[0],answer=respond)
            self.assertTrue(any(t==target for t,_,_,_ in r.calls),(item,target))
        r,respond=self.menu_rig([(0x20,None),(13,10)])
        r.run('0791:ED8A',[0],answer=respond)
        self.assertEqual(r.args('0791:E949'),[(0x2FFE,)])
        r,respond=self.menu_rig([(13,None),(13,10)],item=3,locked=1)
        r.run('0791:ED8A',[0],answer=respond)
        self.assertFalse(r.args('0791:E929'))

    def test_team_menu_home_end_horizontal_and_display_toggle(self):
        for key,membership,want in [(0xAB,False,2),(0xB0,False,10),(0xAE,False,7),(0xAF,False,2),
                                    (0xAE,True,5),(0xAF,True,5)]:
            r,respond=self.menu_rig([(key,None),(13,10)],member=membership)
            r.run('0791:ED8A',[0],answer=respond)
            self.assertEqual(r.menu_highlights[1],want)
        for initial,want in [(0,1),(1,0),(255,0)]:
            r,respond=self.menu_rig([(0xB6,None),(13,10)])
            address=r.mem.ds_far(0xA923)+0x41;r.lin8(address,initial)
            r.run('0791:ED8A',[0],answer=respond)
            self.assertEqual(r.mem.u8(address),want)

    def test_team_menu_escape_before_used_and_invalid_eleven_retry(self):
        r,respond=self.menu_rig([(27,None),(13,10)],used=0)
        r.run('0791:ED8A',[0],answer=respond)
        self.assertEqual(len(r.args('214B:1560')),2)
        r,respond=self.menu_rig([(27,None)],used=1)
        r.run('0791:ED8A',[0],answer=respond)
        self.assertEqual(len(r.args('214B:1560')),1)
        r,respond=self.menu_rig([(13,None),(13,None)],valid=(0,1))
        r.run('0791:ED8A',[0],answer=respond)
        self.assertEqual(len(r.args('0791:EA09')),2)

    def test_timed_notice_keeper_template_and_key_or_escape(self):
        for keeper,waiting in [(0,False),(1,True)]:
            r=Rig();r.mem.waiting=waiting;r.mem.keys=[13] if waiting else []
            r.ds16(0x9B34,7);r.ds16(0x9B36,19)
            def respond(q,mem):return 0 if q.target=='214B:0329' else None
            r.run('0791:7FCF',[1,keeper],answer=respond)
            self.assertEqual(r.args('214B:0329')[0][1],0x5B66 if keeper else 0x5B30)
            self.assertEqual(bool(r.args('1771:0F58')),bool(keeper))
            self.assertEqual(r.mem.ds8(0xA977),13 if waiting else 27)
            if keeper:self.assertEqual(r.args('1771:0F58'),[(19,25,1)])

    def test_wait_key_set_rejects_first_key_then_accepts_second(self):
        r=Rig();r.mem.keys=[ord('N'),ord('Y')]
        r.lin8(0x42000+ord('Y')//8,1<<(ord('Y')%8))
        r.run('214B:09A7',[0,0x4200])
        self.assertEqual(r.mem.ds8(0xA976),ord('Y'))
        self.assertEqual(len(r.mem.key_sites),2)

    def test_yes_no_returns_uppercase_y_only_and_clears_current_key(self):
        for key,want in [(ord('y'),1),(ord('N'),0)]:
            r=Rig();r.lin8(0x42000,3);r.mem.memory[0x42001:0x42004]=b'why'
            def respond(q,mem):
                if q.target=='214B:09A7':r.ds8(0xA976,key);return 0
                if q.target=='214B:0350':return 0
                return None
            r.run('214B:0566',[0,0x4200],answer=respond)
            self.assertEqual(r.mem.reg('ax')&255,want)
            self.assertEqual(r.mem.ds8(0xA976),0)
            self.assertTrue(r.args('214B:0643') or any(t=='214B:0643' for t,_,_,_ in r.calls))

    def test_message_wait_restores_attribute_and_uses_press_any_key(self):
        r=Rig();r.ds8(0x7922,0x17);r.ds8(0x7924,0x70);r.mem.keys=[13]
        r.lin8(0x42000,3);r.mem.memory[0x42001:0x42004]=b'why'
        def respond(q,mem):return 0 if q.target=='214B:0350' else None
        r.run('214B:04F8',[0,0x4200],answer=respond)
        self.assertEqual(r.mem.ds8(0x7922),0x17)
        self.assertEqual((r.mem.ds8(0xA976),r.mem.ds8(0xA977)),(0,13))
        self.assertEqual(r.args('23E4:06B7'),[(0x214B,0x4E7)])

    def test_name_editor_unchanged_changed_and_empty_surname_paths(self):
        cases=[(b'A Smith',0,0,b''),(b'b jones',1,ord('b'),b'Jones'),
               (b'BJones',1,ord('B'),b'Jones'),(b'B',0,ord('B'),b'')]
        for edited,changed,initial,surname in cases:
            with self.subTest(edited=edited):
                r=Rig();r.ds16(0x9B70,0x100);r.ds16(0x9B72,0x4200)
                r.ds16(0x9B6C,0x200);r.ds16(0x9B6E,0x4200)
                def put(pointer,text):
                    r.mem.memory[pointer:pointer+len(text)+1]=bytes([len(text)])+text
                def respond(q,mem):
                    if q.target=='1771:2E93':
                        sp=mem.reg('sp');off=mem.u16(mem.ss_lin(sp+6));seg=mem.u16(mem.ss_lin(sp+8))
                        put(mem.addr(seg,off),b'A Smith');return 0
                    if q.target=='214B:1086':put(q.args[0]*16+q.args[1],edited);return 0
                    return None
                r.run('1771:4859',[2,8,5],answer=respond)
                self.assertEqual(r.mem.ds8(0xC1A),changed)
                self.assertEqual(r.mem.u8(0x42105),initial)
                if surname:
                    self.assertEqual(r.mem.read(0x42200+55,len(surname)+1),bytes([len(surname)])+surname)
                else:self.assertEqual(r.mem.u8(0x42200+55),0)

    def test_marking_second_side_uses_first_country_and_second_mark_array(self):
        r=Rig();r.player(5,0,19);r.player(5,6,3);r.player(5,16,0x40)
        r.ds16(0x9B34,7);r.ds16(0x9B36,19);r.squad(7,list(range(101,112)))
        r.lin16(0x2008,5);r.ds16(0x9A6C,0)
        def respond(q,mem):
            if q.target=='1771:3A82':return 3
            if q.target=='1771:3216':return 0
            return None
        r.run('1771:49B8',[0x2000],answer=respond)
        self.assertEqual(r.mem.ds16(0x9A6C),102)
        self.assertEqual(r.args('1771:3A82'),[(5,19)])

    def test_short_list_page_down_clamps_cursor_to_count(self):
        r=Rig();r.ds8(0xA976,0xB2);r.lin16(0x42020,1);r.lin16(0x42030,1)
        r.run('214B:15B1',[3,5,0x20,0x4200,0x30,0x4200])
        self.assertEqual((r.u16(0x42020),r.u16(0x42030)),(1,3))

    def test_list_pair_writes_parent_far_pointers_in_order(self):
        r=Rig();parent=0x2000
        r.lin16(parent+14,0x20);r.lin16(parent+16,0x4200)
        r.lin16(parent+10,0x30);r.lin16(parent+12,0x4200)
        r.run('214B:158E',[parent,7,3])
        self.assertEqual((r.u16(0x42020),r.u16(0x42030)),(3,7))
        self.assertEqual(r.written('214B:159B'),[(0x42020,2,3)])
        self.assertEqual(r.written('214B:15A8'),[(0x42030,2,7)])

    def test_list_navigation_edges_pages_home_end(self):
        cases=[(0xB1,1,1,1,2),(0xB1,1,5,2,5),(0xB1,16,5,16,5),
               (0xAC,1,1,1,1),(0xAC,4,1,3,1),(0xAC,4,3,4,2),
               (0xAD,1,4,1,1),(0xAD,3,4,1,4),(0xAD,8,4,3,4),
               (0xB2,1,3,6,3),(0xB2,14,3,16,3),(0xB2,16,1,16,5),
               (0xAB,8,4,1,1),(0xB0,1,1,16,5),(0x1B,3,2,3,2)]
        for key,top,cursor,wanttop,wantcursor in cases:
            with self.subTest(key=key,top=top,cursor=cursor):
                r=Rig();r.ds8(0xA976,key);r.lin16(0x42020,top);r.lin16(0x42030,cursor)
                r.run('214B:15B1',[20,5,0x20,0x4200,0x30,0x4200])
                self.assertEqual((r.u16(0x42020),r.u16(0x42030)),(wanttop,wantcursor))

    def test_list_short_page_end_uses_long_signed_max(self):
        r=Rig();r.ds8(0xA976,0xB0);r.lin16(0x42020,1);r.lin16(0x42030,1)
        r.run('214B:15B1',[3,5,0x20,0x4200,0x30,0x4200])
        self.assertEqual((r.u16(0x42020),r.u16(0x42030)),(1,3))


class IVT(unittest.TestCase):
    def run_interrupt(self,target='235C:000B',handler=b'\xCF'):
        from original_match.machine import Machine
        memory=bytearray(0x110000)
        # Synthetic code only: real IRET, without a byte from GOAL.EXE.
        memory[0x40100:0x40100+len(handler)]=handler
        for interrupt in (0x16,0x21):
            memory[interrupt*4:interrupt*4+4]=bytes.fromhex('00010040')
        values=[0x101,0x202,0x303,0x404,0x505,0x606,0x707,0x0A00,0x0B00]
        for k,value in enumerate(values):memory[0x60020+k*2:0x60022+k*2]=value.to_bytes(2,'little')
        m=Machine(memory,load=0)
        args=([0x16] if target.endswith('000B') else [])+[0x6000,0x20]
        end=m.far_call(target,args,'3000:0010',ss=0x5000,sp=0x100)
        m.set_reg('bp',0xA5A5);m.set_reg('eflags',0x602)
        inst=port.install(m,['menus'])
        self.assertIsNone(m.run(end,5,fresh=True))
        actual=[m.word_at(0x60020+2*k) for k in range(10)]
        return m,inst,actual,values

    def test_interrupt_wrapper_actual_iret_preserves_record_and_flags(self):
        m,inst,actual,values=self.run_interrupt()
        self.assertEqual(actual,values+[0x602])
        self.assertEqual((m.reg('sp'),m.reg('bp'),m.reg('ds')),(0x10A,0xA5A5,m.DS))
        self.assertEqual(inst.calls['235C:000B'],1)
        self.assertEqual(m.frames,[])

    def test_msdos_fallthrough_adds_int21_without_changing_pointer_cleanup(self):
        # mov ax,1234; mov bx,5678; iret.
        m,inst,actual,values=self.run_interrupt('235C:0000',bytes.fromhex('b83412bb7856cf'))
        self.assertEqual(actual,[0x1234,0x5678]+values[2:]+[0x602])
        self.assertEqual((m.reg('sp'),m.reg('bp'),m.reg('ds')),(0x108,0xA5A5,m.DS))
        self.assertEqual(inst.calls['235C:0000'],1)
        self.assertEqual(m.frames,[])
        # The original shifted return IP remains atP-2; P andP+2 retain
        # original CS and argument offset. Restoring the entry frame would lie.
        self.assertEqual([m.word_at(0x50000+o) for o in (0xFE,0x100,0x102)],
                         [0x10,0x3000,0x20])

    def test_retf_handler_does_not_masquerade_as_iret(self):
        # RETF leaves the FLAGS word live, so guest.Call must not accept return.
        from original_match.machine import GuestError
        with self.assertRaises(GuestError):
            self.run_interrupt(handler=b'\xCB')


class DecisionPreflight(unittest.TestCase):
    def test_cached_key_is_consumed_once_and_board_is_not_emitted_twice(self):
        from original_match.match import _PortKeys,SITE_BOARD
        match=mock.Mock()
        match.prover=None;match._ported_key=(SITE_BOARD,13)
        match.m.rd.return_value=0
        keys=_PortKeys(match)
        self.assertEqual(keys.key(SITE_BOARD),13)
        self.assertFalse(hasattr(match,'_ported_key') and '_ported_key' in match.__dict__)
        match._key_for.assert_not_called();match._on_board.assert_not_called()
        match.ports.mem.wds8.assert_any_call(0xA976,13,'214B:0947')
        match.ports.mem.wds8.assert_any_call(0xA977,13,'214B:097C')

    def test_entry_hook_leaves_python_unstarted_while_decision_waits(self):
        from original_match.match import Match
        match=mock.Mock(spec=Match)
        match.m=mock.Mock();match.m.where.return_value='214B:157C'
        match.m.rd.return_value=0;match._key_for.return_value=None
        Match._on_readkey(match,False)
        self.assertNotIn('_ported_key',match.__dict__)
        match.m.return_from.assert_not_called()

    def test_entry_hook_caches_a_key_without_early_guest_return(self):
        from original_match.match import Match
        match=mock.Mock(spec=Match)
        match.m=mock.Mock();match.m.where.return_value='214B:157C'
        match.m.rd.return_value=0;match._key_for.return_value=13;match._menus_ported.return_value=True
        Match._on_readkey(match,False)
        self.assertEqual(match._ported_key,('214B:157C',13))
        match._key_for.assert_called_once()
        match.m.return_from.assert_not_called();match.m.wr.assert_not_called()
