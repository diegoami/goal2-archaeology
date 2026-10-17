"""E037's literal cases (F031) run in the unit suite.

`experiments/E037-exchange-windows/test_cases.py` is not found by `python3 -m unittest discover -s tests`
(it lives in the experiment's folder), so a change that broke the predicate, `cases.tsv` or the stage 7
tour decoder would pass the suite. This module loads that file and hands its tests to the discovery
(the `load_tests` protocol); it adds no assertion of its own beyond the guard that the file was found
and carries the tests, so an emptied or moved E037 test fails here instead of silently passing."""
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
E037_TESTS = ROOT / "experiments" / "E037-exchange-windows" / "test_cases.py"


def _load():
    spec = importlib.util.spec_from_file_location("e037_test_cases", E037_TESTS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromModule(_load()))
    suite.addTests(loader.loadTestsFromTestCase(WrapperFindsTheCases))
    return suite


class WrapperFindsTheCases(unittest.TestCase):
    def test_e037_tests_are_found(self):
        found = unittest.defaultTestLoader.loadTestsFromModule(_load()).countTestCases()
        self.assertGreaterEqual(found, 6)


if __name__ == "__main__":
    unittest.main()
