from conditions import answer_provided, numeric_condition, greaterthan, lessthan, equal, notequal, date_condition, maxlength_condition
from factory import Factory
from validators.validation_rule import ValidationRule


class ValidatorFactory(Factory):
    def __init__(self):
        super(ValidatorFactory, self).__init__()

    def create_condition(self, validator_type, validator_value):
        if validator_type:
            instance = super(ValidatorFactory, self).get_instance(validator_type)
            instance.initialize(validator_type, validator_value)
        else:
            instance = None
        return instance

    def get_validation_rule(self, validation_schema):
        validator_type = self._get_value(validation_schema, 'condition')
        validator_value = self._get_value(validation_schema, 'value')

        condition = self.create_condition(validator_type, validator_value)

        rule = ValidationRule(condition, self._get_value(validation_schema, 'type'), self._get_value(validation_schema, 'message'))
        return rule

    def _get_value(self, schema, name):
        value = None
        if schema[name]:
            value = schema[name]
        return value

# create the factory and register the question classes
validation_factory = ValidatorFactory()
validation_factory.register("required", answer_provided.AnswerProvidedCondition)
validation_factory.register("numeric", numeric_condition.IsNumericCondition)
validation_factory.register("greaterthan", greaterthan.IsGreaterThanCondition)
validation_factory.register("lessthan", lessthan.IsLessThanCondition)
validation_factory.register("equal", equal.IsEqualCondition)
validation_factory.register("notequal", notequal.IsNotEqualCondition)
validation_factory.register("date", date_condition.IsDateCondition)
validation_factory.register("maxlength", maxlength_condition.MaxLengthCondition)

