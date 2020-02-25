#!/usr/bin/python3
import subprocess
import os
import sys



print("CDSController launcher:")
test_run = 0
if len(sys.argv) == 2 and sys.argv[1] == "test":
    test_run = 1

my_env = os.environ.copy()
my_env['DISPLAY'] = ":1"
my_env['WINEDEBUG'] = "-all"

print("* Starting Xvfb")
xvfb = subprocess.Popen(["Xvfb",my_env['DISPLAY']],env=my_env)

print("* Starting dscontrol.py in Wine")
if test_run == 1:
    wine = subprocess.Popen(["script","--return","--quiet","-c wine python 'c:\cdsc\dscontrol.py' test","/home/audun/logg"],env=my_env)
else:
    wine = subprocess.Popen(["script","--return","--quiet","-c wine python 'c:\cdsc\dscontrol.py'","/home/audun/logg"],env=my_env)

print("* Starting x11vnc")
x11vnc = subprocess.Popen(["x11vnc","-display",my_env['DISPLAY'],"-nopw","-quiet","-forever","-viewonly"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)

wine.wait()
x11vnc.kill()
xvfb.kill()
