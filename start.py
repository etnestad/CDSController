#!/usr/bin/python3
import subprocess
import os
import sys

test_run = 0

if len(sys.argv) == 2 and sys.argv[1] == "test":
    print("TEST RUN!")
    test_run = 1

my_env = os.environ.copy()
my_env['DISPLAY'] = ":1"
my_env['WINEDEBUG'] = "-all"

xvfb = subprocess.Popen(["Xvfb",my_env['DISPLAY'],"-screen","0"," 1600x1200x24"],env=my_env)

if test_run == 1:
    wine = subprocess.Popen(["script","--flush","--return","--quiet","-c wine python 'c:\cdsc\dscontrol.py' test","/home/audun/logg"],env=my_env)
else:
    wine = subprocess.Popen(["script","--flush","--return","--quiet","-c wine python 'c:\cdsc\dscontrol.py'","/home/audun/logg"],env=my_env)

#x11vnc = subprocess.Popen(["x11vnc","-display",":1","-nopw","-quiet","-forever"])

wine.wait()
#x11vnc.kill()
xvfb.kill()
