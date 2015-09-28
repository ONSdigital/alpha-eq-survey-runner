import os
from flask import Flask, render_template, redirect, request
from flask_zurb_foundation import Foundation
from flask_wtf import Form
from wtforms import StringField, TextField
from wtforms.validators import DataRequired
import requests
import os
from jsonforms import convert_to_wtform
import logging

logging.basicConfig(level=logging.WARN)

app = Flask(__name__)
Foundation(app)
# @TODO change this env variable
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.survey_registry_url = os.environ.get('SURVEY_REGISTRY_URL', None)

@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/questionnaire/<int:questionnaire_id>', methods=('GET', 'POST'))
def questionnaire_viewer(questionnaire_id):
    preview=False
    if request.args.get('preview'):
        preview=True

    qurl = 'http://'+app.survey_registry_url + '/surveys/api/questionnaire/' + str(questionnaire_id) + '/'
    form_schema = requests.get(qurl)
    form = convert_to_wtform(form_schema.content)
    f_form = form(request.form)
    if request.method == 'POST' and f_form.validate():
        return render_template("thanks.html", data=f_form.data)
    return render_template("form.html", form=f_form, preview=preview)



if __name__ == '__main__':
    app.debug = True
    app.run()
