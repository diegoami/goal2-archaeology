import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools", "static"))

import check_result_set  # noqa: E402


class ResultSet(unittest.TestCase):
    def test_ds_0f3e_is_3_4_7_8_to_203(self):
        self.assertEqual(check_result_set.members(), [3, 4, 7] + list(range(8, 204)))

    def test_rule_is_bit_n_not_n_minus_1(self):
        self.assertNotIn(0, check_result_set.members())
        self.assertNotIn(204, check_result_set.members())


if __name__ == "__main__":
    unittest.main()
