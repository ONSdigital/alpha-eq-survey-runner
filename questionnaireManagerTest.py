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

        result = qManager.get_current_question().validate()

        assert len(result) == 1
        assert result[0].is_valid() == True

        assert len(result[0].errors) == 0

    def test_miss_required_question(self):
        qData = self._loadFixture('test_survey.json')

        # Instantiate the questionnaire manager... There is no resume data
        qManager = QuestionnaireManager(qData, {})
        qManager.start_questionnaire()

        q = qManager.get_current_question()

        assert isinstance(q, InputTextQuestion) == True
        assert q.question_text == "How many marbles do you have"

        qManager.update({'q1':'Lots'})

        result = qManager.get_current_question().validate()

        assert len(result) == 1
        assert result[0].is_valid() == True

        qManager.update({'q1':'    '})

        result = qManager.get_current_question().validate()

        assert len(result) == 1
        assert result[0].is_valid() == False

        assert 'This field is required' in result[0].errors


    def test_next_question(self):
        qData = self._loadFixture('test_survey.json')

        qManager = QuestionnaireManager(qData, {})
        qManager.start_questionnaire()

        q = qManager.get_current_question()

        assert isinstance(q, InputTextQuestion) == True
        assert q.question_text == "How many marbles do you have"

        response = {'q1':'35'}
        qManager.update(response)

        result = q.validate()
        assert result[0].is_valid() == True

        q = qManager.get_next_question()

        assert isinstance(q, TextBlock) == True

        result = q.validate()
        assert result[0].is_valid() == True
        assert len(result[0].errors) == 0

        q = qManager.get_next_question()

        assert isinstance(q, MultipleChoiceQuestion)
        assert q.question_text == 'Which colour marble would you prefer?'

        qManager.update({'EQ_q3':' '})
        result =  q.validate()
        assert result[0].is_valid() == False

        qManager.update({'EQ_q3':'Purple'})
        result = q.validate()
        assert result[0].is_valid() == False

        qManager.update({'EQ_q3':'Blue'})
        result = q.validate()
        assert result[0].is_valid() == True

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
            'EQ_start_q1': '6',          # Numeric required field
            'EQ_start_q2': None,         # Rich text text, no response required
            'EQ_start_q3': 'option1',    # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',   # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None,         # Optional numeric
            'EQ_start_q7': '15/07/2015'  # Required date
        }

        qManager.update(responses)

        result = qManager.validate()

        assert result[0].is_valid() == True

    def test_group_fail_validation(self):
        qData = self._loadFixture('groups.json')
        resumeData = {}

        qManager = QuestionnaireManager(qData, resumeData)
        qManager.start_questionnaire()

        q1 = qManager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'EQ_start_q1': '',           # Numeric required field
            'EQ_start_q2': None,         # Rich text text, no response required
            'EQ_start_q3': 'option6',    # Multi-choice, there is no option6
            'EQ_start_q4': [''],         # Checkbox requires selection
            'EQ_start_q5': ' ',          # required free text field
            'EQ_start_q6': '',            # numeric free text field
            'EQ_start_q7': '12/27/2016'  # invalid date
        }

        qManager.update(responses)

        result = q1.validate()

        assert len(result) == 1
        assert result[0].is_valid() == False

        errors = result[0].errors

        assert 'EQ_start_q3:0' in errors
        assert 'EQ_start_q4:0' in errors
        assert 'EQ_start_q5:0' in errors

        EQ_start_q1 = qManager.get_question_by_reference('EQ_start_q1').validate()

        assert 'This field is required' in EQ_start_q1[0].errors

        EQ_start_q3 = qManager.get_question_by_reference('EQ_start_q3').validate()

        assert 'Invalid option' in EQ_start_q3[0].errors

        EQ_start_q4 = qManager.get_question_by_reference('EQ_start_q4').validate()

        assert 'This field is required' in EQ_start_q4[0].errors

        EQ_start_q5 = qManager.get_question_by_reference('EQ_start_q5').validate()

        assert 'This field is required' in EQ_start_q5[0].errors

        EQ_start_q7 = qManager.get_question_by_reference('EQ_start_q7').validate()

        assert 'This field must be a date' in EQ_start_q7[0].errors

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

        result = qManager.validate()

        assert result[0].is_valid() == False

        assert 'EQ_start_q5:0' in result[0].errors

        EQ_start_q5 = qManager.get_question_by_reference('EQ_start_q5').validate()

        assert 'This field is to big' in EQ_start_q5[0].errors

    def test_validate_fail_lessthan(self):
        qData = self._loadFixture('groups.json')
        resumeData = {}

        qManager = QuestionnaireManager(qData, resumeData)
        qManager.start_questionnaire()

        q1 = qManager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'EQ_start_q1': '0',         # Numeric required field
            'EQ_start_q2': None,         # Rich text text, no response required
            'EQ_start_q3': 'option1',    # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',   # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None          # Optional numeric
        }

        qManager.update(responses)

        results = qManager.validate()

        assert results[0].is_valid() == False
        assert 'EQ_start_q1:0' in results[0].errors

        EQ_start_q1 = qManager.get_question_by_reference('EQ_start_q1').validate()

        assert 'This field should be greater than 0' in EQ_start_q1[0].errors

    def test_validate_fail_greaterthan(self):
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

        results = qManager.validate()

        assert results[0].is_valid() ==False
        assert 'EQ_start_q1:0' in results[0].errors

        EQ_start_q1 = qManager.get_question_by_reference('EQ_start_q1').validate()

        assert 'This field should be less than 11' in EQ_start_q1[0].errors

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

        results = qManager.validate()

        assert results[0].is_valid() ==False
        assert 'EQ_start_q1:0' in results[0].errors

        EQ_start_q1 = qManager.get_question_by_reference('EQ_start_q1').validate()

        assert 'should not be 5' in EQ_start_q1[0].errors

    def test_validate_fail_notequal(self):
        qData = self._loadFixture('groups.json')
        resumeData = {}

        qManager = QuestionnaireManager(qData, resumeData)
        qManager.start_questionnaire()

        q1 = qManager.get_current_question()

        assert isinstance(q1, QuestionGroup) == True

        responses = {
            'EQ_start_q1': '7',          # Numeric required field
            'EQ_start_q2': None,         # Rich text text, no response required
            'EQ_start_q3': 'option1',    # Multi-choice, option 1
            'EQ_start_q4': 'Coption1',   # Checkbox, selected
            'EQ_start_q5': 'Some Text',  # required free text field
            'EQ_start_q6': None          # Optional numeric
        }

        qManager.update(responses)

        results = qManager.validate()

        assert results[0].is_valid() ==False
        assert 'EQ_start_q1:0' in results[0].errors

        EQ_start_q1 = qManager.get_question_by_reference('EQ_start_q1').validate()
        assert 'should be 6' in EQ_start_q1[0].errors

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

        results = qManager.validate()

        assert results[0].is_valid() == False

        assert 'This field is long, are you sure?' in results[0].warnings

        responses = {
            'q1': 'Lots and lots and lots',
            'warning_EQ_q1' : 'true',
            'justification_EQ_q1' : 'I have lots'
        }

        qManager.update(responses)

        results = qManager.validate()

        assert results[0].is_valid() == True

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

        responses = {
            'EQ_s1_q1':'',
            'EQ_s1_q2':''
        }

        qManager.update(responses)

        # no responses should fail validation

        results = qManager.validate()

        assert q1.get_repetition() == 0
        assert results[q1.get_repetition()].is_valid() == False


        # answer the question for the first repetition
        responses = {
            'repetition_EQ_s1' : 0,
            'EQ_s1_q1' : 'David',
            'EQ_s1_q2' : '39'
        }

        qManager.update(responses)

        assert q1.get_repetition() == 0

        stored = qManager.get_questionnaire_state()

        assert 'current_question' in stored
        assert stored['current_question'] == 'EQ_s1'
        assert 'current_repetition' in stored
        assert stored['current_repetition'] == 0

        assert len(stored['user_data']) == 2
        assert 'EQ_s1_q1' in stored['user_data'].keys()
        assert isinstance(stored['user_data']['EQ_s1_q1']['answer'], list)
        assert 'David' == stored['user_data']['EQ_s1_q1']['answer'][0]
        assert isinstance(stored['user_data']['EQ_s1_q2']['answer'], list)
        assert '39' == stored['user_data']['EQ_s1_q2']['answer'][0]

        # check validation passes
        results = qManager.validate()
        assert q1.get_repetition() == 0
        assert results[q1.get_repetition()].is_valid() == True


        # call next question (there is only one, but it reepeats)
        qManager.get_next_question()
        assert q1.get_repetition() == 1

        # check we have not completed the questionnaire
        assert qManager.completed == False

        stored = qManager.get_questionnaire_state()

        assert 'current_question' in stored
        assert stored['current_question'] == 'EQ_s1'
        assert 'current_repetition' in stored
        assert stored['current_repetition'] == 1

        # get the current question
        q2 = qManager.get_current_question()
        assert q2._reference == q1._reference
        assert q2.get_repetition() == 1

        responses = {
            'repetition_EQ_s1': 1,
            'EQ_s1_q1' : '',
            'EQ_s1_q2' : ''
        }

        qManager.update(responses)

        # check validation fails until we answer the second repetition
        results = qManager.validate()
        assert results[q2.get_repetition()].is_valid() == False

        responses = {
            'repetition_EQ_s1': 1,
            'EQ_s1_q1' : 'Lewis',
            'EQ_s1_q2' : 'Ten'
        }

        qManager.update(responses)

        stored = qManager.get_questionnaire_state()

        assert len(stored['user_data']) == 2
        assert 'EQ_s1_q1' in stored['user_data'].keys()
        assert isinstance(stored['user_data']['EQ_s1_q1']['answer'], list)
        assert len(stored['user_data']['EQ_s1_q1']['answer']) == 2
        assert 'David' == stored['user_data']['EQ_s1_q1']['answer'][0]
        assert 'Lewis' == stored['user_data']['EQ_s1_q1']['answer'][1]
        assert isinstance(stored['user_data']['EQ_s1_q2']['answer'], list)
        assert len(stored['user_data']['EQ_s1_q2']['answer']) == 2
        assert '39' == stored['user_data']['EQ_s1_q2']['answer'][0]
        assert 'Ten' == stored['user_data']['EQ_s1_q2']['answer'][1]

        # check validation passes with second response
        results = qManager.validate()

        assert results[0].is_valid() == True
        assert results[1].is_valid() == False

        assert 'EQ_s1_q2:1' in results[1].errors

        EQ_s1_q2 = qManager.get_question_by_reference('EQ_s1_q2').validate()

        assert EQ_s1_q2[0].is_valid() == True
        assert EQ_s1_q2[1].is_valid() == False

        assert 'This field is numeric' in EQ_s1_q2[1].errors

        responses = {
            'repetition_EQ_s1': 1,
            'EQ_s1_q1' : 'Lewis',
            'EQ_s1_q2' : '10'
        }

        qManager.update(responses)

        stored = qManager.get_questionnaire_state()

        assert '10' == stored['user_data']['EQ_s1_q2']['answer'][1]

        results = qManager.validate()

        assert results[0].is_valid() == True
        assert results[1].is_valid() == True


if __name__ == '__main__':
    unittest.main()
