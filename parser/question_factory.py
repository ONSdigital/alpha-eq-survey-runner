from schema import question, checkbox, date, daterange, dropdown, inputtext, inputnumber, multiplechoice, numeric_question, questiongroup, textblock
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
factory = QuestionFactory()
factory.register("QuestionGroup", questiongroup.QuestionGroup)
factory.register("CheckBox", checkbox.CheckBox)
factory.register("Date", date.Date)
factory.register("DateRange", daterange.DateRange)
factory.register("Dropdown", dropdown.Dropdown)
factory.register("InputNumber", inputnumber.InputNumber)
factory.register("InputText", inputtext.InputText)
factory.register("MultipleChoice", multiplechoice.MultipleChoice)
factory.register("TextBlock", textblock.TextBlock)
