from condition import Condition


class IsNumericCondition(Condition):
    def condition_is_met(self, response):
        try:
            float(response)
            return True
        except ValueError:
            return False
