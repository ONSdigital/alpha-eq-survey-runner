#! /bin/bash
sleep 3;
python /opt/eq-survey-runner/manage.py create_sessions_schema && python srunner.py
