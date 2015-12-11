from question import QuestionElement


class InputNumber(QuestionElement):
    def __init__(self):
        super(InputNumber, self).__init__()

    def initialize(self, reference, question_type, text):
        super(InputNumber, self).initialize(reference, question_type, text)
