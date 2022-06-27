@ECHO OFF
IF EXIST venv\ (
GOTO runner
)ELSE (
GOTO installer
)

:runner
ECHO removing old installation...
@RD /S /Q %~dp0venv

:installer
ECHO instaling enviroment...
START /B /WAIT py -m venv venv
ECHO installing libraries...
START /B /WAIT %~dp0venv\Scripts\python.exe -m pip install -r %~dp0req.txt
GOTO starter

:starter
ECHO starting programm...
START /B /WAIT %~dp0venv\Scripts\python.exe %~dp0view.py
GOTO end

:end
echo done