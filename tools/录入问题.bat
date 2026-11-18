@echo off
chcp 65001 >nul
cd /d "%~dp0.."
set /p title=请输入问题标题（一句话）:
if "%title%"=="" goto :eof
python tools\kb.py new "%title%"
echo.
pause