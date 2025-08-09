@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: Onyx Windows 自动安装脚本
:: 适用于 Windows 10/11

echo ========================================
echo    Onyx 项目 Windows 自动安装脚本
echo ========================================
echo.

:: 设置颜色
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    echo %GREEN%✓ 以管理员权限运行%NC%
) else (
    echo %YELLOW%⚠ 建议以管理员权限运行此脚本%NC%
    echo   某些操作可能需要管理员权限
    pause
)

echo.
echo %BLUE%步骤 1: 检查系统环境%NC%
echo ----------------------------------------

:: 检查 Python
echo 检查 Python 安装...
python --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo %GREEN%✓ Python 已安装: !PYTHON_VERSION!%NC%
    
    :: 检查 Python 版本
    for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
        set MAJOR=%%a
        set MINOR=%%b
    )
    if !MAJOR! LSS 3 (
        echo %RED%✗ Python 版本过低，需要 Python 3.11+%NC%
        goto :python_install
    )
    if !MAJOR! EQU 3 if !MINOR! LSS 11 (
        echo %RED%✗ Python 版本过低，需要 Python 3.11+%NC%
        goto :python_install
    )
    echo %GREEN%✓ Python 版本符合要求%NC%
) else (
    echo %RED%✗ Python 未安装%NC%
    goto :python_install
)
goto :check_node

:python_install
echo.
echo %YELLOW%Python 3.11+ 未安装或版本过低%NC%
echo 请手动安装 Python 3.11+:
echo 1. 访问 https://www.python.org/downloads/
echo 2. 下载并安装 Python 3.11 或更高版本
echo 3. 安装时勾选 "Add Python to PATH"
echo 4. 重新运行此脚本
pause
exit /b 1

:check_node
:: 检查 Node.js
echo.
echo 检查 Node.js 安装...
node --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
    echo %GREEN%✓ Node.js 已安装: !NODE_VERSION!%NC%
    
    :: 检查 Node.js 版本 (去掉 v 前缀)
    set NODE_VERSION=!NODE_VERSION:~1!
    for /f "tokens=1,2 delims=." %%a in ("!NODE_VERSION!") do (
        set MAJOR=%%a
        set MINOR=%%b
    )
    if !MAJOR! LSS 18 (
        echo %RED%✗ Node.js 版本过低，需要 Node.js 18.18.0+%NC%
        goto :node_install
    )
    if !MAJOR! EQU 18 if !MINOR! LSS 18 (
        echo %RED%✗ Node.js 版本过低，需要 Node.js 18.18.0+%NC%
        goto :node_install
    )
    echo %GREEN%✓ Node.js 版本符合要求%NC%
) else (
    echo %RED%✗ Node.js 未安装%NC%
    goto :node_install
)
goto :check_git

:node_install
echo.
echo %YELLOW%Node.js 18.18.0+ 未安装或版本过低%NC%
echo 请手动安装 Node.js:
echo 1. 访问 https://nodejs.org/
echo 2. 下载并安装 LTS 版本 (推荐 20.x)
echo 3. 重新运行此脚本
pause
exit /b 1

:check_git
:: 检查 Git
echo.
echo 检查 Git 安装...
git --version >nul 2>&1
if %errorLevel% == 0 (
    for /f "tokens=3" %%i in ('git --version') do set GIT_VERSION=%%i
    echo %GREEN%✓ Git 已安装: !GIT_VERSION!%NC%
) else (
    echo %YELLOW%⚠ Git 未安装，建议安装 Git 以便版本控制%NC%
    echo   访问 https://git-scm.com/download/win 下载安装
)

echo.
echo %BLUE%步骤 2: 设置项目目录%NC%
echo ----------------------------------------

:: 获取当前目录
set "PROJECT_DIR=%CD%"
echo 项目目录: %PROJECT_DIR%

:: 检查是否在正确的目录
if not exist "backend" (
    echo %RED%✗ 未找到 backend 目录%NC%
    echo   请确保在 Onyx 项目根目录运行此脚本
    pause
    exit /b 1
)

if not exist "web" (
    echo %RED%✗ 未找到 web 目录%NC%
    echo   请确保在 Onyx 项目根目录运行此脚本
    pause
    exit /b 1
)

echo %GREEN%✓ 项目目录结构正确%NC%

echo.
echo %BLUE%步骤 3: 安装后端依赖%NC%
echo ----------------------------------------

cd /d "%PROJECT_DIR%\..\backend"

:: 检查虚拟环境
if exist "venv" (
    echo %GREEN%✓ 虚拟环境已存在%NC%
) else (
    echo 创建 Python 虚拟环境...
    python -m venv venv
    if %errorLevel% == 0 (
        echo %GREEN%✓ 虚拟环境创建成功%NC%
    ) else (
        echo %RED%✗ 虚拟环境创建失败%NC%
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat
if %errorLevel% == 0 (
    echo %GREEN%✓ 虚拟环境激活成功%NC%
) else (
    echo %RED%✗ 虚拟环境激活失败%NC%
    pause
    exit /b 1
)

:: 升级 pip
echo 升级 pip...
python -m pip install --upgrade pip
if %errorLevel% == 0 (
    echo %GREEN%✓ pip 升级成功%NC%
) else (
    echo %YELLOW%⚠ pip 升级失败，继续安装%NC%
)

:: 安装后端依赖
echo.
echo 安装后端依赖 (这可能需要几分钟)...
echo 正在安装核心依赖...
pip install --retries 5 --timeout 60 -r requirements.txt
if %errorLevel% == 0 (
    echo %GREEN%✓ 核心依赖安装成功%NC%
) else (
    echo %RED%✗ 核心依赖安装失败%NC%
    echo 请检查网络连接和错误信息
    pause
    exit /b 1
)

echo 正在安装开发依赖...
echo 正在安装额外开发依赖...
REM pip install --retries 5 --timeout 60 -r requirements/dev.txt
if %errorLevel% == 0 (
    echo %GREEN%✓ 开发依赖安装成功%NC%
) else (
    echo %YELLOW%⚠ 开发依赖安装失败，但不影响核心功能%NC%
)

:: 验证后端安装
echo.
echo 验证后端安装...
python ..\tests\backend\verify_installation.py
if %errorLevel% == 0 (
    echo %GREEN%✓ 后端依赖验证成功%NC%
) else (
    echo %RED%✗ 后端依赖验证失败%NC%
    echo 请查看上述错误信息
    pause
)

echo.
echo %BLUE%步骤 4: 安装前端依赖%NC%
echo ----------------------------------------

cd /d "%PROJECT_DIR%\..\web"

:: 配置 npm (可选)
echo 配置 npm 镜像源...
npm config set registry https://registry.npmmirror.com
echo %GREEN%✓ npm 镜像源配置完成%NC%

:: 安装前端依赖
echo.
echo 安装前端依赖 (这可能需要几分钟)...
npm install
if %errorLevel% == 0 (
    echo %GREEN%✓ 前端依赖安装成功%NC%
) else (
    echo %RED%✗ 前端依赖安装失败%NC%
    echo 尝试清理缓存后重新安装...
    npm cache clean --force
    npm install
    if %errorLevel% == 0 (
        echo %GREEN%✓ 前端依赖安装成功%NC%
    ) else (
        echo %RED%✗ 前端依赖安装仍然失败%NC%
        pause
        exit /b 1
    )
)

:: 验证前端安装
echo.
echo 验证前端安装...
node ..\tests\frontend\verify_installation.js
if %errorLevel% == 0 (
    echo %GREEN%✓ 前端依赖验证成功%NC%
) else (
    echo %RED%✗ 前端依赖验证失败%NC%
    echo 请查看上述错误信息
    pause
)

echo.
echo %BLUE%步骤 5: 创建配置文件%NC%
echo ----------------------------------------

cd /d "%PROJECT_DIR%"

:: 创建后端环境配置
if not exist "backend\.env" (
    echo 创建后端环境配置文件...
    (
        echo # Onyx 后端环境配置
        echo # 数据库配置
        echo POSTGRES_HOST=localhost
        echo POSTGRES_PORT=5432
        echo POSTGRES_DB=onyx
        echo POSTGRES_USER=postgres
        echo POSTGRES_PASSWORD=password
        echo.
        echo # Redis配置
        echo REDIS_HOST=localhost
        echo REDIS_PORT=6379
        echo.
        echo # API配置
        echo API_HOST=0.0.0.0
        echo API_PORT=8080
        echo.
        echo # 日志级别
        echo LOG_LEVEL=INFO
        echo.
        echo # 认证配置
        echo AUTH_TYPE=basic
        echo REQUIRE_EMAIL_VERIFICATION=false
        echo.
        echo # 禁用遥测
        echo DISABLE_TELEMETRY=true
    ) > backend\.env
    echo %GREEN%✓ 后端环境配置文件创建成功%NC%
) else (
    echo %GREEN%✓ 后端环境配置文件已存在%NC%
)

:: 创建前端环境配置
if not exist "web\.env.local" (
    echo 创建前端环境配置文件...
    (
        echo # Onyx 前端环境配置
        echo # API配置
        echo INTERNAL_URL=http://localhost:8080
        echo NEXT_PUBLIC_API_URL=http://localhost:8080
        echo.
        echo # 功能开关
        echo NEXT_PUBLIC_DISABLE_STREAMING=false
        echo NEXT_PUBLIC_NEW_CHAT_DIRECTS_TO_SAME_PERSONA=false
        echo.
        echo # 主题配置
        echo NEXT_PUBLIC_THEME=default
        echo.
        echo # 开发配置
        echo NEXT_TELEMETRY_DISABLED=1
    ) > web\.env.local
    echo %GREEN%✓ 前端环境配置文件创建成功%NC%
) else (
    echo %GREEN%✓ 前端环境配置文件已存在%NC%
)

echo.
echo %GREEN%========================================%NC%
echo %GREEN%    Onyx 安装完成！%NC%
echo %GREEN%========================================%NC%
echo.
echo %BLUE%下一步操作:%NC%
echo.
echo %YELLOW%1. 启动数据库服务:%NC%
echo    - 安装并启动 PostgreSQL
echo    - 安装并启动 Redis
echo    - 或使用 Docker Compose 启动服务
echo.
echo %YELLOW%2. 初始化数据库:%NC%
echo    cd backend
echo    venv\Scripts\activate
echo    alembic upgrade head
echo.
echo %YELLOW%3. 启动后端服务:%NC%
echo    cd backend
echo    venv\Scripts\activate
echo    python -m onyx.main
echo.
echo %YELLOW%4. 启动前端服务 (新终端):%NC%
echo    cd web
echo    npm run dev
echo.
echo %YELLOW%5. 访问应用:%NC%
echo    http://localhost:3000
echo.
echo %BLUE%有用的命令:%NC%
echo    后端验证: cd backend ^&^& python verify_installation.py
echo    前端验证: cd web ^&^& node verify_installation.js
echo    查看日志: 检查终端输出
echo.
echo %GREEN%安装脚本执行完成！%NC%
pause
