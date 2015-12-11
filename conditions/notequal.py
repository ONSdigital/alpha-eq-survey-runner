from numeric_condition import IsNumericCondition


# Not equal
class IsNotEqualCondition(IsNumericCondition):
    def __init__(self):
        super(IsNotEqualCondition, self).__init__()
        self.value = None

    def initialize(self, condition, value, error_type, message):
        super(IsNotEqualCondition, self).initialize(condition, value, error_type, message)
        self.value = value

    def condition_is_met(self, response):
        return super(IsNotEqualCondition, self).condition_is_met(response) and float(response) == float(self.value)

