from questions.question import Question


class CheckBox(Question):
    def __init__(self, question_schema, parent=None):
        super(CheckBox, self).__init__(question_schema, parent)

    def is_valid_response(self, response, warningsAccepted):
        if isinstance(response, list):
            for item in response:
                if item: # we send a blank with every checkbox question, otherwise they don't show up
                    if not super(CheckBox, self).is_valid_response(item, False):
                        return False
            return True
        else:
            return super(CheckBox, self).is_valid_response(response, False)