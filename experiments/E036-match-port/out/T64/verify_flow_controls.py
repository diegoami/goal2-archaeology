"""T64 flow controls in memory: baseline must pass; each defect must fail an assertion."""
import inspect
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "runtime"))
from tests import test_port_ball as tests
from original_match import port
from original_match.port import ball


def run(suite):
    return unittest.TextTestRunner(verbosity=2).run(suite)


baseline = run(unittest.defaultTestLoader.loadTestsFromModule(tests))
assert baseline.wasSuccessful(), "Unmutated baseline must pass before controls"
print(f"Baseline: {baseline.testsRun} synthetic tests PASS", flush=True)

controls = (
    ("0791:3C3F", ball.shot_or_header, "r.push(r.ax)", "None",
     tests.ShotAndHeaderFlow, "test_shot_coin_word_is_live_and_all_failed_gates_reach_last_draw"),
    ("0791:3D38", ball.find_cross_target, 'if not (mem.reg("eflags") & 0x40):', "if True:",
     tests.CrossTarget, "test_membership_uses_guest_zf_then_unavailability_and_goal_strip"),
    ("0791:333F", ball.mark_offside_candidate,
     'mem.wds8(0x8325, 1, "0791:334C")', 'mem.wds8(0x8325, 0, "0791:334C")',
     tests.NestedOffside, "test_first_launch_only_sets_clock_and_preserves_ax"),
    ("0791:34C1", ball.launch_ball, "high, low = r.dx, r.ax", "high, low = 0, r.ax",
     tests.LaunchBall, "test_long_division_high_word_is_forwarded_to_maximum"),
    ("0791:384C", ball.move_ball_to_slot,
     "r.push(r.ax)                                           # 38A0:", "None                                                 # 38A0:",
     tests.MoveBallToSlot, "test_self_target_keeps_incremented_draw_live_and_divides_toward_zero"),
)
for address, function, old, new, case, method in controls:
    source = inspect.getsource(function)
    source = source[source.index("def " + function.__name__):]
    assert source.count(old) == 1, (address, "control must change exactly one behavior")
    namespace = dict(vars(ball))
    exec(compile(source.replace(old, new), "<T64 flow mutant " + address + ">", "exec"), namespace)
    entry = port._module_registry("ball").entries[address]
    with patch.object(entry, "fn", namespace[function.__name__]):
        failure = run(unittest.TestSuite([case(method)]))
    assert len(failure.failures) == 1 and not failure.errors, (address, failure.failures, failure.errors)
    print(address, "control caught by assertion, no setup errors", flush=True)
print("T64 flow controls PASS; source files untouched", flush=True)
