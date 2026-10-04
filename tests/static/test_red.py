import unittest


class ThisMustBeReverted(unittest.TestCase):
    """Throwaway: proves the tests/static CI step is red when a test fails. Reverted at once."""

    def test_this_must_be_reverted(self):
        self.assertTrue(False)


if __name__ == "__main__":
    unittest.main()
