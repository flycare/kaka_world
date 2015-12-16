#!/usr/bin/env python

from twisted.scripts.twistd import run
import os
import sys

try:
    os.unlink('twistd.pid')
except OSError:
    pass
run()