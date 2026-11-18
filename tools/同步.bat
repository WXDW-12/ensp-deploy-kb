@echo off
chcp 65001 >nul
cd /d "%~dp0.."
echo ===== 同步 eNSP 部署知识库 =====
python tools\kb.py pull
echo.
set /p msg=提交说明（可空回车）:
python tools\kb.py push "%msg%"
echo.
pause