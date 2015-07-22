@echo off
set /P nxver=Enter NX version to launch:
call nx_tools launch %nxver%
PAUSE