@echo off

TASKKILL /f /im nx_tools.exe >NUL 2>&1
TASKKILL /f /im nx_identifier.exe >NUL 2>&1
setlocal ENABLEDELAYEDEXPANSION
set /a counter=1

for %%i in (%~dp0\*.egg) do (
    if !counter! == 2 (
        echo More than one egg?
        goto oops
    )
    set egg=%%i
    set /a counter=!counter!+1
)
if not defined egg (
    echo No Egg found
    goto oops
)
"C:\Python26\Scripts\easy_install.exe" %egg% >NUL
endlocal
echo Installation Complete!
PAUSE
exit /b 0
:oops
PAUSE
exit /b 1