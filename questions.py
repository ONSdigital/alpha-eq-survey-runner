import importlib

class Question(object):
    def __init__(self, question_schema):
        self._schema = question_schema
        self.type = question_schema['questionType']
        self.question_text = question_schema['questionText']
        self.reference = question_schema['questionReference']
        self.display_properties = None
        self.validation = self._build_validation(question_schema['validation'])
        self.parts = self._build_parts(question_schema['parts'])
        self.children = None
        self.display_conditions = None
        self.skip_conditions = None
        self.branch_conditions = None
        self.warnings = []
        self.errors = []

    @staticmethod
    def factory(schema):
        if schema['questionType'] == 'InputText': return InputTextQuestion(schema)
        if schema['questionType'] == 'TextBlock': return TextBlock(schema)
        if schema['questionType'] == 'MultipleChoice': return MultipleChoiceQuestion(schema)

    def _build_validation(self, validation_schema):
        rules = []
        for validation in validation_schema.keys():
            # find the validaton class and instantiate it
            RuleClass = getattr(importlib.import_module('validators'), validation.capitalize())
            rule = RuleClass(validation_schema[validation])

            rules.append(rule)

        return rules

    def _build_parts(self, schema):
        parts = []
        for part in schema:
            parts.append(part['value'])

        return parts

    def is_valid_response(self, response):
        self.errors = []
        for rule in self.validation:
            if not rule.is_valid(response):
                self.errors.append(rule.get_error(response))

        return len(self.errors) == 0

    def get_warnings(self):
        return None

    def get_errors(self):
        return self.errors or None


class MultipleChoiceQuestion(Question):
    def __init__(self, question_schema):
        super(MultipleChoiceQuestion, self).__init__(question_schema)

    def is_valid_response(self, response):
        valid = super(MultipleChoiceQuestion, self).is_valid_response(response)

        if response is not None and not response.isspace():
            for part in self.parts:
                if part == response:
                    return True

            return False

        return valid

class InputTextQuestion(Question):
    def __init__(self, question_schema):
        super(InputTextQuestion, self).__init__(question_schema)


class TextBlock(Question):
    def __init__(self, question_schema):
        super(TextBlock, self).__init__(question_schema)

    def is_valid_response(self, request):
        return True

    def get_warnings(self):
        return None

    def get_warnings(self):
        return None
