@echo off
rem MiraSpeak STOP - SAFE: never touches Explorer/Chrome/browser.
rem Kills ONLY python.exe PIDs that listen on the MiraSpeak port.
rem Detection: .miraspeak.port file, then /api/health signature scan.
rem Usage: stop_miraspeak.bat [all] [nopause]  (all = also stop Ollama)
cd /d "%~dp0"
set BASE_PORT=8000
if not exist .env goto skip_env
for /f "usebackq tokens=1,* delims==" %%A in (`findstr /B /C:"PORT=" ".env"`) do set BASE_PORT=%%B
:skip_env
set KILL_ALL=0
set NOPAUSE=0
if "%1"=="" goto args_done
if /i "%1"=="all" set KILL_ALL=1
if /i "%1"=="nopause" set NOPAUSE=1
if "%2"=="" goto args_done
if /i "%2"=="all" set KILL_ALL=1
if /i "%2"=="nopause" set NOPAUSE=1
:args_done
if defined MIRA_NO_PAUSE set NOPAUSE=1
set FOUND=0
set TMPF=%TEMP%\mira_ports.txt
netstat -ano | findstr LISTENING > "%TMPF%"
if not exist .miraspeak.port goto scan_ports
set /p SAVED_PORT=<.miraspeak.port
echo [INFO] Saved port: %SAVED_PORT%
call :kill_port %SAVED_PORT%
:scan_ports
set SCAN_P=%BASE_PORT%
set /a MAX_PORT=%BASE_PORT%+50
:scan_loop
findstr ":%SCAN_P% " "%TMPF%" >nul 2>&1
if errorlevel 1 goto scan_next
curl -s --max-time 2 "http://127.0.0.1:%SCAN_P%/api/health" | findstr llm_provider >nul 2>&1
if errorlevel 1 goto scan_next
call :kill_port %SCAN_P%
:scan_next
set /a SCAN_P+=1
if %SCAN_P% leq %MAX_PORT% goto scan_loop
goto scan_done
:kill_port
for /f "tokens=5" %%Q in ('findstr ":%1 " "%TMPF%"') do call :kill_pid %%Q %1
goto :eof
:kill_pid
tasklist /FI "PID eq %1" | findstr /I python.exe >nul 2>&1
if errorlevel 1 goto :eof
echo [INFO] Stopping MiraSpeak port %2 (python PID %1)...
taskkill /PID %1 /F >nul 2>&1
set FOUND=1
goto :eof
:scan_done
del "%TMPF%" >nul 2>&1
if not "%KILL_ALL%"=="1" goto skip_ollama
taskkill /FI "IMAGENAME eq ollama.exe" /F >nul 2>&1
echo [INFO] Ollama stop requested.
:skip_ollama
if not exist .miraspeak.port goto report
set /p SAVED_PORT=<.miraspeak.port
netstat -ano | findstr LISTENING | findstr ":%SAVED_PORT% " >nul 2>&1
if errorlevel 1 del .miraspeak.port >nul 2>&1
:report
if "%FOUND%"=="1" echo [OK] MiraSpeak stopped.
if not "%FOUND%"=="1" echo [INFO] No MiraSpeak server found.
if "%NOPAUSE%"=="1" exit /b 0
pause
exit /b 0
