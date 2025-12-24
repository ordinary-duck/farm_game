@echo off
chcp 65001
echo ========================================
echo   农场物语 - 环境配置
echo ========================================
echo.
echo 正在安装依赖...
echo.

pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo 依赖安装失败！
    echo 请检查Python和pip是否正确安装。
    echo.
) else (
    echo.
    echo ========================================
    echo 依赖安装成功！
    echo ========================================
    echo.
    echo 下一步：
    echo 1. 编辑config.py配置数据库连接
    echo 2. 确保SQL Server正在运行
    echo 3. 运行 run_game.bat 启动游戏
    echo.
)

pause

