from questions.question import Question


class InputNumber(Question):
    def __init__(self, question_schema, parent=None):
        super(InputNumber, self).__init__(question_schema, parent)