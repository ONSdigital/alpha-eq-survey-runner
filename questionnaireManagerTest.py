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
        assert q.get_reference() == 'EQ_q1'

        assert isinstance(q, InputTextQuestion) == True
        assert q.question_text == "How many marbles do you have"

        qManager.update({'EQ_q1': '15'})

        assert qManager.validate().is_valid() == True

        assert len(qManager.get_question_errors()) == 0

    def test_miss_required_question(self):
        qData = self._loadFixture('test_survey.json')

        # Instantiate the questionnaire manager... There is no resume data
        qManager = QuestionnaireManager(qData, {})
        qManager.start_questionnaire()

        q = qManager.get_current_question()

        assert isinstance(q, InputTextQuestion) == True
        assert q.question_text == "How many marbles do you have"

        qManager.update({'q1':'Lots'})

        assert q.validate().is_valid() == True

        qManager.update({'q1':'    '})

        assert q.validate().is_valid() == False

        assert 'This field is required' in qManager.get_question_errors()

    def test_next_question(self):
        qData = self._loadFixture('test_survey.json')

        qManager = QuestionnaireManager(qData, {})
        qManager.start_questionnaire()

        q = qManager.get_current_question()

        assert isinstance(q, InputTextQuestion) == True
        assert q.question_text == "How many marbles do you have"

        response = {'q1':'35'}
        qManager.update(response)

        assert qManager.current_question.validate().is_valid() == True

        q = qManager.get_next_question()

        assert isinstance(q, TextBlock) == True

        assert qManager.validate().is_valid() == True
        assert len(qManager.get_question_errors()) == 0

        q = qManager.get_next_question()

        assert isinstance(q, MultipleChoiceQuestion)
        assert q.question_text == 'Which colour marble would you prefer?'

        qManager.update({'EQ_q3':' '})
        assert qManager.validate().is_valid() == False

        qManager.update({'EQ_q3':'Purple'})
        assert qManager.validate().is_valid() == False

        qManager.update({'EQ_q3':'Blue'})
        assert qManager.validate().is_valid() == True

    def test_resume_questionnaire(self):
        qData = self._loadFixture('test_survey.json')

        resumeData = {
            'started' : True,
            'completed' : False,
            'current_question' : 'EQ_q2',
            'history': [],
            'user_data' : {
                'EQ_q1': {
                    'answer': ['123']
                }
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
            'current_question' : 'EQ_q3',
            'history': [],
            'user_data' : {
                'EQ_q1': {
                    'answer': ['123']
                }
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
            'current_question' : 'EQ_q3',
            'history': [],
            'user_data' : {
                'EQ_q1': {
                    'answer': ['123']
                }
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
            'current_question' : 'EQ_q2',
            'history': [],
            'user_data' : {
                'EQ_q1': {
                    'answer': ['123']
                }
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

        q2 = qManager.get_next_question()

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

        qManager.update(responses)

        result = qManager.validate()

        assert result.is_valid() == True

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
            'EQ_start_q4': [''],         # Checkbox requires selection
            'EQ_start_q5': ' ',          # required free text field
            'EQ_start_q6': ''           # numeric free text field
        }

        qManager.update(responses)

        assert qManager.validate().is_valid() == False

        errors = qManager.get_question_errors()

        assert len(errors['EQ_start_q3']) == 1
        assert len(errors['EQ_start_q4']) == 1

        assert 'This field is required' in errors['EQ_start_q1']
        assert 'Invalid option' in errors['EQ_start_q3']
        assert 'This field is required' in errors['EQ_start_q4']
        assert 'This field is required' in errors['EQ_start_q5']

    def test_progress(self):
        qData = self._loadFixture('groups.json')
        resume_data = {}

        q_manager = QuestionnaireManager(qData, resume_data)
        q_manager.start_questionnaire()

        q1 = q_manager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        assert q_manager.get_current_question_number() == 1

        assert q_manager.get_total_questions() == 2

        q2 = q_manager.get_next_question()

        assert q_manager.get_current_question_number() == 2

    def test_jump(self):
        qData = self._loadFixture('groups.json')

        # can't jump unless we have resume data
        resumeData = {
            'started': True,
            'completed': False,
            'current_question': 'EQ_start',
            'history': [],
            'user_data': {
                'EQ_start_q1': {
                    'answer' :'1',          # Numeric required field
                },
                'EQ_start_q2': {
                    'answer' :None,         # Rich text text, no response required
                },
                'EQ_start_q3': {
                    'answer' :'option1',    # Multi-choice, option 1
                },
                'EQ_start_q4': {
                    'answer' :'option1',   # Checkbox, selected
                },
                'EQ_start_q5': {
                    'answer' :'Some Text',  # required free text field
                },
                'EQ_start_q6': {
                    'answer' :None          # Optional numeric
                },
            }
        }

        q_manager = QuestionnaireManager(qData, resumeData)

        # take us to the start of the questionnaire
        q_manager.start_questionnaire()

        start = q_manager.get_current_question()

        assert isinstance(start, QuestionGroup) == True

        assert start.get_reference() == 'EQ_start'

        assert q_manager.get_current_question_number() == 1

        assert q_manager.get_total_questions() == 2

        next_question = q_manager.get_next_question()

        assert next_question.get_reference() == 'EQ_q1' # automatically generated reference 'q1'

        q_manager.jump_to_question('EQ_start')

        current_question = q_manager.get_current_question()

        assert current_question.get_reference() == start.get_reference()
        assert q_manager.get_current_question_number() == 1

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

        sectionFourRep2 = qManager.get_question_by_reference('EQ_sectionFour:2')
        assert isinstance(sectionFourRep2, QuestionGroup) == True
        assert sectionFourRep2.get_reference() == 'EQ_sectionFour'
        assert sectionFourRep2.get_repetition() == 2

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

        q_manager.update(response)

        history = q_manager.get_history()

        assert q1 == q_manager.get_history().keys()[0]

        q2 = q_manager.get_next_question()

        response['EQ_q1_q2'] = 'anything you like'

        q_manager.update(response)

        history = q_manager.get_history()

        assert q2 == q_manager.get_history().keys()[0]
        assert q1 == q_manager.get_history().keys()[1]

    def test_validate_fail_maxlength(self):
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
            'EQ_start_q5': 'Some Text, extra text to make it fail',  # required free text field
            'EQ_start_q6': None          # Optional numeric
        }

        qManager.update(responses)

        assert qManager.validate().is_valid() ==False

        errors = qManager.get_question_errors()

        assert 'EQ_start_q5' in errors.keys()
        assert 'This field is to big' in errors['EQ_start_q5']

    def test_validate_fail_lessthan(self):
        qData = self._loadFixture('groups.json')
        resumeData = {}

        qManager = QuestionnaireManager(qData, resumeData)
        qManager.start_questionnaire()

        q1 = qManager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'EQ_start_q1': '11',          # Numeric required field
            'EQ_start_q2': None,         # Rich text text, no response required
            'EQ_start_q3': 'option1',    # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',   # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None          # Optional numeric

        }

        qManager.update(responses)

        assert qManager.validate().is_valid() ==False

        errors = qManager.get_question_errors()

        assert 'EQ_start_q1' in errors.keys()
        assert 'This field should be less then 11' in errors['EQ_start_q1']

    def test_validate_fail_greaterthan(self):
        qData = self._loadFixture('groups.json')
        resumeData = {}

        qManager = QuestionnaireManager(qData, resumeData)
        qManager.start_questionnaire()

        q1 = qManager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'EQ_start_q1': '0',          # Numeric required field
            'EQ_start_q2': None,         # Rich text text, no response required
            'EQ_start_q3': 'option1',    # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',   # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None          # Optional numeric
        }

        qManager.update(responses)

        assert qManager.validate().is_valid() ==False

        errors = qManager.get_question_errors()

        assert 'EQ_start_q1' in errors.keys()
        assert 'This field  should be greater then 0' in errors['EQ_start_q1']

    def test_validate_fail_equal(self):
        qData = self._loadFixture('groups.json')
        resumeData = {}

        qManager = QuestionnaireManager(qData, resumeData)
        qManager.start_questionnaire()

        q1 = qManager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'EQ_start_q1': '5',          # Numeric required field
            'EQ_start_q2': None,         # Rich text text, no response required
            'EQ_start_q3': 'option1',    # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',   # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None          # Optional numeric
        }
        qManager.update(responses)

        assert qManager.validate().is_valid() ==False

        errors = qManager.get_question_errors()

        assert 'EQ_start_q1' in errors.keys()
        assert 'not 5' in errors['EQ_start_q1']

    def test_validate_fail_notequal(self):
        qData = self._loadFixture('groups.json')
        resumeData = {}

        qManager = QuestionnaireManager(qData, resumeData)
        qManager.start_questionnaire()

        q1 = qManager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'EQ_start_q1': '5',          # Numeric required field
            'EQ_start_q2': None,         # Rich text text, no response required
            'EQ_start_q3': 'option1',    # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',   # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None          # Optional numeric
        }

        qManager.update(responses)

        assert qManager.validate().is_valid() ==False

        errors = qManager.get_question_errors()

        assert 'EQ_start_q1' in errors.keys()
        assert 'not 5' in errors['EQ_start_q1']

    def test_validation_warnings(self):
        qData = self._loadFixture('test_survey.json')

        # Instantiate the questionnaire manager... There is no resume data
        qManager = QuestionnaireManager(qData, {})
        qManager.start_questionnaire()

        q = qManager.get_current_question()

        assert isinstance(q, InputTextQuestion) == True
        assert q.question_text == "How many marbles do you have"

        responses = {
            'q1': 'Lots and lots and lots'
        }

        qManager.update(responses)

        assert qManager.validate().is_valid() == False

        assert 'This field is long, are you sure?' in qManager.get_question_warnings()

        responses = {
            'q1': 'Lots and lots and lots',
            'warning_EQ_q1' : 'true',
            'justification_EQ_q1' : 'I have lots'
        }

        qManager.update(responses)

        assert qManager.validate().is_valid() == True

    def test_repeating_set_number_of_times(self):
        qData = self._loadFixture('repeating_simple.json')
        resumeData = {}

        qManager = QuestionnaireManager(qData, resumeData)
        qManager.start_questionnaire()

        q1 = qManager.get_current_question()

        # Test we have a group
        assert isinstance(q1, QuestionGroup) == True

        # test the group is repeating
        assert q1.repeats() == True
        assert q1.get_repetition() == 0

        responses = {}

        qManager.update(responses)

        # no responses should fail validation
        #assert qManager.validate().is_valid() == False
        assert q1.get_repetition() == 0

        # answer the question for the first repetition
        responses = {
            'repetition' : qManager.get_current_question().get_repetition(),
            'EQ_s1_q1' : 'David',
            'EQ_s1_q2' : '39'
        }

        qManager.update(responses)

        assert q1.get_repetition() == 0

        stored = qManager.get_questionnaire_state()

        print stored

        assert len(stored['user_data']) == 2
        assert 'EQ_s1_q1' in stored['user_data'].keys()
        assert isinstance(stored['user_data']['EQ_s1_q1']['answer'], list)
        assert 'David' == stored['user_data']['EQ_s1_q1']['answer'][0]
        assert isinstance(stored['user_data']['EQ_s1_q2']['answer'], list)
        assert '39' == stored['user_data']['EQ_s1_q2']['answer'][0]

        # check validation passes
        assert qManager.validate().is_valid() == True
        assert q1.get_repetition() == 0


        # call next question (there is only one, but it reepeats)
        qManager.get_next_question()
        assert q1.get_repetition() == 1

        # check we have not completed the questionnaire
        assert qManager.completed == False

        # get the current question
        q2 = qManager.get_current_question()

        responses = {
            'repetition': qManager.get_current_question().get_repetition()
        }

        qManager.update(responses)

        # check validation fails until we answer the second repetition
        assert qManager.validate().is_valid() == False

        responses = {
            'repetition': qManager.get_current_question().get_repetition(),
            'EQ_s1_q1' : 'Lewis',
            'EQ_s1_q2' : 'Ten'
        }

        qManager.update(responses)

        stored = qManager.get_questionnaire_state()

        print stored

        assert len(stored) == 2
        assert 'EQ_s1_q1' in stored,keys()
        assert isinstance(stored['EQ_s1_q1'], list)
        assert 'David' == stored['EQ_s1_q1'][0]
        assert 'Lewis' == stored['EQ_s1_q1'][1]
        assert 'EQ_s1_q2' in stored,keys()
        assert isinstance(stored['EQ_s1_q2'], list)
        assert '39' == stored['EQ_s1_q2'][0]
        assert 'Ten' == stored['EQ_s1_q2'][1]

        # check validation passes with second response
        assert qManager.validation().is_valid() == False

        errors = qManager.get_question_errors()

        assert 'EQ_s1_q2' in errors.keys()

if __name__ == '__main__':
    unittest.main()
