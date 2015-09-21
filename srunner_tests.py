import os
import srunner
import unittest
import tempfile

class SrunnerTestCase(unittest.TestCase):

    def setUp(self):
        srunner.app.config['TESTING'] = True
        self.app = srunner.app.test_client()

    def tearDown(self):
	    pass

    def test_empty_db(self):
        rv = self.app.get('/')
        self.assertIn('Hello world',rv.data)



if __name__ == '__main__':
    unittest.main()
