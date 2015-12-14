from questions.question import Question


class MultipleChoice(Question):
    def __init__(self):
        super(MultipleChoice, self).__init__()

    def is_valid_response(self, response, warning_accepted):
        valid = super(MultipleChoice, self).is_valid_response(response, False)

        if response is not None and not response.isspace():
            for part in self.parts:
                if part == response:
                    return True

            self.errors.append('invalid option')
            return False

        return valid