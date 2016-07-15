
微信公众平台ebtbu内接的查成绩、查课表。

### 爬虫做的事

1. 登录vpn,获得session，外网访问内网，需登录[北京工商大学vpn][1]
![VPN](http://ww3.sinaimg.cn/thumbnail/ce3f70bajw1f58jbvw18vj20g80b0jrz.jpg)

2. 登录教务处，验证码识别，由于是固定字符，准确度可达100%
![jwc](http://ww3.sinaimg.cn/thumbnail/ce3f70bajw1f58jd9l988j20bq0b8t9z.jpg)

3. 构造请求，拿到结果，成绩、课表页面处理
![result](http://ww2.sinaimg.cn/thumbnail/ce3f70bajw1f58jf5shsfj21kw0f8qa3.jpg)

4. Flask [Web][2] 提供用户入口，随登录随爬取，不储存任何信息。
![](http://ww3.sinaimg.cn/thumbnail/ce3f70bajw1f58jl54fr4j21kw0siwjz.jpg)

### 难点
1. 学校网站万年不升级，错综复杂的跳转，重定向。（比如登录之后，必须去访问另一个页面才算登陆成功、查成绩之前必须先去首页后的一串神奇的请求码）。
2. 服务器是在外网，如何穿透内网。

### 未来
1. 前端补补课，做个好看的课表和成绩展示页面。


  [1]: https://vpn.btbu.edu.cn
  [2]: http://ali.ebtbu.com:5000/login.html
