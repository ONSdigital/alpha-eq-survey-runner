from condition import Condition


class AnswerProvidedCondition(Condition):

    def __init__(self):
        super(AnswerProvidedCondition, self).__init__()

    def initialize(self, condition, value, error_type, message):
        super(AnswerProvidedCondition, self).initialize(condition, value, error_type, message)

    def condition_is_met(self, response):
        if self.value:
            # empty strings are falsey
            return response and not response.isspace()
        else:
            # value not required
            return True
