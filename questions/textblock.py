from questions.question import Question


class TextBlock(Question):
    def __init__(self):
        super(TextBlock, self).__init__()

    def is_valid_response(self, request, False):
        return True

    def get_warnings(self, reference=None):
        return None

    def get_warnings(self, reference=None):
        return None