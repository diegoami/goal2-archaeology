"""#682: synthetic coordinator controls; original/PyPy live-data proof is separate."""
import copy
import inspect
import sys
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from original_match.match import Match,VERSION,PLAYERS_PTR,PLAYER_SIZE

class LivePlayers(unittest.TestCase):
    def coordinator(self, enabled=True):
        match=object.__new__(Match)
        match.opts={'managed':7}
        if enabled is not None:match.opts['live_players']=enabled
        match.side=0
        words=list(range(401,421))
        records={w:bytearray((w+i)%256 for i in range(PLAYER_SIZE)) for w in words}
        for record in records.values():record[0]=7
        match.st={'log':{'injuries':[{'team':0,'player':words[0]}]},'menu_half':2}
        base=0x40000;calls=[];packets=[]
        def read(address,length):
            calls.append(('read',address,length))
            word,offset=divmod(address-base,PLAYER_SIZE)
            return bytes(records[word][offset:offset+length])
        match.m=SimpleNamespace(far=lambda pointer:base if pointer==PLAYERS_PTR else None,
             read=read,rd=lambda address,*rest:5,stop=lambda reason:calls.append(('stop',reason)))
        match._flush=lambda:calls.append(('flush',))
        match._squad=lambda country:words[:]
        match._tactics=lambda:0x52
        match._emit=lambda kind,**data:packets.append((kind,copy.deepcopy(data)))
        return match,words,records,packets,calls

    def test_opt_in_carries_every_current_record_in_squad_order_at_all_decisions(self):
        for context in ('pause','half_time','substitution','extra_time','set_piece','shootout_order'):
            with self.subTest(context=context):
                m,words,records,packets,calls=self.coordinator()
                m._decide(context,edited=True)
                data=packets[-1][1]
                self.assertEqual(data.get('player_records'),[[w,bytes(records[w]).hex()] for w in words])
                self.assertEqual(data['eleven']+data['bench'],words)
                self.assertEqual(data['injured'],[words[0]])
                self.assertEqual(data['positions'],[[w,records[w][6]] for w in words])
                self.assertEqual(data['tactics'],0x52)
                self.assertTrue(data['edited'])
                if context=='extra_time':self.assertEqual(data['half'],2)
                self.assertEqual(calls[0],('flush',))
                self.assertEqual(calls[-1],('stop','decision'))

    def test_later_snapshot_is_fresh_and_already_emitted_values_are_immutable(self):
        m,words,records,packets,calls=self.coordinator()
        m._decide('pause')
        first=copy.deepcopy(packets[-1])
        records[words[1]][14]=3
        records[words[1]][18:20]=(205).to_bytes(2,'little')
        records[words[-1]][14]=0   # withdrawn/bench data is present too
        m._decide('half_time')
        self.assertEqual(packets[0],first)
        latest=dict(packets[1][1].get('player_records') or [])
        self.assertEqual(bytes.fromhex(latest[words[1]])[14],3)
        self.assertEqual(bytes.fromhex(latest[words[1]])[18:20],(205).to_bytes(2,'little'))
        self.assertEqual(bytes.fromhex(latest[words[-1]])[14],0)

    def test_legacy_default_and_explicit_false_keep_exact_previous_packet_shape(self):
        values=[]
        for flag in (None,False):
            m,words,records,packets,calls=self.coordinator(flag)
            m._decide('half_time',refused='example')
            values.append(packets)
            self.assertEqual(packets,[('decision',{'refused':'example','context':'half_time',
                'eleven':words[:11],'bench':words[11:],'injured':[words[0]],
                'positions':[[w,records[w][6]] for w in words], 'substitutions_left':5,'tactics':0x52})])
            self.assertFalse(any(c[0]=='read' and c[2]==PLAYER_SIZE for c in calls))
        self.assertEqual(*values)

    def construct(self, **options):
        image=SimpleNamespace(memory=bytes(0x110000),load=0,header=b'',sha256=lambda:'synthetic-image',build_problems=lambda:[])
        fixture=SimpleNamespace(first=7,second=19,index=21,kind=1)
        with ExitStack() as stack:
            stack.enter_context(patch('original_match.match.Machine',return_value=SimpleNamespace(DS=0x1000)))
            for name in ('_write_state','_make_managed','_write_fixture','_declare','_hooks','_install_ports','_install_proof','_call'):
                stack.enter_context(patch.object(Match,name))
            stack.enter_context(patch.object(Match,'_players_now',return_value={}))
            return Match(image,fixture,managed=7,**options)

    def test_public_option_is_strict_boolean_and_absent_by_default(self):
        self.assertIn('live_players',inspect.signature(Match).parameters)
        before=self.construct().opts
        self.assertEqual(self.construct(live_players=False).opts,before)
        self.assertNotIn('live_players',before)
        self.assertEqual(self.construct(live_players=True).opts,{**before,'live_players':True})
        for invalid in (None,0,1,'yes',[]):
            with self.subTest(invalid=invalid),self.assertRaisesRegex(ValueError,'live_players'):
                self.construct(live_players=invalid)

    def test_checkpoint_codec_retains_opt_in_and_waiting_record_payload(self):
        m,words,records,packets,calls=self.coordinator()
        m._decide('pause')
        state={'version':VERSION,'opts':{'live_players':True},'st':{'waiting':packets[-1][1]}}
        encoded=Match._encode_save(state,b'synthetic-memory-payload')
        _,loaded,engine=Match._checkpoint_state(encoded)
        self.assertEqual(engine,'original')
        self.assertEqual(loaded['opts']['live_players'],True)
        self.assertEqual(loaded['st']['waiting']['player_records'],[[w,bytes(records[w]).hex()] for w in words])

    def test_checkpoint_rejects_non_boolean_opt_in_without_rejecting_old_headers(self):
        for flag in (None,0,1,'yes',[]):
            state={'version':VERSION,'opts':{'live_players':flag}}
            blob=Match._encode_save(state,b'synthetic-memory')
            with self.subTest(flag=flag),self.assertRaisesRegex(ValueError,'live_players'):
                Match._checkpoint_state(blob)
        for opts in ({},{'live_players':False},{'live_players':True}):
            state={'version':VERSION,'opts':opts}
            _,loaded,_=Match._checkpoint_state(Match._encode_save(state,b'synthetic-memory'))
            self.assertEqual(loaded,state)

if __name__=='__main__':unittest.main()
