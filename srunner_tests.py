import os
import srunner
import unittest
import tempfile
from jsonforms import convert_to_wtform
import json
import wtforms

class SrunnerTestCase(unittest.TestCase):

    def setUp(self):
        srunner.app.config['TESTING'] = True
        self.app = srunner.app.test_client()

    def tearDown(self):
	    pass

    def test_empty_db(self):
        rv = self.app.get('/')
        assert 'Hello world!' in rv.data

    def test_questionnaire_render(self):
        FORM_SCHEMA = '{"overview": "This is a questionnaire to test stuff", "questionnaire_title": "Hope", "questions": [{"help_text": "All sizes count, even grandfathers.", "error_text": "Sorry - that doesn\'t look like a valid entry.", "title": "How many marbles do you have?"}]}'
        test_form = convert_to_wtform(FORM_SCHEMA)
        self.assertEqual(type(test_form) is  wtforms.form.FormMeta, True)

if __name__ == '__main__':
    unittest.main()
