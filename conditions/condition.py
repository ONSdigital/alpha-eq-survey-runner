################# Condition Elements #################
class Condition(object):
    def __init__(self):
        pass

    def condition_is_met(self, response):
        raise NotImplementedError()
