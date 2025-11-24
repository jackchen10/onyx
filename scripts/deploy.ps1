#!/usr/bin/env pwsh
# Onyx Docker 部署脚本
# 适用于Windows Docker Desktop环境

param(
    [string]$Action = "deploy",
    [switch]$Build = $false,
    [switch]$Clean = $false,
    [switch]$Logs = $false,
    [string]$Service = ""
)

# 颜色输出函数
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green $args }
function Write-Warning { Write-ColorOutput Yellow $args }
function Write-Error { Write-ColorOutput Red $args }
function Write-Info { Write-ColorOutput Cyan $args }

# 检查Docker环境
function Test-DockerEnvironment {
    Write-Info "🔍 检查Docker环境..."
    
    try {
        $dockerVersion = docker version --format "{{.Server.Version}}" 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Docker运行正常 (版本: $dockerVersion)"
        } else {
            throw "Docker未运行"
        }
    } catch {
        Write-Error "❌ Docker未运行，请启动Docker Desktop"
        exit 1
    }

    try {
        $composeVersion = docker-compose version --short 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Docker Compose可用 (版本: $composeVersion)"
        } else {
            throw "Docker Compose不可用"
        }
    } catch {
        Write-Error "❌ Docker Compose不可用"
        exit 1
    }

    # 检查Docker Desktop资源配置
    $dockerInfo = docker system info --format "{{json .}}" | ConvertFrom-Json
    $memoryGB = [math]::Round($dockerInfo.MemTotal / 1GB, 1)
    $cpus = $dockerInfo.NCPU
    
    Write-Info "📊 Docker资源配置:"
    Write-Info "   - 内存: $memoryGB GB"
    Write-Info "   - CPU: $cpus 核心"
    
    if ($memoryGB -lt 6) {
        Write-Warning "⚠️ 建议分配至少8GB内存给Docker Desktop"
    }
}

# 创建必要的目录
function Initialize-Directories {
    Write-Info "📁 创建必要的目录..."
    
    $directories = @(
        "data/postgres",
        "data/redis", 
        "data/model_cache",
        "logs",
        "docker/nginx/conf.d",
        "docker/postgres"
    )

    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Success "✅ 创建目录: $dir"
        }
    }
}

# 检查环境配置
function Test-Configuration {
    Write-Info "⚙️ 检查配置文件..."
    
    # 检查必要的配置文件
    $requiredFiles = @(
        "docker-compose.yml",
        "docker/Dockerfile.backend",
        "docker/Dockerfile.web",
        "docker/nginx/nginx.conf"
    )
    
    foreach ($file in $requiredFiles) {
        if (!(Test-Path $file)) {
            Write-Error "❌ 缺少必要文件: $file"
            exit 1
        }
    }
    
    # 检查环境变量文件
    if (!(Test-Path "backend/.env")) {
        Write-Warning "⚠️ 未找到backend/.env文件，将使用默认配置"
        
        # 创建基本的.env文件
        $envContent = @"
# Onyx环境配置
DATABASE_URL=postgresql://onyx_user:onyx_password@postgres:5432/onyx
REDIS_URL=redis://redis:6379/0
MODEL_SERVER_URL=http://model-server:9000

# 安全配置
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# 日志配置
LOG_LEVEL=INFO

# AI模型配置
OPENAI_API_KEY=your-openai-api-key-here
"@
        $envContent | Out-File -FilePath "backend/.env" -Encoding UTF8
        Write-Info "📝 已创建基本的.env文件，请根据需要修改配置"
    }
    
    Write-Success "✅ 配置检查完成"
}

# 构建镜像
function Build-Images {
    Write-Info "🔨 构建Docker镜像..."
    
    $buildArgs = @()
    if ($Clean) {
        $buildArgs += "--no-cache"
    }
    
    try {
        docker-compose build @buildArgs
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ 镜像构建成功"
        } else {
            throw "镜像构建失败"
        }
    } catch {
        Write-Error "❌ 镜像构建失败"
        exit 1
    }
}

# 启动服务
function Start-Services {
    Write-Info "🚀 启动服务..."
    
    try {
        # 首先启动基础服务
        Write-Info "📊 启动数据库和缓存服务..."
        docker-compose up -d postgres redis
        
        # 等待数据库启动
        Write-Info "⏳ 等待数据库启动..."
        $timeout = 60
        $elapsed = 0
        do {
            Start-Sleep -Seconds 2
            $elapsed += 2
            $dbReady = docker-compose exec -T postgres pg_isready -U onyx_user -d onyx 2>$null
        } while ($LASTEXITCODE -ne 0 -and $elapsed -lt $timeout)
        
        if ($elapsed -ge $timeout) {
            Write-Error "❌ 数据库启动超时"
            exit 1
        }
        
        Write-Success "✅ 数据库已就绪"
        
        # 启动应用服务
        Write-Info "🔧 启动应用服务..."
        docker-compose up -d
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ 所有服务启动成功"
        } else {
            throw "服务启动失败"
        }
    } catch {
        Write-Error "❌ 服务启动失败"
        Show-ServiceStatus
        exit 1
    }
}

# 运行数据库迁移
function Invoke-DatabaseMigration {
    Write-Info "🗄️ 运行数据库迁移..."
    
    # 等待API服务启动
    Write-Info "⏳ 等待API服务启动..."
    $timeout = 120
    $elapsed = 0
    do {
        Start-Sleep -Seconds 3
        $elapsed += 3
        $apiReady = docker-compose exec -T api-backend curl -f http://localhost:8080/health 2>$null
    } while ($LASTEXITCODE -ne 0 -and $elapsed -lt $timeout)
    
    if ($elapsed -ge $timeout) {
        Write-Warning "⚠️ API服务启动超时，跳过数据库迁移"
        return
    }
    
    try {
        docker-compose exec api-backend alembic upgrade head
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ 数据库迁移完成"
        } else {
            Write-Warning "⚠️ 数据库迁移失败，可能需要手动处理"
        }
    } catch {
        Write-Warning "⚠️ 数据库迁移执行失败"
    }
}

# 显示服务状态
function Show-ServiceStatus {
    Write-Info "📊 服务状态:"
    docker-compose ps
    
    Write-Info "`n🌐 访问地址:"
    Write-Info "  - 前端应用: http://localhost"
    Write-Info "  - API文档: http://localhost/api/docs"
    Write-Info "  - 数据库: localhost:5432"
    Write-Info "  - Redis: localhost:6379"
    Write-Info "  - 直接API: http://localhost:8080"
    Write-Info "  - 直接前端: http://localhost:3000"
}

# 显示日志
function Show-Logs {
    if ($Service) {
        Write-Info "📋 显示 $Service 服务日志:"
        docker-compose logs -f $Service
    } else {
        Write-Info "📋 显示所有服务日志:"
        docker-compose logs -f
    }
}

# 停止服务
function Stop-Services {
    Write-Info "🛑 停止服务..."
    docker-compose down
    
    if ($Clean) {
        Write-Warning "🧹 清理数据卷..."
        docker-compose down -v
        docker system prune -f
    }
    
    Write-Success "✅ 服务已停止"
}

# 主函数
function Main {
    Write-Success "🚀 Onyx Docker 部署脚本"
    Write-Info "操作: $Action"
    
    switch ($Action.ToLower()) {
        "deploy" {
            Test-DockerEnvironment
            Initialize-Directories
            Test-Configuration
            
            if ($Build -or $Clean) {
                Build-Images
            }
            
            Start-Services
            Start-Sleep -Seconds 10
            Invoke-DatabaseMigration
            Show-ServiceStatus
        }
        
        "build" {
            Test-DockerEnvironment
            Initialize-Directories
            Build-Images
        }
        
        "start" {
            Test-DockerEnvironment
            Start-Services
            Show-ServiceStatus
        }
        
        "stop" {
            Stop-Services
        }
        
        "restart" {
            Stop-Services
            Start-Sleep -Seconds 5
            Start-Services
            Show-ServiceStatus
        }
        
        "status" {
            Show-ServiceStatus
        }
        
        "logs" {
            Show-Logs
        }
        
        "clean" {
            Write-Warning "🧹 清理所有容器和数据..."
            docker-compose down -v
            docker system prune -af
            Write-Success "✅ 清理完成"
        }
        
        default {
            Write-Error "❌ 未知操作: $Action"
            Write-Info "可用操作: deploy, build, start, stop, restart, status, logs, clean"
            exit 1
        }
    }
}

# 错误处理
trap {
    Write-Error "❌ 脚本执行出错: $_"
    exit 1
}

# 执行主函数
Main
