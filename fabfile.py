# encoding=utf-8
from __future__ import with_statement

from fabric.api import *
from fabric.contrib.console import confirm

env.roledefs = {
    'ali': ['lin@115.28.193.208'],
    'bwg': ['root@b.xrange.top:38000'],
}


def localpull():
    local("git pull --rebase")


def localpush():
    local("git push")


def testurl():
    with settings(warn_only=True):
        result = local("./bg_cmd.sh test -k -p test_all_urls.py")
    if result.failed and not confirm("测试失败.是否立即退出？"):
        abort("Aborting at user request.")
    else:
        print "测试全部通过"


def upload():
    """上传到项目地址"""
    local("tar -zcP -f /tmp/btbu-spider.tar.gz *")
    put("/tmp/btbu-spider.tar.gz", "/tmp/")
    local('rm /tmp/btbu-spider.tar.gz')
    run("sudo tar -zx -f /tmp/btbu-spider.tar.gz -C /home/ebtbu/Documents/github/cls")
    with cd("/home/ebtbu/Documents/github/cls"):
        run("cp -r static/* /srv/static/")


@roles("ali")
@task()
def restart():
    """重启nginx,uwsgi"""
    run("sudo nginx -s reload")
    run("sudo uwsgi --reload /tmp/BTBU-Spider.pid")


@task
def test_upload():
    """上传代码到测试服务器"""
    local("tar -zc -f /tmp/btbu-spider.tar.gz ../BTBU-Spider")
    put("/tmp/btbu-spider.tar.gz", "/tmp/")
    local('rm /tmp/btbu-spider.tar.gz')
    run("tar -zx -f /tmp/btbu-spider.tar.gz -C ~/test/")


@task
def test_runserver():
    """开启测试服务器"""
    with cd('~/test/BTBU-Spider'):
        run('source /home/ebtbu/Documents/pyenv/cls/bin/activate')
        run('python myapp.py')
        run("sleep 3600")


@roles("ali")
@task
def develop():
    """更新项目所有信息"""
    upload()
    restart()
