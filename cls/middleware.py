# -*- coding: utf-8 -*-
import time

from flask import g, request, session

from settings import logger


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
        logger.info("{} id:{} ask {} duration {}s,cost {}s cpu time.".format(
            request.headers.get('X-Forwarded-For', request.remote_addr),
            session.get('id') or None,
            request.url,
            time.time() - g.start_time,
            time.clock() - g.clock_time,
        ))
        return response
