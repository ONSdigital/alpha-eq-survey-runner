import json
from collections import OrderedDict

from branching.skip import SkipCondition
from questions.question import Question


class QuestionnaireManager(object):

    def __init__(self, questionnaire_schema, questionnaire_state):
        self.questionnaire_id = None
        self.survey_id = None
        self.title = None
        self.question_index = 0
        self.started = False
        self.completed = False
        self.questions = []
        self.responses = {}
        self.history = []
        self.warnings_accepted = []
        self.justifications = {}
        self.current_question = None
        self._load_questionnaire_data(json.loads(questionnaire_schema))
        self._ensure_valid_routing()
        if questionnaire_state:
            self._load_questionnaire_state(questionnaire_state)

    def _load_questionnaire_data(self, questionnaire_data):
        self.survey_id = questionnaire_data['survey_id']
        self.questionnaire_id = questionnaire_data['questionnaire_id']
        self.title = questionnaire_data['title']
        self.overview = questionnaire_data['overview']
        for index, schema in enumerate(questionnaire_data['questions']):
            question = Question.factory(schema)

            # TODO: Remove this as it breaks encapsulation.  References should be set in the schema instead
            # all questions need references - should really be set by the author
            # but if not lets set them
            if not question._reference:
                question._reference = 'q' + str(index)
                
            self._add_question(question)

    def _ensure_valid_routing(self):
        for question_index, question in enumerate(self.questions):
            if question.has_branch_conditions():
                target_questions = {}
                for condition in question.get_branch_conditions():
                    # evaluate the condition
                    target_questions[self.get_question_by_reference(condition.target)] = SkipCondition(condition.trigger, condition.state)

                for candidate_index in range(question_index + 1, len(self.questions)):
                    for target_question in target_questions.keys():
                        candidate_question = self.questions[candidate_index]

                        if candidate_question.get_reference() != target_question.get_reference():
                            candidate_question.skip_conditions.append(target_questions[target_question])

    def _load_questionnaire_state(self, questionnaire_state):

        self.started = questionnaire_state['started']
        self.completed = questionnaire_state['completed']
        self.question_index = questionnaire_state['index']
        self.responses = questionnaire_state['responses']
        self.history = questionnaire_state['history']
        self.warnings_accepted = questionnaire_state['warningsAccepted']
        self.justifications= questionnaire_state['justifications']

        # validate any previous data
        if len(self.questions) != 0:
            for index in range(0, self.question_index + 1):
                question = self.questions[index]
                if self._exists_in_history(question.get_reference()):
                    question.is_valid_response(self.responses, self.warnings_accepted)

            # evaluate skip conditions and skip matching questions
            for question in self.questions:
                if question.has_skip_conditions():
                    conditions = question.get_skip_conditions()
                    for condition in conditions:
                        if self.condition_met(condition):
                            question.skipping = True

            self.current_question = self.questions[self.question_index]

    def _add_question(self, question):
        self.questions.append(question)

    def get_current_question_index(self):
        current_position = 1
        for index, question in enumerate(self.questions):
            if index < self.question_index and not question.skipping:
                current_position += 1
        return current_position

    def get_total_questions(self):
        total = 0
        for question in self.questions:
            if not question.skipping:
                total += 1
        return total

    def get_responses(self, *args):
        if len(args) == 1 and args[0] in self.responses.keys():
            return self.responses[args[0]]
        else:
            return self.responses

    def get_justifications(self, *args):
        if len(args) == 1 and args[0] in self.justifications.keys():
            return self.justifications[args[0]]
        else:
            return self.justifications

    def get_warnings_accepted(self, *args):
        return self.warnings_accepted

    def start_questionnaire(self):
        self.started = True
        self.question_index = 0
        if len(self.questions) != 0:
            self.current_question = self.questions[self.question_index]

    def get_questionnaire_state(self):
        return {
            'started': self.started,
            'completed': self.completed,
            'index': self.question_index,
            'responses': self.responses,
            'history': self.history,
            'warningsAccepted': self.warnings_accepted,
            'justifications': self.justifications
        }

    def get_submitted_data(self):
        if self.completed:
            return {
                'surveyId': self.survey_id,
                'questionnaireId': self.questionnaire_id,
                'responses': self.responses,
                'warningsAccepted': self.warnings_accepted,
                'justifications': self.justifications
            }
        else:
            return {}

    def store_response(self, response):
        for ref in response.keys():
            self.responses[ref] = response[ref]
        self._store_in_history(response)

    def store_warnings(self, warnings_accepted):

        for warning in warnings_accepted:
            if warning not in self.warnings_accepted or '':
                self.warnings_accepted.append(warning)

    def store_justifications(self, justifications):
        for ref in justifications.keys():
            self.justifications[ref] = justifications[ref]

    def _store_in_history(self, response):
        if self.current_question:
            if not self._exists_in_history(self.current_question.get_reference()):
                history = {}
                self.history.append(history)
            else:
                history = self._find_history(self.current_question.get_reference())

            history['reference'] = self.current_question.get_reference()
            history['valid'] = self.current_question.is_valid_response(response, self.warnings_accepted)

    def _exists_in_history(self, reference):
        for history in self.history:
            if history['reference'] == reference:
                return True
        return False

    def _find_history(self, reference):
        for history in self.history:
            if history['reference'] == reference:
                return history
        return None

    def is_valid_response(self, user_answer, warnings_accepted):
        if self.current_question:
            return self.current_question.is_valid_response(user_answer, warnings_accepted)
        return True

    def get_question_warnings(self, reference=None):
        if reference is None and self.current_question:
            return self.current_question.get_warnings()
        elif reference in self.responses.keys():
            return self.get_question_by_reference(reference).get_warnings()
        else:
            return []

    def get_question_errors(self, reference=None):
        if reference is None and self.current_question:
            return self.current_question.get_errors()
        elif reference in self.responses.keys():
            return self.get_question_by_reference(reference).get_errors()
        else:
            return []

    def get_current_question(self):
        if not self.completed:
            return self.current_question
        else:
            return None

    def get_next_question(self, response):
        if response and self.current_question.branches(response):
            target_question = self.current_question.get_branch_target(response)
            self.branch_to_question(target_question)
            return self.current_question

        if self.question_index + 1 < len(self.questions):
            self.question_index += 1
            self.current_question = self.questions[self.question_index]
            return self.current_question
        else:
            self.current_question = None
            self.completed = True
            return None

    def jump_to_question(self, questionnaire_location):
        # can only jump to a previously seen question
        if self.completed:
            self.completed = False

        for key in self.responses.keys():
            if key.startswith(questionnaire_location):
                index = 0
                for question in self.questions:
                    if question.get_reference() == questionnaire_location:
                        self.question_index = index
                        self.current_question = self.questions[self.question_index]
                    index += 1

    def branch_to_question(self, questionnaire_location):
        index = 0
        for question in self.questions:
            if question.get_reference() == questionnaire_location:
                self.question_index = index
                self.current_question = self.questions[self.question_index]
            index += 1

    def get_question_by_reference(self, reference):
        if reference.startswith("EQ_"):
            reference = reference.replace("EQ_", "")

        address_parts = reference.split('_')
        if len(address_parts) == 1:
            for question in self.questions:
                if question._reference == reference:
                    return question
        else:
            this_level = address_parts.pop(0)
            for question in self.questions:
                if question._reference == this_level:
                    return question.get_question_by_reference('_'.join(address_parts))

    def complete_questionnaire(self):
        self.completed = True

    def get_history(self):
        # load the question objects
        history_with_question_objects = OrderedDict()
        for history in self.history:
            question = self.get_question_by_reference(history['reference'])

            history_with_question_objects[question] = history['valid']

        return history_with_question_objects

    def condition_met(self, condition):
        return condition.state == self.get_response_by_reference(condition.trigger)

    def get_response_by_reference(self, reference):
        if reference in self.responses:
            return self.responses[reference]
        return None
