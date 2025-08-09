@echo off
REM Onyx 系统智能启动脚本
REM 自动检查环境、启动服务并验证状态

echo ========================================
echo 🚀 Onyx 智能启动系统
echo ========================================

REM 检查环境
echo 🔍 检查系统环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装或不在PATH中
    echo 💡 请安装Python 3.11+并添加到PATH
    pause
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js 未安装或不在PATH中
    echo 💡 请安装Node.js 18+并添加到PATH
    pause
    exit /b 1
)

echo ✅ 基础环境检查通过

REM 运行故障排除检查
echo.
echo 🔧 运行系统诊断...
python troubleshoot.py
if errorlevel 1 (
    echo ⚠️  发现系统问题，请查看上方诊断结果
    echo 💡 建议先解决问题再启动系统
    pause
    exit /b 1
)

echo ✅ 系统诊断通过

REM 启动后端测试服务器
echo.
echo 🔧 启动后端服务器...
start "Onyx Backend" cmd /k "cd /d %~dp0..\backend && echo 🚀 启动后端服务器... && python ..\tests\integration\test_server.py"

REM 等待后端启动并验证
echo ⏳ 等待后端服务器启动...
timeout /t 8 /nobreak >nul

echo 🔍 验证后端服务状态...
python -c "import requests; r=requests.get('http://localhost:8080/health', timeout=5); print('✅ 后端服务正常' if r.status_code==200 else '❌ 后端服务异常')" 2>nul
if errorlevel 1 (
    echo ⚠️  后端服务启动可能有问题，但继续启动前端...
)

REM 启动前端开发服务器
echo.
echo 🌐 启动前端服务器...
start "Onyx Frontend" cmd /k "cd /d %~dp0..\web && echo 🌐 启动前端服务器... && npm run dev"

REM 等待前端启动
echo ⏳ 等待前端服务器启动...
timeout /t 15 /nobreak >nul

REM 运行健康检查
echo.
echo 🏥 运行系统健康检查...
python health_check.py
if errorlevel 1 (
    echo ⚠️  健康检查发现问题，但系统已启动
) else (
    echo ✅ 系统健康检查通过
)

REM 打开浏览器
echo.
echo 🌍 打开浏览器...
timeout /t 2 /nobreak >nul
start http://localhost:3000

echo.
echo ========================================
echo ✅ Onyx 系统启动完成！
echo ========================================
echo 📍 前端地址: http://localhost:3000
echo 📍 后端地址: http://localhost:8080
echo 📍 API文档: http://localhost:8080/docs
echo.
echo 💡 提示:
echo    - 两个命令行窗口将保持打开状态
echo    - 关闭窗口将停止对应的服务器
echo    - 按 Ctrl+C 可以停止服务器
echo.
pause
