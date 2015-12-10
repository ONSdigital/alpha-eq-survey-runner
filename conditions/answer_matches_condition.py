from condition import Condition


class AnswerMatchesCondition(Condition):
    def __init__(self, required_answer):
        super(AnswerMatchesCondition, self).__init__()
        self.required_answer = required_answer

    def condition_is_met(self, response):
        return response == self.required_answer
