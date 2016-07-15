# -*- coding: utf-8 -*-
import sys

from flask import *
from flask import Flask, request

from py.vpn import *

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.secret_key = '/3^#$%^&<|}:FG*^&GH>"wr^&yX R~saffc]LWX/,?RT'

debug = False


@app.before_first_request
def setup():
    # 打开所有缓存
    BaseCodeStore.setup_basecode()


@app.route('/')
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        sessionid = session.get('DSID')
        if sessionid and JWC(sessionid=sessionid).is_ok():
            return redirect('/static/html/center.html')
        else:
            return redirect('static/html/login.html')
    elif request.method == "POST":
        id = request.form.get('idcode')

        internet_pwd = request.form.get('internetpw')

        pwd = request.form.get('pw')

        if not id or not internet_pwd or not pwd:
            return redirect("wrong.html")
        jwc = JWC(id, internet_pwd, pwd)
        try:
            jwc.login()
        except Exception as e:
            return render_template("wrong.html", message=e)

        session['DSID'] = jwc.s.cookies.get('DSID')
        session.permanent = True
        return redirect('/static/html/center.html')


@app.route('/score', methods=['GET', 'POST'])
def score_login():
    term = request.form.get('term')
    if 'DSID' in session and term:
        j = JWC(sessionid=session.get('DSID'))
        scoretable = j.get_score(term)
        return render_template('score.html', scoretable=scoretable)
    return redirect('/static/html/login.html')


# @app.route('/detail', methods=['GET', 'POST'])
# def detail():
#     if request.method == "POST":
#         url = request.form['url']
#         dsid = request.form['cookies']
#         cookies = {'DSID': dsid}
#         r = requests.get(url, verify=False, cookies=cookies)
#
#         soup = BeautifulSoup(r.text, 'html.parser')
#
#         tr = soup.find(attrs={'class': 'smartTr'})
#         list = []
#         find_all = tr.find_all('td')
#         for td in find_all:
#             list.append(td.string)
#         f = {
#             'normal': list[0].encode('utf-8'),
#             'bili1': list[1].encode('utf-8'),
#             'medium': list[2].encode('utf-8'),
#             'bili2': list[3].encode('utf-8'),
#             'finale': list[4].encode('utf-8'),
#             'bili3': list[5].encode('utf-8'),
#             'total': list[6].encode('utf-8'),
#         }
#         return jsonify(**f)
#     return "不要闹"


@app.route('/timetable', methods=['GET', 'POST'])
def timetable():
    term = request.form.get('term')
    if 'DSID' in session and term:
        j = JWC(sessionid=session.get('DSID'))
        table = j.get_timetable(term)
        return render_template('timetable.html', table=table)
    return redirect('/static/html/login.html')

@app.route('/CET', methods=['GET'])
def CET():
    if 'DSID' in session:
        j = JWC(sessionid=session.get('DSID'))
        scorelist= j.get_CET()
        return json.dumps(scorelist)
    return redirect('/static/html/login.html')

@app.route('/logout')
def logout():
    if 'DSID' in session:
        j = JWC(sessionid=session.get('DSID'))
        j.logout()
    session.clear()
    return redirect('/')


# @app.teardown_appcontext
# def teardown_db(exception):
#     pass


if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0', port=38000)
