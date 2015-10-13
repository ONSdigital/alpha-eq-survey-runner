# gunicorn.py
import os

if os.environ.get('MODE') == 'dev':
    reload = True
