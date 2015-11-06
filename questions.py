import importlib
from branching import JumpTo


class Question(object):
    def __init__(self, question_schema, parent=None):
        self.parent = parent
        self._schema = question_schema
        self.type = question_schema['questionType']
        self.question_text = question_schema['questionText']
        self.question_help = question_schema['questionHelp']
        self.reference = question_schema['questionReference']
        self.display_properties = None
        self.validation = self._build_validation(question_schema['validation'])
        self.parts = self._build_parts(question_schema['parts'])
        self.children = None
        self.display_conditions = None
        self.skip_conditions = []
        self.branch_conditions = self._build_branch_conditions(question_schema['branchConditions'])
        self.warnings = []
        self.errors = []

    @staticmethod
    def factory(schema, parent=None):
        if schema['questionType'] == 'InputText': return InputTextQuestion(schema, parent)
        if schema['questionType'] == 'TextBlock': return TextBlock(schema, parent)
        if schema['questionType'] == 'MultipleChoice': return MultipleChoiceQuestion(schema, parent)
        if schema['questionType'] == 'QuestionGroup': return QuestionGroup(schema, parent)
        if schema['questionType'] == 'CheckBox': return CheckBoxQuestion(schema, parent)

    def _build_validation(self, validation_schema):
        rules = []
        for validation in validation_schema.keys():
            # find the validaton class and instantiate it
            RuleClass = getattr(importlib.import_module('validators'), validation.capitalize())
            # this loads the class from the validators.py file
            rule = RuleClass(validation_schema[validation])
            rules.append(rule)

        return rules

    def _build_parts(self, schema):
        parts = []
        for part in schema:
            parts.append(part['value'])

        return parts

    def _build_branch_conditions(self, branch_conditions_schema):
        branch_conditions = []
        for condition in branch_conditions_schema:
             if condition['jumpTo']:
                jumpTo = JumpTo(condition['jumpTo']['question'], self.get_reference(), condition['jumpTo']['condition']['value']['is'])
                branch_conditions.append(jumpTo)

        return branch_conditions

    def branches(self, response):
        for rule in self.branch_conditions:
            if rule.trigger == self.get_reference() and rule.state == response:
                return rule.target

        return None

    def get_branch_target(self, response):
        return self.branches(response)

    def is_valid_response(self, response):
        self.errors = []
        for rule in self.validation:
            if not rule.is_valid(response):
                self.errors.append(rule.get_error(response))

        return len(self.errors) == 0

    def get_warnings(self, reference=None):
        return None

    def get_errors(self, reference=None):
        return self.errors or None

    def get_branch_conditions(self):
        return self.branch_conditions

    def has_branch_conditions(self):
        return len(self.branch_conditions) > 0

    def get_skip_conditions(self):
        return self.skip_conditions

    def has_skip_conditions(self):
        return len(self.skip_conditions) > 0

    def get_question_by_reference(self, reference):
        return None

    def get_reference(self):
        if self.parent:
            return self.parent.get_reference() + ':' + self._reference
        else:
            return self._reference

class MultipleChoiceQuestion(Question):
    def __init__(self, question_schema, parent=None):
        super(MultipleChoiceQuestion, self).__init__(question_schema, parent)

    def is_valid_response(self, response):
        valid = super(MultipleChoiceQuestion, self).is_valid_response(response)

        if response is not None and not response.isspace():
            for part in self.parts:
                if part == response:
                    return True

            self.errors.append('invalid option')
            return False

        return valid


class CheckBoxQuestion(Question):
    def __init__(self, question_schema, parent=None):
        super(CheckBoxQuestion, self).__init__(question_schema, parent)

    def is_valid_response(self, response):
        if isinstance(response, list):
            for item in response:
                if not super(CheckBoxQuestion, self).is_valid_response(item):
                    return False
            return True
        else:
            return super(CheckBoxQuestion, self).is_valid_response(response)


class InputTextQuestion(Question):
    def __init__(self, question_schema, parent=None):
        super(InputTextQuestion, self).__init__(question_schema, parent)


class TextBlock(Question):
    def __init__(self, question_schema, parent=None):
        super(TextBlock, self).__init__(question_schema, parent)

    def is_valid_response(self, request):
        return True

    def get_warnings(self, reference=None):
        return None

    def get_warnings(self, reference=None):
        return None


class QuestionGroup(Question):
    def __init__(self, question_schema, parent=None):
        super(QuestionGroup, self).__init__(question_schema)
        self.children = []
        self.errors = {}
        self._load_children(question_schema['children'])

    def _load_children(self, children_schema):
        for index, child in enumerate(children_schema):
            question = Question.factory(child, self)
            if not question._reference:
                question._reference = 'q' + str(index)
            self.children.append(question)

    def is_valid_response(self, responses):
        self.errors = {}
        for question in self.children:
            if question.get_reference() in responses.keys():
                response = responses[question.get_reference()]
            else:
                response = None

            if not question.is_valid_response(response):
                self.errors[question.get_reference()] = question.get_errors()

        return len(self.errors) == 0

    def get_warnings(self, reference=None):
        return None

    def get_errors(self, reference=None):
        if reference is None:
            return self.errors
        elif reference in self.errors.keys():
            return self.errors[reference]
        else:
            return None

    def branches(self, responses):
        jumps = []
        for child in self.children:
            if child.get_reference() in responses.keys():
                jump = child.branches(responses[child.get_reference()])
                if jump:
                    jumps.append(jump)

        return jumps

    def get_branch_target(self, response):
        jumps = self.branches(response)

        # groups always branch to the first matching target

        if len(jumps) > 0:
            return jumps[0]
        else:
            return None

    def get_branch_conditions(self):
        conditions = []
        for child in self.children:
            if child.has_branch_conditions():
                child_conditions = child.get_branch_conditions()
                for child_condition in child_conditions:
                    conditions.append(child_condition)

        return conditions

    def has_branch_conditions(self):
        return len(self.get_branch_conditions()) > 0

    def get_question_by_reference(self, reference):

        address_parts = reference.split(':')
        if len(address_parts) == 1:
            for question in self.children:
                if question._reference == reference:
                    return question
        else:
            this_level = address_parts.pop(0)
            for question in self.children:
                if question._reference == this_level:
                    return question.get_question_by_reference(':'.join(address_parts))
