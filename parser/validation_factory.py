from conditions import answer_provided, numeric_condition, greaterthan, lessthan, equal, notequal, date_condition, maxlength_condition
from factory import Factory


class ValidatorFactory(Factory):
    def __init__(self):
        super(ValidatorFactory, self).__init__()

    def create_condition(self, validation_schema):
        validator_type = validation_schema['condition']

        if validator_type:
            instance = super(ValidatorFactory, self).get_instance(validator_type)
        else:
            instance = None

        instance.deserialize(validation_schema)
        return instance


# create the factory and register the question classes
validation_factory = ValidatorFactory()
validation_factory.register("required", answer_provided.AnswerProvidedConditon)
validation_factory.register("numeric", numeric_condition.IsNumericCondition)
validation_factory.register("greaterthan", greaterthan.IsGreaterThanCondition)
validation_factory.register("lessthan", lessthan.IsLessThanCondition)
validation_factory.register("equal", equal.IsEqualCondition)
validation_factory.register("notequal", notequal.IsNotEqualCondition)
validation_factory.register("date", date_condition.IsDateCondition)
validation_factory.register("maxlength", maxlength_condition.MaxLengthCondition)

