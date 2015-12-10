from condition import Condition


class AnswerProvidedConditon(Condition):
    def __init__(self):
        super(AnswerProvidedConditon, self).__init__()

    def condition_is_met(self, response):
        return response is not None and response != ""
