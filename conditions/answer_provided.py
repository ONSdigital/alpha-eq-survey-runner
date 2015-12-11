from condition import Condition


class AnswerProvidedConditon(Condition):

    def __init__(self):
        super(AnswerProvidedConditon, self).__init__()

    def initialize(self, condition, value, error_type, message):
        super(AnswerProvidedConditon, self).initialize(condition, value, error_type, message)

    def condition_is_met(self, response):
        return response is not None and response != ""
