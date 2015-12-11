
class Factory(object):

    def __init__(self):
        self.classes = {}

    def register(self, key, class_):
        self.classes[key] = class_

    def get_class(self, name):
        return self.classes[name]

    def get_instance(self, name):
        return self.classes[name]()
