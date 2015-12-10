from questions.question import Question
import importlib


class QuestionFactory:

    @staticmethod
    def create_question(question_schema):
        question_type = QuestionFactory._get_value(question_schema, 'questionType')
        question_text = QuestionFactory._get_value(question_schema, 'questionText')
        question_reference = QuestionFactory._get_value(question_schema, 'questionReference')

        if question_schema['questionType']:
            question_class = getattr(importlib.import_module('schema.'+question_type.lower()), question_type)
            question = question_class(question_reference, question_type, question_text)
            return question
        else:
            return Question(question_reference, question_type, question_text)

    @staticmethod
    def _get_value(schema, name):
        value = None
        if schema[name]:
            value = schema[name]
        return value
