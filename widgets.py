from wtforms import Field
from wtforms import Form
from wtforms import validators
from wtforms.widgets import TextArea, html_params
from flask import Markup

class RichTextDisplayWidget(TextArea):
    html_params = staticmethod(html_params)

    def __init__(self, **kwargs):
        super(RichTextDisplayWidget, self).__init__()

    def __call__(self, field, **kwargs):
        html_temp = '<div class="rich_text_display"><p>%s</p></div>'
        return Markup(html_temp % ( field.default))
