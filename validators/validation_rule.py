################# Validation Elements #################


class ValidationRule(object):
    ERROR = "error"
    WARNING = "warning"

    def __init__(self, condition, type=ERROR, message=""):
        self.condition = condition
        self.type = type
        self.message = message

    def is_valid(self, response):
        return self.condition.condition_is_met(response)