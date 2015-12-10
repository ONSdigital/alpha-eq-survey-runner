class RepeatOnPreviousResponseRule(RepeatRule):
    def __init__(self, question_reference):
        super(RepeatOnPreviousResponseRule, self).__init__()
        self.question_reference = question_reference

    def repeat_count(self, responses):
        return responses.get_response(self.question_reference).responses or 0