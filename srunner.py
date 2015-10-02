import os
from flask import Flask, render_template, redirect, request
from flask_zurb_foundation import Foundation
from flask_wtf import Form
from wtforms import StringField, TextField
from wtforms.validators import DataRequired
import requests
import os
import json
from jsonforms import convert_to_wtform
import random
import logging
from logging import StreamHandler

app = Flask(__name__)
Foundation(app)

# log to stderr

file_handler = StreamHandler()
app.logger.setLevel(logging.DEBUG)  # set the desired logging level here
app.logger.addHandler(file_handler)

# @TODO change this env variable
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.survey_registry_url = os.environ.get('SURVEY_REGISTRY_URL', None)

@app.route('/')
def hello():
    return render_template('index.html')


def get_form_schema(questionnaire_id):
    qurl = app.survey_registry_url + '/surveys/api/questionnaire/' + str(questionnaire_id) + '/'
    form_schema = requests.get(qurl)
    return form_schema.content


@app.route('/questionnaire/<int:questionnaire_id>', methods=('GET', 'POST'))
def questionnaire_viewer(questionnaire_id):
    preview=False
    if request.args.get('preview'):
        preview=True

    form = convert_to_wtform(get_form_schema(questionnaire_id))
    f_form = form(request.form)
    if request.method == 'POST' and f_form.validate():
        receipt_id = random.randrange(10000, 100000)
        app.logger.warning('{"rid": %d, "data": %s} ', receipt_id, json.dumps(f_form.data))
        return render_template("thanks.html",
                                data=f_form.data,
                                receipt_id=receipt_id)

    return render_template("form.html",
                            form=f_form,
                            preview=preview)



if __name__ == '__main__':
    app.debug = True
    app.run()
