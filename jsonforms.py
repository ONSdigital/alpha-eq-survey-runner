from wtforms import fields as f
from wtforms import Form
from wtforms import validators
import re
import json
from unidecode import unidecode

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).split())
    return unicode(delim.join(result))

class Converter(object):
    """docstring for Converter"""

    def convert(self, question):
        """Given a question dict structure, return a TextField"""
        kwargs = {
            'label': question['title'],
            'description': question['help_text'],
            'validators': [],
            'filters': [],
        }
        return  f.StringField( **kwargs)


def json_fields(form_schema):
    """
    Given a form schema in json, return a dictionary of fields,
    having called the converter on each field.
    """
    converter = Converter()
    field_dict = {}
    for question in form_schema['questions']:
        field = converter.convert(question)
        if field is not None:
            field_dict[question['title']] = field

    return field_dict


def convert_to_wtform(form_schema):
    """
    Given a form schema object, convert that to a valid wtforms form object.
    """
    f_schema = json.loads(form_schema)
    field_dict = json_fields(f_schema)
    return type(str(slugify(f_schema['questionnaire_title'])) + 'Form', (Form, ), field_dict)
