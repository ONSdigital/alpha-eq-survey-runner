from question import QuestionElement


class CheckBox(QuestionElement):
    def __init__(self):
        super(CheckBox, self).__init__()

    def initialize(self, reference, question_type, text):
        super(CheckBox, self).initialize(reference, question_type, text)