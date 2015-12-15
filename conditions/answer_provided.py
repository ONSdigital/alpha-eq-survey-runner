from condition import Condition


class AnswerProvidedCondition(Condition):

    def __init__(self):
        super(AnswerProvidedCondition, self).__init__()

    def condition_is_met(self, response):
        if self.value:
            # empty strings are falsey
            return response and not response.isspace()
        else:
            # value not required
            return True
