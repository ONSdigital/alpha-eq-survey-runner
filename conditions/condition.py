################# Condition Elements #################
class Condition(object):
    def __init__(self):
        self.condition = None
        self.value = None

    def initialize(self, condition, value):
        self.condition = condition
        self.value = value

    def deserialize(self, schema):
        condition = self._get_value(schema, 'condition')
        value = self._get_value(schema, 'value')
        self.initialize(condition, value)

    def _get_value(self, schema, name):
        value = None
        if schema[name]:
            value = schema[name]
        return value

    def condition_is_met(self, response):
        raise NotImplementedError()
