# Base validator class
class Validator(object):
    def __init__(self, schema):
        self._schema = schema

    def is_valid(self, response):
        return True

    def get_error(self, response):
        return None

    def get_warning(self, response):
        return None


# Required field
class Required(Validator):
    def __init__(self, schema):
        super(Required, self).__init__(schema)

    def is_valid(self, response):
        if self._schema:
            # empty strings are falsey
            return response and not response.isspace()
        else:
            # value not required
            return True

    def get_error(self, response):
        return 'required'


# Numeric Field
class Numeric(Validator):
    def __init__(self, schema):
        super(Numeric, self).__init__(schema)

    def is_valid(self, response):
        return not response or response.isspace() or unicode(response).isnumeric()

    def get_error(self, response):
        return 'is not numeric'
