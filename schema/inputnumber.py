from question import QuestionElement


class InputNumber(QuestionElement):
    def __init__(self, reference, question_type, text):
        super(InputNumber, self).__init__(reference, question_type, text)
