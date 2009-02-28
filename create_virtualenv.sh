#!/bin/bash
UBUNTUTOOLS="tools-ubuntu-8.10.200902281039.tgz"

virtualenv dolomite-env
source dolomite-env/bin/activate
easy_install web.py
easy_install python-memcached
deactivate

wget -c http://cloud.github.com/downloads/cccarey/dolomite/$UBUNTUTOOLS

tar xvf $UBUNTUTOOLS

rm $UBUNTUTOOLS


