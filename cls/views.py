# coding: utf-8
from flask import *

from py import utils
from py.vpn import JWC, BaseCodeStore
from . import app, logger


@app.before_first_request
def setup():
    # 打开所有缓存
    BaseCodeStore.setup_basecode()


# @app.route('/test')
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
        logger.warning('一开始账号密码输入错误,{} :: {} :: {}'.format(id, internet_pwd, pwd))
        return render_template("wrong.html", message=u"账号密码错误")
    jwc = JWC(id, internet_pwd, pwd)
    try:
        jwc.login()
    except utils.PasswordError as e:
        # 准备封掉用户id
        ip = utils.get_ip(request).encode("utf-8")
        logger.error("准备封掉ip: {}".format(ip))
        utils.incr('cls.vpn.block_ip::' + ip, 600)
        return render_template("wrong.html", message=e.message.decode('utf8'))
    except Exception as e:
        emsg = e.message.decode('utf-8')
        if u'密码错误' in emsg:
            emsg = u"教务处密码错误，请检查后重试"
        logger.warning('教务处登录异常: {}'.format(emsg.encode("utf-8")))
        return render_template("wrong.html", message=emsg)
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


@app.route('/traffic', methods=['GET', 'POST'])
def traffic():
    """流量获取"""
    use2total = []
    if 'id' in session and 'DSID' in session:
        j = JWC(sessionid=session.get('DSID'))
        name = session.get('name') or j.is_ok()
        session['name'] = name
        use2total = j.traffic(session['id'], name)
    return json.dumps(use2total)


@app.route('/logout')
def logout():
    if 'DSID' in session:
        j = JWC(sessionid=session.get('DSID'))
        j.logout()
    session.clear()
    logger.info("logout ...")
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return redirect('404.html')


@app.errorhandler(500)
def service_down(e):
    return redirect('500.html')
