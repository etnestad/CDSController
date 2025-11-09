# Control Condor dedicated server with the awesome power of Python!

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

## Install Condor:
```
wine <condorinstaller>
wine <update>
...
```  
## The scripts:
start.py is run from shell, which in turn starts c:\cdsc\dscontrol.py inside wine.
C:\cdsc folder should be a symbolic link to a folder containg the scripts.
