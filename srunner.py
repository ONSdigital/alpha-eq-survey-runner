from flask import Flask, render_template, redirect, request, session, url_for
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
from questionnaireManager import QuestionnaireManager

app = Flask(__name__)
app.debug = True
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
    result = cassandra_session.execute(cql)
    app.logger.debug(result)
    return result


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
    elif 'debug' in request.form:
        q_data = render_template('survey.json')
    else:
        q_data = get_form_schema(questionnaire_id)

    resume_data = None

    if quest_session_id is not None:
        resume_data = get_session_data(quest_session_id, str(session['uid']))

    q_manager = QuestionnaireManager(q_data, resume_data)
    if request.method == 'POST':
        if 'start' in request.form:
            if resume_data is not None:
                q_manager.resume_questionnaire(resume_data)
            else:
                q_manager.start_questionnaire()
        elif 'next' in request.form:
            q_manager.resume_questionnaire(resume_data)
            # validate response
            if 'user_response' in request.form:
                user_response = request.form['user_response']
            else:
                user_response = None
            if q_manager.is_valid_response(user_response):
                set_session_data(quest_session_id, str(session['uid']), json.dumps(q_manager.get_resume_data()))
                q_manager.get_next_question()


    if q_manager.started:
        q = q_manager.get_current_question()

        if q_manager.completed:
            return render_template('survey_completed.html',
                                    responses=resume_data,
                                    questionnaire=q_manager)


        if 'user_response' in request.form:
            user_response = request.form['user_response']
        elif resume_data is not None and q_manager.current_question.reference in resume_data.keys():
            user_response = resume_data[q_manager.current_question.reference]
        else:
            user_response = ''

        return render_template('questions/' + q.type + '.html',
                                question=q,
                                user_response=user_response,
                                questionnaire=q_manager)
    else:
        return render_template('survey_intro.html',
                                questionnaire=q_manager)


if __name__ == '__main__':
    app.debug = True
    app.survey_registry_url = "http://127.0.0.1:5000"
    app.run()
