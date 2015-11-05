from questions import Question
import json


class QuestionnaireManager:
    def __init__(self, questionnaire_schema, questionnaire_state):
        self.title = None
        self.question_index = 0
        self.started = False
        self.completed = False
        self.questions = []
        self.responses = {}
        self.current_question = None
        self._load_questionnaire_data(json.loads(questionnaire_schema))
        if questionnaire_state:
            self._load_questionnaire_state(questionnaire_state)

    def _load_questionnaire_data(self, questionnaire_data):

        self.title = questionnaire_data['title']
        self.overview = questionnaire_data['overview']
        for index, schema in enumerate(questionnaire_data['questions']):
            question = Question.factory(schema)
            # all questions need references - should really be set by the author
            # but if not lets set them
            if not question.reference:
                question.reference = 'q' + str(index)
                
            self._add_question(question)

    def _load_questionnaire_state(self, questionnaire_state):
        self.started = questionnaire_state['started']
        self.completed = questionnaire_state['completed']
        self.question_index = questionnaire_state['index']
        self.responses = questionnaire_state['responses']

        # validate any previous data
        for index in range(0, self.question_index + 1):
            question = self.questions[index]
            if question.reference in self.responses:
                question.is_valid_response(self.responses[question.reference])

        self.current_question = self.questions[self.question_index]

    def _add_question(self, question):
        self.questions.append(question)

    def get_current_question_index(self):
        return self.question_index + 1

    def get_total_questions(self):
        return len(self.questions)

    def get_responses(self, *args):
        if len(args) == 1 and args[0] in self.responses.keys():
            return self.responses[args[0]]
        else:
            return self.responses

    def start_questionnaire(self):
        self.started = True
        self.question_index = 0
        self.current_question = self.questions[self.question_index]

    def get_questionnaire_state(self):
        return {
            'started': self.started,
            'completed': self.completed,
            'index': self.question_index,
            'responses': self.responses
        }

    def store_response(self, response):
        self.responses[self.current_question.reference] = response

    def is_valid_response(self, user_answer):
        if self.current_question:
            return self.current_question.is_valid_response(user_answer)
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
        if questionnaire_location in self.responses.keys():
            index = 0
            for question in self.questions:
                if question.reference == questionnaire_location:
                    self.question_index = index
                    self.current_question = self.questions[self.question_index]
                index += 1

    def branch_to_question(self, questionnaire_location):
        index = 0
        for question in self.questions:
            if question.reference == questionnaire_location:
                self.question_index = index
                self.current_question = self.questions[self.question_index]
            index += 1

    # will use in template
    def get_question_by_reference(self, reference):
        for question in self.questions:
            if question.reference == reference:
                return question

        return None

    def complete_questionnaire(self):
        self.completed = True
