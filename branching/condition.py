class Condition(object):
    def __init__(self, *args):
        if len(args) == 3:
            self.target = args[0]
            self.trigger = args[1]
            self.state = args[2]
        elif len(args) == 2:
            self.trigger = args[0]
            self.state = args[1]