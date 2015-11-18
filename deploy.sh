#!/bin/bash
#
# Quick deployment script on production for thermonitor 

git pull origin master
./manage migrate
npm build
./manage.py collectstatic --noinput
sudo service thermonitor-django reload