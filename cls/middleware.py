# -*- coding: utf-8 -*-
import time
import traceback

from flask import g, request, session

from cls.settings import logger


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        return self.app(environ, start_response)


class Sentry():
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except Exception as e:
            logger.error(traceback.format_exc())
            raise


class BaseMiddleware(object):
    @classmethod
    def before(cls):
        return None

    @classmethod
    def after(cls, response):
        return response


class ProfileMiddleWare(BaseException):
    """打印时间"""

    @classmethod
    def before(cls):
        g.start_time = time.time()
        g.clock_time = time.clock()

    @classmethod
    def after(cls, response):
        logger.info("{} id:({}) ask for {}({}) duration {:.0f} ms,cost {:.0f} ms cpu-time.".format(
            request.headers.get('X-Forwarded-For', request.remote_addr),
            session.get('id') or None,
            request.url.split(":")[0],
            request.path,
            (time.time() - g.start_time) * 1000,
            (time.clock() - g.clock_time) * 1000,
        ))
        return response


def init_middleware(app):
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    app.wsgi_app = Sentry(app.wsgi_app)

    from .settings import MIDDLEWARES
    for m in MIDDLEWARES:
        m = globals().get(m)
        if m:
            app.before_request(m.before)
            app.after_request(m.after)
