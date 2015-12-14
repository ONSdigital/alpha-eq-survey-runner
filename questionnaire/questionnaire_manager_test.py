import os
import unittest
from questions.inputtext import InputText
from questions.inputnumber import InputNumber
from questions.multiplechoice import MultipleChoice
from questions.questiongroup import QuestionGroup
from questionnaire_manager import QuestionnaireManager
from questions.textblock import TextBlock
from settings import APP_FIXTURES


class QuestionnaireManagerTest(unittest.TestCase):
    def _loadFixture(self, filename):
        with open(os.path.join(APP_FIXTURES, filename)) as f:
            q_data = f.read()
            f.close()
            return q_data

    def test_start_questionnaire(self):
        q_data = self._loadFixture('test_survey.json')

        # Instantiate the questionnaire manager... There is no resume data
        q_manager = QuestionnaireManager(q_data, {})

        assert q_manager.title == "welcome to my survey about crayons"

        q_manager.start_questionnaire()

        q = q_manager.get_current_question()

        assert q.question_text == "How many marbles do you have"

    def test_answer_required_question(self):
        q_data = self._loadFixture('test_survey.json')

        # Instantiate the questionnaire manager... There is no resume data
        q_manager = QuestionnaireManager(q_data, {})
        q_manager.start_questionnaire()

        q = q_manager.get_current_question()

        assert isinstance(q, InputText) == True
        assert q.question_text == "How many marbles do you have"

        response = '15'
        warnings_accepted = []

        assert q_manager.is_valid_response(response, warnings_accepted)

        assert q_manager.get_question_errors() is None

    def test_miss_required_question(self):
        q_data = self._loadFixture('test_survey.json')

        # Instantiate the questionnaire manager... There is no resume data
        q_manager = QuestionnaireManager(q_data, {})
        q_manager.start_questionnaire()

        q = q_manager.get_current_question()

        assert isinstance(q, InputText) == True
        assert q.question_text == "How many marbles do you have"

        response = 'Lots'
        warnings_accepted = []

        assert q_manager.is_valid_response(response, warnings_accepted)

        response = '   '

        assert q_manager.is_valid_response(response, warnings_accepted) == False

        assert 'This field is required' in q_manager.get_question_errors()

    def test_next_question(self):
        q_data = self._loadFixture('test_survey.json')

        q_manager = QuestionnaireManager(q_data, {})
        q_manager.start_questionnaire()

        q = q_manager.get_current_question()

        assert isinstance(q, InputText)
        assert q.question_text == "How many marbles do you have"

        response = '35'
        warnings_accepted = []
        assert q_manager.is_valid_response(response, warnings_accepted)

        q = q_manager.get_next_question(response)

        assert isinstance(q, TextBlock)

        assert q_manager.is_valid_response('anything you like', warnings_accepted)
        assert q_manager.get_question_errors() is None

        q = q_manager.get_next_question(response)

        assert isinstance(q, MultipleChoice)
        assert q.question_text == 'Which colour marble would you prefer?'

        invalid_response_1 = ' '
        assert q_manager.is_valid_response(invalid_response_1, warnings_accepted) == False

        invalid_response_2 = 'Purple'
        assert q_manager.is_valid_response(invalid_response_2, warnings_accepted) == False

        valid_response = 'Blue'
        assert q_manager.is_valid_response(valid_response, warnings_accepted)

    def test_resume_questionnaire(self):
        q_data = self._loadFixture('test_survey.json')

        resume_data = {
            'started': True,
            'completed': False,
            'index': 1,
            'history': {},
            'warningsAccepted': [],
            'justifications': {},
            'responses': {
                'EQ_q1': '123'
            }
        }

        q_manager = QuestionnaireManager(q_data, resume_data)

        q = q_manager.get_current_question()

        assert q.get_reference() == 'EQ_q2'

    def test_resume_from_text_block(self):
        q_data = self._loadFixture('test_survey.json')
        resume_data = {
            'started': True,
            'completed': False,
            'index': 2,
            'history': {},
            'warningsAccepted': [],
            'justifications': {},
            'responses': {
                'EQ_q1': '123',
                'EQ_q2': None
            }
        }

        q_manager = QuestionnaireManager(q_data, resume_data)

        q = q_manager.get_current_question()

        assert q.get_reference() == 'EQ_q3'
        assert q_manager.completed is False

    def test_resume_from_last_question(self):
        q_data = self._loadFixture('test_survey.json')
        resume_data = {
            'started': True,
            'completed': False,
            'index': 2,
            'history': {},
            'warningsAccepted': [],
            'justifications': {},
            'responses': {
                'EQ_q1': '123',
                'EQ_q2': None,
                'EQ_q3': None
            }
        }

        q_manager = QuestionnaireManager(q_data, resume_data)

        q = q_manager.get_current_question()

        assert q.get_reference() == 'EQ_q3'
        assert q_manager.completed is False

    def test_resume_completed_questionnaire(self):
        q_data = self._loadFixture('test_survey.json')
        resume_data = {
            'started': True,
            'completed': True,
            'index': 2,
            'history': {},
            'warningsAccepted': [],
            'justifications': {},
            'responses': {
                'EQ_q1': '123',
                'EQ_q2': None,
                'EQ_q3': None
            }
        }

        q_manager = QuestionnaireManager(q_data, resume_data)

        q = q_manager.get_current_question()

        assert q is None
        assert q_manager.completed

    def test_groups_navigation(self):
        q_data = self._loadFixture('groups.json')
        resume_data = {}

        q_manager = QuestionnaireManager(q_data, resume_data)
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        assert isinstance(q1, QuestionGroup)

        q2 = q_manager.get_next_question(None)

        assert isinstance(q2, QuestionGroup)

        assert q1 != q2

    def test_validate_group(self):
        q_data = self._loadFixture('groups.json')
        resume_data = {}

        q_manager = QuestionnaireManager(q_data, resume_data)
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'EQ_start_q1': '6',  # Numeric required field
            'EQ_start_q2': None,  # Rich text text, no response required
            'EQ_start_q3': 'option1',  # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',  # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None,  # Optional numeric
            'EQ_start_q7': '15/07/2015'  # Required date
        }
        warnings_accepted = []
        assert q_manager.is_valid_response(responses, warnings_accepted) == True

    def test_group_fail_validation(self):
        q_data = self._loadFixture('groups.json')
        resume_data = {}

        q_manager = QuestionnaireManager(q_data, resume_data)
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'EQ_start_q1': '',  # Numeric required field
            'EQ_start_q2': None,  # Rich text text, no response required
            'EQ_start_q3': 'option6',  # Multi-choice, there is no option6
            'EQ_start_q4': None,  # Checkbox requires selection
            'EQ_start_q5': ' ',  # required free text field
            'EQ_start_q6': '',  # numeric free text field
            'EQ_start_q7': '12/27/2016'  # invalid date
        }
        warnings_accepted = []

        assert q_manager.is_valid_response(responses, warnings_accepted) == False

        errors = q_manager.get_question_errors()

        assert 'EQ_start_q1' in errors.keys()
        assert 'EQ_start_q2' not in errors.keys()
        assert 'EQ_start_q3' in errors.keys()
        assert 'EQ_start_q4' in errors.keys()
        assert 'EQ_start_q5' in errors.keys()
        assert 'EQ_start_q7' in errors.keys()

        assert 'This field is required' in errors['EQ_start_q1']

        assert 'invalid option' in errors['EQ_start_q3']
        assert 'This field is required' in errors['EQ_start_q4']
        assert 'This field is required' in errors['EQ_start_q5']
        assert 'This field must be a date' in errors['EQ_start_q7']

    def test_progress(self):
        q_data = self._loadFixture('groups.json')
        resume_data = {}

        q_manager = QuestionnaireManager(q_data, resume_data)
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        assert q_manager.get_current_question_index() == 1

        assert q_manager.get_total_questions() == 2

        q_manager.get_next_question(None)

        assert q_manager.get_current_question_index() == 2

    def test_jump(self):
        q_data = self._loadFixture('groups.json')

        # can't jump unless we have resume data
        resume_data = {
            'started': True,
            'completed': False,
            'index': 1,
            'history': {},
            'warningsAccepted': [],
            'justifications': {},
            'responses': {
                'EQ_start_q1': '1',  # Numeric required field
                'EQ_start_q2': None,  # Rich text text, no response required
                'EQ_start_q3': 'option1',  # Multi-choice, option 1
                'EQ_start_q4': 'option1',  # Checkbox, selected
                'EQ_start_q5': 'Some Text',  # required free text field
                'EQ_start_q6': None  # Optional numeric
            }
        }

        q_manager = QuestionnaireManager(q_data, resume_data)

        # take us to the start of the questionnaire
        q_manager.start_questionnaire()

        start = q_manager.get_current_question()

        assert isinstance(start, QuestionGroup) == True

        assert start.get_reference() == 'EQ_start'

        assert q_manager.get_current_question_index() == 1

        assert q_manager.get_total_questions() == 2

        next_question = q_manager.get_next_question(None)

        assert next_question.get_reference() == 'EQ_q1'  # automatically generated reference 'q1'

        q_manager.jump_to_question('EQ_start')

        current_question = q_manager.get_current_question()

        assert current_question.get_reference() == start.get_reference()
        assert q_manager.get_current_question_index() == 1

    def test_get_question_by_reference(self):
        q_data = self._loadFixture('starwars.json')

        q_manager = QuestionnaireManager(q_data, {})

        section_one = q_manager.get_question_by_reference('sectionOne')

        assert section_one.get_reference() == 'EQ_sectionOne'

        section_one_q1 = q_manager.get_question_by_reference('sectionOne_q1')

        assert isinstance(section_one_q1, TextBlock) == True
        assert section_one_q1.get_reference() == 'EQ_sectionOne_q1'
        # check 'private' internal reference
        assert section_one_q1._reference == 'q1'

        section_two_q1 = q_manager.get_question_by_reference('sectionTwo_q1')


        assert isinstance(section_two_q1, InputNumber) == True
        assert section_two_q1.get_reference() == 'EQ_sectionTwo_q1'
        # check 'private' internal reference
        assert section_two_q1._reference == 'q1'

    def test_skip_conditions_added_by_branching(self):
        q_data = self._loadFixture('starwars.json')

        q_manager = QuestionnaireManager(q_data, {})

        section_one_q3 = q_manager.get_question_by_reference('EQ_sectionOne_q3')

        assert section_one_q3.has_branch_conditions()

        section_two = q_manager.get_question_by_reference('EQ_sectionTwo')

        assert len(section_two.skip_conditions) == 1

        skip_condition = section_two.skip_conditions[0]

        assert skip_condition.trigger == "EQ_sectionOne_q3"
        assert skip_condition.state == "Episode 1: The Phantom Menance"

        section_three = q_manager.get_question_by_reference('sectionThree')

        assert len(section_three.skip_conditions) == 0

    def test_empty_routing_rule(self):
        q_data = self._loadFixture('empty-rule-schema.json')

        q_manager = QuestionnaireManager(q_data, {})
        q_manager.start_questionnaire()

        question = q_manager.get_current_question()

        assert not question.has_branch_conditions()

    def test_history_order_correct(self):
        q_data = self._loadFixture('groups.json')

        q_manager = QuestionnaireManager(q_data, {})
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        response = {
            'EQ_start_q1': '1',  # Numeric required field
            'EQ_start_q2': None,  # Rich text text, no response required
            'EQ_start_q3': 'option1',  # Multi-choice, option 1
            'EQ_start_q4': 'option1',  # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None  # Optional numeric
        }

        q_manager.store_response(response)

        assert q1 == q_manager.get_history().keys()[0]

        q2 = q_manager.get_next_question(response)

        response['EQ_q1_q2'] = 'anything you like'

        q_manager.store_response(response)

        assert q2 == q_manager.get_history().keys()[1]

    def test_validate_fail_maxlength(self):
        q_data = self._loadFixture('groups.json')
        resume_data = {}

        q_manager = QuestionnaireManager(q_data, resume_data)
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {

            'EQ_start_q1': '1',  # Numeric required field
            'EQ_start_q2': None,  # Rich text text, no response required
            'EQ_start_q3': 'option1',  # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',  # Checkbox, selected
            'EQ_start_q5': 'Some Text, extra text to make it fail',  # required free text field
            'EQ_start_q6': None  # Optional numeric
        }
        warnings_accepted = []
        assert q_manager.is_valid_response(responses, warnings_accepted) == False

        errors = q_manager.get_question_errors()
        assert 'EQ_start_q5' in errors.keys()
        assert 'This field is to big' in errors['EQ_start_q5']

    def test_validate_fail_lessthan(self):
        q_data = self._loadFixture('groups.json')
        resume_data = {}

        q_manager = QuestionnaireManager(q_data, resume_data)
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'EQ_start_q1': '0',  # Numeric required field
            'EQ_start_q2': None,  # Rich text text, no response required
            'EQ_start_q3': 'option1',  # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',  # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None  # Optional numeric
        }
        warnings_accepted = []
        assert q_manager.is_valid_response(responses, warnings_accepted) == False

        errors = q_manager.get_question_errors()

        assert 'EQ_start_q1' in errors.keys()
        assert 'This field should be greater than 0' in errors['EQ_start_q1']

    def test_validate_fail_greaterthan(self):
        q_data = self._loadFixture('groups.json')
        resume_data = {}

        q_manager = QuestionnaireManager(q_data, resume_data)
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'EQ_start_q1': '11',  # Numeric required field
            'EQ_start_q2': None,  # Rich text text, no response required
            'EQ_start_q3': 'option1',  # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',  # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None  # Optional numeric
        }
        warnings_accepted = []
        assert q_manager.is_valid_response(responses, warnings_accepted) == False

        errors = q_manager.get_question_errors()

        assert 'EQ_start_q1' in errors.keys()
        assert 'This field should be less than 11' in errors['EQ_start_q1']

    def test_validate_fail_equal(self):
        q_data = self._loadFixture('groups.json')
        resume_data = {}

        q_manager = QuestionnaireManager(q_data, resume_data)
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'EQ_start_q1': '5',  # Numeric required field
            'EQ_start_q2': None,  # Rich text text, no response required
            'EQ_start_q3': 'option1',  # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',  # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None  # Optional numeric
        }
        warnings_accepted = []
        assert q_manager.is_valid_response(responses, warnings_accepted) == False

        errors = q_manager.get_question_errors()

        assert 'EQ_start_q1' in errors.keys()
        assert 'should not be 5' in errors['EQ_start_q1']

    def test_validate_fail_notequal(self):
        q_data = self._loadFixture('groups.json')
        resume_data = {}

        q_manager = QuestionnaireManager(q_data, resume_data)
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'EQ_start_q1': '7',  # Numeric required field
            'EQ_start_q2': None,  # Rich text text, no response required
            'EQ_start_q3': 'option1',  # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',  # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None  # Optional numeric
        }

        warnings_accepted = []
        assert q_manager.is_valid_response(responses, warnings_accepted) == False

        errors = q_manager.get_question_errors()

        assert 'EQ_start_q1' in errors.keys()
        assert 'should be 6' in errors['EQ_start_q1']

    def test_validation_warnings(self):
        q_data = self._loadFixture('test_survey.json')

        # Instantiate the questionnaire manager... There is no resume data
        q_manager = QuestionnaireManager(q_data, {})
        q_manager.start_questionnaire()

        q = q_manager.get_current_question()

        assert isinstance(q, InputText) == True
        assert q.question_text == "How many marbles do you have"

        response = 'Lots and lots and lots'
        warnings_accepted = []

        assert q_manager.is_valid_response(response, warnings_accepted) == False

        assert 'This field is long, are you sure?' in q_manager.get_question_warnings()

        warnings_accepted = ['q1']
        assert q_manager.is_valid_response(response, warnings_accepted) == True


if __name__ == '__main__':
    unittest.main()
