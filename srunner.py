from flask import Flask, render_template, redirect, request, session
from flask_zurb_foundation import Foundation
import requests
import os
import json
from flask_cassandra import CassandraCluster
from jsonforms import convert_to_wtform
import random
import logging
from logging import StreamHandler
import uuid

app = Flask(__name__)
Foundation(app)

cassandra = CassandraCluster()
app.config['CASSANDRA_NODES'] = [os.environ.get('CASSANDRA_NODE', 'cassandra')]

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


@app.route('/autosave/<int:questionnaire_id>/<quest_session_id>', methods=['POST'])
def autosave(questionnaire_id, quest_session_id):
    data = request.get_data()
    rtn = set_session_data(quest_session_id, session['uid'], data)
    if rtn == None:
        return 'OK'
    else:
        return 'ERROR'


def get_form_schema(questionnaire_id):
    qurl = app.survey_registry_url + '/surveys/api/questionnaire/' + str(questionnaire_id) + '/'
    form_schema = requests.get(qurl)
    return form_schema.content


def get_session_data(quest_session_id, session_id):
    cassandra_session = cassandra.connection
    cassandra_session.set_keyspace("sessionstore")
    cql = "SELECT data FROM sessions WHERE  quest_session_id = '{}' LIMIT 1;".format(quest_session_id)
    r = cassandra_session.execute(cql)

    if r:
        payload = json.loads(r[0].data)
        return payload
    return None


def set_session_data(quest_session_id, session_id, data):
    cassandra_session = cassandra.connection
    cassandra_session.set_keyspace("sessionstore")
    cql = "INSERT into sessions (session_id, quest_session_id, data) VALUES ('{}', '{}', '{}');".format(session_id, quest_session_id, data)
    app.logger.debug(cql)
    r = cassandra_session.execute(cql)
    app.logger.debug(r)
    return r


@app.route('/questionnaire/<int:questionnaire_id>', methods=('GET', 'POST'), strict_slashes=False)
@app.route('/questionnaire/<int:questionnaire_id>/<quest_session_id>', methods=('GET', 'POST'), strict_slashes=False)
def questionnaire_viewer(questionnaire_id, quest_session_id=None):

    if not session.get('uid'):
        session['uid'] = uuid.uuid4()

    preview = False

    if request.args.get('preview'):
        preview = True

    if 'debug' in request.args:
        q_data = render_template('survey.json')
    else:
        q_data = get_form_schema(questionnaire_id)


    resume_data = None

    if quest_session_id is not None:
        resume_data = get_session_data(quest_session_id, str(session['uid']))

    q_manager = QuestionnnaireManager(q_data, resume_data)

    if q_manager.started:
        print q_manager.get_current_question().question_text
    else:
        return render_template('survey_intro.html')


    # if request.method == 'POST':
    #     f_form = form(request.form)
    #     if f_form.validate():
    #         receipt_id = random.randrange(10000, 100000)
    #         app.logger.warning('{"rid": %d, "data": %s} ', receipt_id, json.dumps(f_form.data))
    #         return render_template("thanks.html",
    #                                 data=f_form.data,
    #                                 receipt_id=receipt_id)
    # elif resume_data:
    #     f_form = form(**resume_data)
    #
    # else:
    #     f_form = form()
    #
    # questionnaire = json.loads(raw_form)
    # return render_template("survey_index.html",
    #                         form=f_form,
    #                         questionnaire=questionnaire,
    #                         preview=preview)



if __name__ == '__main__':
    app.debug = True
    app.survey_registry_url = "http://127.0.0.1:5000"
    app.run()
