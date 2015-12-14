
class Question(object):
    def __init__(self):
        self.parent = None
        self.skipping = False
        self.type = None
        self.text = None
        self.question_help = None
        self._reference = None
        self.display_properties = None
        self.validation = []
        self.parts = []
        self.children = None
        self.display_conditions = None
        self.skip_conditions = []
        self.branch_conditions = []
        self.warnings = []
        self.errors = []
        self.allWarningsAccepted = True

    def initialize(self, reference, question_type, text, question_help):
        self._reference = reference
        self.type = question_type
        self.text = text
        self.question_help = question_help

    def deserialize(self, schema):
        question_type = self._get_value(schema, 'questionType')
        question_text = self._get_value(schema, 'questionText')
        question_reference = self._get_value(schema, 'questionReference')
        question_help = self._get_value(schema, 'questionHelp')
        self.initialize(question_reference, question_type, question_text, question_help)

    def _get_value(self, schema, name):
        value = None
        if schema[name]:
            value = schema[name]
        return value

    def add_validation_rule(self, rule):
        self.validation.append(rule)

    def add_part(self, part):
        self.parts.append(part)

    def add_branch_condition(self, condition):
        self.branch_conditions.append(condition)

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


