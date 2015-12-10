from numeric_condition import IsNumericCondition
import unittest


class IsNumericConditonTest(unittest.TestCase):

    def test_is_numeric(self):
        number = "1"
        condition = IsNumericCondition()
        assert condition.condition_is_met(number)

    def test_is_decimal(self):
        number = "1.0"
        condition = IsNumericCondition()
        assert condition.condition_is_met(number)

    def test_is_negative_zero(self):
        number = "-0"
        condition = IsNumericCondition()
        assert condition.condition_is_met(number)

    def test_is_numeric_negative(self):
        number = "-1"
        condition = IsNumericCondition()
        assert condition.condition_is_met(number)

    def test_is_not_numeric(self):
        number = 'a'
        condition = IsNumericCondition()
        assert condition.condition_is_met(number) == False

if __name__ == '__main__':
    unittest.main()