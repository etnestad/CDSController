#!/usr/bin/python3
import subprocess
import os
import sys
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--vnc",action="store_true",help="Starts a VNC-server")
args, unknown_args = parser.parse_known_args()

my_env = os.environ.copy()
my_env['DISPLAY'] = ":1"
my_env['WINEDEBUG'] = "-all"

xvfb = subprocess.Popen(["Xvfb",my_env['DISPLAY'],"-screen","0"," 1600x1200x24"],env=my_env)

# Find the path to dscontrol.py in Wine
dscontrol_dir = "z:" + str(Path(__file__).resolve().parent)
dscontrol_dir = dscontrol_dir.replace('/','\\')
ds_control_cmd = "-c wine python '" + dscontrol_dir + "\\dscontrol.py' " + " ".join(unknown_args)

wine = subprocess.Popen(["script","--flush","--return","--quiet",ds_control_cmd,"/home/audun/logg"],env=my_env)

if args.vnc:
    x11vnc = subprocess.Popen(["x11vnc","-display",my_env['DISPLAY'],"-nopw","-quiet","-forever"],stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL)

wine.wait()

if args.vnc:
    x11vnc.kill()
    
xvfb.kill()
