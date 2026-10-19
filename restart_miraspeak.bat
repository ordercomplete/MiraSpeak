@echo off
rem MiraSpeak RESTART - safe stop, then start (port auto-pick lives in start).
rem Usage: restart_miraspeak.bat [all]   (all = also restart Ollama)
cd /d "%~dp0"
if /i "%1"=="all" goto stop_all
call "%~dp0stop_miraspeak.bat" nopause
goto stopped
:stop_all
call "%~dp0stop_miraspeak.bat" all nopause
:stopped
echo ----------------------------------------
timeout /t 3 /nobreak >nul
call "%~dp0start_miraspeak.bat"
exit /b %errorlevel%
