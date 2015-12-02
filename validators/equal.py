from numeric import Numeric


# Equal
class Equal(Numeric):
    def __init__(self, schema):
        super(Equal, self).__init__(schema)

    def is_valid(self, response):
        value = self._schema['value']
        return not value or super(Equal, self).is_valid(response)and int(response) != int(value)

    def get_message(self, response):
        value = self._schema['value']
        return self._schema['message'] or "This field should not be equal to {value}".format(value=value)