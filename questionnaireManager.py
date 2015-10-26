from questions import Question
import json
import pprint

class QuestionnaireManager:
    def __init__(self, questionnaire_json, resume_data):
        self.title = None
        self.question_index = 0
        self.started = False
        self.completed = False
        self.questions = []

        self.questionnaire_json = json.loads(questionnaire_json)
        self.resume_data = resume_data
        self._load_questionnaire_data(self.questionnaire_json)

    def _load_questionnaire_data(self, question_data):

        self.title = question_data['title']
        self.overview = question_data['overview']

        for schema in question_data['questions']:
            self._add_question(
                Question.factory(schema)
            )

    def _add_question(self, question):
        self.questions.append(question)

    def start_questionnaire(self):
        self.started = True
        self.question_index = 0;
        self.current_question = self.questions[self.question_index];

    def is_valid_response(self, request):
        return self.current_question.is_valid_response(request)

    def get_question_warnings(self, request):
        return self.current_question.get_warnings(request)

    def get_question_errors(self, request):
        return self.current_question.get_errors(request)

    def get_current_question(self):
        return self.current_question

    def get_next_question(self):
        if self.question_index + 1 <= len(self.questions):
            self.question_index += 1
            self.current_question = self.questions[self.question_index]
            return self.current_question

        return None

    def jump_to_question(self):
        # can only jump to a previously seen question
        return None

    def complete_questionnaire(self):
        self.completed = True

    def get_question_by_reference(self, reference):
        return None
