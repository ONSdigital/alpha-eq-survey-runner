from condition import Condition


class MaxLengthCondition(Condition):
    def __init__(self, max_length=None):
        super(MaxLengthCondition, self).__init__()
        self.max_length = max_length

    def condition_is_met(self, response):
        return len(response) < self.max_length
