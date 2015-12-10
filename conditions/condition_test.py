from condition import Condition
import unittest


class ConditionTest(unittest.TestCase):

    def test_condition(self):
        condition = Condition()
        try:
            condition.condition_is_met(None)
        except NotImplementedError:
            unittest.expectedFailure(NotImplementedError)
