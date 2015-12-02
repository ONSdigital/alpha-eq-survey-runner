from validator import Validator
import datetime


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