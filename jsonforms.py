from wtforms import fields as f
from wtforms import Form
from wtforms import validators
import re
import json
from unidecode import unidecode
from widgets import RichTextDisplayWidget
import bleach
from bleach_whitelist import print_tags, print_attrs, all_styles


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'_'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))


class Converter(object):
    """docstring for Converter"""

    field = {}

    def __init__(self, question):
        questiontype = question['questionType']

        if questiontype == "InputText":
            self.convert_textfield(question)
        elif questiontype == "MultipleChoice":
            self.convert_radiofield(question)
        elif questiontype == "TextBlock":
            self.convert_textblock(question)
        return

    def get_field(self):
        return self.field

    def convert_textfield(self, question):
        """Given a question dict structure, return a TextField"""
        kwargs = {
            '_name': slugify(question['questionText']),
            'label': question['questionText'],
            'description': question['questionHelp'],
            'validators': [],
            'filters': [],
        }
        self.field = f.StringField(**kwargs)

    def convert_radiofield(self, question):
        """Given a multipe choice question dict structure, return a Radio Field"""
        kwargs = {
            '_name': slugify(question['questionText']),
            'label': question['questionText'],
            'description': question['questionHelp'],
            'choices': self.get_choices(question['parts']),
            'validators': [],
            'filters': [],
        }
        self.field = f.RadioField(**kwargs)

    def get_choices(self, parts):
        choices = []
        for part in parts:
            value = part['value']
            description = part['value']
            choice = (value, description)
            choices.append(choice)
        return choices

    def convert_textblock(self, question):
        """Given a question dict structure, return a TextBlock"""
        kwargs = {
            '_name': slugify(question['questionText']),
            'label': '',
            'default': bleach.clean(question['questionText'], print_tags),
            'description': '',
            'validators': [validators.optional()],
            'filters': [],
            'widget': RichTextDisplayWidget()
        }
        self.field = f.TextAreaField(**kwargs)


def json_fields(form_schema):
    """
    Given a form schema in json, return a dictionary of fields,
    having called the converter on each field.
    """

    field_dict = {}
    for question in form_schema['questions']:
        converter = Converter(question)
        field = converter.get_field()
        if field is not None:
            field_dict[slugify(question['questionText'])] = field

    return field_dict


def convert_to_wtform(form_schema):
    """
    Given a form schema object, convert that to a valid wtforms form object.
    """
    f_schema = json.loads(form_schema)
    field_dict = json_fields(f_schema)
    return type(str(slugify(f_schema['questionnaire_title'])) + 'Form', (Form, ), field_dict)