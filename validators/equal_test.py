import unittest
import json
from validators.equal import Equal


class EqualTest(unittest.TestCase):

    def _load_test_data(self):
        self.validation = json.loads('{"condition": "equal","value": "1","type": "error","message": "Come on, really?"}')

    def test_is_equal(self):
        self._load_test_data()
        number = "1"
        validator = Equal(self.validation)
        assert validator.is_valid(number) == False

    def test_is_not_equal(self):
        self._load_test_data()
        number = "2"
        validator = Equal(self.validation)
        assert validator.is_valid(number)

    def test_is_equal_with_decimal(self):
        self._load_test_data()
        number = "1.0"
        validator = Equal(self.validation)
        assert validator.is_valid(number) == False

if __name__ == '__main__':
    unittest.main()
