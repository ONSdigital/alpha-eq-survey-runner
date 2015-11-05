class Condition(object):
    def __init__(self, *args):
        if len(args) == 3:
            self.target = args[0]
            self.trigger = args[1]
            self.state = args[2]
        elif len(args) == 2:
            self.trigger = args[0]
            self.state = args[1]


class JumpTo(Condition):
    def __init__(self, target, trigger, state):
        super(JumpTo, self).__init__(target, trigger, state)

class SkipCondition(Condition):
    def __init__(self, trigger, state):
        super(SkipCondition, self).__init__(trigger, state)

