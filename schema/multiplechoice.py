from question import QuestionElement


class MultipleChoice(QuestionElement):
    def __init__(self, reference, question_type, text):
        super(MultipleChoice, self).__init__(reference, question_type, text)