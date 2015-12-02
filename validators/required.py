from validator import Validator


# Required field
class Required(Validator):
    def __init__(self, schema):
        super(Required, self).__init__(schema)

    def is_valid(self, response):
        if self._schema['value']:
            # empty strings are falsey
            return response and not response.isspace()
        else:
            # value not required
            return True

    def get_message(self, response):
        return self._schema['message'] or "This field is required"