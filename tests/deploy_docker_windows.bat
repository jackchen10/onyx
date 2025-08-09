@echo off
REM Onyx Docker 完整部署脚本 - Windows Docker Desktop
REM 部署所有10个Docker容器和中间件服务

echo ========================================
echo 🐳 Onyx Docker 完整部署系统
echo ========================================

REM 检查Docker Desktop
echo 🔍 检查Docker环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker 未安装或未启动
    echo 💡 请安装并启动Docker Desktop for Windows
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose 未安装
    echo 💡 请确保Docker Desktop包含Docker Compose
    pause
    exit /b 1
)

echo ✅ Docker环境检查通过

REM 检查Docker Desktop运行状态
echo 🔍 检查Docker Desktop状态...
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Desktop 未运行
    echo 💡 请启动Docker Desktop应用程序
    pause
    exit /b 1
)

echo ✅ Docker Desktop 运行正常

REM 显示系统资源
echo.
echo 💻 系统资源检查:
for /f "tokens=2 delims=:" %%a in ('wmic computersystem get TotalPhysicalMemory /value ^| find "="') do (
    set /a "ram_gb=%%a/1024/1024/1024"
)
echo    总内存: %ram_gb%GB
if %ram_gb% LSS 16 (
    echo ⚠️  警告: 推荐至少16GB内存，当前可能不足
)

REM 检查磁盘空间
for /f "tokens=3" %%a in ('dir C:\ ^| find "bytes free"') do set free_space=%%a
echo    C盘剩余空间: %free_space% bytes
echo ✅ 资源检查完成

REM 第一阶段：准备配置文件
echo.
echo ========================================
echo ⚙️  第一阶段：准备配置文件
echo ========================================

cd /d "%~dp0.."

REM 检查docker-compose文件
if not exist "deployment\docker_compose\docker-compose.dev.yml" (
    echo ❌ Docker Compose 配置文件缺失
    echo 💡 请确保deployment目录完整
    pause
    exit /b 1
)

echo ✅ Docker Compose 配置文件存在

REM 创建环境配置文件
if not exist ".env" (
    echo 🔧 创建环境配置文件...
    copy deployment\docker_compose\.env.template .env
    echo 💡 请编辑.env文件配置必要的环境变量
    echo    特别是: POSTGRES_PASSWORD, GEN_AI_API_KEY
    pause
)

echo ✅ 环境配置准备完成

REM 第二阶段：拉取Docker镜像
echo.
echo ========================================
echo 📥 第二阶段：拉取Docker镜像
echo ========================================

echo 🐳 拉取基础服务镜像...
docker pull postgres:15.2-alpine
docker pull redis:7.4-alpine
docker pull minio/minio:latest
docker pull vespaengine/vespa:8.526.15
docker pull nginx:1.23.4-alpine

echo ✅ 基础镜像拉取完成

REM 第三阶段：构建应用镜像
echo.
echo ========================================
echo 🏗️  第三阶段：构建应用镜像
echo ========================================

echo 🔧 构建后端镜像...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml build api_server
if errorlevel 1 (
    echo ❌ 后端镜像构建失败
    pause
    exit /b 1
)

echo 🌐 构建前端镜像...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml build web_server
if errorlevel 1 (
    echo ❌ 前端镜像构建失败
    pause
    exit /b 1
)

echo 🤖 构建模型服务器镜像...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml build inference_model_server
if errorlevel 1 (
    echo ❌ 模型服务器镜像构建失败
    pause
    exit /b 1
)

echo ✅ 应用镜像构建完成

REM 第四阶段：启动基础服务
echo.
echo ========================================
echo 🗄️  第四阶段：启动基础服务
echo ========================================

echo 🔧 启动PostgreSQL数据库...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml up -d relational_db
timeout /t 10 /nobreak >nul

echo 🔧 启动Redis缓存...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml up -d cache
timeout /t 5 /nobreak >nul

echo 🔧 启动MinIO文件存储...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml up -d minio
timeout /t 10 /nobreak >nul

echo 🔧 启动Vespa搜索引擎...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml up -d index
timeout /t 30 /nobreak >nul

echo ✅ 基础服务启动完成

REM 第五阶段：启动AI模型服务
echo.
echo ========================================
echo 🤖 第五阶段：启动AI模型服务
echo ========================================

echo 🧠 启动推理模型服务器...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml up -d inference_model_server
timeout /t 30 /nobreak >nul

echo 📚 启动索引模型服务器...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml up -d indexing_model_server
timeout /t 30 /nobreak >nul

echo ✅ AI模型服务启动完成

REM 第六阶段：启动应用服务
echo.
echo ========================================
echo 🚀 第六阶段：启动应用服务
echo ========================================

echo 🔧 启动后端API服务器...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml up -d api_server
timeout /t 20 /nobreak >nul

echo 🔄 启动后台任务处理器...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml up -d background
timeout /t 15 /nobreak >nul

echo 🌐 启动前端Web服务器...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml up -d web_server
timeout /t 20 /nobreak >nul

echo ✅ 应用服务启动完成

REM 第七阶段：启动代理服务
echo.
echo ========================================
echo 🌐 第七阶段：启动代理服务
echo ========================================

echo 🔀 启动Nginx反向代理...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml up -d nginx
timeout /t 10 /nobreak >nul

echo ✅ 代理服务启动完成

REM 第八阶段：验证部署
echo.
echo ========================================
echo ✅ 第八阶段：验证部署
echo ========================================

echo 🔍 检查容器状态...
docker-compose -f deployment\docker_compose\docker-compose.dev.yml ps

echo.
echo 🏥 运行健康检查...
timeout /t 30 /nobreak >nul
python tests\health_check.py

echo.
echo ========================================
echo 🎉 Onyx Docker 部署完成！
echo ========================================
echo.
echo 📍 服务地址:
echo    🌐 前端应用: http://localhost
echo    🔧 后端API: http://localhost/api
echo    📚 API文档: http://localhost/api/docs
echo    💾 MinIO控制台: http://localhost:9005
echo    🔍 Vespa控制台: http://localhost:8081
echo.
echo 🐳 Docker管理命令:
echo    查看状态: docker-compose -f deployment\docker_compose\docker-compose.dev.yml ps
echo    查看日志: docker-compose -f deployment\docker_compose\docker-compose.dev.yml logs
echo    停止服务: docker-compose -f deployment\docker_compose\docker-compose.dev.yml down
echo    重启服务: docker-compose -f deployment\docker_compose\docker-compose.dev.yml restart
echo.
echo 💡 提示: 首次启动可能需要下载AI模型，请耐心等待
echo 🌍 正在打开浏览器...
timeout /t 5 /nobreak >nul
start http://localhost

pause
