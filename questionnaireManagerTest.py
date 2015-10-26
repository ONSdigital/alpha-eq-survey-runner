import unittest
import os
from settings import APP_FIXTURES
from questionnaireManager import QuestionnaireManager
import pprint

from questions import TextBlock, MultipleChoiceQuestion, InputTextQuestion

class QuestionnaireManagerTest(unittest.TestCase):

    def _loadFixture(self, filename):
        qData = None
        with open(os.path.join(APP_FIXTURES, filename)) as f:
            qData = f.read()
            f.close()
        return qData

    def test_start_questionnaire(self):
        qData = self._loadFixture('test_survey.json')

        # Instantiate the questionnaire manager... There is no resume data
        qManager = QuestionnaireManager(qData, {})

        assert qManager.title == "welcome to my survey about crayons"

        qManager.start_questionnaire()

        q = qManager.get_current_question()

        assert q.question_text == "How many marbles do you have"

    def test_answer_required_question(self):
        qData = self._loadFixture('test_survey.json')

        # Instantiate the questionnaire manager... There is no resume data
        qManager = QuestionnaireManager(qData, {})
        qManager.start_questionnaire()

        q = qManager.get_current_question()

        assert isinstance(q, InputTextQuestion) == True
        assert q.question_text == "How many marbles do you have"

        response = '15'

        assert qManager.is_valid_response(response) == True

        assert qManager.get_question_errors(response) == None
        assert qManager.get_question_warnings(response) == None

    def test_miss_required_question(self):
        qData = self._loadFixture('test_survey.json')

        # Instantiate the questionnaire manager... There is no resume data
        qManager = QuestionnaireManager(qData, {})
        qManager.start_questionnaire()

        q = qManager.get_current_question()

        assert isinstance(q, InputTextQuestion) == True
        assert q.question_text == "How many marbles do you have"

        response = 'Lots'

        assert qManager.is_valid_response(response) == False

        response = '   '

        assert qManager.is_valid_response(response) == False

        assert 'required' in qManager.get_question_errors(response)

    def test_next_question(self):
        qData = self._loadFixture('test_survey.json')

        qManager = QuestionnaireManager(qData, {})
        qManager.start_questionnaire()

        q = qManager.get_current_question()

        assert isinstance(q, InputTextQuestion) == True
        assert q.question_text == "How many marbles do you have"

        response = '35'

        assert qManager.is_valid_response(response) == True

        q = qManager.get_next_question()

        assert isinstance(q, TextBlock) == True

        assert qManager.is_valid_response('anything you like') == True
        assert qManager.get_question_errors('still anything') == None

        q = qManager.get_next_question()

        assert isinstance(q, MultipleChoiceQuestion)
        assert q.question_text == 'Which colour marble would you prefer?'

        invalid_response_1 = ' '
        assert qManager.is_valid_response(invalid_response_1) == False

        invalid_response_2 = 'Purple'
        assert qManager.is_valid_response(invalid_response_2) == False

        valid_response = 'Blue'
        assert qManager.is_valid_response(valid_response) == True


if __name__ == '__main__':
    unittest.main()
