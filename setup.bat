@ECHO OFF
IF EXIST venv\ GOTO runner
ELSE GOTO installer


:installer
ECHO instaling enviroment...
START /B /WAIT py -m venv %~dp0venv
ECHO installing libraries...
START /B /WAIT %~dp0venv\Scripts\python.exe -m pip install -r %~dp0req.txt
GOTO runner

:runner
ECHO starting programm...
START /B /WAIT %~dp0venv\Scripts\python.exe %~dp0view.py
GOTO end

:end
echo done
