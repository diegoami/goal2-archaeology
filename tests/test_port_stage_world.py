"""T124d listing ownership; behavioral and actual-world lineage tests extend this failing-first scaffold."""
import unittest
from tests.test_port_stages import _Calls,RET
from original_match.port import stages as ST

RET.update({'1771:6FEB':'1771:711C','1771:7090':'1771:76E2','1771:71B2':'1771:76EB','1771:74BE':'1771:76F4'})
ENTRIES={'1771:6FEB':'ret 2','1771:7090':'ret','1771:71B2':'ret','1771:74BE':'ret'}

class World(_Calls):
    def test_world_entries_with_true_return_abis(self):
        self.assertEqual({a:ST.PORTS.entries[a].ret for a in ENTRIES},ENTRIES)
