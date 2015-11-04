""" Fabric Config for Django Projects. """

import sys
import os

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm
from fabric.contrib.files import comment, sed
from fabric.decorators import hosts

import thermonitor.settings as djsettings

# Global settings ------------------------------------------------------------

env.local_tmp_path = "~/tmp/"
env.remote_tmp_path = "/home/django/tmp/"
env.project_name = "thermonitor"
env.project_path = os.getcwd()
env.remote_project_path = "~/projects/" + env.project_name

env.staging_server = djsettings.STAGING_HOST
env.production_server = djsettings.PRODUCTION_HOST

env.dbuser = djsettings.DATABASES['default']['USER']
env.dbpass = djsettings.DATABASES['default']['PASSWORD']
env.dbname = djsettings.DATABASES['default']['NAME']

# Environments ---------------------------------------------------------------

def all():
    "HOST: Use both Staging & Production servers."
    env.hosts = [staging_server, production_server]

def staging():
    "HOST: Use the staging server"
    env.fqdn = djsettings.FQDN_STAGING
    env.nginx_conf = "nginx_staging.conf"
    env.hosts = [env.staging_server]

def production():
    "HOST: Use the production server"
    env.fqdn = djsettings.FQDN_PRODUCTION
    env.nginx_conf = "nginx_production.conf"
    env.hosts = [env.production_server]

# System Tasks ---------------------------------------------------------------

def op():
    "Lists remote hosts ports that are set to LISTENING"
    run('netstat -an | grep LIST | grep tcp')

def host_type():
    run('uname -s')

def delpyc():
    "Remove unwanted files on the remote host."
    with cd('%(remote_project_path)s' % env):
        run('find . \( -name "*.pyc" -o -name "._*" -o -name ".DS_*" \) -delete')

# Media / Static Asset Tasks -------------------------------------------------

@hosts(env.production_server)
def getmedia():
    "Grabs remote media directory and sync's it locally."
    local('rsync -vraz %(user)s@%(host)s:%(remote_project_path)s/media .' % env, capture=False)

def collectstatic():
    "Runs the collectstatic command on the remote server."
    run('/home/django/.virtualenvs/%s/bin/python %s/manage.py collectstatic --noinput' % (env.project_name, env.remote_project_path))

# Database Tasks -------------------------------------------------------------

def initdb():
    "Initialize the local database"
    local('mysql -uroot -e "DROP DATABASE IF EXISTS %(dbname)s; CREATE DATABASE %(dbname)s DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"' % env)
    local('mysql -uroot -e "GRANT ALL ON %(dbname)s.* TO \'%(dbuser)s\'@\'localhost\' IDENTIFIED BY \'%(dbpass)s\';"' % env)

def getdb():
    "Refreshes local db with a fresh dump from specified server."
    run('mysqldump -u%(dbuser)s -p%(dbpass)s %(dbname)s | bzip2 -c > %(local_tmp_path)s%(dbname)s.sql.bz2' % env)
    get('%(local_tmp_path)s%(dbname)s.sql.bz2' % env, '%(local_tmp_path)s%(dbname)s.sql.bz2' % env)

def loaddb():
    "Load the database locally."
    local('bunzip2 -f %(local_tmp_path)s%(dbname)s.sql.bz2' % env)
    initdb()
    local('mysql -uroot %(dbname)s < %(local_tmp_path)s%(dbname)s.sql' % env, capture=False)
    local('bzip2 -f %(local_tmp_path)s%(dbname)s.sql' % env)

def loadlocaldb():
    "Load the database locally."
    with cd('/vagrant/'):
        local('bunzip2 -f %(dbname)s.sql.bz2' % env)
        initdb()
        local('mysql -uroot %(dbname)s < %(dbname)s.sql' % env, capture=False)
        local('bzip2 -f %(dbname)s.sql' % env)

def pushdb():
    "Push a local db dump to a remote server."
    put('%(local_tmp_path)s%(dbname)s.sql.bz2' % env, '%(remote_tmp_path)s' % env)
    run('bunzip2 -f %(remote_tmp_path)s%(dbname)s.sql.bz2' % env)
    run('mysql -u%(dbuser)s -p%(dbpass)s %(dbname)s < %(remote_tmp_path)s%(dbname)s.sql' % env)
    run('bzip2 -f %(remote_tmp_path)s%(dbname)s.sql' % env)

def dumpdb():
    "Dumps the local database to the tmp bzip file. Ment for pushdb'ing"
    local('mysqldump -uroot %(dbname)s | bzip2 -c > %(local_tmp_path)s%(dbname)s.sql.bz2' % env)

def dumplocaldb():
    "Dumps the local database to a local tmp bzip file."""
    local('mysqldump -uroot %(dbname)s | bzip2 -c > %(dbname)s.sql.bz2' % env)

# Git Tasks ------------------------------------------------------------------

def gitpull():
    "Issue a 'git pull origin master'"
    with cd('%(remote_project_path)s/' % env):
        run('git pull origin master')

# Nginx Tasks ----------------------------------------------------------------

def copy_nginx_conf():
    "Copy nginx_production.conf to /etc/nginx/sites-available."
    with cd('%(remote_project_path)s' % env):
        sudo('cp %(nginx_conf)s /etc/nginx/sites-available/%(fqdn)s' % env)

def unlink_nginx_conf():
    "Unlink nginx configuration from sites-enabled."
    sudo('unlink /etc/nginx/sites-enabled/%(fqdn)s' % env)

def link_nginx_conf():
    "Symlink nginx configuration from sites-available to sites-enabled."
    sudo('ln -s /etc/nginx/sites-available/%(fqdn)s  /etc/nginx/sites-enabled/' % env)

def test_nginx_conf():
    sudo('/etc/init.d/nginx configtest')

def restart_nginx():
    "Restart Nginx Server."
    sudo('/etc/init.d/nginx restart')

def update_nginx():
    "Copy Nginx conf from project, enable it, test it and restart server."
    copy_nginx_conf()
    unlink_nginx_conf()
    link_nginx_conf()
    test_nginx_conf()
    restart_nginx()

# Gunicorn Tasks -------------------------------------------------------------
# Assuming you are using Ubuntu's Upstart to control Gunicorn.
# https://github.com/bkeating/djlongbtes/blob/master/gunicorn_upstart.conf

def deploy_gunicorn():
    "Deploy the Gunicorn Upstart Script to /etc/init/"
    with cd('%(remote_project_path)s' % env):
        sudo('cp gunicorn_upstart.conf /etc/init/thermonitor.conf' % env)
        sudo('initctl reload-configuration')

def start_gunicorn():
    "Start the Gunicorn process"
    sudo('start thermonitor')

def stop_gunicorn():
    "Stop the Gunicorn process"
    sudo('stop thermonitor')

def reload_gunicorn():
    "Reload the Gunicorn configuration"
    sudo('reload thermonitor')

def restart_gunicorn():
    "Restart the Gunicorn process"
    stop_gunicorn()
    start_gunicorn()

def status_gunicorn():
    "Status of Gunicorn"
    sudo('status thermonitor')

# Bundles (the above tasks, grouped together) --------------------------------

def getpayload():
    "Grab both media and database dump for local consumption"
    getdb()
    loaddb()
    getmedia()

def update():
    "Update the remote host with the latest from HEAD/trunk."
    gitpull()
    delpyc()
    collectstatic()

def update_all():
    "Update source, delete pycs', update nginx and reload Gunicorn."
    gitpull()
    delpyc()
    update_nginx()
    reload_gunicorn()
    collectstatic()
