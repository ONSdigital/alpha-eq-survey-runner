from numeric_condition import IsNumericCondition


# Not equal
class IsNotEqualCondition(IsNumericCondition):
    def __init__(self, value):
        super(IsNotEqualCondition, self).__init__()
        self.value = value

    def condition_is_met(self, response):
        return super(IsNotEqualCondition, self).condition_is_met(response) and float(response) == float(self.value)

