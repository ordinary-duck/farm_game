@echo off
chcp 65001 >nul
echo ====================================
echo 清除缓存并重新启动游戏
echo ====================================
echo.

echo 正在清除Python缓存...
if exist __pycache__ rmdir /s /q __pycache__
echo ? 缓存已清除

echo.
echo 正在启动游戏...
python main.py

pause

