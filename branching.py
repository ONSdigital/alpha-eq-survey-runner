class Condition(object):
    def __init__(self, *args):
        self.target = args[0]
        self.trigger = args[1]
        self.state = args[2]

    def matches(self):
        return False


class JumpTo(Condition):
    def __init__(self, target, trigger, state):
        super(JumpTo, self).__init__(target, trigger, state)
