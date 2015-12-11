from question import QuestionElement


class InputText(QuestionElement):
    def __init__(self):
        super(InputText, self).__init__()

    def initialize(self, reference, question_type, text):
        super(InputText, self).initialize(reference, question_type, text)