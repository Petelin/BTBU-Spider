# coding: utf-8
from flask import *
from settings import logger

app = Flask(__name__, static_url_path='', static_folder='static/html')
app.config.from_pyfile('settings.py')
app.config.from_pyfile('../instance/settings.py')

from middleware import ProfileMiddleWare
middlewares = [ProfileMiddleWare]

for m in middlewares:
    app.before_request(m.before)
    app.after_request(m.after)

import views

