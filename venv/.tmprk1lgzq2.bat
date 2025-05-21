@ECHO OFF
@SET PYTHONIOENCODING=utf-8
@SET PYTHONUTF8=1
@FOR /F "tokens=2 delims=:." %%A in ('chcp') do for %%B in (%%A) do set "_CONDA_OLD_CHCP=%%B"
@chcp 65001 > NUL
@CALL "C:\Users\Lenovo\anaconda3\condabin\conda.bat" activate "c:\Users\Lenovo\Desktop\Dummy\venv"
@IF %ERRORLEVEL% NEQ 0 EXIT /b %ERRORLEVEL%
@c:\Users\Lenovo\Desktop\Dummy\venv\python.exe -Wi -m compileall -q -l -i C:\Users\Lenovo\AppData\Local\Temp\tmpit4wkanv -j 0
@IF %ERRORLEVEL% NEQ 0 EXIT /b %ERRORLEVEL%
@chcp %_CONDA_OLD_CHCP%>NUL
