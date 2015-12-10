from repeat_rule import RepeatRule


class NoRepeatRule(RepeatRule):
    def repeat_count(self, responses):
        return 0