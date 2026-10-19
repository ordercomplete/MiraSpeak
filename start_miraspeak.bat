@echo off
rem MiraSpeak START - auto next free port, health check, open browser
rem Safe: kills nothing, only starts. Stop script never touches Explorer/Chrome.
cd /d "%~dp0"
set HOST=127.0.0.1
set BASE_PORT=8000
if not exist .env goto skip_env
for /f "usebackq tokens=1,* delims==" %%A in (`findstr /B /C:"HOST=" ".env"`) do set HOST=%%B
for /f "usebackq tokens=1,* delims==" %%A in (`findstr /B /C:"PORT=" ".env"`) do set BASE_PORT=%%B
:skip_env
set PORT=%BASE_PORT%
set /a MAX_PORT=%BASE_PORT%+50
:find_free_port
netstat -ano | findstr LISTENING | findstr ":%PORT% " >nul
if errorlevel 1 goto port_is_free
echo [INFO] Port %PORT% busy - trying next
set /a PORT+=1
if %PORT% gtr %MAX_PORT% goto no_port
goto find_free_port
:no_port
echo [ERROR] No free port %BASE_PORT%-%MAX_PORT%. Run stop_miraspeak.bat first.
goto need_pause
:port_is_free
if not "%PORT%"=="%BASE_PORT%" echo [INFO] Base port %BASE_PORT% busy - using %PORT%.
echo %PORT%>.miraspeak.port
if not exist logs mkdir logs
tasklist /FI "IMAGENAME eq ollama.exe" | findstr ollama.exe >nul
if not errorlevel 1 goto ollama_ok
echo [WARN] ollama not running - answers may fail with llm_error.
echo [WARN] Start Ollama manually: ollama serve
goto ollama_done
:ollama_ok
echo [INFO] Ollama already running.
:ollama_done
echo [INFO] Starting MiraSpeak on http://%HOST%:%PORT%/
start "MiraSpeak-%PORT%" /min .\.venv\Scripts\python.exe -m uvicorn app.main:app --host %HOST% --port %PORT%
echo [INFO] Waiting for /api/health ...
set TRIES=0
:health_loop
curl -s -o nul --max-time 2 "http://%HOST%:%PORT%/api/health" >nul
if not errorlevel 1 goto healthy
timeout /t 2 /nobreak >nul
set /a TRIES+=1
if %TRIES% lss 60 goto health_loop
echo [ERROR] No health - see the MiraSpeak server window.
goto need_pause
:healthy
curl -s --max-time 5 "http://%HOST%:%PORT%/api/health"
echo.
echo [OK] Open http://%HOST%:%PORT%/ in browser.
echo [OK] Do NOT open static\index.html via file:// - mic and API need http://127.0.0.1:PORT.
if defined MIRA_NO_BROWSER goto no_browser
start "" "http://%HOST%:%PORT%/"
:no_browser
if defined MIRA_NO_PAUSE goto end_ok
pause
:end_ok
exit /b 0
:need_pause
if defined MIRA_NO_PAUSE exit /b 1
pause
exit /b 1
