from flask import Flask, render_template, redirect, request, session, url_for
from flask_zurb_foundation import Foundation
import requests
import os
import json
import logging
from logging import StreamHandler
import uuid
from questionnaireManager import QuestionnaireManager
from settings import APP_FIXTURES
import eq_cassandra
import boto3

app = Flask(__name__)
app.debug = True
Foundation(app)


# log to stderr
file_handler = StreamHandler()
app.logger.setLevel(logging.DEBUG)  # set the desired logging level here
app.logger.addHandler(file_handler)

# @TODO change this env variable
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.survey_registry_url = os.environ.get('SURVEY_REGISTRY_URL', 'http://localhost:8000/')


# store the responses in a S3 bucket
def submit_data(sessionid, data):
    key = sessionid + '.json'
    data_in_json = json.dumps(data)
    s3 = boto3.resource('s3')
    s3.Bucket('digitaleq').put_object(Key=key, Body=data_in_json)


def _load_fixture(filename):
    q_data = None
    with open(os.path.join(APP_FIXTURES, filename)) as f:
        q_data = f.read()
        f.close()
    return q_data


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
    cql = "SELECT data FROM sessions WHERE  quest_session_id = '{}' LIMIT 1;".format(quest_session_id)
    r = cassandra_session.execute(cql)
    if r:
        payload = json.loads(r[0].data)
        return payload
    return None


def set_session_data(quest_session_id, session_id, data):
    cql = "INSERT into sessions (session_id, quest_session_id, data) VALUES ('{}', '{}', '{}');".format(session_id, quest_session_id, data)
    app.logger.debug(cql)
    result = cassandra_session.execute(cql)
    app.logger.debug(result)
    return result


def get_jump_link(request, reference):
    jump_url = request.base_url + '?jumpTo=' + reference
    if 'debug' in request.args.keys():
        jump_url += '&debug=' + request.args['debug']
    return jump_url

@app.context_processor
def inject_jump_link():
    return dict(get_jump_link=get_jump_link)

@app.context_processor
def inject_isinstance():
    return dict(isinstance=isinstance)

@app.route('/questionnaire/<int:questionnaire_id>', methods=('GET', 'POST'), strict_slashes=False)
@app.route('/questionnaire/<int:questionnaire_id>/<quest_session_id>', methods=('GET', 'POST'), strict_slashes=False)
def questionnaire_viewer(questionnaire_id, quest_session_id=None):

    if not session.get('uid'):
        session['uid'] = uuid.uuid4()

    if not quest_session_id:
        quest_session_id = uuid.uuid4()
        new_url = request.base_url + '/' + str(quest_session_id) + '/'
        if 'debug' in request.args.keys():
            new_url += '?debug=' + request.args['debug']
        return redirect(new_url)

    preview = False

    if request.args.get('preview'):
        preview = True

    if 'debug' in request.args:
        q_schema = _load_fixture('starwars.json')
    else:
        q_schema = get_form_schema(questionnaire_id)

    questionnaire_state = None

    if quest_session_id is not None:
        questionnaire_state = get_session_data(quest_session_id, str(session['uid']))

    q_manager = QuestionnaireManager(q_schema, questionnaire_state)

    if request.method == 'POST':
        if 'start' in request.form:
                q_manager.start_questionnaire()
        elif 'next' in request.form and q_manager.started:
            # validate response
            user_responses = {}
            warningsAccepted = []
            justifications ={}
            for key in request.form.keys():
                response = request.form.getlist(key)
                # Separate out warning checkbox responses from questionnaire question  responses
                if key.startswith( 'warning_' ):
                    warningsAccepted.append(key.replace("warning_", ""))
                if key.startswith( 'justification_' ):
                     justifications[key.replace("justification_", "")] = response[0]
                elif key != 'next' and key != 'start':
                    if len(response) > 1:
                        user_responses[key] = response
                    elif len(response) == 0:
                        user_responses[key] = None
                    else:
                        user_responses[key] = response[0]

            q_manager.store_response(user_responses)

            # Save the current accepted warnings to cassandra
            q_manager.store_warnings(warningsAccepted)

            # Save the justifications
            q_manager.store_justifications(justifications)

            if q_manager.is_valid_response(user_responses, warningsAccepted):
                q_manager.get_next_question(user_responses)

        set_session_data(quest_session_id, str(session['uid']), json.dumps(q_manager.get_questionnaire_state()))

        redirect_url = request.base_url
        if 'debug' in request.args.keys():
            redirect_url += '?debug=' + request.args['debug']

        return redirect(redirect_url, 302)

    else:
        jump_to = request.args.get('jumpTo')
        if jump_to:
            q_manager.jump_to_question(jump_to)
            set_session_data(quest_session_id, str(session['uid']), json.dumps(q_manager.get_questionnaire_state()))
            base_url = request.base_url
            if 'debug' in request.args.keys():
                base_url += '?debug=' + request.args['debug']
            return redirect(base_url, 302)

        if q_manager.started:
            if q_manager.completed:
                submit_data(quest_session_id, q_manager.get_questionnaire_state());
                return render_template('survey_completed.html',
                                        responses=q_manager.get_responses(),
                                        questionnaire=q_manager,
                                        request=request,
                                        current="completed")
            else:
                question = q_manager.get_current_question()
                if question:
                    return render_template('questions/' + question.type + '.html',
                                    question=question,
                                    user_response=q_manager.get_responses(),
                                    user_warningsAccepted=q_manager.get_warningsAccepted(),
                                    user_justification=q_manager.get_justifications(),
                                    questionnaire=q_manager,
                                    request=request,
                                    current="question")
                else:
                    return render_template('survey_error.html',
                                           questionnaire=q_manager,
                                           error="This survey has no questions",
                                           active="error")

        else:
            return render_template('survey_intro.html',
                                    questionnaire=q_manager,
                                    request=request,
                                    current="intro")


cassandra_cluster, cassandra_session = eq_cassandra.connect_to_cassandra("sessionstore")

if __name__ == '__main__':
    app.debug = True
    app.run(host="0.0.0.0", port=8080)
