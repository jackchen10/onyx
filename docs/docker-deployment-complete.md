# Onyx Docker 完整部署指南

## 🎯 部署概述

基于对Onyx系统架构的完整分析，在Windows Docker Desktop中部署完整的Onyx系统需要**10个Docker容器**和**9个存储卷**。

## 🐳 完整容器清单

### 📊 容器总览表

| 序号 | 容器名称 | 镜像 | 端口映射 | 功能描述 | 关键性 |
|------|----------|------|----------|----------|--------|
| 1 | `relational_db` | `postgres:15.2-alpine` | `5432:5432` | PostgreSQL主数据库 | 🔥 关键 |
| 2 | `cache` | `redis:7.4-alpine` | `6379:6379` | Redis缓存服务 | 🔥 关键 |
| 3 | `minio` | `minio/minio:latest` | `9004:9000`, `9005:9001` | S3兼容文件存储 | 🔥 关键 |
| 4 | `index` | `vespaengine/vespa:8.526.15` | `19071:19071`, `8081:8081` | Vespa搜索引擎 | 🔥 关键 |
| 5 | `inference_model_server` | `onyxdotapp/onyx-model-server:latest` | `9000:9000` | AI推理模型服务 | 🔥 关键 |
| 6 | `indexing_model_server` | `onyxdotapp/onyx-model-server:latest` | `9001:9000` | AI索引模型服务 | 🔥 关键 |
| 7 | `api_server` | `onyxdotapp/onyx-backend:latest` | `8080:8080` | FastAPI后端服务 | 🔥 关键 |
| 8 | `background` | `onyxdotapp/onyx-backend:latest` | - | Celery后台任务 | 🔥 关键 |
| 9 | `web_server` | `onyxdotapp/onyx-web-server:latest` | `3000:3000` | Next.js前端服务 | 🔥 关键 |
| 10 | `nginx` | `nginx:1.23.4-alpine` | `80:80` | 反向代理服务 | ⚠️ 可选 |

## 💾 存储卷清单

### 持久化存储卷 (5个)
1. **db_volume** - PostgreSQL数据持久化
2. **vespa_volume** - Vespa搜索索引持久化
3. **minio_data** - MinIO文件存储持久化
4. **model_cache_huggingface** - 推理模型缓存
5. **indexing_huggingface_model_cache** - 索引模型缓存

### 日志存储卷 (4个)
6. **api_server_logs** - API服务器日志
7. **background_logs** - 后台任务日志
8. **inference_model_server_logs** - 推理服务日志
9. **indexing_model_server_logs** - 索引服务日志

## 🔧 Windows Docker Desktop 配置要求

### 📋 系统要求
- **操作系统**: Windows 10/11 Pro, Enterprise, 或 Education
- **内存**: 至少 16GB RAM (推荐 32GB)
- **磁盘**: 至少 100GB 可用空间
- **CPU**: 至少 4核心 (推荐 8核心)

### ⚙️ Docker Desktop 设置
```
Resources配置:
├── Memory: 12GB (最小8GB)
├── CPUs: 6核心 (最小4核心)  
├── Disk image size: 80GB
└── Swap: 2GB
```

### 🌐 网络端口配置
```
必需端口:
├── 80     - Nginx HTTP入口
├── 3000   - 前端Web服务 (备用访问)
├── 5432   - PostgreSQL数据库
├── 6379   - Redis缓存
├── 8080   - 后端API服务器
├── 8081   - Vespa管理界面
├── 9000   - 推理模型服务器
├── 9001   - 索引模型服务器
├── 9004   - MinIO API
├── 9005   - MinIO管理控制台
└── 19071  - Vespa应用端口
```

## 🚀 部署流程

### 第一步：环境准备
```bash
# 1. 确保Docker Desktop运行
# 2. 检查系统资源
# 3. 配置环境变量文件
cp deployment/docker_compose/.env.template .env
```

### 第二步：使用一键部署脚本
```bash
# 运行完整Docker部署脚本
tests/deploy_docker_windows.bat
```

### 第三步：手动分阶段部署 (可选)
```bash
# 阶段1: 基础服务 (数据库、缓存、存储)
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d relational_db cache minio

# 阶段2: 搜索引擎
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d index

# 阶段3: AI模型服务
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d inference_model_server indexing_model_server

# 阶段4: 应用服务
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d api_server background web_server

# 阶段5: 代理服务
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d nginx
```

## 🔍 部署验证

### 使用验证脚本
```bash
# 检查所有容器状态
python tests/docker_container_checklist.py

# Docker容器管理
python tests/docker_manager.py

# 系统健康检查
python tests/health_check.py
```

### 手动验证步骤
```bash
# 1. 检查容器状态
docker-compose -f deployment/docker_compose/docker-compose.dev.yml ps

# 2. 检查容器日志
docker-compose -f deployment/docker_compose/docker-compose.dev.yml logs

# 3. 测试服务端点
curl http://localhost/api/health
curl http://localhost:9004/minio/health/live
curl http://localhost:19071/ApplicationStatus
```

## 📊 资源使用预估

### 内存分配
```
PostgreSQL:     512MB
Redis:          256MB
MinIO:          256MB
Vespa:          2GB
推理模型服务器:   4GB
索引模型服务器:   4GB
后端API:        1GB
后台任务:       1GB
前端Web:        512MB
Nginx:          64MB
系统开销:       512MB
总计:          ~14GB
```

### 磁盘使用
```
Docker镜像:     ~8GB
PostgreSQL数据: ~2GB
Vespa索引:      ~5GB
MinIO文件:      ~10GB
模型缓存:       ~15GB
日志文件:       ~2GB
总计:          ~42GB
```

## ⚠️ 常见问题和解决方案

### 🔧 容器启动失败
**问题**: 容器无法启动
**解决方案**:
```bash
# 检查Docker Desktop状态
docker info

# 检查端口占用
netstat -ano | findstr :8080

# 重新构建镜像
docker-compose -f deployment/docker_compose/docker-compose.dev.yml build --no-cache
```

### 💾 内存不足
**问题**: 系统内存不足
**解决方案**:
```bash
# 增加Docker Desktop内存分配
# Settings -> Resources -> Memory -> 12GB+

# 或者禁用部分非关键服务
# 在.env文件中设置:
DISABLE_MODEL_SERVER=True
```

### 🌐 端口冲突
**问题**: 端口被占用
**解决方案**:
```bash
# 查找占用进程
netstat -ano | findstr :端口号

# 终止占用进程
taskkill /PID 进程ID /F

# 或修改docker-compose.yml中的端口映射
```

## 🎯 部署成功标志

### ✅ 所有容器运行正常
```bash
docker-compose -f deployment/docker_compose/docker-compose.dev.yml ps
# 应显示10个容器都是"Up"状态
```

### ✅ 服务健康检查通过
- 🟢 PostgreSQL: 接受连接
- 🟢 Redis: PONG响应
- 🟢 MinIO: 健康检查通过
- 🟢 Vespa: 应用状态正常
- 🟢 API服务器: /health端点返回200
- 🟢 前端服务: 页面正常加载
- 🟢 Nginx: 代理正常工作

### ✅ 功能验证通过
- 🟢 前端界面正常访问: http://localhost
- 🟢 API文档正常访问: http://localhost/api/docs
- 🟢 MinIO控制台: http://localhost:9005
- 🟢 Vespa控制台: http://localhost:8081

## 🛠️ 管理命令

### 日常管理
```bash
# 查看状态
docker-compose -f deployment/docker_compose/docker-compose.dev.yml ps

# 查看日志
docker-compose -f deployment/docker_compose/docker-compose.dev.yml logs -f

# 重启服务
docker-compose -f deployment/docker_compose/docker-compose.dev.yml restart

# 停止所有服务
docker-compose -f deployment/docker_compose/docker-compose.dev.yml down

# 完全清理 (包括数据)
docker-compose -f deployment/docker_compose/docker-compose.dev.yml down -v
```

### 故障排除
```bash
# 重新构建镜像
docker-compose -f deployment/docker_compose/docker-compose.dev.yml build --no-cache

# 查看特定容器日志
docker-compose -f deployment/docker_compose/docker-compose.dev.yml logs api_server

# 进入容器调试
docker-compose -f deployment/docker_compose/docker-compose.dev.yml exec api_server bash
```

---

**📋 总结**: Onyx完整Docker部署需要10个容器、9个存储卷、12个端口，约14GB内存和42GB磁盘空间。
