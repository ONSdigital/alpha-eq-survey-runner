from validators.validation_failure import ValidationFailure


class QuestionElement(object):

    def __init__(self):
        self.reference = ""
        self.type = ""
        self.text = ""
        self.subtext = ""
        self.parts = []
        self._validation_rules = []
        self._branch_rules = []
        self.parent = None

    def initialize(self, reference, question_type, text):
        self.reference = reference
        self.type = question_type
        self.text = text

    def deserialize(self, schema):
        question_type = self._get_value(schema, 'questionType')
        question_text = self._get_value(schema, 'questionText')
        question_reference = self._get_value(schema, 'questionReference')
        self.initialize(question_reference, question_type, question_text)

    def _get_value(self, schema, name):
        value = None
        if schema[name]:
            value = schema[name]
        return value

    # validation ...
    def add_validation_rule(self, rule):
        self._validation_rules.append(rule)

    def validation_failures(self, response):
        failures = []

        for rule in self._validation_rules:
            if not rule.is_valid(response.responses):
                failure = ValidationFailure(rule, self.reference)
                failures.append(failure)

        return failures

    # branching...
    def add_branching_rule(self, rule):
        self._branch_rules.append(rule)

    def next_question(self, response):
        for condition in self._branch_rules:
            target = condition.branch(response)
            if target is not None:
                return target
        return None
