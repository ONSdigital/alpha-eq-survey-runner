from questions.question import Question


class DateRange(Question):
    def __init__(self, question_schema, parent=None):
        super(DateRange, self).__init__(question_schema, parent)

    def is_valid_response(self, response, warnings_accepted):
        if isinstance(response, list):
            for r in response:
               if not super(DateRange, self).is_valid_response(r, False):
                   return False
            return True
        else:
            return False