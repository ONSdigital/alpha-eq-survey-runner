from condition import Condition


class MaxLengthCondition(Condition):
    def __init__(self):
        super(MaxLengthCondition, self).__init__()
        self.value = None

    def initialize(self, condition, value, error_type, message):
        super(MaxLengthCondition, self).initialize(condition, value, error_type, message)
        self.value = value

    def condition_is_met(self, response):
        return not self.value or unicode(response).__len__() <= int(self.value)
