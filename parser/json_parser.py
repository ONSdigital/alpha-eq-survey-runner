import json
from question_factory import question_factory
from validation_factory import validation_factory
from questionnaire.questionnaire import Questionnaire
from questions.questiongroup import QuestionGroup
from branching.skip import SkipCondition
from branching.jump_to import JumpTo


class JsonParser:
    def __init__(self, questionnaire_schema):
        self.schema = json.loads(questionnaire_schema)
        self.questionnaire = self._create_questionnaire()
        self.add_questions(self.schema)

    def _create_questionnaire(self):
        questionnaire = Questionnaire()
        questionnaire.questionnaire_id = self._get_value('questionnaire_id')
        questionnaire.survey_id = self._get_value('survey_id')
        questionnaire.overview = self._get_value('overview')
        questionnaire.title = self._get_value('title')
        questionnaire.questionnaire_title = self._get_value('questionnaire_title')
        return questionnaire

    def add_questions(self, schema):
        for index, question_schema in enumerate(schema['questions']):

            question = question_factory.create_question(question_schema)
            # TODO: Remove this as it breaks encapsulation.  References should be set in the schema instead
            # all questions need references - should really be set by the author but if not lets set them
            if not question._reference:
                question._reference = 'q' + str(index)

            self.add_validation(question, question_schema)
            self.questionnaire.add_question(question)
            self.build_parts(question, question_schema)
            self.build_branch_conditions(question, question_schema)

            if isinstance(question, QuestionGroup):
                for child_index, child_schema in enumerate(question_schema['children']):
                    child_question = question_factory.create_question(child_schema)
                    if not child_question._reference:
                        question._reference = 'q' + str(index)

                    question.add_child(child_question)
                    self.add_validation(child_question, child_schema)
                    self.build_parts(child_question, child_schema)
                    self.build_branch_conditions(child_question, child_schema)

    def add_validation(self, question, question_schema):
        for validation in question_schema['validation']:
            rule = validation_factory.get_validation_rule(validation)
            question.add_validation_rule(rule)

    def build_parts(self, question, question_schema):
        for part in question_schema['parts']:
            question.add_part(part['value'])

    def build_branch_conditions(self, question, question_schema):
        for condition in question_schema['branchConditions']:
             if condition['jumpTo'] and condition['jumpTo']['condition']['value']['is']:
                jump_to = JumpTo(condition['jumpTo']['question'], question.get_reference(), condition['jumpTo']['condition']['value']['is'])
                question.add_branch_condition(jump_to)

    def _get_value(self, name):
        value = None
        if self.schema[name]:
            value = self.schema[name]
        return value

