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
class Maxlength(Validator):
    def __init__(self, schema):
        super(Maxlength, self).__init__(schema)

    def is_valid(self, response):
        return unicode(response).__len__() <= self._schema['value']


# Less than
class Lessthan(Validator):
    def __init__(self, schema):
        super(Lessthan, self).__init__(schema)

    def is_valid(self, response):
        return unicode(response).isnumeric() and int(response) < self._schema['value']


# Great than
class Greaterthan(Validator):
    def __init__(self, schema):
        super(Greaterthan, self).__init__(schema)

    def is_valid(self, response):
        return unicode(response).isnumeric() and int(response) > self._schema['value']


# Equal
class Equal(Validator):
    def __init__(self, schema):
        super(Equal, self).__init__(schema)

    def is_valid(self, response):
        return unicode(response).isnumeric() and int(response) == self._schema['value']


# Not equal
class Notequal(Validator):
    def __init__(self, schema):
        super(Notequal, self).__init__(schema)

    def is_valid(self, response):
        return unicode(response).isnumeric() and int(response) != self._schema['value']