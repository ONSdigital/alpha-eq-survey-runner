import json
from question_factory import factory
from schema.questionnaire import Questionnaire
from schema.questiongroup import QuestionGroup


class JsonParser:
    def __init__(self, questionnaire_schema):
        self.schema = json.loads(questionnaire_schema)
        self.questionnaire = self._create_questionnaire()
        self.add_questions()

    def _create_questionnaire(self):
        questionnaire = Questionnaire()
        questionnaire.questionnaire_id = self._get_value('questionnaire_id')
        questionnaire.survey_id = self._get_value('survey_id')
        questionnaire.overview = self._get_value('overview')
        questionnaire.title = self._get_value('title')
        questionnaire.questionnaire_title = self._get_value('questionnaire_title')
        return questionnaire

    def add_questions(self):
        for question_schema in self.schema['questions']:
            question = factory.create_question(question_schema)
            self.questionnaire.add_question(question)

            if isinstance(question, QuestionGroup):
                for child_schema in question_schema['children']:
                    child_question = factory.create_question(child_schema)
                    question.add_child(child_question)

    def add_validation(self, question, question_schema):
        pass

    def _get_value(self, name):
        value = None
        if self.schema[name]:
            value = self.schema[name]
        return value

