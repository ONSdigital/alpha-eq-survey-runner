import os
import srunner
import unittest
import tempfile
from jsonforms import convert_to_wtform
import json
import wtforms
import logging
from mock import patch

class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs.

    Messages are available from an instance's ``messages`` dict, in order, indexed by
    a lowercase log level string (e.g., 'debug', 'info', etc.).
    """

    def __init__(self, *args, **kwargs):
        self.messages = {'debug': [], 'info': [], 'warning': [], 'error': [],
                         'critical': []}
        super(MockLoggingHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        "Store a message from ``record`` in the instance's ``messages`` dict."
        self.acquire()
        try:
            self.messages[record.levelname.lower()].append(record.getMessage())
        finally:
            self.release()

    def reset(self):
        self.acquire()
        try:
            for message_list in self.messages.values():
                message_list.clear()
        finally:
            self.release()


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
        FORM_SCHEMA = '{"overview": "This is a questionnaire to test stuff", "questionnaire_title": "Hope", "questions": [{"description": "All sizes count, even grandfathers.", "error_text": "Sorry - that doesn\'t look like a valid entry.", "title": "How many marbles do you have?"}]}'
        test_form = convert_to_wtform(FORM_SCHEMA)
        self.assertEqual(type(test_form) is  wtforms.form.FormMeta, True)


class SrunnerLoggingTest(unittest.TestCase):

    def setUp(self):
        self.FORM_SCHEMA = '{"overview": "This is a questionnaire to test stuff", "questionnaire_title": "Hope", "questions": [{"description": "All sizes count, even grandfathers.", "error_text": "Sorry - that doesn\'t look like a valid entry.", "title": "How many marbles do you have?"}]}'
        srunner.app.config['TESTING'] = True
        self.app = srunner.app
        self.patcher = patch('srunner.get_form_schema')
        self.mock_get_form_schema = self.patcher.start()
        self.mock_get_form_schema.return_value = self.FORM_SCHEMA
        self.app.logger.addHandler(MockLoggingHandler())

    def test_data_logs_correctly(self):
        # Need to generate a questionnaire and then
        # check that given a submission we log
        # the correct data.
        self.app.logger.warning('{"rid": , "data": {"what is your hair colour?": "blue"}} ')
        self.assertEqual(len(self.app.logger.handlers[2].messages['warning']), 1)
        self.client = srunner.app.test_client()
        response = self.client.post("/questionnaire/1",  data={
                                                        'How many marbles do you have?':'4'
                                }, follow_redirects=True)
        self.assertEqual(len(self.app.logger.handlers[2].messages['warning']), 2)

    def tearDown(self):
        self.mock_get_form_schema.stop()

if __name__ == '__main__':
    unittest.main()
