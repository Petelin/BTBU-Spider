# -*- coding: utf-8 -*-

from flask import *
from flask import Flask, request

from py.vpn import *

app = Flask(__name__, static_url_path='', static_folder='static/html')
app.secret_key = '/3^#$%^&<|}:FG*^&GH>"wr^&yX R~saffc]LWX/,?RT'

debug = False

logger = settings.logger


@app.before_first_request
def setup():
    # 打开所有缓存
    BaseCodeStore.setup_basecode()


@app.route('/test')
def test1vpn(id, pwd):
    logger.debug("开始 。。。")
    j = JWC('2', '3', '2')
    j.login()
    logger.debug("结束 。。。")
    msg = j.get_CET()
    logger.debug("msg", msg)
    return msg


@app.route('/')
def index():
    sessionid = session.get('DSID')
    if sessionid and JWC(sessionid=sessionid).is_ok():
        return redirect('/center.html')
    else:
        return redirect('/login.html')


@app.route('/login', methods=['POST'])
def login():
    id = request.form.get('idcode')
    internet_pwd = request.form.get('internetpw')
    pwd = request.form.get('pw')
    if not id or not internet_pwd or not pwd or len(id) != 10:
        logger.warning('一开始账号密码输入错误')
        return render_template("wrong.html", message="账号密码错误")
    jwc = JWC(id, internet_pwd, pwd)
    try:
        jwc.login()
    except utils.PasswordError as e:
        # 准备封掉用户id
        ip = utils.get_ip(request)
        logger.error("准备封掉ip: %s" % ip)
        utils.incr('cls.vpn.block_ip::' + ip, 600)
        return render_template("wrong.html", message=e)
    except Exception as e:
        return render_template("wrong.html", message=e)
    session['DSID'] = jwc.s.cookies.get('DSID')
    session['id'] = jwc.id
    session.permanent = True
    return redirect('/center.html')


@app.route('/score', methods=['POST'])
def score_login():
    term = request.form.get('term')
    if 'DSID' in session and term:
        j = JWC(sessionid=session.get('DSID'))
        scoretable = j.get_score(term)
        return render_template('score.html', scoretable=scoretable)
    return redirect('/login.html')


@app.route('/detail', methods=['POST'])
def detail():
    params = request.form.get('params')
    if 'DSID' in session and params:
        j = JWC(sessionid=session.get('DSID'))
        return json.dumps(j.get_score_detial(params))
    return json.dumps({'isok': False})


@app.route('/timetable', methods=['GET', 'POST'])
def timetable():
    term = request.form.get('term')
    if 'DSID' in session and term:
        j = JWC(sessionid=session.get('DSID'))
        table = j.get_timetable(term)
        return render_template('timetable.html', table=table)
    return redirect('/login.html')


@app.route('/CET', methods=['GET'])
def CET():
    if 'DSID' in session:
        j = JWC(sessionid=session.get('DSID'))
        scorelist = j.get_CET()
        return json.dumps(scorelist)
    return redirect('/login.html')


@app.route('/logout')
def logout():
    if 'DSID' in session:
        j = JWC(sessionid=session.get('DSID'))
        j.logout()
    session.clear()
    logger.info("logout ...")
    return redirect('/')


# @app.teardown_appcontext
# def teardown_db(exception):
#     pass


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', port=28000)
