from validator import Validator


# Great than
class Greaterthan(Validator):
    def __init__(self, schema):
        super(Greaterthan, self).__init__(schema)

    def is_valid(self, response):
        value = self._schema['value']
        return not value or unicode(response).isnumeric() and int(response) <= int(value)

    def get_message(self, response):
        value = self._schema['value']
        return self._schema['message'] or "This field should be less than or equal to {value}".format(value=value)