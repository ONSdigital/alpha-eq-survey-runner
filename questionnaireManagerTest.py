import unittest
import os
from settings import APP_FIXTURES
from questionnaireManager import QuestionnaireManager

from questions import TextBlock, MultipleChoiceQuestion, InputTextQuestion, QuestionGroup

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

        assert qManager.get_question_errors() == None
        assert qManager.get_question_warnings() == None

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

        assert 'required' in qManager.get_question_errors()

    def test_next_question(self):
        qData = self._loadFixture('test_survey.json')

        qManager = QuestionnaireManager(qData, {})
        qManager.start_questionnaire()

        q = qManager.get_current_question()

        assert isinstance(q, InputTextQuestion) == True
        assert q.question_text == "How many marbles do you have"

        response = '35'

        assert qManager.is_valid_response(response) == True

        q = qManager.get_next_question(response)

        assert isinstance(q, TextBlock) == True

        assert qManager.is_valid_response('anything you like') == True
        assert qManager.get_question_errors() == None

        q = qManager.get_next_question(response)

        assert isinstance(q, MultipleChoiceQuestion)
        assert q.question_text == 'Which colour marble would you prefer?'

        invalid_response_1 = ' '
        assert qManager.is_valid_response(invalid_response_1) == False

        invalid_response_2 = 'Purple'
        assert qManager.is_valid_response(invalid_response_2) == False

        valid_response = 'Blue'
        assert qManager.is_valid_response(valid_response) == True

    def test_resume_questionnaire(self):
        qData = self._loadFixture('test_survey.json')

        resumeData = {
            'started' : True,
            'completed' : False,
            'index' : 1,
            'responses' : {
                'q1': '123'
            }
        }

        qManager = QuestionnaireManager(qData, resumeData)

        q = qManager.get_current_question()

        assert q.reference == 'q2'

    def test_resume_from_text_block(self):
        qData = self._loadFixture('test_survey.json')
        resumeData = {
            'started' : True,
            'completed' : False,
            'index' : 2,
            'responses' : {
                'q1': '123',
                'q2': None
            }
        }

        qManager = QuestionnaireManager(qData, resumeData)

        q = qManager.get_current_question()

        assert q.reference == 'q3'
        assert qManager.completed == False

    def test_resume_from_last_question(self):
        qData = self._loadFixture('test_survey.json')
        resumeData = {
            'started' : True,
            'completed' : False,
            'index' : 2,
            'responses' : {
                'q1': '123',
                'q2':None,
                'q3':None
            }
        }

        qManager = QuestionnaireManager(qData, resumeData)

        q = qManager.get_current_question()

        assert q.reference == 'q3'
        assert qManager.completed == False

    def test_resume_completed_questionnaire(self):
        qData = self._loadFixture('test_survey.json')
        resumeData = {
            'started' : True,
            'completed' : True,
            'index' : 2,
            'responses' : {
                'q1': '123',
                'q2':None,
                'q3':None
            }
        }

        qManager = QuestionnaireManager(qData, resumeData)

        q = qManager.get_current_question()

        assert q is None
        assert qManager.completed == True

    def test_groups_navigation(self):
        qData = self._loadFixture('groups.json')
        resumeData = {}

        qManager = QuestionnaireManager(qData, resumeData)
        qManager.start_questionnaire()

        q1 = qManager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        q2 = qManager.get_next_question(None)

        assert isinstance(q2, QuestionGroup) == True

        assert q1 != q2

    def test_validate_group(self):
        qData = self._loadFixture('groups.json')
        resumeData = {}

        qManager = QuestionnaireManager(qData, resumeData)
        qManager.start_questionnaire()

        q1 = qManager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'q1': '1',          # Numeric required field
            'q2': None,         # Rich text text, no response required
            'q3': 'option1',    # Multi-choice, option 1
            'q4': 'Coption1',   # Checkbox, selected
            'q5': 'Some Text',  # required free text field
            'q6': None          # Optional numeric
        }

        assert qManager.is_valid_response(responses) == True

    def test_group_fail_validation(self):
        qData = self._loadFixture('groups.json')
        resumeData = {}

        qManager = QuestionnaireManager(qData, resumeData)
        qManager.start_questionnaire()

        q1 = qManager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'q1': '',            # Numeric required field
            'q2': None,         # Rich text text, no response required
            'q3': 'option6',    # Multi-choice, there is no option6
            'q4': None,         # Checkbox requires selection
            'q5': ' ',          # required free text field
            'q6': 'a'           # numeric free text field
        }

        assert qManager.is_valid_response(responses) == False

        errors = qManager.get_question_errors()

        assert 'q1' in errors.keys()
        assert 'q2' not in errors.keys()
        assert 'q3' in errors.keys()
        assert 'q4' in errors.keys()
        assert 'q5' in errors.keys()

        assert 'required' in errors['q1']

        assert 'invalid option' in errors['q3']

        assert 'required' in errors['q4']

        assert 'required' in errors['q5']

    def test_progress(self):
        qData = self._loadFixture('groups.json')
        resume_data = {}

        q_manager = QuestionnaireManager(qData, resume_data)
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        assert q_manager.get_current_question_index() == 1

        assert q_manager.get_total_questions() == 2

        q2 = q_manager.get_next_question(None)

        assert q_manager.get_current_question_index() == 2

    def test_jump(self):
        qData = self._loadFixture('groups.json')

        # can't jump unless we have resume data
        resumeData = {
            'started': False,
            'completed': False,
            'index': 0,
            'responses': {
                "start":{
                    'q1': '1',          # Numeric required field
                    'q2': None,         # Rich text text, no response required
                    'q3': 'option1',    # Multi-choice, option 1
                    'q4': 'option1',   # Checkbox, selected
                    'q5': 'Some Text',  # required free text field
                    'q6': None          # Optional numeric
                }
            }
        }

        q_manager = QuestionnaireManager(qData, resumeData)
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        assert q_manager.get_current_question_index() == 1

        assert q_manager.get_total_questions() == 2

        q2 = q_manager.get_next_question(None)

        q_manager.jump_to_question('start')

        current_question = q_manager.get_current_question()
        assert current_question.reference == q1.reference
        assert q_manager.get_current_question_index() == 1

    def test_get_question_by_reference(self):

        qData = self._loadFixture('starwars.json')

        qManager = QuestionnaireManager(qData, {})

        sectionOne = qManager.get_question_by_reference('sectionOne')

        assert sectionOne.reference == 'sectionOne'

        sectionOneQ1 = qManager.get_question_by_reference('sectionOne:q1')

        assert isinstance(sectionOneQ1, TextBlock) == True
        assert sectionOneQ1.reference == 'q1'

        sectionTwoQ1 = qManager.get_question_by_reference('sectionTwo:q1')

        assert isinstance(sectionTwoQ1, InputTextQuestion) == True
        assert sectionTwoQ1.reference == 'q1'

    def test_skip_conditions_added_by_branching(self):
        qData = self._loadFixture('starwars.json')

        qManager = QuestionnaireManager(qData, {})

        sectionOneQ3 = qManager.get_question_by_reference('sectionOne:q3')

        assert sectionOneQ3.has_branch_conditions()

        sectionTwo = qManager.get_question_by_reference('sectionTwo')

        assert len(sectionTwo.skip_conditions) == 1

        sectionThree = qManager.get_question_by_reference('sectionThree')

        assert len(sectionThree.skip_conditions) == 0


if __name__ == '__main__':
    unittest.main()
