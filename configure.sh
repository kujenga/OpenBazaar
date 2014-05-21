#!/bin/bash

mkdir ~/install
cd ~/install

git clone https://github.com/warner/python-ecdsa
cd python-ecdsa
sudo python setup.py install
cd ..

git clone https://github.com/darkwallet/python-obelisk
cd python-obelisk
sudo python setup.py install
cd ..

sudo apt-get install mongodb

sudo apt-get install gcc
sudo apt-get install g++

wget http://download.zeromq.org/zeromq-4.0.4.tar.gz
tar -xvf zeromq-4.0.4.tar.gz
cd zeromq-4.0.4
./configure
sudo make install
sudo ldconfig
cd ..

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | sudo tee /etc/apt/sources.list.d/mongodb.list
sudo apt-get update
sudo apt-get install mongodb-org

sudo apt-get install build-essential python-dev

wget --no-check-certificate https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py

sudo pip install pyzmq
sudo pip install tornado
sudo pip install pyelliptic
sudo pip install pymongo
sudo pip install pycountry

echo 'use openbazaar' | mongo
