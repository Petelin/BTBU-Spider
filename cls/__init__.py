# coding: utf-8
from flask import *

from .middleware import ReverseProxied, ProfileMiddleWare, init_middleware
from .settings import logger

app = Flask(__name__, static_url_path='', static_folder='static/html')
app.config.from_pyfile('settings.py')
app.config.from_pyfile('../instance/settings.py')

init_middleware(app)
from .views import *
