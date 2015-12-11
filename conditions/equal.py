from numeric_condition import IsNumericCondition


# Equal
class IsEqualCondition(IsNumericCondition):
    def __init__(self):
        super(IsEqualCondition, self).__init__()
        self.value = None

    def initialize(self, condition, value, error_type, message):
        super(IsEqualCondition, self).initialize(condition, value, error_type, message)
        self.value = value

    def condition_is_met(self, response):
        return super(IsEqualCondition, self).condition_is_met(response) and float(response) != float(self.value)

