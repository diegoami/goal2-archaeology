"""Budget/audit mechanism tests only: no reference loading, Machine construction or target calls."""
import tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from runner import Budget,require_registered_target
from check import write_new


class Guards(unittest.TestCase):
    def budget(self):
        temp=tempfile.TemporaryDirectory(prefix='T106-software-');self.addCleanup(temp.cleanup)
        return Budget(Path(temp.name))
    def reserve_record(self,b,seq,group='launch',batch='fixture'):
        write_new(b.base/'reservations'/f'{seq:04}.json',dict(seq=seq,group=group,batch=batch,logical=str(seq)))
    def test_sixty_first_attempt_is_refused(self):
        b=self.budget()
        for seq in range(1,61):self.reserve_record(b,seq,'launch' if seq<=16 else 'wall')
        self.assertEqual(b.audit()['invocations'],60)
        with self.assertRaisesRegex(AssertionError,'global invocation cap'):b.reserve('new','wall','new','hash',{'cpu_s':0,'active_wall_s':0})
        self.assertEqual(len(b.read('reservations')),60)
    def test_launch_suballocation_and_resource_reserves_are_binding(self):
        b=self.budget()
        for seq in range(1,17):self.reserve_record(b,seq)
        with self.assertRaisesRegex(AssertionError,'slice invocation cap'):b.reserve('new','launch','new','hash',{'cpu_s':0,'active_wall_s':0})
        empty=self.budget()
        with self.assertRaisesRegex(AssertionError,'CPU reserve cap'):empty.reserve('new','launch','new','hash',{'cpu_s':600,'active_wall_s':0})
        with self.assertRaisesRegex(AssertionError,'wall reserve cap'):empty.reserve('new','launch','new','hash',{'cpu_s':0,'active_wall_s':900})
        self.assertFalse(empty.read('reservations'))
    def test_missing_outcome_is_charged_and_cannot_be_retried(self):
        b=self.budget();self.reserve_record(b,1)
        self.assertEqual((b.audit()['cpu_s'],b.audit()['active_wall_s']),(5,10))
        with self.assertRaisesRegex(AssertionError,'unfinished'):b.start('new',{})
    def test_open_batch_blocks_budget_reset(self):
        b=self.budget();write_new(b.base/'starts'/'old.json',dict(batch='old'))
        self.assertEqual(b.audit()['cpu_s'],600)
        with self.assertRaisesRegex(AssertionError,'unfinished'):b.start('new',{})
    def test_known_callee_passes_and_missing_callee_cannot_fall_back(self):
        machine=SimpleNamespace(lin=lambda target:target,_ports={'known':object()})
        require_registered_target(machine,'known')
        with self.assertRaisesRegex(AssertionError,'unregistered native fallback'):require_registered_target(machine,'missing')


if __name__=='__main__':unittest.main()
