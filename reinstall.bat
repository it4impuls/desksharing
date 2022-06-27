@ECHO OFF
IF EXIST venv\ (
GOTO runner
)ELSE (
GOTO installer
)

:runner
ECHO removing old installation...
@RD /S /Q venv

:installer
ECHO instaling enviroment...
START /B /WAIT py -m venv venv
ECHO installing libraries...
START /B /WAIT venv\Scripts\python.exe -m pip install -r req.txt
GOTO starter

:starter
ECHO starting programm...
START /B /WAIT venv\Scripts\python.exe view.py
GOTO end

:end
echo done