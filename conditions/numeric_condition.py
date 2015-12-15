from condition import Condition


class IsNumericCondition(Condition):
    def __init__(self):
        super(IsNumericCondition, self).__init__()
        self.value = None

    def condition_is_met(self, response):
        return not response or response.isspace() or self.isnumeric(unicode(response))

    @staticmethod
    def isnumeric(response):
        try:
            float(response)
            return True
        except ValueError:
            return False
