import unittest

from conditions.lessthan import IsLessThanCondition


class IsLessThanConditionTest(unittest.TestCase):

    def test_is_less_than(self):
        number = "11"
        condition = IsLessThanCondition(0)
        assert condition.condition_is_met(number)

    def test_is_greater_than(self):
        number = "-1"
        condition = IsLessThanCondition(0)
        assert condition.condition_is_met(number) == False

    def test_is_less_than_with_decimal(self):
        number = "1.0"
        condition = IsLessThanCondition(0)
        assert condition.condition_is_met(number)

if __name__ == '__main__':
    unittest.main()
