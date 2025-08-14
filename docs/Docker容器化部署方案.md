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

## Linux服务器生产部署方案

### 完整镜像和容器清单

#### 必需的Docker镜像列表
```yaml
基础镜像 (从Docker Hub拉取):
  - postgres:14-alpine          # 数据库 (~200MB)
  - redis:7-alpine              # 缓存 (~30MB)
  - nginx:alpine                # 反向代理 (~40MB)
  - python:3.11-slim            # Python运行时 (~120MB)
  - node:18-alpine              # Node.js构建环境 (~170MB)

自定义镜像 (需要构建):
  - onyx/api-backend:latest      # FastAPI后端 (~800MB)
  - onyx/model-server:latest     # AI模型服务 (~1.2GB)
  - onyx/celery-worker:latest    # 任务队列 (~800MB)
  - onyx/web-frontend:latest     # Next.js前端 (~100MB)

监控镜像 (可选):
  - prometheus/prometheus:latest # 监控 (~200MB)
  - grafana/grafana:latest       # 可视化 (~300MB)
  - prom/node-exporter:latest    # 节点监控 (~20MB)

总镜像大小: ~4GB (不含AI模型文件)
```

#### 运行时容器列表
```yaml
核心容器 (必需):
  1. onyx-postgres              # PostgreSQL数据库
  2. onyx-redis                 # Redis缓存
  3. onyx-api-backend           # FastAPI API服务
  4. onyx-model-server          # AI模型推理服务
  5. onyx-celery-worker         # Celery后台任务
  6. onyx-web-frontend          # Next.js前端
  7. onyx-nginx-proxy           # Nginx反向代理

监控容器 (可选):
  8. onyx-prometheus            # 监控数据收集
  9. onyx-grafana               # 监控仪表板
  10. onyx-node-exporter        # 系统指标收集

总容器数: 7个核心容器 + 3个监控容器
```

### 服务器资源需求和部署策略

#### 方案1: 单服务器部署 (小规模)
```yaml
服务器配置:
  CPU: 8核心 (Intel Xeon或AMD EPYC)
  内存: 32GB RAM
  存储: 500GB SSD
  网络: 1Gbps
  操作系统: Ubuntu 22.04 LTS

容器分布:
  - 所有7个核心容器部署在同一台服务器
  - 数据持久化使用本地存储卷
  - 适用场景: 100-500用户，小型企业

资源分配:
  PostgreSQL: 4GB RAM, 2核心
  Redis: 2GB RAM, 1核心
  API Backend: 6GB RAM, 2核心
  Model Server: 12GB RAM, 2核心
  Celery Worker: 2GB RAM, 0.5核心
  Web Frontend: 1GB RAM, 0.5核心
  Nginx Proxy: 512MB RAM, 0.5核心
  系统预留: 4.5GB RAM, 0.5核心

预计成本: $2,000-3,000/年 (云服务器)
```

#### 方案2: 双服务器部署 (中等规模)
```yaml
服务器1 - 应用服务器:
  CPU: 8核心
  内存: 32GB RAM
  存储: 300GB SSD
  部署容器:
    - onyx-api-backend
    - onyx-web-frontend
    - onyx-celery-worker
    - onyx-nginx-proxy

服务器2 - 数据和AI服务器:
  CPU: 12核心
  内存: 64GB RAM
  存储: 1TB SSD
  GPU: RTX 4080 (可选)
  部署容器:
    - onyx-postgres
    - onyx-redis
    - onyx-model-server

适用场景: 500-2000用户，中型企业
预计成本: $4,000-6,000/年 (云服务器)
```

#### 方案3: 多服务器集群 (大规模)
```yaml
负载均衡器 (1台):
  CPU: 4核心
  内存: 8GB RAM
  存储: 100GB SSD
  部署: Nginx负载均衡 + SSL终端

应用服务器 (2-3台):
  CPU: 8核心/台
  内存: 32GB RAM/台
  存储: 200GB SSD/台
  部署容器:
    - onyx-api-backend (多实例)
    - onyx-web-frontend
    - onyx-celery-worker

AI模型服务器 (1-2台):
  CPU: 16核心/台
  内存: 64GB RAM/台
  存储: 500GB SSD/台
  GPU: RTX 4090/台
  部署容器:
    - onyx-model-server (多实例)

数据库服务器 (1台主 + 1台从):
  CPU: 12核心
  内存: 64GB RAM
  存储: 2TB SSD (RAID 1)
  部署容器:
    - onyx-postgres (主从复制)
    - onyx-redis (集群模式)

监控服务器 (1台):
  CPU: 4核心
  内存: 16GB RAM
  存储: 500GB SSD
  部署容器:
    - onyx-prometheus
    - onyx-grafana
    - onyx-elasticsearch
    - onyx-kibana

适用场景: 2000+用户，大型企业
预计成本: $15,000-25,000/年 (云服务器)
```

### Linux部署脚本

#### deploy-linux.sh
```bash
#!/bin/bash
# Onyx Linux服务器部署脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo_success() { echo -e "${GREEN}✅ $1${NC}"; }
echo_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
echo_error() { echo -e "${RED}❌ $1${NC}"; }
echo_info() { echo -e "${CYAN}ℹ️ $1${NC}"; }

# 检查系统要求
check_system_requirements() {
    echo_info "检查系统要求..."

    # 检查操作系统
    if [[ ! -f /etc/os-release ]]; then
        echo_error "不支持的操作系统"
        exit 1
    fi

    source /etc/os-release
    echo_success "操作系统: $PRETTY_NAME"

    # 检查CPU核心数
    CPU_CORES=$(nproc)
    if [[ $CPU_CORES -lt 4 ]]; then
        echo_error "CPU核心数不足，最少需要4核心，当前: $CPU_CORES"
        exit 1
    fi
    echo_success "CPU核心: $CPU_CORES"

    # 检查内存
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $MEMORY_GB -lt 16 ]]; then
        echo_error "内存不足，最少需要16GB，当前: ${MEMORY_GB}GB"
        exit 1
    fi
    echo_success "内存: ${MEMORY_GB}GB"

    # 检查磁盘空间
    DISK_GB=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
    if [[ $DISK_GB -lt 50 ]]; then
        echo_error "磁盘空间不足，最少需要50GB，当前可用: ${DISK_GB}GB"
        exit 1
    fi
    echo_success "可用磁盘空间: ${DISK_GB}GB"
}

# 安装Docker
install_docker() {
    echo_info "安装Docker..."

    if command -v docker &> /dev/null; then
        echo_success "Docker已安装: $(docker --version)"
        return
    fi

    # 更新包索引
    sudo apt-get update

    # 安装必要的包
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # 添加Docker官方GPG密钥
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # 设置稳定版仓库
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # 安装Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # 启动Docker服务
    sudo systemctl start docker
    sudo systemctl enable docker

    # 添加当前用户到docker组
    sudo usermod -aG docker $USER

    echo_success "Docker安装完成"
    echo_warning "请重新登录以使docker组权限生效"
}

# 安装Docker Compose
install_docker_compose() {
    echo_info "安装Docker Compose..."

    if command -v docker-compose &> /dev/null; then
        echo_success "Docker Compose已安装: $(docker-compose --version)"
        return
    fi

    # 下载Docker Compose
    COMPOSE_VERSION="2.24.0"
    sudo curl -L "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

    # 设置执行权限
    sudo chmod +x /usr/local/bin/docker-compose

    echo_success "Docker Compose安装完成"
}

# 创建必要目录
create_directories() {
    echo_info "创建必要目录..."

    directories=(
        "data/postgres"
        "data/redis"
        "data/model_cache"
        "logs"
        "docker/nginx/conf.d"
        "docker/postgres"
        "secrets"
    )

    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        echo_success "创建目录: $dir"
    done
}

# 配置环境变量
setup_environment() {
    echo_info "配置环境变量..."

    if [[ ! -f backend/.env ]]; then
        cat > backend/.env << EOF
# Onyx生产环境配置
DATABASE_URL=postgresql://onyx_user:onyx_password@postgres:5432/onyx
REDIS_URL=redis://redis:6379/0
MODEL_SERVER_URL=http://model-server:9000

# 安全配置
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)

# 日志配置
LOG_LEVEL=INFO

# AI模型配置
OPENAI_API_KEY=your-openai-api-key-here
HUGGINGFACE_API_TOKEN=your-huggingface-token-here

# 生产环境标识
ENVIRONMENT=production
EOF
        echo_success "创建环境配置文件"
    else
        echo_success "环境配置文件已存在"
    fi
}

# 部署服务
deploy_services() {
    echo_info "部署服务..."

    # 停止现有服务
    docker-compose down 2>/dev/null || true

    # 构建镜像
    echo_info "构建Docker镜像..."
    docker-compose build --no-cache

    # 启动基础服务
    echo_info "启动数据库和缓存服务..."
    docker-compose up -d postgres redis

    # 等待数据库启动
    echo_info "等待数据库启动..."
    timeout=60
    elapsed=0
    while ! docker-compose exec -T postgres pg_isready -U onyx_user -d onyx &>/dev/null; do
        sleep 2
        elapsed=$((elapsed + 2))
        if [[ $elapsed -ge $timeout ]]; then
            echo_error "数据库启动超时"
            exit 1
        fi
    done
    echo_success "数据库已就绪"

    # 启动应用服务
    echo_info "启动应用服务..."
    docker-compose up -d

    # 等待API服务启动
    echo_info "等待API服务启动..."
    timeout=120
    elapsed=0
    while ! curl -f http://localhost:8080/health &>/dev/null; do
        sleep 3
        elapsed=$((elapsed + 3))
        if [[ $elapsed -ge $timeout ]]; then
            echo_warning "API服务启动超时，跳过数据库迁移"
            break
        fi
    done

    if [[ $elapsed -lt $timeout ]]; then
        # 运行数据库迁移
        echo_info "运行数据库迁移..."
        docker-compose exec api-backend alembic upgrade head
        echo_success "数据库迁移完成"
    fi
}

# 显示部署状态
show_deployment_status() {
    echo_info "部署状态:"
    docker-compose ps

    echo_info ""
    echo_info "访问地址:"
    echo_info "  - 前端应用: http://$(hostname -I | awk '{print $1}')"
    echo_info "  - API文档: http://$(hostname -I | awk '{print $1}')/api/docs"
    echo_info "  - 数据库: $(hostname -I | awk '{print $1}'):5432"
    echo_info "  - Redis: $(hostname -I | awk '{print $1}'):6379"
}

# 主函数
main() {
    echo_success "🚀 Onyx Linux服务器部署脚本"

    check_system_requirements
    install_docker
    install_docker_compose
    create_directories
    setup_environment
    deploy_services
    show_deployment_status

    echo_success "🎉 部署完成!"
}

# 执行主函数
main "$@"
```

### 生产环境Docker Compose配置

#### docker-compose.prod.yml
```yaml
version: '3.8'

services:
  # PostgreSQL数据库 - 主从复制
  postgres-master:
    image: postgres:14-alpine
    container_name: onyx-postgres-master
    environment:
      POSTGRES_DB: onyx
      POSTGRES_USER: onyx_user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
      POSTGRES_REPLICATION_USER: replicator
      POSTGRES_REPLICATION_PASSWORD_FILE: /run/secrets/replication_password
    volumes:
      - postgres_master_data:/var/lib/postgresql/data
      - ./docker/postgres/postgresql.conf:/etc/postgresql/postgresql.conf
      - ./docker/postgres/pg_hba.conf:/etc/postgresql/pg_hba.conf
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - onyx-backend-network
    restart: unless-stopped
    secrets:
      - db_password
      - replication_password
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G

  postgres-slave:
    image: postgres:14-alpine
    container_name: onyx-postgres-slave
    environment:
      POSTGRES_MASTER_SERVICE: postgres-master
      POSTGRES_USER: onyx_user
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
      PGUSER: postgres
    volumes:
      - postgres_slave_data:/var/lib/postgresql/data
    ports:
      - "5433:5432"
    networks:
      - onyx-backend-network
    restart: unless-stopped
    secrets:
      - db_password
      - replication_password
    depends_on:
      - postgres-master

  # Redis集群
  redis-master:
    image: redis:7-alpine
    container_name: onyx-redis-master
    command: redis-server /etc/redis/redis.conf
    volumes:
      - redis_master_data:/data
      - ./docker/redis/redis-master.conf:/etc/redis/redis.conf
    ports:
      - "6379:6379"
    networks:
      - onyx-backend-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G

  redis-slave:
    image: redis:7-alpine
    container_name: onyx-redis-slave
    command: redis-server /etc/redis/redis.conf
    volumes:
      - redis_slave_data:/data
      - ./docker/redis/redis-slave.conf:/etc/redis/redis.conf
    ports:
      - "6380:6379"
    networks:
      - onyx-backend-network
    restart: unless-stopped
    depends_on:
      - redis-master

  # API后端服务 - 多实例
  api-backend-1:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    container_name: onyx-api-1
    environment:
      - DATABASE_URL=postgresql://onyx_user:onyx_password@postgres-master:5432/onyx
      - REDIS_URL=redis://redis-master:6379/0
      - MODEL_SERVER_URL=http://model-server:9000
      - INSTANCE_ID=api-1
    volumes:
      - app_logs:/app/logs
    networks:
      - onyx-backend-network
      - onyx-frontend-network
    restart: unless-stopped
    secrets:
      - db_password
      - jwt_secret
    depends_on:
      - postgres-master
      - redis-master
    deploy:
      resources:
        limits:
          cpus: '3.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  api-backend-2:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    container_name: onyx-api-2
    environment:
      - DATABASE_URL=postgresql://onyx_user:onyx_password@postgres-master:5432/onyx
      - REDIS_URL=redis://redis-master:6379/0
      - MODEL_SERVER_URL=http://model-server:9000
      - INSTANCE_ID=api-2
    volumes:
      - app_logs:/app/logs
    networks:
      - onyx-backend-network
      - onyx-frontend-network
    restart: unless-stopped
    secrets:
      - db_password
      - jwt_secret
    depends_on:
      - postgres-master
      - redis-master

  # AI模型服务 - 多实例负载均衡
  model-server-1:
    build:
      context: .
      dockerfile: docker/Dockerfile.model-server
    container_name: onyx-model-1
    environment:
      - REDIS_URL=redis://redis-master:6379/1
      - MODEL_CACHE_DIR=/app/model_cache
      - INSTANCE_ID=model-1
      - CUDA_VISIBLE_DEVICES=0
    volumes:
      - model_cache:/app/model_cache
      - app_logs:/app/logs
    networks:
      - onyx-backend-network
    restart: unless-stopped
    depends_on:
      - redis-master
    deploy:
      resources:
        limits:
          cpus: '6.0'
          memory: 16G
        reservations:
          cpus: '4.0'
          memory: 8G

  model-server-2:
    build:
      context: .
      dockerfile: docker/Dockerfile.model-server
    container_name: onyx-model-2
    environment:
      - REDIS_URL=redis://redis-master:6379/1
      - MODEL_CACHE_DIR=/app/model_cache
      - INSTANCE_ID=model-2
      - CUDA_VISIBLE_DEVICES=1
    volumes:
      - model_cache:/app/model_cache
      - app_logs:/app/logs
    networks:
      - onyx-backend-network
    restart: unless-stopped
    depends_on:
      - redis-master

  # Celery Worker - 多实例
  celery-worker-1:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    container_name: onyx-worker-1
    environment:
      - DATABASE_URL=postgresql://onyx_user:onyx_password@postgres-master:5432/onyx
      - REDIS_URL=redis://redis-master:6379/0
      - WORKER_ID=worker-1
    volumes:
      - app_logs:/app/logs
    networks:
      - onyx-backend-network
    restart: unless-stopped
    depends_on:
      - postgres-master
      - redis-master
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

  celery-worker-2:
    build:
      context: .
      dockerfile: docker/Dockerfile.worker
    container_name: onyx-worker-2
    environment:
      - DATABASE_URL=postgresql://onyx_user:onyx_password@postgres-master:5432/onyx
      - REDIS_URL=redis://redis-master:6379/0
      - WORKER_ID=worker-2
    volumes:
      - app_logs:/app/logs
    networks:
      - onyx-backend-network
    restart: unless-stopped
    depends_on:
      - postgres-master
      - redis-master

  # 前端Web服务 - 多实例
  web-frontend-1:
    build:
      context: .
      dockerfile: docker/Dockerfile.web
    container_name: onyx-web-1
    environment:
      - NEXT_PUBLIC_API_URL=http://api-backend:8080
      - INSTANCE_ID=web-1
    networks:
      - onyx-frontend-network
    restart: unless-stopped
    depends_on:
      - api-backend-1
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 256M

  web-frontend-2:
    build:
      context: .
      dockerfile: docker/Dockerfile.web
    container_name: onyx-web-2
    environment:
      - NEXT_PUBLIC_API_URL=http://api-backend:8080
      - INSTANCE_ID=web-2
    networks:
      - onyx-frontend-network
    restart: unless-stopped
    depends_on:
      - api-backend-2

  # Nginx负载均衡器
  nginx-lb:
    image: nginx:alpine
    container_name: onyx-nginx-lb
    volumes:
      - ./docker/nginx/nginx-prod.conf:/etc/nginx/nginx.conf
      - ./docker/nginx/conf.d:/etc/nginx/conf.d
      - ./docker/nginx/ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    networks:
      - onyx-frontend-network
      - public-network
    restart: unless-stopped
    depends_on:
      - web-frontend-1
      - web-frontend-2
      - api-backend-1
      - api-backend-2
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M

# 密钥管理
secrets:
  db_password:
    file: ./secrets/db_password.txt
  replication_password:
    file: ./secrets/replication_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt

# 数据卷定义
volumes:
  postgres_master_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/onyx/data/postgres_master
  postgres_slave_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/onyx/data/postgres_slave
  redis_master_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/onyx/data/redis_master
  redis_slave_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/onyx/data/redis_slave
  app_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/onyx/logs
  model_cache:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/onyx/data/model_cache

# 网络定义
networks:
  onyx-backend-network:
    driver: bridge
    internal: true
  onyx-frontend-network:
    driver: bridge
    internal: true
  public-network:
    driver: bridge
```

### 监控和日志配置

#### docker-compose.monitoring.yml
```yaml
version: '3.8'

services:
  # Prometheus监控
  prometheus:
    image: prom/prometheus:latest
    container_name: onyx-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - onyx-monitoring-network
      - onyx-backend-network
    restart: unless-stopped

  # Grafana可视化
  grafana:
    image: grafana/grafana:latest
    container_name: onyx-grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./docker/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./docker/grafana/datasources:/etc/grafana/provisioning/datasources
    ports:
      - "3001:3000"
    networks:
      - onyx-monitoring-network
    restart: unless-stopped
    depends_on:
      - prometheus

  # 节点监控
  node-exporter:
    image: prom/node-exporter:latest
    container_name: onyx-node-exporter
    command:
      - '--path.rootfs=/host'
    volumes:
      - '/:/host:ro,rslave'
    ports:
      - "9100:9100"
    networks:
      - onyx-monitoring-network
    restart: unless-stopped

  # 容器监控
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: onyx-cadvisor
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    ports:
      - "8081:8080"
    networks:
      - onyx-monitoring-network
    restart: unless-stopped

volumes:
  prometheus_data:
    driver: local
  grafana_data:
    driver: local

networks:
  onyx-monitoring-network:
    driver: bridge
```

### 服务器硬件配置详细建议

#### 小型部署 (100-500用户)
```yaml
服务器数量: 1台
服务器规格:
  CPU: 8核心 2.4GHz+ (Intel Xeon E-2288G 或 AMD EPYC 7302P)
  内存: 32GB DDR4 ECC
  存储: 500GB NVMe SSD + 2TB SATA SSD
  网络: 1Gbps
  操作系统: Ubuntu 22.04 LTS Server

容器部署:
  - onyx-postgres (4GB RAM, 2核心)
  - onyx-redis (2GB RAM, 1核心)
  - onyx-api-backend (6GB RAM, 2核心)
  - onyx-model-server (12GB RAM, 2核心)
  - onyx-celery-worker (2GB RAM, 0.5核心)
  - onyx-web-frontend (1GB RAM, 0.5核心)
  - onyx-nginx-proxy (512MB RAM, 0.5核心)

资源使用:
  总CPU使用: 8.5核心 (留0.5核心系统)
  总内存使用: 27.5GB (留4.5GB系统)
  存储分配: 100GB应用 + 400GB数据

云服务器成本:
  AWS EC2 m6i.2xlarge: $350/月
  Azure Standard_D8s_v5: $320/月
  阿里云ecs.g7.2xlarge: $280/月
```

#### 中型部署 (500-2000用户)
```yaml
服务器数量: 2台

应用服务器:
  CPU: 8核心 2.8GHz+ (Intel Xeon Gold 6248R)
  内存: 32GB DDR4 ECC
  存储: 300GB NVMe SSD
  网络: 10Gbps
  部署容器:
    - onyx-api-backend-1 (6GB RAM, 3核心)
    - onyx-api-backend-2 (6GB RAM, 3核心)
    - onyx-web-frontend (2GB RAM, 1核心)
    - onyx-celery-worker (4GB RAM, 1核心)
    - onyx-nginx-proxy (1GB RAM, 0.5核心)

数据和AI服务器:
  CPU: 16核心 3.0GHz+ (Intel Xeon Gold 6326)
  内存: 64GB DDR4 ECC
  存储: 1TB NVMe SSD + 4TB SATA SSD
  GPU: NVIDIA RTX A4000 或 Tesla T4
  网络: 10Gbps
  部署容器:
    - onyx-postgres-master (8GB RAM, 4核心)
    - onyx-postgres-slave (4GB RAM, 2核心)
    - onyx-redis-master (4GB RAM, 2核心)
    - onyx-redis-slave (2GB RAM, 1核心)
    - onyx-model-server-1 (20GB RAM, 4核心)
    - onyx-model-server-2 (20GB RAM, 3核心)

云服务器成本:
  应用服务器: $350/月
  数据AI服务器: $800/月 (含GPU)
  总成本: $1,150/月
```

#### 大型部署 (2000+用户)
```yaml
服务器数量: 6台

负载均衡器 (1台):
  CPU: 4核心 3.0GHz+
  内存: 16GB DDR4
  存储: 200GB SSD
  网络: 10Gbps
  部署: HAProxy + Nginx

应用服务器 (2台):
  CPU: 12核心 3.2GHz+ (Intel Xeon Platinum 8352Y)
  内存: 48GB DDR4 ECC
  存储: 500GB NVMe SSD
  网络: 10Gbps
  部署容器:
    每台服务器:
    - onyx-api-backend (多实例)
    - onyx-web-frontend
    - onyx-celery-worker

AI模型服务器 (2台):
  CPU: 20核心 3.5GHz+ (Intel Xeon Platinum 8380)
  内存: 128GB DDR4 ECC
  存储: 2TB NVMe SSD
  GPU: 2x NVIDIA A100 40GB 或 4x RTX 4090
  网络: 25Gbps
  部署容器:
    - onyx-model-server (多实例，GPU分配)

数据库服务器 (1台):
  CPU: 16核心 3.8GHz+ (Intel Xeon Platinum 8375C)
  内存: 128GB DDR4 ECC
  存储: 4TB NVMe SSD RAID 1 + 16TB SATA RAID 5
  网络: 10Gbps
  部署容器:
    - onyx-postgres-master
    - onyx-postgres-slave
    - onyx-redis-cluster (多节点)

监控服务器 (1台):
  CPU: 8核心 2.8GHz+
  内存: 32GB DDR4
  存储: 2TB SSD
  网络: 1Gbps
  部署容器:
    - prometheus
    - grafana
    - elasticsearch
    - kibana
    - alertmanager

云服务器成本:
  负载均衡器: $200/月
  应用服务器: $600/月 × 2 = $1,200/月
  AI服务器: $2,000/月 × 2 = $4,000/月
  数据库服务器: $1,500/月
  监控服务器: $400/月
  总成本: $7,300/月
```

### 部署架构图

#### 单服务器架构
```mermaid
graph TB
    subgraph "单台Linux服务器"
        subgraph "容器层"
            A[nginx-proxy:80/443]
            B[web-frontend:3000]
            C[api-backend:8080]
            D[model-server:9000]
            E[celery-worker]
            F[postgres:5432]
            G[redis:6379]
        end

        subgraph "数据层"
            H[postgres_data]
            I[redis_data]
            J[model_cache]
            K[app_logs]
        end
    end

    L[用户] --> A
    A --> B
    A --> C
    C --> D
    C --> F
    C --> G
    D --> G
    E --> F
    E --> G
    F --> H
    G --> I
    D --> J
    C --> K
```

#### 多服务器集群架构
```mermaid
graph TB
    subgraph "负载均衡器"
        LB[HAProxy/Nginx]
    end

    subgraph "应用服务器1"
        A1[api-backend-1]
        W1[web-frontend-1]
        C1[celery-worker-1]
    end

    subgraph "应用服务器2"
        A2[api-backend-2]
        W2[web-frontend-2]
        C2[celery-worker-2]
    end

    subgraph "AI服务器1"
        M1[model-server-1]
        M2[model-server-2]
    end

    subgraph "AI服务器2"
        M3[model-server-3]
        M4[model-server-4]
    end

    subgraph "数据库服务器"
        DB1[postgres-master]
        DB2[postgres-slave]
        R1[redis-master]
        R2[redis-slave]
    end

    subgraph "监控服务器"
        P[prometheus]
        G[grafana]
        E[elasticsearch]
    end

    U[用户] --> LB
    LB --> W1
    LB --> W2
    LB --> A1
    LB --> A2
    A1 --> M1
    A1 --> M2
    A2 --> M3
    A2 --> M4
    A1 --> DB1
    A2 --> DB1
    C1 --> DB1
    C2 --> DB1
    M1 --> R1
    M2 --> R1
    M3 --> R1
    M4 --> R1
    DB1 --> DB2
    R1 --> R2

    P --> A1
    P --> A2
    P --> M1
    P --> M2
    P --> DB1
    P --> R1
```

### 资源监控和告警

#### Prometheus配置
```yaml
# docker/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'onyx-api'
    static_configs:
      - targets: ['api-backend-1:8080', 'api-backend-2:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'onyx-model'
    static_configs:
      - targets: ['model-server-1:9000', 'model-server-2:9000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-master:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-master:6379']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### 性能基准测试

#### 负载测试脚本
```bash
#!/bin/bash
# load-test.sh - 性能基准测试

echo "🚀 开始Onyx性能基准测试..."

# 安装测试工具
if ! command -v wrk &> /dev/null; then
    echo "安装wrk负载测试工具..."
    sudo apt-get update
    sudo apt-get install -y wrk
fi

# 测试API性能
echo "📊 测试API性能..."
wrk -t12 -c400 -d30s --timeout 30s http://localhost/api/health

# 测试前端性能
echo "📊 测试前端性能..."
wrk -t8 -c200 -d30s http://localhost/

# 测试数据库连接
echo "📊 测试数据库性能..."
docker-compose exec postgres pgbench -i -s 10 onyx
docker-compose exec postgres pgbench -c 10 -j 2 -t 1000 onyx

# 测试Redis性能
echo "📊 测试Redis性能..."
docker-compose exec redis redis-benchmark -n 100000 -c 50

echo "✅ 性能测试完成"
```

### 备份和恢复策略

#### 自动备份脚本
```bash
#!/bin/bash
# backup-prod.sh - 生产环境备份脚本

BACKUP_DIR="/opt/onyx/backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "🗄️ 开始数据备份..."

# 备份PostgreSQL
echo "备份PostgreSQL数据库..."
docker-compose exec -T postgres-master pg_dump -U onyx_user onyx | gzip > "$BACKUP_DIR/postgres.sql.gz"

# 备份Redis
echo "备份Redis数据..."
docker-compose exec redis-master redis-cli BGSAVE
docker cp onyx-redis-master:/data/dump.rdb "$BACKUP_DIR/redis.rdb"

# 备份应用配置
echo "备份应用配置..."
tar -czf "$BACKUP_DIR/config.tar.gz" docker/ backend/.env

# 备份模型缓存
echo "备份模型缓存..."
tar -czf "$BACKUP_DIR/model_cache.tar.gz" data/model_cache/

# 备份日志
echo "备份应用日志..."
tar -czf "$BACKUP_DIR/logs.tar.gz" logs/

# 创建备份清单
cat > "$BACKUP_DIR/backup_info.txt" << EOF
备份时间: $(date)
备份类型: 完整备份
数据库大小: $(du -sh "$BACKUP_DIR/postgres.sql.gz" | cut -f1)
Redis大小: $(du -sh "$BACKUP_DIR/redis.rdb" | cut -f1)
配置大小: $(du -sh "$BACKUP_DIR/config.tar.gz" | cut -f1)
模型缓存大小: $(du -sh "$BACKUP_DIR/model_cache.tar.gz" | cut -f1)
日志大小: $(du -sh "$BACKUP_DIR/logs.tar.gz" | cut -f1)
总大小: $(du -sh "$BACKUP_DIR" | cut -f1)
EOF

echo "✅ 备份完成: $BACKUP_DIR"

# 清理旧备份 (保留30天)
find /opt/onyx/backups/ -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null || true
```

### 高可用性配置

#### HAProxy负载均衡配置
```haproxy
# /etc/haproxy/haproxy.cfg
global
    daemon
    maxconn 4096
    log stdout local0

defaults
    mode http
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms
    option httplog

# 前端负载均衡
frontend onyx_frontend
    bind *:80
    bind *:443 ssl crt /etc/ssl/certs/onyx.pem
    redirect scheme https if !{ ssl_fc }

    # 路由规则
    acl is_api path_beg /api/
    acl is_model path_beg /model/

    use_backend onyx_api if is_api
    use_backend onyx_model if is_model
    default_backend onyx_web

# 后端API负载均衡
backend onyx_api
    balance roundrobin
    option httpchk GET /health
    server api1 app-server-1:8080 check
    server api2 app-server-2:8080 check

# AI模型负载均衡
backend onyx_model
    balance leastconn
    option httpchk GET /health
    server model1 ai-server-1:9000 check
    server model2 ai-server-2:9000 check

# 前端负载均衡
backend onyx_web
    balance roundrobin
    option httpchk GET /health
    server web1 app-server-1:3000 check
    server web2 app-server-2:3000 check

# 统计页面
stats enable
stats uri /haproxy-stats
stats refresh 30s
```

### 部署检查清单

#### 生产环境部署检查
```yaml
部署前检查:
  - [ ] 服务器硬件配置满足要求
  - [ ] 操作系统已安装并更新
  - [ ] Docker和Docker Compose已安装
  - [ ] 防火墙规则已配置
  - [ ] SSL证书已准备
  - [ ] 域名DNS已配置
  - [ ] 备份策略已制定

部署过程检查:
  - [ ] 所有镜像构建成功
  - [ ] 容器启动正常
  - [ ] 健康检查通过
  - [ ] 数据库迁移完成
  - [ ] 网络连通性正常
  - [ ] 负载均衡配置正确

部署后验证:
  - [ ] 前端页面正常访问
  - [ ] API接口响应正常
  - [ ] 用户注册登录功能
  - [ ] 文档上传和搜索功能
  - [ ] AI对话功能正常
  - [ ] 性能指标正常
  - [ ] 监控告警正常
  - [ ] 备份恢复测试通过
```

### 成本效益分析

#### 云服务器 vs 自建服务器
```yaml
小型部署 (3年TCO):
  云服务器: $12,600 (AWS m6i.2xlarge)
  自建服务器: $8,000 (硬件) + $2,000 (运维) = $10,000
  节省: $2,600 (21%)

中型部署 (3年TCO):
  云服务器: $41,400 (含GPU实例)
  自建服务器: $25,000 (硬件) + $6,000 (运维) = $31,000
  节省: $10,400 (25%)

大型部署 (3年TCO):
  云服务器: $262,800 (多实例集群)
  自建服务器: $150,000 (硬件) + $30,000 (运维) = $180,000
  节省: $82,800 (31%)
```

### 迁移和升级策略

#### 蓝绿部署
```bash
#!/bin/bash
# blue-green-deploy.sh - 零停机部署

# 构建新版本镜像
docker-compose -f docker-compose.green.yml build

# 启动绿色环境
docker-compose -f docker-compose.green.yml up -d

# 健康检查
./health-check.sh green

# 切换流量
./switch-traffic.sh blue green

# 停止蓝色环境
docker-compose -f docker-compose.blue.yml down

echo "✅ 蓝绿部署完成"
```

#### 滚动更新
```bash
#!/bin/bash
# rolling-update.sh - 滚动更新部署

services=("api-backend-1" "api-backend-2" "model-server-1" "model-server-2")

for service in "${services[@]}"; do
    echo "更新服务: $service"

    # 停止一个实例
    docker-compose stop "$service"

    # 重新构建和启动
    docker-compose build "$service"
    docker-compose up -d "$service"

    # 等待健康检查
    ./wait-for-health.sh "$service"

    echo "✅ $service 更新完成"
done
```

---

**最后更新**: 2025-02-19
**适用环境**: Windows Docker Desktop / Linux服务器生产环境
**版本要求**: Docker 20.10+, Docker Compose 2.0+
**支持架构**: x86_64, ARM64
