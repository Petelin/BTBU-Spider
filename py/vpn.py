# coding: utf-8
import random
import re
import time

import bs4
from bs4 import BeautifulSoup

from idcode import *


class Proxies():
    @staticmethod
    def get():
        all = (("", 1), ("http://202.106.16.36:3128", 1),)
        ip = random.choice([k for k, v in all for i in range(v)])
        p = dict(https=ip, http=ip)
        try:
            r = requests.get("http://www.baidu.com", timeout=2, proxies=p)
        except requests.exceptions.Timeout as e:
            return {'https': ''}
        return p


class VPN(object):
    def __init__(self, id, internet_pwd):
        if not id or not internet_pwd:
            raise RuntimeError("wrong arguments")
        self.id = id
        self.internet_pwd = internet_pwd
        self.s = requests.session()
        self.s.verify = False
        proxies = Proxies.get()
        self.s.proxies.update(proxies)

    def login(self):
        login_url = "https://vpn.btbu.edu.cn/dana-na/auth/url_default/login.cgi"
        login_data = {'tz_offset': '480',
                      'username': self.id,
                      'password': self.internet_pwd,
                      'realm': '教师',
                      'btnSubmit': '登陆'}

        # 必须设置超时时间
        try:
            r = self.s.post(login_url, data=login_data, timeout=1)
        except Exception as e:
            try:
                r = self.s.post(login_url, data=login_data, timeout=2)
            except Exception as e:
                raise RuntimeError("error:vpn超过3s没有反应")

        # 判断密码正确:
        if not re.match(r'.+p=failed', r.url) is None:
            print("密码不对")
            raise RuntimeError("error:上网登录密码错误")

        soup = bs4.BeautifulSoup(r.text.encode("gbk", errors='replace').decode("gbk"), 'html.parser')
        # 在特殊情况下才能拿到cookies
        DSIDFormDataStrs = soup.find_all(id="DSIDFormDataStr")
        if len(DSIDFormDataStrs) > 0:
            formdatastr = DSIDFormDataStrs[0]['value']
            continue_data = {"btnContinue": "%E7%BB%A7%E7%BB%AD%E4%BC%9A%E8%AF%9D",
                             "FormDataStr": formdatastr}
            self.s.post(login_url, data=continue_data, verify=False, allow_redirects=False)

        if not self.s.cookies.get('DSID'):
            print("error:查询次数太多,学校vpn拉黑了服务器ip,大约20分钟后解封.没人的时候再来吧")
            raise RuntimeError("error:查询次数太多,学校vpn拉黑了服务器ip,大约20分钟后解封.没人的时候再来吧~~")

    def logout(self):
        logout_url = "https://vpn.btbu.edu.cn/dana-na/auth/logout.cgi"
        self.s.get(logout_url)


class JWC(VPN):
    def __init__(self, id=None, internet_pwd=None, pwd=None, sessionid=None):
        """use id + internet pwd + pwd or sessionid to get object"""
        if id and internet_pwd and pwd:
            super(JWC, self).__init__(id, internet_pwd)
            self.pwd = pwd
        elif sessionid:
            self.s = requests.session()
            self.s.verify = False
            self.s.cookies['DSID'] = sessionid
            proxies = Proxies.get()
            self.s.proxies.update(proxies)
        else:
            raise TypeError

    def is_ok(self):
        """是否能正常访问"""
        # timetable_url = "https://vpn.btbu.edu.cn/jsxsjz/,DanaInfo=10.0.40.192,Port=80+tkglAction.do?method=kbxxXs"
        main_url = "https://vpn.btbu.edu.cn/framework/,DanaInfo=jwgl.btbu.edu.cn+main.jsp"
        r = self.s.get(main_url)
        g = re.search(u"""<!--界面使用的初始化""", r.text)
        return True if g else False

    def login(self):
        # 登录vpn
        try:
            super(JWC, self).login()
        except:
            # 异常发生再次尝试
            super(JWC, self).login()

        idcode_url = "https://vpn.btbu.edu.cn/,DanaInfo=jwgl.btbu.edu.cn+verifycode.servlet"
        login_url = 'https://vpn.btbu.edu.cn/,DanaInfo=jwgl.btbu.edu.cn+Logon.do'
        idcode = get_idcode(idcode_url, cookies=self.s.cookies)

        login_data = {"method": "logon",
                      "USERNAME": self.id,
                      "PASSWORD": self.pwd,
                      "RANDOMCODE": idcode}
        r = self.s.post(login_url, data=login_data)

        if re.search("http://jwgl.btbu.edu.cn/framework/main.jsp", r.text) or re.search(
                "http://10.0.40.192/jsxsjz/framework/main.jsp", r.text):
            # 登陆成功之后必须先访问这个网站，拿到权限
            r = self.s.post(login_url, data={'method': 'logonBySSO'});
            if r.status_code == 200:
                print("jwc登录成功")
                return self.s.cookies
        elif (re.search("验证码错误", r.text)):
            print("wrong idcode,try login again...")
            # self.login()
            raise RuntimeError("error:访问人数太多,试试人流过去之后再来吧~")

        elif re.search("该帐号不存在或密码错误", r.text):
            print("error:passwd or id wrong!")
            raise RuntimeError("error:密码或学号错误,默认密码为学号或身份证后六位.")
        else:
            print("error:some unknow exception happen")
            raise RuntimeError("error:some unknow exception happen")

    def get_score(self, time='2015-2016-1'):
        """
        TODO
        callCount=1
        page=/jsxsjz/jiaowu/cjgl/xszq/query_xscj.jsp
        httpSessionId=7CE28C1FFCBB50A56A3C98372C5894A6
        scriptSessionId=A690BEE6027439B649BE609DC0059A19494
        c0-scriptName=dwrMonitor
        c0-methodName=setSearchBaseBean
        c0-id=0
        c0-param0=string:query_xscj.jspE5AEF10185BC2071E0430100007F50A4
        c0-e1=string:
        c0-e2=string:2015-2016-1
        c0-e3=string:13
        c0-e4=string:qbcj
        c0-param1=Object_Object:{kcmc:reference:c0-e1, kksj:reference:c0-e2, kcxz:reference:c0-e3, xsfs:reference:c0-e4}
        batchId=1
        """
        query_data = {"kksj": time}
        score_url = "https://vpn.btbu.edu.cn/,DanaInfo=jwgl.btbu.edu.cn+xszqcjglAction.do?method=queryxscj"
        r = self.s.post(score_url, data=query_data)
        return self.__parse_score(r.text)

    def __parse_score(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        for tag in soup.find_all("img"):
            tag.decompose()
        html = soup.find(id="mxhDiv")
        if not html:
            return soup.text
        else:
            scores = []
            tds = html.find_all("td")
            for score_row in [tds[i:i + 14] for i in range(0, len(tds), 14)]:
                score = []
                for td in score_row:
                    if td.a:
                        score.append((td.get_text().strip(), td.a['onclick']))
                    else:
                        score.append(td.get_text().strip())
                scores.append(score)
            for hint in soup.find_all(id="tblBmDiv"):
                scores.append([hint.get_text().strip()])
            return scores

    def get_timetable(self, time):
        # get significant
        # timetable_url = "https://vpn.btbu.edu.cn/jsxsjz/,DanaInfo=10.0.40.192,Port=80+tkglAction.do"
        timetable_url = "https://vpn.btbu.edu.cn/,DanaInfo=jwgl.btbu.edu.cn+tkglAction.do"
        params = "?method=kbxxXs"
        r = self.s.get(timetable_url + params)
        g = re.findall("""<input.*"xs0101id".*value ?= ?"(.*)".*/>""", r.text)
        if len(g) < 1:
            print r.text
            return u"网站改版，拿不到id码"

        # get html
        signid = g[0]
        # signid = "A48908FA3D1A430B9582E5457D2E99E1"
        params = "?method=goListKbByXs&istsxx=no&xnxqh=" + time + "&zc=&xs0101id=" + signid
        r = self.s.get(timetable_url + params)
        return self.__parse_timetable(r.content)

    def __parse_timetable(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        html = soup.find_all(id='kbtable')
        if html:
            return html[0].encode('utf-8')
        else:
            return soup.text

    def get_CET(self):
        url = "https://vpn.btbu.edu.cn/,DanaInfo=jwgl.btbu.edu.cn+kjlbgl.do?method=findXskjcjXszq&tktime=%d" % int(
            time.time() * 100)
        r = self.s.get(url)
        return self.__parse_CET(r.text)

    def __parse_CET(self, html):
        paser = """<table border="1" width="1425" bordercolorlight="#D1E4F8" cellspacing="0" cellpadding="0" bordercolor="#D1E4F8" bordercolordark="#ffffff" id=mxh STYLE="table-layout:fixed" >.*</table>"""
        r = re.findall(paser, html)
        if not r:
            return None
        else:
            scores = []
            table = r[0]
            trs = re.findall(r"<tr.*?/tr>", table)
            for tr in trs:
                r = re.findall(r"<td.*?>(.*?)<.*?/td>", tr)
                scores.append(r[1:8])
        return scores

    def get_score_detial(self, params):
        url = "https://vpn.btbu.edu.cn/,DanaInfo=jwgl.btbu.edu.cn+"
        r = self.s.get(url + params)

        soup = BeautifulSoup(r.text, 'html.parser')

        tr = soup.find(attrs={'class': 'smartTr'})
        if not tr:
            return {"isok": False}

        list = []
        find_all = tr.find_all('td')
        for td in find_all:
            list.append(td.string)
        f = {
            'isok': True,
            'normal': list[0].encode('utf-8') or 0,
            'bili1': list[1].encode('utf-8') or 0,
            'medium': list[2].encode('utf-8') or 0,
            'bili2': list[3].encode('utf-8') or 0,
            'finale': list[4].encode('utf-8') or 0,
            'bili3': list[5].encode('utf-8') or 0,
            'total': list[6].encode('utf-8') or 0,
        }
        return f


if __name__ == "__main__":
    BaseCodeStore.setup_basecode()
    id = 1302010635
    i_pwd = "petelin1120"

    j = JWC(id, i_pwd, i_pwd)
    j.login()
    #print j.get_timetable('2015-2016-2')
    print j.get_score('2015-2016-2')
    #print j.get_CET()

    #print(Proxies.get())
