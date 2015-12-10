import unittest
import os
from settings import APP_FIXTURES

from json_parser import JsonParser
from schema.questiongroup import QuestionGroup


class JsonParserTest(unittest.TestCase):
    def _load_fixture(self, filename):
        with open(os.path.join(APP_FIXTURES, filename)) as f:
            schema = f.read()
            f.close()
            return schema

    def setUp(self):
        self.questionnaire_schema = self. _load_fixture('starwars.json')
        self.json_parser = JsonParser(self.questionnaire_schema)

    def test_questionnaire_creation(self):
        questionnaire = self.json_parser.questionnaire
        assert questionnaire
        assert questionnaire.questionnaire_id == "1234"
        assert questionnaire.survey_id == "0001"
        assert questionnaire.title == "Census 2021"
        assert questionnaire.questionnaire_title == "Star Wars Census"
        assert questionnaire.overview == "This is census survey for the population to discuss their views on Star Wars"

    def test_section_creation(self):
        questionnaire = self.json_parser.questionnaire
        assert questionnaire.questions
        assert questionnaire.questions.__len__() == 3
        assert isinstance(questionnaire.questions[0], QuestionGroup)
        assert isinstance(questionnaire.questions[1], QuestionGroup)
        assert isinstance(questionnaire.questions[2], QuestionGroup)

        assert questionnaire.questions[0].text == "Star Wars Favourites"
        assert questionnaire.questions[0].reference == "sectionOne"
        assert questionnaire.questions[0].type == "QuestionGroup"

        assert questionnaire.questions[1].text == "The New Film"
        assert questionnaire.questions[1].reference == "sectionTwo"
        assert questionnaire.questions[1].type == "QuestionGroup"

        assert questionnaire.questions[2].text == "Future Improvements"
        assert questionnaire.questions[2].reference == "sectionThree"
        assert questionnaire.questions[2].type == "QuestionGroup"

    def test_question_creation_section_one(self):
        section_one = self.json_parser.questionnaire.questions[0]
        assert section_one.has_children()
        assert section_one.number_of_children() == 5
        assert section_one.get_child(0).type == 'TextBlock'
        assert section_one.get_child(1).type == 'InputText'
        assert section_one.get_child(2).type == 'MultipleChoice'
        assert section_one.get_child(3).type == 'CheckBox'
        assert section_one.get_child(4).type == 'Dropdown'

    def test_question_creation_section_two(self):
        section_two = self.json_parser.questionnaire.questions[1]
        assert section_two.has_children()
        assert section_two.number_of_children() == 2
        assert section_two.get_child(0).type == 'InputNumber'
        assert section_two.get_child(1).type == 'Date'

    def test_question_creation_section_three(self):
        section_three = self.json_parser.questionnaire.questions[2]
        assert section_three.has_children()
        assert section_three.number_of_children() == 2
        assert section_three.get_child(0).type == 'InputText'
        assert section_three.get_child(1).type == 'DateRange'


if __name__ == '__main__':
    unittest.main()
