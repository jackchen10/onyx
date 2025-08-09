@echo off
REM Onyx 一键部署脚本
REM 完整的安装、配置和启动流程

echo ========================================
echo 🚀 Onyx 一键部署系统
echo ========================================

REM 检查管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo ⚠️  建议以管理员身份运行以避免权限问题
    echo 💡 右键点击脚本选择"以管理员身份运行"
    pause
)

REM 显示系统信息
echo 🖥️  系统信息:
echo    操作系统: %OS%
echo    计算机名: %COMPUTERNAME%
echo    用户名: %USERNAME%
echo    当前目录: %CD%

REM 第一阶段：环境检查
echo.
echo ========================================
echo 📋 第一阶段：环境检查
echo ========================================

REM 检查Python
echo 🐍 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装
    echo 💡 请从 https://python.org 下载并安装Python 3.11+
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version') do echo ✅ Python版本: %%i
)

REM 检查Node.js
echo 🟢 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js 未安装
    echo 💡 请从 https://nodejs.org 下载并安装Node.js 18+
    pause
    exit /b 1
) else (
    for /f %%i in ('node --version') do echo ✅ Node.js版本: %%i
)

REM 检查Git
echo 📦 检查Git环境...
git --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Git 未安装，某些功能可能受限
) else (
    for /f "tokens=3" %%i in ('git --version') do echo ✅ Git版本: %%i
)

echo ✅ 环境检查完成

REM 第二阶段：依赖安装
echo.
echo ========================================
echo 📦 第二阶段：依赖安装
echo ========================================

REM 安装后端依赖
echo 🔧 安装后端依赖...
cd /d "%~dp0..\backend"
if not exist "venv" (
    echo 🏗️  创建Python虚拟环境...
    python -m venv venv
)

echo 🔄 激活虚拟环境...
call venv\Scripts\activate

echo 📥 安装Python依赖包...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 后端依赖安装失败
    pause
    exit /b 1
)
echo ✅ 后端依赖安装完成

REM 安装前端依赖
echo.
echo 🌐 安装前端依赖...
cd /d "%~dp0..\web"
echo 📥 安装Node.js依赖包...
npm install
if errorlevel 1 (
    echo ❌ 前端依赖安装失败
    pause
    exit /b 1
)
echo ✅ 前端依赖安装完成

REM 第三阶段：配置验证
echo.
echo ========================================
echo ⚙️  第三阶段：配置验证
echo ========================================

cd /d "%~dp0"
echo 🔍 运行系统诊断...
python troubleshoot.py
if errorlevel 1 (
    echo ⚠️  发现配置问题，但继续部署...
) else (
    echo ✅ 配置验证通过
)

REM 第四阶段：服务启动
echo.
echo ========================================
echo 🚀 第四阶段：服务启动
echo ========================================

echo 🔧 启动后端服务...
start "Onyx Backend" cmd /k "cd /d %~dp0..\backend && call venv\Scripts\activate && python ..\tests\integration\test_server.py"

echo ⏳ 等待后端服务启动...
timeout /t 10 /nobreak >nul

echo 🌐 启动前端服务...
start "Onyx Frontend" cmd /k "cd /d %~dp0..\web && npm run dev"

echo ⏳ 等待前端服务启动...
timeout /t 15 /nobreak >nul

REM 第五阶段：部署验证
echo.
echo ========================================
echo ✅ 第五阶段：部署验证
echo ========================================

echo 🏥 运行健康检查...
python health_check.py
if errorlevel 1 (
    echo ⚠️  健康检查发现问题
) else (
    echo ✅ 健康检查通过
)

echo.
echo 🧪 运行端到端测试...
python e2e_test.py
if errorlevel 1 (
    echo ⚠️  端到端测试发现问题
) else (
    echo ✅ 端到端测试通过
)

REM 部署完成
echo.
echo ========================================
echo 🎉 Onyx 部署完成！
echo ========================================
echo 📍 前端地址: http://localhost:3000
echo 📍 后端地址: http://localhost:8080
echo 📍 API文档: http://localhost:8080/docs
echo.
echo 🛠️  管理命令:
echo    健康检查: python tests\health_check.py
echo    性能测试: python tests\performance_test.py
echo    系统监控: python tests\monitor_system.py
echo    故障排除: python tests\troubleshoot.py
echo.
echo 🌍 正在打开浏览器...
timeout /t 3 /nobreak >nul
start http://localhost:3000

echo.
echo 💡 提示: 两个服务器窗口将保持运行，关闭窗口将停止服务
pause
