################# Condition Elements #################
class Condition(object):
    def __init__(self):
        pass

    def condition_is_met(self, response):
        raise NotImplementedError()


class IsNumericCondition(Condition):
    def condition_is_met(self, response):
        try:
            float(response)
            return True
        except TypeError:
            return False

class MaxLengthCondition(Condition):
    def __init__(self, max_legnth = None):
        super(MaxLengthCondition, self).__init__()
        self.max_length = max_legnth

    def condition_is_met(self, response):
        return len(response) < self.max_length


class AnswerProvidedConditon(Condition):
    def __init__(self):
        super(AnswerProvidedConditon, self).__init__()

    def condition_is_met(self, response):
        return response is not None and response != ""


class AnswerMatchesCondition(Condition):
    def __init__(self, required_answer):
        super(AnswerMatchesCondition, self).__init__()
        self.required_answer = required_answer

    def condition_is_met(self, response):
        return response == self.required_answer


################# Validation Elements #################
class ValidationRule(object):
    ERROR = "error"
    WARNING = "warning"

    def __init__(self, condition, type=ERROR, message=""):
        self.condition = condition
        self.type = type
        self.message = message

    def is_valid(self, response):
        return self.condition.condition_is_met(response)


class ValidationFailure(object):
    def __init__(self, question_reference, rule):
        self.question_reference = question_reference
        self.rule = rule


class BranchingRule(object):
    def __init__(self, condition, target):
        self._condition = condition
        self._target = target

    def branch(self, response):
        if (self._condition.condition_is_met(response)):
            return self._target
        return None


################# REPEATING #################
class RepeatRule(object):
    def __init__(self):
        pass

    def repeat_count(self, responses):
        raise NotImplementedError()


class NoRepeatRule(RepeatRule):
    def repeat_count(self, responses):
        return 0


class RepeatOnPreviousResponseRule(RepeatRule):
    def __init__(self, question_reference):
        super(RepeatOnPreviousResponseRule, self).__init__()
        self.question_reference = question_reference

    def repeat_count(self, responses):
        return responses.get_response(self.question_reference).responses or 0


################# Questionnaire Elements #################
class QuestionElement(object):
    def __init__(self, reference, type, text):
        self.reference = reference
        self.type = type
        self.text = text
        self.subtext = ""
        self.parts = []
        self._validation_rules = []
        self._branch_rules = []
        self.parent = None

    # validation ...
    def add_validation_rule(self, rule):
        self._validation_rules.append(rule)

    def validation_failures(self, response):
        failures = []

        for rule in self._validation_rules:
            if not rule.is_valid(response.responses):
                failure = ValidationFailure(rule, self.reference)
                failures.append(failure)

        return failures

    # branching...
    def add_branching_rule(self, rule):
        self._branch_rules.append(rule)


    def next_question(self, response):
        for condition in self._branch_rules:
            target = condition.branch(response)
            if target is not None:
                return target
        return None




class QuestionBlock(QuestionElement):
    def __init__(self, reference, text):
        super(QuestionBlock, self).__init__(reference, "block", text)
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

class QuestionSection(QuestionElement):
    def __init__(self, reference, text):
        super(QuestionSection, self).__init__(reference, "section", text)
        self._blocks = []

    def add_block(self, block):
        self._blocks.append(block)

    def get_block(self, index):
        return self._blocks[index]

    def number_of_blocks(self):
        return len(self._blocks)


class NumericQuestion(QuestionElement):
    def __init__(self, reference, text):
        super(NumericQuestion, self).__init__(reference, "numeric", text)
        self.add_validation_rule(ValidationRule(IsNumericCondition(), ValidationRule.ERROR))


################# Questionnaire Management #################

class QuestionnaireIterator(object):

    def __init__(self, root, current_secction = None, current_block = None, current_question = None):
        self.root = root
        # todo: encapsulate these...
        self.current_section = current_secction or root
        self.current_block = current_block or self.root.get_block(0)
        self.current_question = current_question or self.current_block.get_child(0)
        self._current_block_index = 0
        self._current_child_index = 0
        self._current_block_repeat = 0


    def _find_child(self, question_reference):
        return self.root.find_child(question_reference)


    def _repeat_current_block(self, responses):
        repeat_count = self.current_block.repeat_count(responses)
        if self._current_block_repeat < repeat_count:
            self._current_block_repeat += 1
            self._current_child_index = 0
            self.current_question = self.current_block.get_child(0)
            return True

        return False

    def _branch_to_next_question(self, responses):
        target = self.current_block.next_question(responses)
        if target is not None:
            self.current_question = self._find_child(target)
            self._current_block_repeat = 0
            self._current_child_index = self.current_parent.get_child_index(self.current_question)
            return True

        return False

    def _move_to_next_question_sibling(self):
        if self._current_child_index + 1 < self.current_block.number_of_children():
            self._current_child_index += 1
            self.current_question = self.current_block.get_child(self._current_child_index)
            return True
        return False

    def _move_to_next_block(self):
        if self._current_block_index + 1 < self.current_section.number_of_blocks():
            self._current_block_index += 1
            self.current_block = self.current_section.get_block(self._current_block_index)
            self.current_question = self.current_block.get_child(0)
            self._current_child_index = 0
            self._current_block_repeat = 0
            return True
        return False

    def next_question(self, responses):
        if self._move_to_next_question_sibling():
            return
        elif self._repeat_current_block(responses):
            return
        elif self._branch_to_next_question(responses):
            return
        elif self._move_to_next_block():
            return
        else:
            return


################# Response Management #################
class Response(object):
    def __init__(self, question_reference, repetition, responses):
        self.question_reference = question_reference
        self.repetition = repetition
        self.responses = responses


class Responses(object):
    def __init__(self):
        self._responses = {}

    def add_response(self, question_reference, repetition, response):
        # todo: support lists of responses etc...
        self._responses[question_reference] = Response(question_reference, repetition, response)

    def get_response(self, question_reference, repetition=0):
        return self._responses.get(question_reference) or None

    def __len__(self):
        return len(self._responses)


################# Example Usage  #################
# QUESTIONS
e = NumericQuestion("3", "How many children?")
e.branch_conditions = [ BranchingRule(AnswerMatchesCondition(0),target="5")]


g = QuestionElement("4", "text", "What is their name?")
g.validation_rules = [ ValidationRule(MaxLengthCondition(5), ValidationRule.WARNING),
                       ValidationRule(AnswerProvidedConditon(), ValidationRule.ERROR)]

h = QuestionElement("5", "date", "What is their age?")

z = QuestionElement("6", "text", "Thanks!")

# BLOCKS
block1 = QuestionBlock("1", "Intro")
block1.add_children([e,])

block2 = QuestionBlock("2", "Children")
block2.set_repeat_condition(RepeatOnPreviousResponseRule(question_reference="3"))
block2.add_children([g, h])

block3 = QuestionBlock("7", "End")
block3.add_children([z,])

# SECTIONS
root = QuestionSection("0",  "root")
root.add_block(block1)
root.add_block(block2)
root.add_block(block3)


responses = Responses()

iter = QuestionnaireIterator(root)
assert iter.current_section == root
assert iter.current_block == block1
assert iter.current_question == e # Number of children
assert len(responses) == 0

responses.add_response(question_reference="3", repetition=0, response=1) # repeat once...
assert len(responses) == 1

# validate response for current question
assert iter.current_question.validation_failures(responses.get_response("3")) == []
# validate response for current block (and all questions within)
assert iter.current_block.validation_failures(responses) == []

iter.next_question(responses)
assert iter.current_section == root
assert iter.current_block == block2
assert iter.current_question == g
assert iter._current_block_repeat == 0

iter.next_question(responses)
assert iter.current_section == root
assert iter.current_block == block2
assert iter.current_question == h
assert iter._current_block_repeat == 0

iter.next_question(responses)
assert iter.current_section == root
assert iter.current_block == block2
assert iter.current_question == g
assert iter._current_block_repeat == 1

iter.next_question(responses)
assert iter.current_section == root
assert iter.current_block == block2
assert iter.current_question == h
assert iter._current_block_repeat == 1

iter.next_question(responses)
assert iter.current_section == root
assert iter.current_block == block3
assert iter.current_question == z
assert iter._current_block_repeat == 0