from questions.question import Question


class CheckBox(Question):
    def __init__(self):
        super(CheckBox, self).__init__()

    def is_valid_response(self, response, warnings_accepted):
        if isinstance(response, list):
            for item in response:
                if item:
                    # we send a blank with every checkbox question, otherwise they don't show up
                    if not super(CheckBox, self).is_valid_response(item, False):
                        return False
            return True
        else:
            return super(CheckBox, self).is_valid_response(response, False)