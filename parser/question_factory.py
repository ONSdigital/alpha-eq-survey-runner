from schema import question, checkbox, date, daterange, dropdown, inputtext, inputnumber, multiplechoice, questiongroup, textblock
from factory import Factory


class QuestionFactory(Factory):

    def __init__(self):
        super(QuestionFactory, self).__init__()

    def create_question(self, question_schema):
        question_type = question_schema['questionType']

        if question_type:
            instance = super(QuestionFactory, self).get_instance(question_type)
        else:
            instance = question.QuestionElement()

        instance.deserialize(question_schema)
        return instance

# create the factory and register the question classes
question_factory = QuestionFactory()
question_factory.register("QuestionGroup", questiongroup.QuestionGroup)
question_factory.register("CheckBox", checkbox.CheckBox)
question_factory.register("Date", date.Date)
question_factory.register("DateRange", daterange.DateRange)
question_factory.register("Dropdown", dropdown.Dropdown)
question_factory.register("InputNumber", inputnumber.InputNumber)
question_factory.register("InputText", inputtext.InputText)
question_factory.register("MultipleChoice", multiplechoice.MultipleChoice)
question_factory.register("TextBlock", textblock.TextBlock)
