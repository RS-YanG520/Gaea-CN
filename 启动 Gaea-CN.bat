@echo off
cd /d "%~dp0"
python tools\launcher.py
if errorlevel 1 (
  echo.
  echo 启动失败。若提示找不到 python，请先安装 Python 并勾选 Add to PATH。
  pause
)
