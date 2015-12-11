from question import QuestionElement
from validators.validation_rule import ValidationRule
from conditions.numeric_condition import IsNumericCondition


class NumericQuestion(QuestionElement):
    def __init__(self):
        super(NumericQuestion, self).__init__()

    def initialize(self, reference, question_type, text):
        super(NumericQuestion, self).__init__(reference, "numeric", text)
        self.add_validation_rule(ValidationRule(IsNumericCondition(), ValidationRule.ERROR))