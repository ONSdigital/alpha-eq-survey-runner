from question import QuestionElement


class MultipleChoice(QuestionElement):
    def __init__(self):
        super(MultipleChoice, self).__init__()

    def initialize(self, reference, question_type, text):
        super(MultipleChoice, self).initialize(reference, question_type, text)