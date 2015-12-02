from validator import Validator


# Numeric Field
class Numeric(Validator):
    def __init__(self, schema):
        super(Numeric, self).__init__(schema)

    def is_valid(self, response):
        return not response or response.isspace() or self.isnumeric(unicode(response))

    @staticmethod
    def isnumeric(response):
        if response.startswith('-'):
            # replace the - with an empty space once only
            value = response.replace('-', '', 1)
        else:
            value = response
        return value.isnumeric()

    def get_message(self, response):
        return self._schema['message'] or "This field should be a number"
