#!/usr/bin/python3
import subprocess
import os
import time

my_env = os.environ.copy()
my_env['DISPLAY'] = ":1"
my_env['WINEDEBUG'] = "-all"

xvfb = subprocess.Popen(["Xvfb",":1","-screen","0"," 1600x1200x24"],env=my_env)

wine = subprocess.Popen(["script","--return","--quiet","-c wine python 'c:\cdsc\dscontrol.py'","/home/audun/logg"],env=my_env)

x11vnc = subprocess.Popen(["x11vnc","-display",":1","-nopw","-quiet","-forever"])

wine.wait()
x11vnc.kill()
xvfb.kill()
