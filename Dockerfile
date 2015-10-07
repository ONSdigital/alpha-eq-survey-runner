FROM python:2.7.10

RUN mkdir /opt/eq-survey-runner
COPY requirements.txt /opt/eq-survey-runner/requirements.txt
COPY srunner.py /opt/eq-survey-runner/srunner.py
COPY jsonforms.py /opt/eq-survey-runner/jsonforms.py
COPY static /opt/eq-survey-runner/static
COPY templates /opt/eq-survey-runner/templates
RUN pip install -r /opt/eq-survey-runner/requirements.txt

EXPOSE 8080

WORKDIR /opt/eq-survey-runner
ENTRYPOINT gunicorn -w 4 -b 0.0.0.0:8080 srunner:app
