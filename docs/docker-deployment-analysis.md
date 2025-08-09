# Onyx Docker 部署分析报告

## 🐳 Docker 容器架构分析

基于对 `backend/Dockerfile`、`web/Dockerfile`、`docker-compose.dev.yml` 等文件的分析，Onyx系统需要以下Docker容器实例：

## 📦 必需的Docker容器列表

### 🔧 核心应用容器 (5个)

#### 1. **api_server** - 后端API服务器
- **镜像**: `onyxdotapp/onyx-backend:latest`
- **构建**: `backend/Dockerfile`
- **端口**: `8080:8080`
- **功能**: FastAPI后端服务，处理所有API请求
- **依赖**: relational_db, index, cache, inference_model_server, minio

#### 2. **background** - 后台任务处理器
- **镜像**: `onyxdotapp/onyx-backend:latest`
- **构建**: `backend/Dockerfile`
- **功能**: Celery后台任务，文档处理、索引更新
- **依赖**: relational_db, index, cache, inference_model_server, indexing_model_server

#### 3. **web_server** - 前端Web服务器
- **镜像**: `onyxdotapp/onyx-web-server:latest`
- **构建**: `web/Dockerfile`
- **功能**: Next.js前端应用
- **依赖**: api_server

#### 4. **inference_model_server** - 推理模型服务器
- **镜像**: `onyxdotapp/onyx-model-server:latest`
- **构建**: `backend/Dockerfile.model_server`
- **端口**: `9000:9000`
- **功能**: AI模型推理服务，处理嵌入和重排序

#### 5. **indexing_model_server** - 索引模型服务器
- **镜像**: `onyxdotapp/onyx-model-server:latest`
- **构建**: `backend/Dockerfile.model_server`
- **端口**: `9001:9000`
- **功能**: 文档索引时的AI模型服务

### 🗄️ 数据存储容器 (3个)

#### 6. **relational_db** - PostgreSQL数据库
- **镜像**: `postgres:15.2-alpine`
- **端口**: `5432:5432`
- **功能**: 主数据库，存储用户、配置、元数据
- **存储**: `db_volume:/var/lib/postgresql/data`
- **配置**: 最大连接数250

#### 7. **cache** - Redis缓存
- **镜像**: `redis:7.4-alpine`
- **端口**: `6379:6379`
- **功能**: 缓存服务，会话存储
- **配置**: 临时存储模式

#### 8. **minio** - 对象存储服务
- **镜像**: `minio/minio:latest`
- **端口**: `9004:9000` (API), `9005:9001` (控制台)
- **功能**: S3兼容的文件存储
- **存储**: `minio_data:/data`

### 🔍 搜索引擎容器 (1个)

#### 9. **index** - Vespa搜索引擎
- **镜像**: `vespaengine/vespa:8.526.15`
- **端口**: `19071:19071`, `8081:8081`
- **功能**: 向量搜索和全文搜索
- **存储**: `vespa_volume:/opt/vespa/var`

### 🌐 网络代理容器 (1个)

#### 10. **nginx** - 反向代理
- **镜像**: `nginx:1.23.4-alpine`
- **端口**: `80:80`, `3000:80`
- **功能**: 反向代理，负载均衡
- **配置**: 自定义nginx配置
- **依赖**: api_server, web_server

## 💾 Docker存储卷 (7个)

### 持久化存储卷
1. **db_volume** - PostgreSQL数据
2. **vespa_volume** - Vespa搜索索引
3. **minio_data** - MinIO文件存储

### 缓存存储卷
4. **model_cache_huggingface** - 推理模型缓存
5. **indexing_huggingface_model_cache** - 索引模型缓存

### 日志存储卷
6. **api_server_logs** - API服务器日志
7. **background_logs** - 后台任务日志
8. **inference_model_server_logs** - 推理服务日志
9. **indexing_model_server_logs** - 索引服务日志

## 🔧 Windows Docker Desktop 部署要求

### 📋 前提条件

#### 1. **系统要求**
- Windows 10/11 Pro, Enterprise, 或 Education
- WSL 2 已启用
- Hyper-V 已启用（或使用WSL 2后端）
- 至少 16GB RAM（推荐 32GB）
- 至少 100GB 可用磁盘空间

#### 2. **Docker Desktop 配置**
- Docker Desktop for Windows 4.0+
- 分配给Docker的内存: 至少 8GB（推荐 12GB）
- 分配给Docker的CPU: 至少 4核（推荐 8核）
- 启用 Kubernetes（可选，用于Helm部署）

#### 3. **网络端口要求**
```
80     - Nginx HTTP
3000   - 前端Web服务 (备用)
5432   - PostgreSQL数据库
6379   - Redis缓存
8080   - 后端API服务器
8081   - Vespa搜索引擎
9000   - 推理模型服务器
9001   - 索引模型服务器
9004   - MinIO API
9005   - MinIO控制台
19071  - Vespa管理端口
```

### 🚀 部署步骤

#### 第一步：准备环境文件
```bash
# 创建环境配置文件
cp deployment/docker_compose/.env.template .env

# 配置必要的环境变量
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=onyx
GEN_AI_API_KEY=your_openai_api_key
```

#### 第二步：启动基础服务
```bash
# 启动数据库和缓存
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d relational_db cache minio index
```

#### 第三步：启动AI模型服务
```bash
# 启动模型服务器
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d inference_model_server indexing_model_server
```

#### 第四步：启动应用服务
```bash
# 启动后端和前端
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d api_server background web_server
```

#### 第五步：启动代理服务
```bash
# 启动nginx代理
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d nginx
```

### 📊 资源需求估算

#### 内存需求
- **PostgreSQL**: ~512MB
- **Redis**: ~256MB
- **MinIO**: ~256MB
- **Vespa**: ~2GB
- **后端API**: ~1GB
- **后台任务**: ~1GB
- **前端Web**: ~512MB
- **推理模型**: ~4GB
- **索引模型**: ~4GB
- **Nginx**: ~64MB
- **总计**: ~14GB

#### CPU需求
- **轻负载**: 4核心
- **中等负载**: 8核心
- **重负载**: 16核心

#### 磁盘需求
- **系统镜像**: ~10GB
- **数据库**: ~5GB
- **搜索索引**: ~10GB
- **文件存储**: ~20GB
- **模型缓存**: ~15GB
- **日志**: ~5GB
- **总计**: ~65GB

## ⚠️ 注意事项

### 🔒 安全配置
1. **修改默认密码**: PostgreSQL, MinIO管理员密码
2. **配置防火墙**: 只开放必要端口
3. **SSL证书**: 生产环境启用HTTPS
4. **API密钥**: 配置真实的LLM API密钥

### 🔧 性能优化
1. **模型缓存**: 预下载AI模型到本地卷
2. **数据库调优**: 调整PostgreSQL连接池
3. **搜索优化**: 配置Vespa内存分配
4. **网络优化**: 配置nginx缓存策略

### 📊 监控配置
1. **健康检查**: 所有容器配置健康检查
2. **日志收集**: 配置日志轮转和收集
3. **指标监控**: 可选配置Prometheus监控
4. **告警通知**: 配置Sentry错误监控

## 🎯 部署验证清单

### ✅ 容器启动验证
- [ ] 所有10个容器成功启动
- [ ] 所有端口正常监听
- [ ] 容器间网络通信正常

### ✅ 服务功能验证
- [ ] PostgreSQL数据库连接正常
- [ ] Redis缓存服务正常
- [ ] Vespa搜索引擎正常
- [ ] MinIO文件存储正常
- [ ] AI模型服务正常

### ✅ 应用功能验证
- [ ] 前端界面正常加载
- [ ] 用户认证功能正常
- [ ] 聊天功能正常工作
- [ ] 文档上传和搜索正常

---

**📋 总结**: Onyx系统需要10个Docker容器，9个存储卷，占用12个网络端口，需要约14GB内存和65GB磁盘空间。
