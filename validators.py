import datetime

class ValidationResult(object):
    def __init__(self, errors, warnings, accepted):
        self.errors = errors
        self.warnings = warnings
        self.accepted = accepted

    def is_valid(self):
        return len(self.errors) == 0 and (len(self.warnings) == 0 or self.accepted)

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

    def get_message(self, response):
        return self._schema['message'] or "This field is requried"


# Numeric Field
class Numeric(Validator):
    def __init__(self, schema):
        super(Numeric, self).__init__(schema)

    def is_valid(self, response):
        return not response or response.isspace() or unicode(response).isnumeric()

    def get_message(self, response):
        return self._schema['message'] or "This field should be a number"


# Date Field
class Date(Validator):
    def __init__(self, schema):
        super(Date, self).__init__(schema)

    def is_valid(self, response):
        if response and not response.isspace():
            try:
                datetime.datetime.strptime(response, "%d/%m/%Y")
                return True
            except ValueError:
                return False
        return True

    def get_message(self, response):
        return self._schema['message'] or "This field should be a date"


# Max length
class Maxlength(Validator):
    def __init__(self, schema):
        super(Maxlength, self).__init__(schema)

    def is_valid(self, response):
        value = self._schema['value']
        return not value or unicode(response).__len__() <= int(value)

    def get_message(self, response):
        return self._schema['message'] or "This field has exceeded maximum length"


# Less than
class Lessthan(Validator):
    def __init__(self, schema):
        super(Lessthan, self).__init__(schema)

    def is_valid(self, response):
        value = self._schema['value']
        return not value or unicode(response).isnumeric() and int(response) >= int(value)

    def get_message(self, response):
        value = self._schema['value']
        return self._schema['message'] or "This field should be greater than or equal to {value}".format(value=value)


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


# Equal
class Equal(Validator):
    def __init__(self, schema):
        super(Equal, self).__init__(schema)

    def is_valid(self, response):
        value = self._schema['value']
        return not value or unicode(response).isnumeric() and int(response) != int(value)

    def get_message(self, response):
        value = self._schema['value']
        return self._schema['message'] or "This field should not be equal to {value}".format(value=value)


# Not equal
class Notequal(Validator):
    def __init__(self, schema):
        super(Notequal, self).__init__(schema)

    def is_valid(self, response):
        value = self._schema['value']
        return not value or unicode(response).isnumeric() and int(response) == int(value)

    def get_message(self, response):
        value = self._schema['value']
        return self._schema['message'] or "This field should be equal to {value}".format(value=value)
