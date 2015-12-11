from question import QuestionElement


class QuestionSection(QuestionElement):
    def __init__(self):
        super(QuestionSection, self).__init__()

    def initialize(self, reference, question_type, text):
        super(QuestionSection, self).initialize(reference, "section", text)
        self._blocks = []

    def add_block(self, block):
        self._blocks.append(block)

    def get_block(self, index):
        return self._blocks[index]

    def number_of_blocks(self):
        return len(self._blocks)