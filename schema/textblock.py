from question import QuestionElement


class TextBlock(QuestionElement):
    def __init__(self, reference, question_type, text):
        super(TextBlock, self).__init__(reference, question_type, text)
