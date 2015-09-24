import os
from flask import Flask, render_template, redirect
from flask_zurb_foundation import Foundation
from flask_wtf import Form
from wtforms import StringField, TextField
from wtforms.validators import DataRequired
import requests


app = Flask(__name__)
Foundation(app)
# @TODO change this env variable
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/questionnaire/<int:questionnaire_id>', methods=('GET', 'POST'))
def questionnaire_viewer(questionnaire_id):
    if request.method == 'POST':
        pass
    qurl = app.survey_registry_url + '/questionnaire/' + questionnaire_id
    form_schema = requests.get(qurl)
    form = convert_to_wtform(form_schema)
    return render_template("form.html", form=form)


if __name__ == '__main__':
    app.debug = True
    app.run()
