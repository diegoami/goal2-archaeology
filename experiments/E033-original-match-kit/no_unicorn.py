"""Run the kit's tests as CI would without unicorn: block the import, then run the test module."""
import sys
import unittest

sys.modules["unicorn"] = None          # `import unicorn` now raises ImportError
sys.path.insert(0, sys.argv[1])
suite = unittest.defaultTestLoader.loadTestsFromName("tests.test_original_match")
r = unittest.TextTestRunner(verbosity=1).run(suite)
print("skipped:", len(r.skipped), "errors:", len(r.errors), "failures:", len(r.failures))
import original_match  # noqa: E402
try:
    original_match.Match.__init__  # the import worked
    from original_match.machine import Machine
    Machine(bytes(0x110000), 0)
except ModuleNotFoundError as e:
    print("a match without unicorn:", e)
