# Control [Condor3](https://www.condorsoaring.com/) dedicated server with the awesome power of Python!

These scripts makes it possible to run the dedicated server on a Linux machine
by taking advantage of [Wine](https://www.winehq.org/) and the [Python](https://www.python.org/) library [pywinauto](https://github.com/pywinauto/pywinauto)

## Install Wine:
```
apt install wine winetricks
```

## Initialize wineprefix and install required Python libraries:
```
wget https://www.python.org/ftp/python/3.7.5/python-3.7.5.exe
WINEDLLOVERRIDES="mscoree,mshtml=" WINEARCH=win32 wineboot --init
wine python-3.7.5.exe /quiet InstallAllUsers=1 PrependPath=1
wine pip install pywinauto pillow
wine pip uninstall -y comtypes
winetricks directplay
```

## Install Condor3 dedicated server:
Copy whole or parts of the condor3 installation from windows into the wine.
The destination in wine should be ~/.wine/drive_c/condor3.

You need all the files in c:\condor3, c:\condor3\planes folder and the c:\condor3\landscapes folder.
The .dds and .tga files can be deleted from the landscapes folder to save space.

Under ~/.wine/drive_c/condor3, create the folders logs and settings.

### Update registry:
On the windows computer run ``` reg /export HKCU\Software\Condor3 condor3.reg ```
On the Linux computer run ``` wine reg import condor3.reg ```

## The scripts:
The dedicated server is started by running start.py in the Linux shell. This script starts
dscontrol.py inside Wine which in turn starts the dedicated server.
