from questions import Question, QuestionGroup
import json
from branching import SkipCondition
from collections import OrderedDict

class QuestionnaireManager:
    def __init__(self, questionnaire_schema, questionnaire_state):
        self.questionnaire_id = None
        self.survey_id = None
        self.title = None
        self.question_index = 0
        self.started = False
        self.completed = False
        self.questions = []
        self.history = []
        self.warningsAccepted = []
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
        self.user_data = questionnaire_state['user_data']
        self.history = self._load_history(questionnaire_state['history'])

        # validate any previous data
        if len(self.questions) != 0:
            # for index in range(0, self.question_index + 1):
            #     question = self.questions[index]
            #     if self._exists_in_history(question.get_reference()):
            #         question.is_valid_response(self.responses, self.warningsAccepted)

            for question in self.questions:
                # evaluate skip conditions and skip matching questions
                if question.has_skip_conditions():
                    conditions = question.get_skip_conditions()
                    for condition in conditions:
                        if self.condition_met(condition):
                            question.skipping = True


            for reference in self.user_data.keys():
                question = self.get_question_by_reference(reference)
                question.set_user_data(self.user_data[reference])

            if 'current_question' in questionnaire_state.keys():
                self.current_question = self.get_question_by_reference(questionnaire_state['current_question'])
                self.question_index = self._current_question_index()
            else:
                self.question_index = 0
                self.current_question = self.questions[0]

            if 'current_repetition' in questionnaire_state.keys():
                self.current_question.set_repetition(questionnaire_state['current_repetition'])


    def _build_user_data(self):
        user_data = {}
        for question in self.questions:
            if isinstance(question, QuestionGroup):
                question_data = question.get_user_data()
                for child in question_data.keys():
                    user_data[child] = question_data[child]
            else:
                user_data[question.get_reference()] = question.get_user_data()

        return user_data

    def _load_history(self, state):
        history = []
        for entry in state:
            history.append(entry)

        return history

    def _add_question(self, question):
        self.questions.append(question)

    def get_current_question_number(self):
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

    def _current_question_index(self):
        for index, question in enumerate(self.questions):
            if question.get_reference() == self.current_question.get_reference():
                return index

        return 0

    def get_responses(self, *args):
        pass

    def get_justifications(self, *args):
        if len(args) == 1 and args[0] in self.justifications.keys():
            return self.justifications[args[0]]
        else:
            return self.justifications

    def get_warningsAccepted(self, *args):
        return self.warningsAccepted

    def start_questionnaire(self):
        self.started = True
        self.question_index = 0
        if len(self.questions) != 0:
            self.current_question = self.questions[self.question_index]

    def get_questionnaire_state(self):
        state = {
            'started': self.started,
            'completed': self.completed,
            'history': self.history,
            'user_data' : self._build_user_data()
        }

        if self.current_question:
            state['current_question'] = self.current_question.get_reference()
            state['current_repetition'] = self.current_question.get_repetition()

        return state

    def get_submitted_data(self):
        if self.completed:
            return {
                'surveyId': self.survey_id,
                'questionnaireId': self.questionnaire_id,
                'user_data': self._build_user_data()
            }
        else:
            return {}

    def store_response(self, response):
        if 'repetition' in response:
            index = int(response['repetition'])
            for ref in response.keys():
                if ref is not 'repetition':
                    if ref not in self.responses:
                        self.responses[ref] = []

                    while len(self.responses[ref]) <= index:
                        self.responses[ref].append('')

                    self.responses[ref][index] = response[ref]
        else:
            for ref in response.keys():
                self.responses[ref] = response[ref]

        self._store_in_history(response)

    def _store_in_history(self):
        self.history.append(self.current_question.get_reference() + ':' + str(self.current_question.get_repetition()))
        # make unique
        self.history = list(set(self.history))

    def _exists_in_history(self, reference):
        for history in self.history:
            if history == reference:
                return True
        return False

    def validate(self):
        if self.current_question:
            return self.current_question.validate()
        return None

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

    def get_next_question(self):
        self._store_in_history()

        if self.current_question.should_repeat():
            self.current_question._repetition += 1
            return self.current_question

        if self.current_question.branches():
            target_question = self.current_question.get_branch_target()
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

        if not ':' in questionnaire_location:
            questionnaire_location += ':0'  # jump to repetition 0 unless specified otherwise

        if self._exists_in_history(questionnaire_location):
            self._store_in_history()
            self.current_question = self.get_question_by_reference(questionnaire_location)
            self.question_index = self._current_question_index()


    def branch_to_question(self, questionnaire_location):
        index = 0
        for question in self.questions:
            if question.get_reference() == questionnaire_location:
                self.question_index = index
                self.current_question = self.questions[self.question_index]
            index += 1

    # will use in template
    def get_question_by_reference(self, reference):
        repetition = 0
        if ':' in reference:
            repetition = int(reference[reference.index(':') + 1:])
            reference = reference[:reference.index(':')]

        if reference.startswith("EQ_"):
            reference = reference.replace("EQ_", "")

        address_parts = reference.split('_')
        if len(address_parts) == 1:
            for question in self.questions:
                if question._reference == reference:
                    # don't use the setter here as children might not have been initialised
                    question._repetition = repetition
                    return question
        else:
            this_level = address_parts.pop(0)
            for question in self.questions:
                if question._reference == this_level:
                    # don't use the setter here as children might not have been initialised
                    question._repetition = repetition
                    return question.get_question_by_reference('_'.join(address_parts))

    def complete_questionnaire(self):
        self.completed = True

    def get_history(self):
        # load the question objects
        history_with_question_objects = OrderedDict()
        # for reference in self.history:
        #     question = self.get_question_by_reference(reference)
        #
        #     if not question.skipping:
        #         history_with_question_objects[question] = question.validate()

        return history_with_question_objects

    def condition_met(self, condition):
       return condition.state == self.get_response_by_reference(condition.trigger)

    def get_response_by_reference(self, reference):
        question = self.get_question_by_reference(reference)

        if question:
            return question.get_answer()

        return None

    def update(self, responses):
        repetition = 0
        for reference in responses.keys():
            if reference.startswith('repetition_'):
                repetition = int(responses[reference])
                question = self.get_question_by_reference(reference.replace('repetition_', ''))
                question.set_repetition(repetition)

        for reference in responses.keys():
            if reference.startswith('justification_'):
                question = self.get_question_by_reference(reference.replace('justification_', ''))
                question.set_repetition(repetition)
                question.set_justification(responses[reference])

            elif reference.startswith('warning_'):
                question = self.get_question_by_reference(reference.replace('warning_', ''))
                question.set_repetition(repetition)
                question.set_accepted(True)

            elif not reference.startswith('repetition_'):
                question = self.get_question_by_reference(reference)
                if question.is_repeating():
                    question.set_repetition(repetition)
                if question.parent and  question.parent.is_repeating():
                    question.parent.set_repetition(repetition)

                question.update(responses[reference])

        # store current question in history
        self._store_in_history()
