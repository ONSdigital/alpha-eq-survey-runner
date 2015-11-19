# Base validator class
class Validator(object):
    def __init__(self, schema):
        self._schema = schema

    def is_valid(self, response):
        return True

    def get_message(self, response):
        return self._schema['message']

    def get_type(self):
         return self._schema['type']

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

# Numeric Field
class Numeric(Validator):
    def __init__(self, schema):
        super(Numeric, self).__init__(schema)

    def is_valid(self, response):
        return not response or response.isspace() or unicode(response).isnumeric()


# Max length
class Max(Validator):
    def __init__(self, schema):
        super(Max, self).__init__(schema)

    def is_valid(self, response):
        return  (unicode(response).__len__() <= self._schema['value'])

