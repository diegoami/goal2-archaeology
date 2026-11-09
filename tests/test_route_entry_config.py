"""T127 supported configuration of the real held F1F6 Match; original assets remain private."""
import copy
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path[:0]=[str(Path(__file__).resolve().parents[1]/'runtime')]
from original_match.match import Match,Fixture,SEED
from original_match.machine import MEM_SIZE,REGS
from tests.test_route_sealed import _fixtures


def snapshot(m):
    return (m.m.read(0,MEM_SIZE),tuple(m.m.reg(k) for k in REGS),copy.deepcopy(m.opts),
            copy.deepcopy(m.st),copy.deepcopy(m.inputs),
            {a:len(v) for a,v in m.m._handlers.items()},len(m.m._writes))


class Controls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image,cls.context,cls.fixture=_fixtures().entry()

    def match(self):
        return Match.from_route_entry(self.image,Fixture(**self.fixture),self.context)

    def test_all_default_configuration_preserves_entry_and_options(self):
        m=self.match();before=snapshot(m)
        self.assertIsNone(m.configure_route_entry())
        self.assertEqual(snapshot(m),before)
        with self.assertRaises(ValueError):m.configure_route_entry()
        self.assertEqual(snapshot(m),before)

    def test_boolean_validation_is_atomic_and_failure_does_not_consume(self):
        for field in ('ticks','record_draws','set_piece','live_players','substitution_control'):
            for value in (0,1,None,'yes',[]):
                with self.subTest(field=field,value=value):
                    m=self.match();before=snapshot(m)
                    with self.assertRaises(ValueError):m.configure_route_entry(**{field:value,'captain':m._squad(m.opts['managed'])[0]})
                    self.assertEqual(snapshot(m),before)
                    m.configure_route_entry()

    def test_captain_and_budget_validation_precedes_every_change(self):
        invalid=[{'captain':v} for v in (True,0,-1,3061,self.match()._squad(self.fixture['first'])[11])]
        invalid += [{'substitutions':v} for v in (True,-1,256,[],[1],[1,2,3],[True,2],[0,256],'5')]
        for options in invalid:
            with self.subTest(options=options):
                m=self.match();before=snapshot(m)
                with self.assertRaises(ValueError):m.configure_route_entry(ticks=True,record_draws=True,**options)
                self.assertEqual(snapshot(m),before);m.configure_route_entry()

    def test_options_detach_budget_and_preserve_complete_incoming_context(self):
        for budget in (0,255,[0,255],(5,5),None):
            m=self.match();before=snapshot(m);captain=m._squad(m.opts['managed'])[0]
            m.configure_route_entry(captain=captain,substitutions=budget,ticks=True,set_piece=True,
                                    live_players=True,substitution_control=True)
            after=snapshot(m)
            self.assertEqual(after[:2],before[:2]);self.assertEqual(after[3:],before[3:])
            self.assertEqual(m.opts['substitutions'],[budget,budget] if type(budget)is int else list(budget) if budget is not None else None)
            if isinstance(budget,list):budget[0]=7;self.assertEqual(m.opts['substitutions'],[0,255])
            self.assertEqual(m.opts['captain'],captain)
            for field in ('ticks','set_piece','live_players','substitution_control'):self.assertIs(m.opts[field],True)
            configured=snapshot(m)
            with self.assertRaises(ValueError):m.configure_route_entry(record_draws=True)
            self.assertEqual(snapshot(m),configured)

    def test_draw_recorder_is_installed_once_without_reinstalling_hooks(self):
        m=self.match();before=snapshot(m)
        with patch.object(m,'_hooks',side_effect=AssertionError('hooks rerun')):
            m.configure_route_entry(record_draws=True)
        after=snapshot(m);self.assertEqual(after[:2],before[:2]);self.assertEqual(after[3:6],before[3:6])
        self.assertEqual(after[6],before[6]+1)
        m._install_draw_recorder()
        self.assertEqual(len(m.m._writes),before[6]+1)
        m.st['recording']=True;old=m.m.rd(SEED);m.m.write_as(m.m.DS*16+SEED,2,(old+1)&65535,m.m.pc())
        self.assertEqual(len(m.st['draws']),1)
        self.assertEqual(m.st['draws'][0][2:],[old,(old+1)&65535])

    def test_lazy_events_creation_allows_configuration_but_replay_capture_locks_it(self):
        a=self.match();b=self.match();iterator=b.events()
        self.assertEqual(snapshot(a),snapshot(b))
        a.configure_route_entry(ticks=True);b.configure_route_entry(ticks=True)
        self.assertEqual(snapshot(a),snapshot(b));iterator.close()
        c=self.match();c._replay_start();before=snapshot(c)
        with self.assertRaises(ValueError):c.configure_route_entry(ticks=True)
        self.assertEqual(snapshot(c),before)

    def test_original_child_requires_an_inactive_parent(self):
        class ReachedChild(Exception):pass
        def child(parent,match,controlled):
            self.assertFalse(parent.m.running,'a child original emulator must not run inside a live parent')
            self.assertEqual(parent.m.pc(),parent.m.lin('0791:F1F6'))
            self.assertTrue(parent.m.read(0,MEM_SIZE)==match.m.read(0,MEM_SIZE),'child entry memory differs')
            self.assertEqual({k:parent.m.reg(k) for k in REGS},{k:match.m.reg(k) for k in REGS})
            raise ReachedChild
        with self.assertRaises(ReachedChild):
            _original_round(_fixtures().image(),False,child_driver=child)

    def test_unknown_and_setup_options_are_rejected_without_consumption(self):
        for key in ('seed','reference_seed','delay_byte','players','countries','managed','fixture','index','engine','tail','ports','prove','opts'):
            m=self.match();before=snapshot(m)
            with self.assertRaises(TypeError):m.configure_route_entry(**{key:True})
            self.assertEqual(snapshot(m),before);m.configure_route_entry()

    def test_ordinary_loaded_and_changed_entry_targets_refuse_without_changes(self):
        ordinary=Match(self.image,Fixture(**self.fixture),engine='port',tail=False)
        loaded=Match.load(self.match().save())
        moved=self.match();moved.m.set_reg('eax',moved.m.reg('eax')^1)
        for m in (ordinary,loaded,moved):
            before=snapshot(m)
            with self.assertRaises(ValueError):m.configure_route_entry()
            self.assertEqual(snapshot(m),before)


# Proof helpers deliberately share only the declared player/input policy. The
# original arm runs actual guest instructions; the public candidate stays sealed.
def _captain(image,fixture):
    from original_match.image import COUNTRIES_PTR,COUNTRY_SIZE,MANAGER,PLAYERS_PTR,PLAYER_SIZE
    from original_match.route_team import choose_eleven
    humans=[c for c in (fixture.first,fixture.second)
            if image.memory[image.far(COUNTRIES_PTR)+COUNTRY_SIZE*c+MANAGER]>128]
    assert len(humans)==1
    squad=image.squad(humans[0]);base=image.far(PLAYERS_PTR)
    swaps=choose_eleven(squad,lambda w,o:image.memory[base+PLAYER_SIZE*w+o])
    return next(w for w in squad[:11] if w not in {off for off,on in swaps})


def _drive_entry(m,controlled):
    import hashlib
    from dataclasses import asdict
    from original_match import screens as S
    from original_match.match import TEAM_MENU,MINUTE,SUBTICK
    from original_match.route_team import choose_eleven,PreMatchPlan
    events=[];independent=[];keys=[];captains=[];captain_prompt=[False];paused=False;operations=[];accepted=False;requests=[True,False,True]
    previous_key=m._key_for
    def key(site):
        value=previous_key(site)
        if value is not None:keys.append([site,value])
        return value
    m._key_for=key
    def prompt(replay):
        if not replay:captain_prompt[0]=m.m.stack_word(2)==1 and m.m.stack_word(4)==m.side
    def chosen(replay):
        if not replay and captain_prompt[0]:captains.append(m.m.reg('ax'));captain_prompt[0]=False
    m.m.at('0791:CC7B',prompt);m.m.at('0791:D010',chosen)
    def select(replay):
        if not replay and m.st['menu_context']=='pre_match' and m.side is not None:
            swaps=choose_eleven(m._squad(m.opts['managed']),m._player)
            m._menu=PreMatchPlan(m.side,subs=swaps)
    m.m.at(TEAM_MENU,select)  # Explicit proof-only original SELECT TEAM inputs.
    def draw(old,new):
        if m.st['recording']:
            independent.append([m.m.rd(MINUTE),m.m.rd(SUBTICK),int.from_bytes(old,'little'),int.from_bytes(new,'little')])
    m.m.watch(m.m.DS*16+SEED,2,draw)
    for event in m.events():
        events.append(asdict(event))
        if event.kind=='tick' and controlled and not paused and event.minute>=2:
            m.pause();paused=True
        if event.kind!='decision':continue
        d=event.data;c=d['context']
        if controlled:
            assert d['team_context']==dict(match_set_up=m.m.rd(0xC1E,1),
                in_match_menu_used=m.m.rd(0xC1F,1),sides=[m.m.rd(0x9B34,2),m.m.rd(0x9B36,2)])
            records=d['player_records'];assert [w for w,raw in records]==d['eleven']+d['bench']
            for w,raw in records:
                assert bytes.fromhex(raw)==m.m.read(m.m.far(0xA91B)+20*w,20)
            assert d['request_substitution'] is bool(m.m.rd(S.SUBS_REQUEST,1))
        else:
            assert 'player_records' not in d and 'request_substitution' not in d and 'team_context' not in d
        if controlled and c=='pause' and paused and requests:
            desired=requests.pop(0)
            if operations:assert d['request_substitution'] is operations[-1]
            m.answer(request_substitution=desired,edit_only=True);operations.append(desired)
        elif controlled and c=='pause' and paused and operations:
            assert d['request_substitution'] is operations[-1];m.answer()
        elif c=='substitution_opportunity':
            assert controlled
            assert d['timeout_polls']==(1000 if d['keeper_unavailable'] else 400)
            m.answer(opportunity='accept');accepted=True
        elif c in ('half_time','substitution'):
            swaps=choose_eleven(m._squad(m.opts['managed']),m._player) if d.get('refused') else []
            m.answer(substitutions=swaps)
        elif c=='set_piece':m.answer(taker=None)
        elif c=='shootout_order':m.answer(shootout_order=[])
        else:m.answer()
    assert m.over and m.m.pc()==m.m.lin('000E:6F1D') and m.m.reg('sp')==0x3EC8
    if controlled:
        assert paused and operations==[True,False,True] and accepted
        assert captains and captains[0]==m.opts['captain'],'actual chosen captain differs'
        assert m.result()['substitution_budget']==[255,255]
        assert independent and m.st['draws']==independent,'independent ordered guest RNG writes differ'
        digest=hashlib.sha256('\n'.join('%d %d %04x %04x'%tuple(v) for v in independent).encode()).hexdigest()
        assert m.result()['draws_digest']==digest
    else:assert m.st['draws']==[] and m.result()['draws_digest'] is None
    return dict(result=copy.deepcopy(m.result()),events=events,draws=independent,keys=keys,captains=captains,
                recorded_draw_count=len(m.st['draws']),
                returned={k:m.m.reg(k) for k in REGS},request_operations=operations,
                opportunity_accepted=accepted,memory=m.m.read(0,MEM_SIZE))


def _candidate(state,table_record,controlled):
    import hashlib
    from original_match import route as R
    from original_match.port.tables import from_record
    from tests.test_route_sealed import _denials
    assert sys.implementation.name=='pypy' and sys.version_info[:2]==(3,11)
    _denials()
    tables=from_record(table_record);step=R.play_round(state,tables,R.DEFAULT_KEYS)
    assert step.status=='match' and type(step.match)is Match
    m=step.match;before=snapshot(m)
    if controlled:
        from original_match.image import Image
        image=Image.from_state(step.state,tables)
        fixture=Fixture(m.opts['first'],m.opts['second'],m.opts['index'],m.opts['kind'])
        m.configure_route_entry(captain=_captain(image,fixture),substitutions=(255,255),ticks=True,
                                record_draws=True,set_piece=True,live_players=True,substitution_control=True)
    else:m.configure_route_entry()
    after=snapshot(m);assert after[:2]==before[:2]
    result=_drive_entry(m,controlled)
    from original_match.image import Image
    assert result['result']['image_sha256']==Image.from_state(step.state,tables).sha256()
    context=result['returned'];seen=[];continuation=step.continuation;updates=[]
    for site in ('0791:B7FA','1771:8757'):
        continuation.m.at(site,lambda replay,site=site:None if replay else updates.append(site))
    continuation.m.at('000E:6F1D',lambda replay:None if replay else seen.append({k:continuation.m.reg(k) for k in REGS}))
    next_step=R.resume_round(continuation,m)
    assert seen==[context],'actual returned ALL16 did not reach route unchanged'
    assert updates.count('0791:B7FA')==1 and updates.count('1771:8757')==1,updates
    before_memory=continuation.m.read(0,MEM_SIZE);before_record=copy.deepcopy(continuation.record)
    for args in ((continuation,m),(object(),m),(continuation,object())):
        try:R.resume_round(*args)
        except ValueError:pass
        else:raise AssertionError('foreign/consumed resume accepted')
        assert continuation.m.read(0,MEM_SIZE)==before_memory and continuation.record==before_record
    result.update(state=next_step.state,pages=[dict(p.__dict__) for p in next_step.news_pages],
                  played=next_step.played_fixtures,record=next_step.record,status=next_step.status,
                  entry_pure=True,all16_returned=True,resume_pure=True,denials=True,
                  implementation=sys.implementation.name,updates=updates)
    return result


def _original_round(image,controlled,child_driver=None):
    """Original reference; child_driver is a focused lifecycle tripwire only."""
    from original_match import route as R
    from original_match.image import Image
    matches=[];original_returned=[];updates=[]
    class Oracle(R.Route):
        def _match(self):
            # Pause the real entry; Route.call already drives a stopped match
            # outside the parent emulator. Never nest original emulators or
            # rewrite its active translation block inside the F1F6 hook.
            assert self.m.pc()==self.m.lin('0791:F1F6')
            here=(self.m.read(0,MEM_SIZE),{k:self.m.reg(k) for k in REGS})
            if self.m.running:
                self.paused_entry=here
                self.entry_pause_count=getattr(self,'entry_pause_count',0)+1
                self.m.stop('match')
                return
            assert self.paused_entry==here,'stopped original entry memory/ALL16 changed'
            self.entry_unchanged=True
            self.child_parent_inactive=not self.m.running
            assert self.child_parent_inactive
            context=here[1];g=self.m.far(0xA923)
            idx=self.m.word_at(g+0x26);raw=self.m.read(self.m.far(0xA92B)+8*(idx-1),8)
            fixture=Fixture(int.from_bytes(raw[4:6],'little'),int.from_bytes(raw[6:8],'little'),idx,raw[2])
            entry=Image(self.header+self.m.read(0,MEM_SIZE)+self.tail);entry.tables=self.tables
            options=dict(captain=_captain(entry,fixture),substitutions=(255,255),ticks=True,record_draws=True,
                         set_piece=True,live_players=True,substitution_control=True) if controlled else {}
            m=Match(entry,fixture,engine='original',tail=False,timeout_s=600,**options)
            assert m.inputs==[] and m.m.read(0,MEM_SIZE)==self.m.read(0,MEM_SIZE),'original constructor changed actual entry'
            for k,v in context.items():m.m.set_reg(k,v)
            for site in ('0791:B7FA','1771:8757'):
                self.m.at(site,lambda replay,site=site:None if replay else updates.append(site))
            self.m.at('000E:6F1D',lambda replay:None if replay else original_returned.append({k:self.m.reg(k) for k in REGS}))
            result=(_drive_entry(m,controlled) if child_driver is None else child_driver(self,m,controlled))
            assert result['result']['image_sha256']==entry.sha256()
            matches.append(result)
            assert not self.m.running,'parent resumed while its child was driven'
            runs=R._runs(self.m.read(0,MEM_SIZE),result['memory'])
            for begin,end in runs:self.m.write(begin,result['memory'][begin:end])
            self.net_write_runs=len(runs)
            self.net_write_full_equal=self.m.read(0,MEM_SIZE)==result['memory']
            assert self.net_write_full_equal,'net original writeback differs from FULL child memory'
            for k,v in result['returned'].items():self.m.set_reg(k,v)
    oracle=Oracle(image,entry='play_round',record_writes=False,match_entry=True);oracle.call()
    return oracle,matches,original_returned,updates


def accepted_default_fields(record):
    """Main701-counter-compatibility: retain the immutable historical profile."""
    import hashlib,json
    historical=copy.deepcopy(record)
    calls=historical['result'].get('ports',{}).get('calls',{})
    for address,name in (('0791:DDCB','DDCB'),('0791:E2E6','E2E6')):
        if address in calls:
            assert calls[address]==0,'historical default executed '+name
            del calls[address]
    canonical=lambda v:json.dumps(v,sort_keys=True,separators=(',',':')).encode()
    return {k:hashlib.sha256(historical[k] if k=='memory' else canonical(historical[k])).hexdigest()
            for k in ('result','events','keys','draws','returned','memory')}


class ActualEntry(unittest.TestCase):
    def test_actual_original_and_denied_pypy_same_options_full_route(self):
        import hashlib,json,os,time
        from original_match import route as R
        from original_match.image import Image
        from original_match.port.tables import to_record
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
        from port_test_runtime import call_in_pypy
        root=Path(__file__).resolve().parents[1]
        stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
        for controlled in (False,True):
            with self.subTest(controlled=controlled):
                image=_fixtures().image();state=image.state(image.tables)
                oracle,matches,original_returned,updates=_original_round(image,controlled)
                self.assertEqual(len(matches),1)
                expected=matches[0]
                actual=call_in_pypy('test_route_entry_config','_candidate',args=(state,to_record(image.tables),controlled))
                final=Image(oracle.header+oracle.m.read(0,MEM_SIZE)+oracle.tail);final.tables=image.tables
                private=root/'.cache/t127'/f'{stamp}-{int(controlled)}';private.mkdir(parents=True,exist_ok=False)
                import pickle
                (private/'pair.pickle').write_bytes(pickle.dumps((expected,actual),protocol=4))
                self.assertTrue(actual['state']==final.state(image.tables),'complete sealed state/2 differs')
                self.assertTrue(actual['pages']==[dict(p.__dict__) for p in oracle.news_history],'ordered original news differs')
                # Main-owned81ef03e7 clarification: preserve own ALL16; the
                # accepted c6a baseline already differs only in raw EFLAGS.
                self.assertEqual({k:v for k,v in actual['returned'].items() if k!='EFLAGS'},
                                 {k:v for k,v in expected['returned'].items() if k!='EFLAGS'},'other15 return registers differ')
                self.assertEqual(original_returned,[expected['returned']],'original ALL16 actual route resume differs')
                self.assertEqual(updates,actual['updates'],'route update calls differ')
                if not controlled:
                    binding=json.loads((root/'experiments/E040-route-fixture-writes/out/T127/accepted-default-binding-v2.json').read_text())
                    self.assertEqual(accepted_default_fields(expected),binding['original'],'original configured-default regression vs accepted c6a')
                    self.assertEqual(accepted_default_fields(actual),binding['port'],'port configured-default regression vs accepted c6a')
                self.assertEqual(actual['keys'],expected['keys'],'actual match read keys differ')
                self.assertEqual([r for r in actual['record'] if r[0]=='key'],[r for r in oracle.record if r[0]=='key'],'route first-poll/read keys differ')
                self.assertTrue(actual['events']==expected['events'],'complete event transcript differs')
                self.assertTrue(actual['draws']==expected['draws'],'ordered independent guest draws differ')
                a=actual['result'];b=expected['result']
                # Existing T123 representation: opcode-free state/2 has its own
                # input image hash; assert each declared input separately.
                differences={k for k in set(a)|set(b) if a.get(k)!=b.get(k)}
                self.assertEqual(differences,{'ports','image_sha256'})
                self.assertTrue({k:v for k,v in a.items() if k not in differences}=={k:v for k,v in b.items() if k not in differences})
                digest=lambda v:hashlib.sha256(pickle.dumps(v,protocol=4)).hexdigest()
                sources={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in [*sorted((root/'runtime/original_match').rglob('*.py')),Path(__file__),
                                   root/'experiments/E040-route-fixture-writes/out/T127/verify-v3.py',
                                   root/'experiments/E040-route-fixture-writes/out/T127/accepted-default-binding-v2.json',
                                   root/'experiments/E040-route-fixture-writes/out/T127/accepted-default-baseline-70f38677-v2.json',
                                   root/'experiments/E040-route-fixture-writes/out/T127/t127_entry_baseline_v2.py']}
                receipt=dict(schema='t127-entry-config/1',controlled=controlled,sources=sources,
                    same_result_except_declared_execution_metadata=sorted(differences),
                    complete_state_equal=True,events_equal=True,ordered_draws_equal=True,news_equal=True,
                    all16_actual_transfer_equal=True,other15_returned_equal=True,
                    raw_returned_registers={'original':expected['returned'],'port':actual['returned']},
                    accepted_default_within_backend_equal=not controlled,
                    entry_configuration_pure=actual['entry_pure'],
                    original_parent_inactive=oracle.child_parent_inactive,
                    original_entry_unchanged=oracle.entry_unchanged,
                    original_entry_pause_count=oracle.entry_pause_count,
                    original_net_write_full_equal=oracle.net_write_full_equal,
                    original_net_write_runs=oracle.net_write_runs,original_timeout_s=oracle.timeout_s,
                    invalid_resume_pure=actual['resume_pure'],positive_denials=actual['denials'],
                    draw_count=len(actual['draws']),recorded_draw_count=actual['recorded_draw_count'],
                    substitution_budget=actual['result']['substitution_budget'],
                    team_context_decisions=sum(e['kind']=='decision' and 'team_context' in e['data'] for e in actual['events']),update_calls=actual['updates'],captains=actual['captains'],event_count=len(actual['events']),page_count=len(actual['pages']),
                    request_operations=actual['request_operations'],opportunity_accepted=actual['opportunity_accepted'],
                    state_sha256=digest(actual['state']),events_sha256=digest(actual['events']),
                    original_full_memory_sha256=hashlib.sha256(expected['memory']).hexdigest(),
                    sealed_full_memory_sha256=hashlib.sha256(actual['memory']).hexdigest(),
                    physical_representation='existing T123 state/2 opcode elision; no new memory mask',
                    raw_private_sha256=hashlib.sha256((private/'pair.pickle').read_bytes()).hexdigest())
                out=root/'experiments/E040-route-fixture-writes/out/T127'/f'proof-{stamp}-{int(controlled)}.json'
                with out.open('x')as f:json.dump(receipt,f,indent=2);f.write('\n')
                print('T127_ACTUAL '+str(out.relative_to(root))+' PASS',flush=True)
