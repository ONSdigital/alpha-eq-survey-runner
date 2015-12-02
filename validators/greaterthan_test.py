import unittest
import json
from validators.greaterthan import Greaterthan


class GreaterthanTest(unittest.TestCase):

    def _load_test_data(self):
        self.validation = json.loads('{"condition": "greaterthan","value": "10","type": "error","message": "This field should be less than 11"}')

    def test_is_greater_than(self):
        self._load_test_data()
        number = "11"
        validator = Greaterthan(self.validation)
        assert validator.is_valid(number) == False

    def test_is_less_than(self):
        self._load_test_data()
        number = "2"
        validator = Greaterthan(self.validation)
        assert validator.is_valid(number)

    def test_is_than_with_decimal(self):
        self._load_test_data()
        number = "1.0"
        validator = Greaterthan(self.validation)
        assert validator.is_valid(number)

if __name__ == '__main__':
    unittest.main()
