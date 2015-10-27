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
        self._load_questionnaire_data(self.questionnaire_json)
        self._load_resume_data(resume_data)

    def _load_questionnaire_data(self, question_data):

        self.title = question_data['title']
        self.overview = question_data['overview']

        for schema in question_data['questions']:
            self._add_question(
                Question.factory(schema)
            )

    def _load_resume_data(self, resume_data):
        if resume_data is None:
            self.resume_data = {}

        else:
            self.resume_data = resume_data
            if '_last' in resume_data.keys():
                if resume_data['_last'] == 'completed':
                    self.completed = True
                    self.current_question = None
                else:
                    self.jump_to_question(resume_data['_last'])
                    self.get_next_question()

    def _add_question(self, question):
        self.questions.append(question)

    def start_questionnaire(self):
        self.started = True
        self.question_index = 0
        self.current_question = self.questions[self.question_index]

    def resume_questionnaire(self, resume_data):
        self.started = True
        self.question_index = 0
        self.current_question = self.questions[self.question_index]
        self._load_resume_data(resume_data)

    def get_resume_data(self):
        return self.resume_data

    def is_valid_response(self, request):
        if self.current_question is not None:
            valid = self.current_question.is_valid_response(request)
            if valid:
                value = request
                if value is None: value = ''
                self.resume_data[self.current_question.reference] = request
                self.resume_data['_last'] = self.current_question.reference

            return valid

        return True

    def get_question_warnings(self):
        if self.current_question:
            return self.current_question.get_warnings()
        else:
            return []

    def get_question_errors(self):
        if self.current_question:
            return self.current_question.get_errors()
        else:
            return []

    def get_current_question(self):
        return self.current_question

    def get_next_question(self):
        if self.question_index + 1 <= len(self.questions) - 1:
            self.question_index += 1
            self.current_question = self.questions[self.question_index]
            return self.current_question
        else:
            self.current_question = None
            self.completed = True
            self.resume_data['_last'] = 'completed'
            return None

    def jump_to_question(self, reference):
        # can only jump to a previously seen question
        if reference in self.resume_data.keys():
            index = 0
            for question in self.questions:
                if question.reference == reference:
                    self.question_index = index
                    self.current_question = self.questions[self.question_index]
                index += 1


    def complete_questionnaire(self):
        self.completed = True

    def get_question_by_reference(self, reference):
        return None
