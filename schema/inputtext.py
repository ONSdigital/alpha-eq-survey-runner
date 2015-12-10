from question import QuestionElement


class InputText(QuestionElement):
    def __init__(self, reference, question_type, text):
        super(InputText, self).__init__(reference, question_type, text)