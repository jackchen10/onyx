# Onyx Docker 容器化部署完整方案

## 项目概述

本方案将Onyx项目完全容器化，支持在Windows Docker Desktop环境中一键部署，包含前端、后端、数据库、缓存、AI模型服务等所有组件。

## 容器架构设计

### 服务拆分策略
```
onyx-system/
├── web-frontend/          # Next.js前端服务
├── api-backend/           # FastAPI后端API
├── model-server/          # AI模型推理服务
├── worker-celery/         # Celery后台任务
├── database-postgres/     # PostgreSQL数据库
├── cache-redis/           # Redis缓存
├── proxy-nginx/           # Nginx反向代理
└── monitoring/            # 监控服务(可选)
```

### 容器依赖关系
```mermaid
graph LR
    A[nginx-proxy] --> B[web-frontend]
    A --> C[api-backend]
    A --> D[model-server]
    C --> E[database-postgres]
    C --> F[cache-redis]
    D --> F
    G[worker-celery] --> E
    G --> F
```

## Docker镜像构建

### 1. 前端镜像 (Next.js)

#### Dockerfile.web
```dockerfile
# 多阶段构建 - 构建阶段
FROM node:18-alpine AS builder

WORKDIR /app

# 复制package文件
COPY web/package.json web/yarn.lock ./

# 安装依赖
RUN yarn install --frozen-lockfile

# 复制源代码
COPY web/ .

# 构建应用
RUN yarn build

# 生产阶段
FROM nginx:alpine AS runner

# 复制构建产物
COPY --from=builder /app/out /usr/share/nginx/html

# 复制nginx配置
COPY docker/nginx/web.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 2. 后端API镜像 (FastAPI)

#### Dockerfile.backend
```dockerfile
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements文件
COPY backend/requirements/ ./requirements/

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements/default.txt

# 复制应用代码
COPY backend/ .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["uvicorn", "onyx.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### 3. AI模型服务镜像

#### Dockerfile.model-server
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制模型服务相关文件
COPY backend/requirements/ ./requirements/
COPY backend/model_server/ ./model_server/
COPY backend/onyx/llm/ ./onyx/llm/
COPY backend/onyx/utils/ ./onyx/utils/

# 安装依赖
RUN pip install --no-cache-dir -r requirements/default.txt

# 创建模型缓存目录
RUN mkdir -p /app/model_cache
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# 暴露端口
EXPOSE 9000

# 启动模型服务
CMD ["python", "-m", "model_server.main"]
```

### 4. Celery Worker镜像

#### Dockerfile.worker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制requirements和代码
COPY backend/requirements/ ./requirements/
COPY backend/ .

# 安装依赖
RUN pip install --no-cache-dir -r requirements/default.txt

# 创建用户
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# 启动Celery Worker
CMD ["celery", "-A", "onyx.background.celery_app", "worker", "--loglevel=info"]
```

## Docker Compose 编排

### docker-compose.yml
```yaml
version: '3.8'

services:
  # PostgreSQL数据库
  postgres:
    image: postgres:14-alpine
    container_name: onyx-postgres
    environment:
      POSTGRES_DB: onyx
      POSTGRES_USER: onyx_user
      POSTGRES_PASSWORD: onyx_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - onyx-network
    restart: unless-stopped

  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: onyx-redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - onyx-network
    restart: unless-stopped

  # 后端API服务
  api-backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    container_name: onyx-api
    environment:
      - DATABASE_URL=postgresql://onyx_user:onyx_password@postgres:5432/onyx
      - REDIS_URL=redis://redis:6379/0
      - MODEL_SERVER_URL=http://model-server:9000
    volumes:
      - app_logs:/app/logs
      - ./backend/.env:/app/.env
    ports:
      - "8080:8080"
    depends_on:
      - postgres
      - redis
    networks:
      - onyx-network
    restart: unless-stopped

  # AI模型服务
  model-server:
    build:
      context: .
      dockerfile: docker/Dockerfile.model-server
    container_name: onyx-model-server
    environment:
      - REDIS_URL=redis://redis:6379/1
    volumes:
      - model_cache:/app/model_cache
    ports:
      - "9000:9000"
    depends_on:
      - redis
    networks:
      - onyx-network
    restart: unless-stopped

  # Celery Worker
  celery-worker:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    container_name: onyx-worker
    environment:
      - DATABASE_URL=postgresql://onyx_user:onyx_password@postgres:5432/onyx
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - app_logs:/app/logs
    depends_on:
      - postgres
      - redis
    networks:
      - onyx-network
    restart: unless-stopped

  # 前端Web服务
  web-frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.web
    container_name: onyx-web
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8080
    ports:
      - "3000:80"
    depends_on:
      - api-backend
    networks:
      - onyx-network
    restart: unless-stopped

  # Nginx反向代理
  nginx-proxy:
    image: nginx:alpine
    container_name: onyx-nginx
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./docker/nginx/conf.d:/etc/nginx/conf.d
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web-frontend
      - api-backend
    networks:
      - onyx-network
    restart: unless-stopped

# 数据卷定义
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  app_logs:
    driver: local
  model_cache:
    driver: local

# 网络定义
networks:
  onyx-network:
    driver: bridge
```

## 配置文件

### Nginx配置

#### docker/nginx/nginx.conf
```nginx
events {
    worker_connections 1024;
}

http {
    upstream api_backend {
        server api-backend:8080;
    }
    
    upstream model_server {
        server model-server:9000;
    }
    
    upstream web_frontend {
        server web-frontend:80;
    }

    # 包含具体的服务配置
    include /etc/nginx/conf.d/*.conf;
}
```

#### docker/nginx/conf.d/default.conf
```nginx
server {
    listen 80;
    server_name localhost;

    # 前端静态文件
    location / {
        proxy_pass http://web_frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API接口
    location /api/ {
        proxy_pass http://api_backend/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 模型服务接口
    location /model/ {
        proxy_pass http://model_server/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 数据库初始化

#### docker/postgres/init.sql
```sql
-- 创建数据库和用户
CREATE DATABASE onyx;
CREATE USER onyx_user WITH PASSWORD 'onyx_password';
GRANT ALL PRIVILEGES ON DATABASE onyx TO onyx_user;

-- 连接到onyx数据库
\c onyx;

-- 创建必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 授权
GRANT ALL ON SCHEMA public TO onyx_user;
```

## Windows Docker Desktop 优化

### 1. 资源配置
```json
{
  "memoryMiB": 8192,
  "cpus": 4,
  "swapMiB": 2048,
  "diskSizeMiB": 102400
}
```

### 2. WSL2 优化
```bash
# .wslconfig文件配置
[wsl2]
memory=8GB
processors=4
swap=2GB
```

### 3. Docker Desktop设置
- 启用WSL2集成
- 配置文件共享目录
- 启用Kubernetes (可选)
- 配置代理设置 (如需要)

## 部署脚本

### Windows PowerShell部署脚本

#### deploy.ps1
```powershell
#!/usr/bin/env pwsh

Write-Host "🚀 开始部署Onyx Docker容器..." -ForegroundColor Green

# 检查Docker是否运行
try {
    docker version | Out-Null
    Write-Host "✅ Docker运行正常" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker未运行，请启动Docker Desktop" -ForegroundColor Red
    exit 1
}

# 检查Docker Compose
try {
    docker-compose version | Out-Null
    Write-Host "✅ Docker Compose可用" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose不可用" -ForegroundColor Red
    exit 1
}

# 创建必要的目录
$directories = @(
    "docker/nginx/conf.d",
    "docker/postgres",
    "logs"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
        Write-Host "📁 创建目录: $dir" -ForegroundColor Cyan
    }
}

# 停止现有容器
Write-Host "🛑 停止现有容器..." -ForegroundColor Yellow
docker-compose down

# 构建镜像
Write-Host "🔨 构建Docker镜像..." -ForegroundColor Yellow
docker-compose build --no-cache

# 启动服务
Write-Host "🚀 启动服务..." -ForegroundColor Yellow
docker-compose up -d

# 等待服务启动
Write-Host "⏳ 等待服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# 检查服务状态
Write-Host "📊 检查服务状态..." -ForegroundColor Yellow
docker-compose ps

# 运行数据库迁移
Write-Host "🗄️ 运行数据库迁移..." -ForegroundColor Yellow
docker-compose exec api-backend alembic upgrade head

Write-Host "🎉 部署完成!" -ForegroundColor Green
Write-Host "🌐 访问地址:" -ForegroundColor Cyan
Write-Host "  - 前端: http://localhost" -ForegroundColor White
Write-Host "  - API文档: http://localhost/api/docs" -ForegroundColor White
Write-Host "  - 数据库: localhost:5432" -ForegroundColor White
Write-Host "  - Redis: localhost:6379" -ForegroundColor White
```

## 镜像打包和分发

### 1. 镜像导出脚本

#### export-images.ps1
```powershell
#!/usr/bin/env pwsh

Write-Host "📦 开始导出Docker镜像..." -ForegroundColor Green

# 创建导出目录
$exportDir = "docker-images"
if (!(Test-Path $exportDir)) {
    New-Item -ItemType Directory -Path $exportDir -Force
}

# 定义要导出的镜像
$images = @(
    "onyx-api",
    "onyx-web",
    "onyx-model-server",
    "onyx-worker",
    "postgres:14-alpine",
    "redis:7-alpine",
    "nginx:alpine"
)

# 导出每个镜像
foreach ($image in $images) {
    $filename = "$exportDir/$($image -replace ':', '_' -replace '/', '_').tar"
    Write-Host "📤 导出镜像: $image -> $filename" -ForegroundColor Cyan
    docker save -o $filename $image

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 成功导出: $image" -ForegroundColor Green
    } else {
        Write-Host "❌ 导出失败: $image" -ForegroundColor Red
    }
}

# 创建导入脚本
$importScript = @"
#!/usr/bin/env pwsh
Write-Host "📥 开始导入Docker镜像..." -ForegroundColor Green

`$images = Get-ChildItem -Path "docker-images" -Filter "*.tar"
foreach (`$image in `$images) {
    Write-Host "📥 导入镜像: `$(`$image.Name)" -ForegroundColor Cyan
    docker load -i `$image.FullName
}

Write-Host "🎉 镜像导入完成!" -ForegroundColor Green
"@

$importScript | Out-File -FilePath "$exportDir/import-images.ps1" -Encoding UTF8

Write-Host "🎉 镜像导出完成!" -ForegroundColor Green
Write-Host "📁 导出目录: $exportDir" -ForegroundColor Cyan
Write-Host "💡 使用 $exportDir/import-images.ps1 导入镜像" -ForegroundColor Yellow
```

### 2. 完整部署包创建

#### create-deployment-package.ps1
```powershell
#!/usr/bin/env pwsh

Write-Host "📦 创建完整部署包..." -ForegroundColor Green

$packageName = "onyx-docker-deployment-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$packageDir = "deployment-packages/$packageName"

# 创建包目录
New-Item -ItemType Directory -Path $packageDir -Force

# 复制必要文件
$filesToCopy = @(
    "docker-compose.yml",
    "docker/",
    "deployment/docker_compose/env.dev.template",
    "docs/Docker容器化部署方案.md"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Copy-Item -Path $file -Destination $packageDir -Recurse -Force
        Write-Host "📄 复制文件: $file" -ForegroundColor Cyan
    }
}

# 导出镜像到包中
& "./export-images.ps1"
Move-Item -Path "docker-images" -Destination "$packageDir/" -Force

# 创建部署说明
$deploymentGuide = @"
# Onyx Docker 部署包

## 部署步骤

1. 确保Docker Desktop已安装并运行
2. 导入Docker镜像:
   ```powershell
   cd docker-images
   ./import-images.ps1
   ```

3. 配置环境变量:
   ```powershell
   cp env.dev.template .env
   # 编辑.env文件配置必要参数
   ```

4. 启动服务:
   ```powershell
   docker-compose up -d
   ```

5. 访问应用:
   - 前端: http://localhost
   - API: http://localhost/api/docs

## 包含内容

- Docker镜像文件 (docker-images/)
- Docker Compose配置 (docker-compose.yml)
- Nginx配置文件 (docker/nginx/)
- 数据库初始化脚本 (docker/postgres/)
- 环境变量模板 (env.dev.template)
- 部署文档 (Docker容器化部署方案.md)

## 系统要求

- Windows 10/11 with Docker Desktop
- 最少8GB RAM
- 最少20GB可用磁盘空间
- WSL2支持

生成时间: $(Get-Date)
"@

$deploymentGuide | Out-File -FilePath "$packageDir/README.md" -Encoding UTF8

# 创建压缩包
Compress-Archive -Path $packageDir -DestinationPath "$packageDir.zip" -Force

Write-Host "🎉 部署包创建完成!" -ForegroundColor Green
Write-Host "📦 包位置: $packageDir.zip" -ForegroundColor Cyan
Write-Host "📊 包大小: $([math]::Round((Get-Item "$packageDir.zip").Length / 1MB, 2)) MB" -ForegroundColor Yellow
```

## 监控和日志

### 1. 日志聚合配置

#### docker-compose.logging.yml
```yaml
version: '3.8'

services:
  # 日志聚合服务
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    container_name: onyx-elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    networks:
      - onyx-network

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    container_name: onyx-kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - onyx-network

  # 日志收集
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.8.0
    container_name: onyx-filebeat
    volumes:
      - ./docker/filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml
      - app_logs:/var/log/app
    depends_on:
      - elasticsearch
    networks:
      - onyx-network

volumes:
  elasticsearch_data:
    driver: local
```

### 2. 健康检查配置

在docker-compose.yml中添加健康检查:
```yaml
services:
  api-backend:
    # ... 其他配置
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    # ... 其他配置
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U onyx_user -d onyx"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    # ... 其他配置
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 性能优化

### 1. 镜像优化
- 使用多阶段构建减少镜像大小
- 使用alpine基础镜像
- 清理不必要的包和缓存
- 使用.dockerignore排除不需要的文件

### 2. 资源限制
```yaml
services:
  api-backend:
    # ... 其他配置
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 3. 缓存策略
- 使用Docker层缓存
- 配置Redis持久化
- 使用CDN加速静态资源

## 安全配置

### 1. 网络安全
```yaml
networks:
  onyx-network:
    driver: bridge
    internal: true  # 内部网络，不暴露到外部

  public-network:
    driver: bridge  # 只有nginx暴露到公网
```

### 2. 密钥管理
```yaml
secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt

services:
  api-backend:
    secrets:
      - db_password
      - jwt_secret
```

### 3. 用户权限
- 所有容器使用非root用户运行
- 最小权限原则
- 定期更新基础镜像

## 故障排除

### 常见问题解决

1. **容器启动失败**
   ```powershell
   # 查看容器日志
   docker-compose logs [service-name]

   # 检查容器状态
   docker-compose ps
   ```

2. **数据库连接失败**
   ```powershell
   # 检查数据库容器
   docker-compose exec postgres psql -U onyx_user -d onyx
   ```

3. **端口冲突**
   ```powershell
   # 检查端口占用
   netstat -an | findstr :8080
   ```

4. **内存不足**
   ```powershell
   # 增加Docker Desktop内存限制
   # 或减少并发容器数量
   ```

## 备份和恢复

### 数据备份脚本
```powershell
# backup.ps1
$backupDir = "backups/$(Get-Date -Format 'yyyyMMdd-HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force

# 备份数据库
docker-compose exec postgres pg_dump -U onyx_user onyx > "$backupDir/database.sql"

# 备份Redis数据
docker-compose exec redis redis-cli BGSAVE
docker cp onyx-redis:/data/dump.rdb "$backupDir/redis.rdb"

# 备份应用日志
Copy-Item -Path "logs/" -Destination "$backupDir/logs/" -Recurse

Write-Host "✅ 备份完成: $backupDir"
```

---

**最后更新**: 2025-02-19
**适用环境**: Windows Docker Desktop
**版本要求**: Docker 20.10+, Docker Compose 2.0+
