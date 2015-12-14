import unittest

from conditions.equal import IsEqualCondition


class IsEqualConditionTest(unittest.TestCase):

    def test_is_equal(self):
        number = "1"
        condition = IsEqualCondition()
        condition.initialize("equal", "1", "error", "message")
        assert condition.condition_is_met(number) == False

    def test_is_not_equal(self):
        number = "2"
        condition = IsEqualCondition()
        condition.initialize("equal", "1", "error", "message")
        assert condition.condition_is_met(number)

    def test_is_equal_with_decimal(self):
        number = "1.0"
        condition = IsEqualCondition()
        condition.initialize("equal", "1", "error", "message")
        assert condition.condition_is_met(number) == False

if __name__ == '__main__':
    unittest.main()
