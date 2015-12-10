from response import Response

class Responses(object):
    def __init__(self):
        self._responses = {}

    def add_response(self, question_reference, repetition, response):
        # todo: support lists of responses etc...
        self._responses[question_reference] = Response(question_reference, repetition, response)

    def get_response(self, question_reference, repetition=0):
        return self._responses.get(question_reference) or None

    def __len__(self):
        return len(self._responses)
