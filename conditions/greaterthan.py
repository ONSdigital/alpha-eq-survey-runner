from numeric_condition import IsNumericCondition


# Great than
class IsGreaterThanCondition(IsNumericCondition):
    def __init__(self, value):
        super(IsGreaterThanCondition, self).__init__()
        self.value = value

    def condition_is_met(self, response):
        return super(IsGreaterThanCondition, self).condition_is_met(response) and float(response) <= float(self.value)
