@ECHO OFF
SET env_foldername=venv
SET modulefile=req.txt
SET runfile=view.py

SET root=%~dp0

IF EXIST %env_foldername%\ (
GOTO runner
)ELSE (
GOTO installer
)

:runner
ECHO removing old installation...
@RD /S /Q %root%%env_foldername%

:installer
ECHO instaling enviroment (this might take a few minutes)...
START /B /WAIT py -m venv %env_foldername%
ECHO installing libraries...
IF EXIST %root%%modulefile% START /B /WAIT %root%%env_foldername%\Scripts\python.exe -m pip install -r %root%%modulefile%
GOTO starter

:starter
ECHO starting programm...
START /B /WAIT %root%%env_foldername%\Scripts\python.exe %root%%runfile%
GOTO end

:end
echo done