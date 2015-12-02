from questions.question import Question


class InputText(Question):
    def __init__(self, question_schema, parent=None):
        super(InputText, self).__init__(question_schema, parent)