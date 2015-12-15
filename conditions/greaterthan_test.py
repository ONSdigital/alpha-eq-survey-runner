import unittest

from conditions.greaterthan import IsGreaterThanCondition


class IsGreaterThanConditionTest(unittest.TestCase):

    def test_is_greater_than(self):
        number = "11"
        condition = IsGreaterThanCondition()
        condition.initialize("greaterthan", "10")
        assert condition.condition_is_met(number) == False

    def test_is_less_than(self):
        number = "2"
        condition = IsGreaterThanCondition()
        condition.initialize("greaterthan", "10")
        assert condition.condition_is_met(number)

    def test_is_than_with_decimal(self):
        number = "1.0"
        condition = IsGreaterThanCondition()
        condition.initialize("greaterthan", "10")
        assert condition.condition_is_met(number)

if __name__ == '__main__':
    unittest.main()
