from questions.question import Question


class Date(Question):
    def __init__(self, question_schema, parent=None):
        super(Date, self).__init__(question_schema, parent)