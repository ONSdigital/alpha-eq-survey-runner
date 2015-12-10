from validators.validation_failure import ValidationFailure


class QuestionElement(object):
    def __init__(self, reference, question_type, text):
        self.reference = reference
        self.type = question_type
        self.text = text
        self.subtext = ""
        self.parts = []
        self._validation_rules = []
        self._branch_rules = []
        self.parent = None

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
