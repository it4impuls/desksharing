@ECHO OFF
IF EXIST venv\ (
	GOTO runner
)ELSE (
GOTO installer
)


:installer
ECHO instaling enviroment...
START /B /WAIT py -m venv venv
ECHO installing libraries...
START /B /WAIT venv\Scripts\python.exe -m pip install -r req.txt
GOTO runner

:runner
ECHO starting programm...
START /B /WAIT venv\Scripts\python.exe view.py
GOTO end

:end
echo done
