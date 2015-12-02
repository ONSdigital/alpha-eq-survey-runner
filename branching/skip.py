from branching.condition import Condition


class SkipCondition(Condition):
    def __init__(self, trigger, state):
        super(SkipCondition, self).__init__(trigger, state)