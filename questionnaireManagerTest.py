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
            'history': {},
            'responses' : {
                'EQ_q1': '123'
            }
        }

        qManager = QuestionnaireManager(qData, resumeData)

        q = qManager.get_current_question()

        assert q.get_reference() == 'EQ_q2'

    def test_resume_from_text_block(self):
        qData = self._loadFixture('test_survey.json')
        resumeData = {
            'started' : True,
            'completed' : False,
            'index' : 2,
            'history': {},
            'responses' : {
                'EQ_q1': '123',
                'EQ_q2': None
            }
        }

        qManager = QuestionnaireManager(qData, resumeData)

        q = qManager.get_current_question()

        assert q.get_reference() == 'EQ_q3'
        assert qManager.completed == False

    def test_resume_from_last_question(self):
        qData = self._loadFixture('test_survey.json')
        resumeData = {
            'started' : True,
            'completed' : False,
            'index' : 2,
            'history': {},
            'responses' : {
                'EQ_q1': '123',
                'EQ_q2':None,
                'EQ_q3':None
            }
        }

        qManager = QuestionnaireManager(qData, resumeData)

        q = qManager.get_current_question()

        assert q.get_reference() == 'EQ_q3'
        assert qManager.completed == False

    def test_resume_completed_questionnaire(self):
        qData = self._loadFixture('test_survey.json')
        resumeData = {
            'started' : True,
            'completed' : True,
            'index' : 2,
            'history': {},
            'responses' : {
                'EQ_q1': '123',
                'EQ_q2':None,
                'EQ_q3':None
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
            'EQ_start_q1': '1',          # Numeric required field
            'EQ_start_q2': None,         # Rich text text, no response required
            'EQ_start_q3': 'option1',    # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',   # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None          # Optional numeric
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
            'EQ_start_q1': '',            # Numeric required field
            'EQ_start_q2': None,         # Rich text text, no response required
            'EQ_start_q3': 'option6',    # Multi-choice, there is no option6
            'EQ_start_q4': None,         # Checkbox requires selection
            'EQ_start_q5': ' ',          # required free text field
            'EQ_start_q6': 'a'           # numeric free text field
        }

        assert qManager.is_valid_response(responses) == False

        errors = qManager.get_question_errors()

        assert 'EQ_start_q1' in errors.keys()
        assert 'EQ_start_q2' not in errors.keys()
        assert 'EQ_start_q3' in errors.keys()
        assert 'EQ_start_q4' in errors.keys()
        assert 'EQ_start_q5' in errors.keys()

        assert 'required' in errors['EQ_start_q1']

        assert 'invalid option' in errors['EQ_start_q3']

        assert 'required' in errors['EQ_start_q4']

        assert 'required' in errors['EQ_start_q5']

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
            'started': True,
            'completed': False,
            'index': 1,
            'history': {},
            'responses': {
                'EQ_start_q1': '1',          # Numeric required field
                'EQ_start_q2': None,         # Rich text text, no response required
                'EQ_start_q3': 'option1',    # Multi-choice, option 1
                'EQ_start_q4': 'option1',   # Checkbox, selected
                'EQ_start_q5': 'Some Text',  # required free text field
                'EQ_start_q6': None          # Optional numeric
            }
        }

        q_manager = QuestionnaireManager(qData, resumeData)

        # take us to the start of the questionnaire
        q_manager.start_questionnaire()

        start = q_manager.get_current_question()

        assert isinstance(start, QuestionGroup) == True

        assert start.get_reference() == 'EQ_start'

        assert q_manager.get_current_question_index() == 1

        assert q_manager.get_total_questions() == 2

        next_question = q_manager.get_next_question(None)

        assert next_question.get_reference() == 'EQ_q1' # automatically generated reference 'q1'

        q_manager.jump_to_question('EQ_start')

        current_question = q_manager.get_current_question()

        assert current_question.get_reference() == start.get_reference()
        assert q_manager.get_current_question_index() == 1

    def test_get_question_by_reference(self):

        qData = self._loadFixture('starwars.json')

        qManager = QuestionnaireManager(qData, {})

        sectionOne = qManager.get_question_by_reference('sectionOne')

        assert sectionOne.get_reference() == 'EQ_sectionOne'

        sectionOneQ1 = qManager.get_question_by_reference('sectionOne_q1')

        assert isinstance(sectionOneQ1, TextBlock) == True
        assert sectionOneQ1.get_reference() == 'EQ_sectionOne_q1'
        # check 'private' internal reference
        assert sectionOneQ1._reference == 'q1'

        sectionTwoQ1 = qManager.get_question_by_reference('sectionTwo_q1')

        assert isinstance(sectionTwoQ1, InputTextQuestion) == True
        assert sectionTwoQ1.get_reference() == 'EQ_sectionTwo_q1'
        # check 'private' internal reference
        assert sectionTwoQ1._reference == 'q1'

    def test_skip_conditions_added_by_branching(self):
        qData = self._loadFixture('starwars.json')

        qManager = QuestionnaireManager(qData, {})

        sectionOneQ3 = qManager.get_question_by_reference('EQ_sectionOne_q3')

        assert sectionOneQ3.has_branch_conditions()

        sectionTwo = qManager.get_question_by_reference('EQ_sectionTwo')

        assert len(sectionTwo.skip_conditions) == 1

        skipCondition = sectionTwo.skip_conditions[0]

        assert skipCondition.trigger == "EQ_sectionOne_q3"
        assert skipCondition.state == "Episode 1: The Phantom Menance"

        sectionThree = qManager.get_question_by_reference('sectionThree')

        assert len(sectionThree.skip_conditions) == 0

    def test_empty_routing_rule(self):
        q_data = self._loadFixture('empty-rule-schema.json')

        q_manager = QuestionnaireManager(q_data, {});
        q_manager.start_questionnaire()

        question = q_manager.get_current_question()

        assert not question.has_branch_conditions()

    def test_history_order_correct(self):
        q_data = self._loadFixture('groups.json')

        q_manager = QuestionnaireManager(q_data, {})
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        response = {
                'EQ_start_q1': '1',          # Numeric required field
                'EQ_start_q2': None,         # Rich text text, no response required
                'EQ_start_q3': 'option1',    # Multi-choice, option 1
                'EQ_start_q4': 'option1',   # Checkbox, selected
                'EQ_start_q5': 'Some Text',  # required free text field
                'EQ_start_q6': None          # Optional numeric
            }

        q_manager.store_response(response)

        assert q1 == q_manager.get_history().keys()[0]

        q2 = q_manager.get_next_question(response)

        response['EQ_q1_q2'] = 'anything you like'

        q_manager.store_response(response)

        assert q2 == q_manager.get_history().keys()[1]

if __name__ == '__main__':
    unittest.main()
