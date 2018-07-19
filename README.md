
##微信公众平台ebtbu内接的查成绩、查课表。

###
使用: 
1. pip install -r requirements.txt
2. python3 run.py
done.


### 爬虫做的事

1. 登录vpn,获得session，外网访问内网，需登录[北京工商大学vpn][1]
![VPN](http://ww3.sinaimg.cn/thumbnail/ce3f70bajw1f58jbvw18vj20g80b0jrz.jpg)

2. 登录教务处，验证码识别，由于是固定字符(10个左右)，准确度可达100%
![jwc](http://ww3.sinaimg.cn/thumbnail/ce3f70bajw1f58jd9l988j20bq0b8t9z.jpg)

3. 构造请求，拿到结果，成绩、课表页面处理
![result](http://ww2.sinaimg.cn/thumbnail/ce3f70bajw1f58jf5shsfj21kw0f8qa3.jpg)

4. Flask [Web][2] 提供用户入口，随登录随爬取，不储存任何信息。
![](http://ww3.sinaimg.cn/thumbnail/ce3f70bajw1f58jl54fr4j21kw0siwjz.jpg)

5. 推荐一下`fabric` 在我项目里，可以一键更新代码，重启服务器，一键在服务器创建独立的测试页面。

### 难点
1. 服务器是在外网，如何穿透内网。
2. 学校网站万年不升级,只能用ie访问,所有手机都不能登录，错综复杂的跳转，重定向,比如登录之后，必须去访问另一个页面才算登陆成功、查成绩之前必须先去首页后的一串神奇的请求码。
3. vpn 登录错误次数多了会封我们的ip，现在是做了两台机器，Nginx分发，暑假访问量大的时候临时从网上爬了一批ip代理，手动加了几个ip算是扛过去了（出成绩那天，在线人数300+,感觉真的是技术有用！！！）

### 未来
1. 前端补补课，做个好看的课表和成绩展示页面。 -- 完成，BootStrap神器加身。
2. 拓展一下ip代理,不要写死，搞个池子,随时能添加，想着是放redis里面。

### 感谢
有人start这个项目,好兴奋啊,花了很多时间在这上面,这绝对是对我的肯定。欢迎诸位和我多多交流。

### 离校,已经不维护了.
tip: 2018/7/19日亲测可用
