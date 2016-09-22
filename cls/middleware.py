# -*- coding: utf-8 -*-
import time

from flask import g, request, session


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
        print ("id:{} ask {} duration {}s,cost {}s cpu time.".format(
            session.get('id') or None,
            request.path,
            time.time() - g.start_time,
            time.clock() - g.clock_time,
        ))
        return response
