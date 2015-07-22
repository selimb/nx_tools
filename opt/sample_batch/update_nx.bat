@echo off
set /P nxver=Enter NX version to update:
call nx_tools update %nxver%
PAUSE