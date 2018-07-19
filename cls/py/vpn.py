# coding: utf - 8
import random
import re
import time

import bs4
from bs4 import BeautifulSoup

from cls import logger, settings
from cls.py import utils
from cls.py.utils import get_proxy, rm_proxy, good_proxy
from cls.py.idcode import *
from .exception import BaseException, VPN_EXCEPTION, JWC_EXCEPTION
# close ssl warning. i know urls is safe and have no certify certificate
requests.packages.urllib3.disable_warnings()

class Proxies():
    @staticmethod
    def get():
        (ip, port), name = get_proxy()
        if ip is None or port is None:
            return dict(https='', http='')
        ip, port = ip.decode(), port.decode()
        url = 'http://{0}:{1}'.format(ip, port)
        p = dict(https=url, http=url)
        try:
            requests.get("https://www.baidu.com", timeout=1, proxies=p)
            good_proxy(name)
        except:
            logger.error("proxies not use able: %s" % ip)
            rm_proxy(name)
            return dict(https='', http='')
        return p


class VPN(object):
    def __init__(self, id, internet_pwd):
        if not id or not internet_pwd:
            raise Exception("wrong arguments")
        self.id = id
        self.internet_pwd = internet_pwd
        self.s = requests.session()
        self.s.verify = False
        # proxies = Proxies.get()
        # self.s.proxies.update(proxies)

    def login(self):
        login_url = "https://vpn.btbu.edu.cn/dana-na/auth/url_default/login.cgi"
        login_data = {'tz_offset': '480',
                      'username': self.id,
                      'password': self.internet_pwd,
                      'realm': '教师',
                      'btnSubmit': '登陆'}

        # 必须设置超时时间,超时证明密码不正确，服务器响应时间太长了
        try:
            r = self.s.post(login_url, data=login_data, timeout=2)
        except Exception as e:
            raise BaseException(VPN_EXCEPTION.PASSWORD_ERROR)

        # 判断密码正确:
        if not re.match(r'.+p=failed', r.url) is None:
            # utils.incr(settings.VPN_FAIL_KEY)
            # if utils.over_limit(settings.VPN_FAIL_KEY):
            #     logger.error("vpn登录失败超过限制: %d" % settings.fail_count_limit)
            # logger.warning("vpn密码不对 %s,vpn登录失败超过 %s次" % (str(login_data), utils.get(settings.VPN_FAIL_KEY)))
            raise BaseException(VPN_EXCEPTION.PASSWORD_ERROR)

        # 在特殊情况下才能拿到cookies
        soup = bs4.BeautifulSoup(r.text.encode("gbk", errors='replace').decode("gbk"), 'html.parser')
        DSIDFormDataStrs = soup.find_all(id="DSIDFormDataStr")
        if len(DSIDFormDataStrs) > 0:
            formdatastr = DSIDFormDataStrs[0]['value']
            continue_data = {"btnContinue": "%E7%BB%A7%E7%BB%AD%E4%BC%9A%E8%AF%9D",
                             "FormDataStr": formdatastr}
            self.s.post(login_url, data=continue_data, verify=False, allow_redirects=False)

        if not self.s.cookies.get('DSID'):
            raise BaseException(VPN_EXCEPTION.OVERLOAD)

    def logout(self):
        logout_url = "https://vpn.btbu.edu.cn/dana-na/auth/logout.cgi"
        self.s.get(logout_url)

    def close(self):
        self.s.close()


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
            raise BaseException(JWC_EXCEPTION.PARAM_ERROR)

    def is_ok(self):
        """是否能正常访问"""
        main_url = "https://vpn.btbu.edu.cn/framework/,DanaInfo=jwgl.btbu.edu.cn+main.jsp"
        r = self.s.get(main_url)
        g = re.search(u"""<title>(.*?)\[\d+\]北京工商大学综合教学管理系统-强智科技</title>""", r.text)
        if g is not None:
            return g.groups()[0]
        else:
            return None

    def login(self):
        # 登录vpn
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
            r = self.s.post(login_url, data={'method': 'logonBySSO'})
            if r.status_code == 200:
                return self.s.cookies
            else:
                raise BaseException(JWC_EXCEPTION.PASSWORD_ERROR)
        else:
            result = re.findall('''<span id="errorinfo">(.*)</span>''', r.text)
            if result:
                error_msg = result[0]
                raise BaseException(JWC_EXCEPTION.ERROR, error_msg)
            else:
                logger.error(r.text)
                raise BaseException(JWC_EXCEPTION.UNKNOW_ERROR)

    def get_score(self, time='2015-2016-1'):
        def _page(page=1):
            query_data = {"kksj": time, 'PageNum': page}
            score_url = "https://vpn.btbu.edu.cn/,DanaInfo=jwgl.btbu.edu.cn+xszqcjglAction.do?method=queryxscj"
            r = self.s.post(score_url, data=query_data)
            return self.__parse_score(r.text)

        result = _page(1)
        if len(result) == 12:
            second_page = _page(2)
            result = result[:-2]
            result.extend(second_page)
        return result

    def __parse_score(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        for tag in soup.find_all("img"):
            tag.decompose()
        html = soup.find(id="mxhDiv")
        if not html:
            return []
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
                scores.append("".join(hint.get_text().split()[:-1]))
            return scores

    def get_timetable(self, time):
        # get significant
        # timetable_url = "https://vpn.btbu.edu.cn/jsxsjz/,DanaInfo=10.0.40.192,Port=80+tkglAction.do"
        timetable_url = "https://vpn.btbu.edu.cn/,DanaInfo=jwgl.btbu.edu.cn+tkglAction.do"
        params = "?method=kbxxXs"
        r = self.s.get(timetable_url + params)
        g = re.findall("""<input.*"xs0101id".*value ?= ?"(.*)".*/>""", r.text)
        if len(g) < 1:
            logger.error('get_timetable,拿不到操作码')
            return "登录已失效"
        signid = g[0]
        logger.info(signid)
        params = "?method=goListKbByXs&istsxx=no&xnxqh=" + time + "&zc=&xs0101id=" + signid
        r = self.s.get(timetable_url + params)
        return self.__parse_timetable(r.content)

    def __parse_timetable(self, html):
        soup = bs4.BeautifulSoup(html, 'html.parser')
        html = soup.find_all(id='kbtable')
        if html:
            return html[0]
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

        detail = [td.string for td in tr.find_all('td')]
        return {
            'isok': True,
            'normal': detail[0] or 0,
            'bili1': detail[1] or 0,
            'medium': detail[2] or 0,
            'bili2': detail[3] or 0,
            'finale': detail[4] or 0,
            'bili3': detail[5] or 0,
            'total': detail[6] or 0,
        }

    def traffic(self, id, name, radio=2):
        # 先要授权
        url = 'https://vpn.btbu.edu.cn/dana/home/invalidsslsite_confirm.cgi'
        result = self.s.post(url)
        match = re.search(r"""<input id="xsauth_400" type="hidden" name="xsauth" value="(.*?)">""", result.text)
        xsauth = match.groups()[0]
        data = 'xsauth={}&url=%2F%2CDanaInfo%3Dself.btbu.edu.cn%2CSSL%252B&certHost=self.btbu.edu.cn&certPort=443&certDigest=048ef3a83ef7af63e9651ba47b2ff39e&errorCount=1&notAfter=1450339235&action=%E7%BB%A7%E7%BB%AD'.format(
            xsauth)
        self.s.post(url, data)

        url = 'https://vpn.btbu.edu.cn/,DanaInfo=self.btbu.edu.cn,SSL+chaxjg.php'
        data = {'UserAccount': id,
                'UserName': requests.utils.quote(name.encode('gbk')),
                'radio': radio,
                'button': requests.utils.quote(u'查询'.encode('gbk')),}

        data_str = ""
        for k, v in data.items():
            data_str += "{}={}&".format(k, v)
        headers = {'Content-Type': 'application/x-www-form-urlencoded',}
        result = self.s.post(url, headers=headers, data=data_str)
        html = result.text.encode('latin1').decode('gbk')

        # 解析
        soup = BeautifulSoup(html, 'html.parser')
        print(html)
        logger.debug(html)
        logger.error(html)
        u2t = [soup.find_all('strong')[-1].parent.parent.parent.parent.text.strip().split('\n')[i] for i in [-2, 3]]
        return u2t

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    BaseCodeStore.setup_basecode()
    id = u'1302010635'
    i_pwd = "petelin1120"

    j = JWC(id, i_pwd, i_pwd)
    j.login()
    print(j.get_timetable('2016-2017-2'))
    # print(j.get_score('2015-2016-2'))
    # print j.get_CET()

    # print(Proxies.get())
