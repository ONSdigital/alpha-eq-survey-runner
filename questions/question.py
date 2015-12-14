import importlib

from branching.jump_to import JumpTo
from parser.validation_factory import validation_factory
from validators.validation_rule import ValidationRule


class Question(object):
    def __init__(self, question_schema, parent=None):
        self.parent = parent
        self.skipping = False
        self._schema = question_schema
        self.type = question_schema['questionType']
        self.question_text = question_schema['questionText']
        self.question_help = question_schema['questionHelp']
        self._reference = question_schema['questionReference']
        self.display_properties = None
        self.validation = self._build_validation(question_schema['validation'])
        self.parts = self._build_parts(question_schema['parts'])
        self.children = None
        self.display_conditions = None
        self.skip_conditions = []
        self.branch_conditions = self._build_branch_conditions(question_schema['branchConditions'])
        self.warnings = []
        self.errors = []
        self.allWarningsAccepted =True

    @staticmethod
    def factory(schema, parent=None):
        if schema['questionType']:
            question_class = getattr(importlib.import_module('questions.'+schema['questionType'].lower()), schema['questionType'])
            question = question_class(schema, parent)
            return question
        else:
            return Question()

    @staticmethod
    def _build_validation(validation_schema):
        rules = []

        for validation in validation_schema:
            if validation['condition']:
                condition = validation_factory.create_condition(validation)
                rule = ValidationRule(condition, condition.get_type(), condition.get_message())
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
             if condition['jumpTo'] and condition['jumpTo']['condition']['value']['is']:
                jump_to = JumpTo(condition['jumpTo']['question'], self.get_reference(), condition['jumpTo']['condition']['value']['is'])
                branch_conditions.append(jump_to)

        return branch_conditions

    def branches(self, response):
        for rule in self.branch_conditions:
            if rule.trigger == self.get_reference() and rule.state == response:
                # need to append the EQ_ rule.target comes from the schema
                return "EQ_" + rule.target

        return None

    def get_branch_target(self, response):
        return self.branches(response)

    def is_valid_response(self, response, warning_accepted):

        self.errors = []
        self.allWarningsAccepted = True

        for rule in self.validation:
            if rule.get_type() == 'error':
                if not rule.is_valid(response):
                    self.errors.append(rule.get_message())
                    break
            elif rule.get_type() == 'warning':
                if not rule.is_valid(response):
                    # All warnings need to be recorded to populate checkboxes and messages
                    self.warnings.append(rule.get_message())
                    # If there is a single warning on the page which hasn't been accepted
                    # submission should be blocked
                    if not warning_accepted:
                        self.allWarningsAccepted = False

        return self.allWarningsAccepted and len(self.errors) == 0

    def get_warnings(self, reference=None):
        return self.warnings or None

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
            return self.parent.get_reference() + '_' + self._reference
        else:
            return "EQ_" + self._reference


