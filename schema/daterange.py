from question import QuestionElement


class DateRange(QuestionElement):
    def __init__(self):
        super(DateRange, self).__init__()

    def initialize(self, reference, question_type, text):
        super(DateRange, self).initialize(reference, question_type, text)

