#!/usr/bin/env python2.7
import logging
logging.basicConfig(level=logging.INFO)

import os
import sys
from pydb.executionenvironment import using_py2exe
import pydb.config


def get_main_dir():
    if using_py2exe():
        return os.path.dirname(sys.executable)
    return os.path.dirname(sys.argv[0])


pydb.config.read_config()
os.chdir(os.path.join(get_main_dir(), 'web2py'))
sys.path.append('.')
sys.path.append('gluon')

import web2py.gluon.widget

# commandline for web2py to parse
sys.argv = ['web2py.py', '-a', '12345', '-i', '0.0.0.0']
web2py.gluon.widget.start(cron=True)