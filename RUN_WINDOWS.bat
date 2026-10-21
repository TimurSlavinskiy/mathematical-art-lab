@echo off
setlocal
cd /d "%~dp0"
echo =========================================
echo  HORIZON - Mathematical Art Generator
 echo =========================================
where py >nul 2>nul
if %errorlevel% == 0 (
    set "PY=py -3"
) else (
    set "PY=python"
)
%PY% -m pip install -r requirements.txt
if errorlevel 1 goto :fail
%PY% generate.py
if errorlevel 1 goto :fail
%PY% render_my_formula.py
if errorlevel 1 goto :fail
echo.
echo Images created: horizon.png and my_formula.png
start "" "horizon.png"
pause
exit /b 0
:fail
echo An error occurred. Check that Python 3.10+ is installed.
pause
exit /b 1
