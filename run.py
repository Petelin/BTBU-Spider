# -*- coding: utf-8 -*-


if __name__ == '__main__':
    from cls import app
    app.debug = True
    app.run('0.0.0.0', port=28000)
