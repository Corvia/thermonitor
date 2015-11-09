#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive

HOMEDIR="/home/vagrant/"
PROJECTNAME="thermonitor"
PROJECTDIR="${HOMEDIR}${PROJECTNAME}/"

sudo apt-get update

sudo apt-get install -y debconf-utils pkg-config python-software-properties
sudo apt-get install -y apache2-utils git-core lynx mytop nginx nmap rdiff-backup s3cmd wget webalizer nodejs npm
sudo apt-get install -y graphviz graphviz-dev libgraphviz-dev libjpeg-dev libjpeg62
sudo apt-get install -y python-dev python-pip python-imaging libfreetype6 libfreetype6-dev libpq-dev
sudo apt-get install -y postgresql postgresql-contrib

sudo debconf-set-selections <<< "postfix postfix/mailname string ${HOSTNAME}"
sudo debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"
sudo apt-get install -y postfix mailutils

sudo pip install virtualenv virtualenvwrapper

mkdir ~/tmp
mkdir ~/.virtualenvs
ln -s /vagrant ~/${PROJECTNAME}

echo "export WORKON_HOME=~/.virtualenvs" >> ~/.profile
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.profile

. ~/.profile

mkvirtualenv ${PROJECTNAME}
source ~/.virtualenvs/thermonitor/bin/activate
pip install -r ${PROJECTDIR}requirements.txt

ssh-keygen -t dsa -f ~/.ssh/id_dsa -N ""

echo "workon thermonitor" >> ~/.profile
echo "cd ~/thermonitor" >> ~/.profile

chown -R vagrant:vagrant ${HOMEDIR}

sudo ln -s /usr/bin/nodejs /usr/bin/node
sudo npm install -g bower

cd ${PROJECTDIR}
bower install jquery bootstrap