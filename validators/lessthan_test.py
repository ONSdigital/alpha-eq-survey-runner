import unittest
import json
from validators.lessthan import Lessthan


class LessthanTest(unittest.TestCase):

    def _load_test_data(self):
        self.validation = json.loads('{"condition": "lessthan","value": "0","type": "error","message": "This field should be greater than 0"}')

    def test_is_less_than(self):
        self._load_test_data()
        number = "11"
        validator = Lessthan(self.validation)
        assert validator.is_valid(number)

    def test_is_greater_than(self):
        self._load_test_data()
        number = "-1"
        validator = Lessthan(self.validation)
        assert validator.is_valid(number) == False

    def test_is_less_than_with_decimal(self):
        self._load_test_data()
        number = "1.0"
        validator = Lessthan(self.validation)
        assert validator.is_valid(number)

if __name__ == '__main__':
    unittest.main()
