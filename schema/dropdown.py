from question import QuestionElement


class Dropdown(QuestionElement):
    def __init__(self):
        super(Dropdown, self).__init__()

    def initialize(self, reference, question_type, text):
        super(Dropdown, self).initialize(reference, question_type, text)
