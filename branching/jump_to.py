from branching.condition import Condition


class JumpTo(Condition):
    def __init__(self, target, trigger, state):
        super(JumpTo, self).__init__(target, trigger, state)