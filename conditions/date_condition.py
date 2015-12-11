from condition import Condition

import datetime


# Date Field
class IsDateCondition(Condition):
    def __init__(self,):
        super(IsDateCondition, self).__init__()

    def initialize(self, condition, value, error_type, message):
        super(IsDateCondition, self).initialize(condition, value, error_type, message)

    def condition_is_met(self, response):
        if response and not response.isspace():
            try:
                datetime.datetime.strptime(response, "%d/%m/%Y")
                return True
            except ValueError:
                return False
        return True

