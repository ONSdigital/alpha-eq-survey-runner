import unittest
import json
from validators.notequal import Notequal


class NotequalTest(unittest.TestCase):

    def _load_test_data(self):
        self.validation = json.loads('{"condition": "notequal","value": "10","type": "warning","message": "you could always change it to 10"}')

    def test_is_not_equal(self):
        self._load_test_data()
        number = "1"
        validator = Notequal(self.validation)
        assert validator.is_valid(number) == False

    def test_is_equal(self):
        self._load_test_data()
        number = "10"
        validator = Notequal(self.validation)
        assert validator.is_valid(number)

    def test_is_equal_with_decimal(self):
        self._load_test_data()
        number = "10.0"
        validator = Notequal(self.validation)
        assert validator.is_valid(number)

if __name__ == '__main__':
    unittest.main()
