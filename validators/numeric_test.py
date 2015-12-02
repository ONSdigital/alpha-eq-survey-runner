import unittest
import json
from validators.numeric import Numeric


class NumericTest(unittest.TestCase):

    def _load_test_data(self):
        self.validation = json.loads('{"condition": "numeric","value": true,"type": "error","message": "This field is should be a number"}')

    def test_is_numeric(self):
        self._load_test_data()
        number = "1"
        validator = Numeric(self.validation)
        assert validator.is_valid(number)

    def test_is_decimal(self):
        self._load_test_data()
        number = "1.0"
        validator = Numeric(self.validation)
        assert validator.is_valid(number)

    def test_is_negative_zero(self):
        self._load_test_data()
        number = "-0"
        validator = Numeric(self.validation)
        assert validator.is_valid(number)

    def test_is_numeric_negative(self):
        self._load_test_data()
        number = "-1"
        validator = Numeric(self.validation)
        assert validator.is_valid(number)

    def test_is_not_numeric(self):
        self._load_test_data()
        text = 'a'
        validator = Numeric(self.validation)
        assert validator.is_valid(text) == False


if __name__ == '__main__':
    unittest.main()
