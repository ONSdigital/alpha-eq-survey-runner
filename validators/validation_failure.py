class ValidationFailure(object):
    def __init__(self, question_reference, rule):
        self.question_reference = question_reference
        self.rule = rule
