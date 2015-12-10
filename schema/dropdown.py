from question import QuestionElement


class Dropdown(QuestionElement):
    def __init__(self, reference, question_type, text):
        super(Dropdown, self).__init__(reference, question_type, text)
