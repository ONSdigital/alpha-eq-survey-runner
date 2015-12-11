################# Condition Elements #################
class Condition(object):
    def __init__(self):
        self.condition = None
        self.value = None
        self.error_type = None
        self.message = None

    def initialize(self, condition, value, error_type, message):
        self.condition = condition
        self.value = value
        self.error_type = error_type
        self.message = message

    def deserialize(self, schema):
        condition = self._get_value(schema, 'condition')
        value = self._get_value(schema, 'value')
        error_type = self._get_value(schema, 'type')
        message = self._get_value(schema, 'message')
        self.initialize(condition, value, error_type, message)

    def _get_value(self, schema, name):
        value = None
        if schema[name]:
            value = schema[name]
        return value


    def condition_is_met(self, response):
        raise NotImplementedError()
