#!/bin/bash

con_python=`which python`

# install dependencies
${con_python} _dependency.py # no sudo!

# install packages
sudo ${con_python} _install.py # give me sudo!
