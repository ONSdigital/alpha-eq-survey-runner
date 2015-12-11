from numeric_condition import IsNumericCondition


# Great than
class IsGreaterThanCondition(IsNumericCondition):
    def __init__(self):
        super(IsGreaterThanCondition, self).__init__()
        self.value = None

    def initialize(self, condition, value, error_type, message):
        super(IsGreaterThanCondition, self).initialize(condition, value, error_type, message)
        self.value = value

    def condition_is_met(self, response):
        return super(IsGreaterThanCondition, self).condition_is_met(response) and float(response) <= float(self.value)
