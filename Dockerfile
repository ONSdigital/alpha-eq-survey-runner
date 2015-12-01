FROM python:2.7.10

RUN mkdir /opt/eq-survey-runner
ADD ./requirements.txt /opt/eq-survey-runner/requirements.txt
RUN pip install -r /opt/eq-survey-runner/requirements.txt
ADD . /opt/eq-survey-runner
WORKDIR /opt/eq-survey-runner
EXPOSE 8080

WORKDIR /opt/eq-survey-runner
ENTRYPOINT python eq_cassandra.py && gunicorn -w 4 -b 0.0.0.0:8080 --config=gunicorn.py srunner:app
