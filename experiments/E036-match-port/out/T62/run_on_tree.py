"""Run one test module against another tree (main's, extracted with git archive): the before-check of a new test.

    python3 -B experiments/E036-match-port/out/T62/run_on_tree.py TREE tests.test_port_motion"""
import sys
import unittest
from pathlib import Path

tree = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(tree))
print(f"tree {tree}, module {sys.argv[2]}")
suite = unittest.defaultTestLoader.loadTestsFromName(sys.argv[2])
mod = sys.modules.get(sys.argv[2])
print(f"loaded from {getattr(mod, '__file__', None)}")
result = unittest.TextTestRunner(verbosity=1).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
