# -*- coding: utf-8 -*-
from cls.settings import logger
from traceback import extract_stack

if __name__ == '__main__':
    from cls import app
    app.debug = True
    app.run('0.0.0.0', port=28000)
