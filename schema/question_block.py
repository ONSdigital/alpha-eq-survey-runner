from question import QuestionElement
from reapting.no_repeat_rule import NoRepeatRule


class QuestionBlock(QuestionElement):
    def __init__(self):
        pass

    def initialize(self, reference, question_type, text):
        super(QuestionBlock, self).initialize(reference, "block", text)
        self._children = []
        self._repeat_condition = NoRepeatRule()

    def add_children(self, children):
        for child in children:
            assert child.parent is None
            child.parent = self
            self._children.append(child)

    def has_children(self):
        return len(self._children) > 0

    def number_of_children(self):
        return len(self._children)

    def get_child(self, index):
        return self._children[index]

    def get_child_index(self, child):
        return self._children.index(child)

    def find_child(self, question_reference):
        for child in self._children:
            if child.question_reference == question_reference:
                return child
            elif child.has_children():
                result = child.find_child(question_reference)
                if  result is not None:
                    return result
        return None

    # validation ...
    def validation_failures(self, responses):
        failures = []

        for child in self._children:
            # todo: for each repeat...
            response = responses.get_response(child.reference)
            child_failures = child.validation_failures(response)
            failures.extend(child_failures)

        return failures

    # repeating ...
    def set_repeat_condition(self, condition):
        self._repeat_condition = condition

    def repeat_count(self, responses):
        return self._repeat_condition.repeat_count(responses)

    # branching...
    def next_question(self, responses):
        for child in self._children:
            target = child.next_question(responses.get_response(child.reference))
            if target:
                return target

        return None