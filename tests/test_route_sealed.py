"""T123 sealed public round API and literal outer frames.

Published reference executions and positive denied PyPy workers are retained
under out/T123. Small boundary fixtures below contain no original code bytes.
"""
import dataclasses,hashlib,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'runtime'),str(ROOT/'tools')]
from original_match import route as R
from original_match.image import Image
from original_match.machine import MEM_SIZE
from original_match.port import route as P
from original_match.port.tables import load as load_tables
from tests.test_port_stages import _Calls,RET
RET.update({'000E:7072':'000E:70EE','000E:70B9':'000E:77C2'})


def terminal_state(stage):
    """Declared empty completed calendar; tests entry guard before any kit write."""
    tables=load_tables(ROOT/'static/goal-exe/tables')
    image=Image.__new__(Image);image.header=bytes(32);image.memory=bytearray(MEM_SIZE)
    image.load=0;image.DS=0x2581;image.tables=tables;tables.place(image.memory,0)
    ds=image.DS*16;image.memory[ds+0xA923:ds+0xA927]=(0x100).to_bytes(2,'little')+(0x5000).to_bytes(2,'little')
    game=0x50100
    for off,value in [(0x26,1),(0x28,1)]:image.memory[game+off:game+off+2]=value.to_bytes(2,'little')
    image.memory[game+0x3C]=stage;image.memory[game+0x3D]=1
    return image.state(tables),tables


class OuterFrames(_Calls):
    def test_shareware_leaf_preserves_AH_and_real_frame(self):
        self.assertEqual(P.PORTS.entries['000E:7072'].ret,'ret')
        m,p=self.call('000E:7072',specs=[(P.PORTS,None)],before=lambda m:m.set_reg('ax',0xABCD))
        self.proved(p,'000E:7072');self.assertEqual(m.reg('ax'),0xAB00)


class Boundary(unittest.TestCase):
    def test_terminal_entry_returns_immutable_step_without_starting_backend(self):
        from unittest.mock import patch
        from original_match import machine
        for stage in (4,8):
            with self.subTest(stage=stage):
                state,tables=terminal_state(stage);before=json.dumps(state,sort_keys=True)
                with patch.object(machine,'Uc',side_effect=AssertionError('denied original backend')):
                    step=R.play_round(state,tables,R.DEFAULT_KEYS)
                self.assertEqual(step.status,'deferred-rollover');self.assertEqual(step.state,state)
                self.assertIsNot(step.state,state);self.assertEqual(step.played_fixtures,());self.assertEqual(step.news_pages,())
                self.assertIsNone(step.match);self.assertIsNone(step.continuation)
                with self.assertRaises(dataclasses.FrozenInstanceError):step.status='complete'
                self.assertEqual(json.dumps(state,sort_keys=True),before)

    def test_repeated_terminal_request_preserves_every_state_byte(self):
        state,tables=terminal_state(8);first=R.play_round(state,tables,None)
        second=R.play_round(first.state,tables,None)
        self.assertEqual(first.state,second.state);self.assertEqual(second.status,'deferred-rollover')
        self.assertEqual(second.played_fixtures,());self.assertEqual(second.news_pages,())
