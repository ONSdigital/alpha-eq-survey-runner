from numeric_condition import IsNumericCondition


# Less than
class IsLessThanCondition(IsNumericCondition):
    def __init__(self):
        super(IsLessThanCondition, self).__init__()
        self.value = None

    def condition_is_met(self, response):
        return super(IsLessThanCondition, self).condition_is_met(response) and float(response) >= float(self.value)
