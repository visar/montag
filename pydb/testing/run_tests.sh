#!/bin/bash

cd $(dirname $(readlink -f $0))
nosetests test*.py
