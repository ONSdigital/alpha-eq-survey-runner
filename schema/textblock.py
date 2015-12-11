from question import QuestionElement


class TextBlock(QuestionElement):
    def __init__(self):
        super(TextBlock, self).__init__()

    def initialize(self, reference, question_type, text):
        super(TextBlock, self).initialize(reference, question_type, text)
