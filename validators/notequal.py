from numeric import Numeric


# Not equal
class Notequal(Numeric):
    def __init__(self, schema):
        super(Notequal, self).__init__(schema)

    def is_valid(self, response):
        value = self._schema['value']
        return not value or super(Notequal, self).is_valid(response) and int(response) == int(value)

    def get_message(self, response):
        value = self._schema['value']
        return self._schema['message'] or "This field should be equal to {value}".format(value=value)