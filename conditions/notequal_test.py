import unittest

from conditions.notequal import IsNotEqualCondition


class NotequalTest(unittest.TestCase):

    def test_is_not_equal(self):
        number = "1"
        condition = IsNotEqualCondition()
        condition.initialize("notequal", "10", "error", "message")
        assert condition.condition_is_met(number) == False

    def test_is_equal(self):
        number = "10"
        condition = IsNotEqualCondition()
        condition.initialize("notequal", "10", "error", "message")
        assert condition.condition_is_met(number)

    def test_is_equal_with_decimal(self):
        number = "10.0"
        condition = IsNotEqualCondition()
        condition.initialize("notequal", "10", "error", "message")
        assert condition.condition_is_met(number)

if __name__ == '__main__':
    unittest.main()
