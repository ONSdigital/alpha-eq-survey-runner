class QuestionnaireIterator(object):

    def __init__(self, root, current_section=None, current_block=None, current_question=None):
        self.root = root
        # todo: encapsulate these...
        self.current_section = current_section or root
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
