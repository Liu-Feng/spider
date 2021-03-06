# -*- coding: UTF-8 -*-
import os, re
from datetime import datetime
from fabric.api import *
from fabric.contrib.console import confirm

__author__ = 'zhangxind'

_TAR_FILE = 'dist-spider.tar.gz'
_CODE_DIR = os.path.abspath('../../../')
_DIST_DIR = os.path.join(_CODE_DIR, 'utils/dist')
_DIST_FILE_PATH = os.path.join(_DIST_DIR, _TAR_FILE)
_TARGET_PATH = '/data0/sourcecode/spider'
_TARGET_TMP_FILE = '/tmp/%s' % _TAR_FILE
_SUPERVISOR_CONF_PATH = '/etc/supervisor'

env.user = 'root'
env.colorize_errors = True
env.roledefs = {
    'spiderWorker': [
        '172.20.13.215'
    ]
}


def getNewCode():
    with lcd(_CODE_DIR):
        local('git pull origin master')


def build():
  includes = ['hbase', '*.txt', '*.cfg', 'spider', 'utils']
  excludes = ['*.pyc','*.tar.gz']
  with settings(warn_only=True):
    if local('test -f %s' % _DIST_FILE_PATH).return_code == 0:
      print 'Remove dist file.'
      local('rm -f %s' % _DIST_FILE_PATH)

    with lcd(_CODE_DIR):
      cmd = ['tar', 'zcvf', _DIST_FILE_PATH]
      cmd.extend(['--exclude=\'%s\'' % i for i in excludes])
      cmd.extend(includes)
      local(' '.join(cmd))


def copyFile():
  newDir = 'spider-%s' % datetime.now().strftime('%Y%m%d_%H%M%S')

  with settings(warn_only=True):
    if run('test -d %s' % _TARGET_PATH).failed:
      run('mkdir -p %s' % _TARGET_PATH)

    run('rm -f %s' % _TARGET_TMP_FILE)
    put(_DIST_FILE_PATH, _TARGET_TMP_FILE)

    with cd(_TARGET_PATH):
      run('mkdir %s' % newDir)
      run('rm -f current')
      run('ln -s %s current' % newDir)

    with cd('%s/%s' % (_TARGET_PATH, newDir)):
      if not run('test -f %s' % _TARGET_TMP_FILE).failed:
        run('tar zxvf %s' % _TARGET_TMP_FILE)

    with cd(_TARGET_PATH):
      run('chown root:root current')
      run('chown -R root:root %s' % newDir)


@task
@roles('spiderWorker')
def deploySpiderCode():
    '''向所有节点部署爬虫相关代码'''
    # getNewCode()
    build()
    copyFile()
    put('./spider_env/settings.py', '/data0/sourcecode/spider/current/spider/')


def testEnv():
    print "Executing on %(host)s as %(user)s" % env
