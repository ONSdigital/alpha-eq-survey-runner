from question import QuestionElement


class CheckBox(QuestionElement):
    def __init__(self, reference, question_type, text):
        super(CheckBox, self).__init__(reference, question_type, text)