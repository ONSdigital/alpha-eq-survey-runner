class BranchingRule(object):
    def __init__(self, condition, target):
        self._condition = condition
        self._target = target

    def branch(self, response):
        if (self._condition.condition_is_met(response)):
            return self._target
        return None