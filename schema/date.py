from question import QuestionElement


class Date(QuestionElement):
    def __init__(self):
        super(Date, self).__init__()

    def initialize(self, reference, question_type, text):
        super(Date, self).initialize(reference, question_type, text)

