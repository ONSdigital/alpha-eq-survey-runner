from questions.question import Question


class QuestionGroup(Question):
    def __init__(self):
        super(QuestionGroup, self).__init__()
        self.children = []
        self.errors = {}

    def add_child(self, child):
        assert child.parent is None
        child.parent = self
        self.children.append(child)

    def has_children(self):
        return len(self.children) > 0

    def number_of_children(self):
        return len(self.children)

    def get_child(self, index):
        return self.children[index]

    def is_valid_response(self, responses, warningsAccepted):
        self.errors = {}
        warning = False

        for question in self.children:

            if question.get_reference() in responses.keys():
                response = responses[question.get_reference()]
                warning = question.get_reference() in warningsAccepted
            else:
                response = None

            if not question.is_valid_response(response, warning):
                self.errors[question.get_reference()] = question.get_errors()

        return len(self.errors) == 0

    def get_warnings(self, reference=None):
        return None

    def get_errors(self, reference=None):
        if reference is None:
            return self.errors
        elif reference in self.errors.keys():
            return self.errors[reference]
        else:
            return None

    def branches(self, responses):
        jumps = []
        for child in self.children:
            if child.get_reference() in responses.keys():
                jump = child.branches(responses[child.get_reference()])
                if jump:
                    jumps.append(jump)

        return jumps

    def get_branch_target(self, response):
        jumps = self.branches(response)

        # groups always branch to the first matching target

        if len(jumps) > 0:
            return jumps[0]
        else:
            return None

    def get_branch_conditions(self):
        conditions = []
        for child in self.children:
            if child.has_branch_conditions():
                child_conditions = child.get_branch_conditions()
                for child_condition in child_conditions:
                    conditions.append(child_condition)

        return conditions

    def has_branch_conditions(self):
        return len(self.get_branch_conditions()) > 0

    def get_question_by_reference(self, reference):

        address_parts = reference.split('_')
        if len(address_parts) == 1:
            for question in self.children:
                if question._reference == reference:
                    return question
        else:
            this_level = address_parts.pop(0)
            for question in self.children:
                if question._reference == this_level:
                    return question.get_question_by_reference('_'.join(address_parts))