from validator import Validator


# Max length
class Maxlength(Validator):
    def __init__(self, schema):
        super(Maxlength, self).__init__(schema)

    def is_valid(self, response):
        value = self._schema['value']
        return not value or unicode(response).__len__() <= int(value)

    def get_message(self, response):
        return self._schema['message'] or "This field has exceeded maximum length"