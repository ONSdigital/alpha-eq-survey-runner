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

