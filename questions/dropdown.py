from questions.question import Question


class Dropdown(Question):
    def __init__(self, question_schema, parent=None):
        super(Dropdown, self).__init__(question_schema, parent)