# Onyx 完整系统分析报告

## 🎯 系统分析总结

**分析日期**: 2025年1月9日  
**系统版本**: Onyx CE (Community Edition)  
**分析范围**: 完整的Docker部署架构和LLM配置  

## 🐳 Docker容器完整清单

### 📊 10个必需容器详细信息

| 容器 | 镜像 | 版本 | 端口 | 内存需求 | 磁盘需求 | 关键性 |
|------|------|------|------|----------|----------|--------|
| **relational_db** | postgres | 15.2-alpine | 5432 | 512MB | 5GB | 🔥 关键 |
| **cache** | redis | 7.4-alpine | 6379 | 256MB | 100MB | 🔥 关键 |
| **minio** | minio/minio | latest | 9004,9005 | 256MB | 20GB | 🔥 关键 |
| **index** | vespaengine/vespa | 8.526.15 | 8081,19071 | 2GB | 10GB | 🔥 关键 |
| **inference_model_server** | onyxdotapp/onyx-model-server | latest | 9000 | 4GB | 8GB | 🔥 关键 |
| **indexing_model_server** | onyxdotapp/onyx-model-server | latest | 9001 | 4GB | 8GB | 🔥 关键 |
| **api_server** | onyxdotapp/onyx-backend | latest | 8080 | 1GB | 2GB | 🔥 关键 |
| **background** | onyxdotapp/onyx-backend | latest | - | 1GB | 1GB | 🔥 关键 |
| **web_server** | onyxdotapp/onyx-web-server | latest | 3000 | 512MB | 1GB | 🔥 关键 |
| **nginx** | nginx | 1.23.4-alpine | 80 | 64MB | 100MB | ⚠️ 可选 |

### 💾 9个存储卷详细信息

| 存储卷 | 用途 | 大小 | 备份重要性 | 数据类型 |
|--------|------|------|------------|----------|
| **db_volume** | PostgreSQL数据 | ~5GB | 🔥 关键 | 用户数据、配置 |
| **vespa_volume** | Vespa搜索索引 | ~10GB | 🔥 关键 | 搜索索引 |
| **minio_data** | MinIO文件存储 | ~20GB | 🔥 关键 | 用户文件 |
| **model_cache_huggingface** | 推理模型缓存 | ~8GB | ⚠️ 可选 | AI模型文件 |
| **indexing_huggingface_model_cache** | 索引模型缓存 | ~8GB | ⚠️ 可选 | AI模型文件 |
| **api_server_logs** | API服务日志 | ~1GB | ⚠️ 可选 | 应用日志 |
| **background_logs** | 后台任务日志 | ~1GB | ⚠️ 可选 | 任务日志 |
| **inference_model_server_logs** | 推理服务日志 | ~500MB | ⚠️ 可选 | 模型日志 |
| **indexing_model_server_logs** | 索引服务日志 | ~500MB | ⚠️ 可选 | 模型日志 |

## 🤖 LLM提供商完整分析

### 📋 5个支持的LLM提供商

| 提供商 | 显示名称 | API密钥 | 自定义配置 | 支持模型数 | 默认模型 | 快速模型 |
|--------|----------|---------|------------|------------|----------|----------|
| **openai** | OpenAI | ✅ 必需 | API Base | 25个 | gpt-4o | gpt-4o-mini |
| **anthropic** | Anthropic | ✅ 必需 | API Base | 4个 | claude-3-7-sonnet | claude-3-5-sonnet |
| **azure** | Azure OpenAI | ✅ 必需 | Endpoint, Version, Deployment | 所有OpenAI | 自定义 | 自定义 |
| **bedrock** | AWS Bedrock | ❌ 可选 | Region, Access Key | 4个 | claude-3-5-sonnet | claude-3-5-sonnet |
| **vertex_ai** | GCP Vertex AI | ❌ 不需要 | Credentials, Location | 18个 | gemini-2.0-flash | gemini-2.0-flash-lite |

### 🎯 推荐的LLM配置

#### 🏢 企业级配置 (高质量)
```yaml
主要提供商: OpenAI
主模型: gpt-4o
快速模型: gpt-4o-mini
备用提供商: Anthropic (claude-3-7-sonnet)
成本: 高
质量: 最高
```

#### 💰 成本优化配置 (平衡)
```yaml
主要提供商: Vertex AI
主模型: gemini-2.0-flash
快速模型: gemini-2.0-flash-lite
备用提供商: OpenAI (gpt-4o-mini)
成本: 中等
质量: 高
```

#### 🔒 私有化配置 (安全)
```yaml
主要提供商: Azure OpenAI
主模型: 自定义部署的gpt-4o
快速模型: 自定义部署的gpt-4o-mini
备用提供商: AWS Bedrock
成本: 中等
质量: 高
安全性: 最高
```

## 🌐 网络架构分析

### 🔌 端口分配策略

#### 对外服务端口 (3个)
- **80** - Nginx HTTP (主入口)
- **3000** - 前端直接访问
- **8080** - API直接访问

#### 管理端口 (2个)
- **8081** - Vespa管理界面
- **9005** - MinIO管理控制台

#### 内部服务端口 (7个)
- **5432** - PostgreSQL数据库
- **6379** - Redis缓存
- **9000** - AI推理模型
- **9001** - AI索引模型
- **9004** - MinIO API
- **19071** - Vespa应用

### 🔗 服务通信矩阵

```
前端(3000) → API(8080) → 数据库(5432)
                      → 缓存(6379)
                      → 搜索(19071)
                      → 推理模型(9000)
                      → 文件存储(9004)

后台任务 → 数据库(5432)
        → 缓存(6379)
        → 搜索(19071)
        → 索引模型(9001)
        → 文件存储(9004)

Nginx(80) → 前端(3000)
          → API(8080)
```

## 📊 资源需求完整分析

### 💻 Windows Docker Desktop 最低配置
```yaml
系统要求:
  - Windows 10/11 Pro, Enterprise, 或 Education
  - WSL 2 已启用
  - Hyper-V 已启用

Docker Desktop 配置:
  - 内存分配: 12GB (最低8GB)
  - CPU分配: 6核心 (最低4核心)
  - 磁盘镜像大小: 80GB
  - 交换空间: 2GB

网络配置:
  - 端口转发: 12个端口
  - 防火墙: 允许Docker网络
```

### 📈 性能基准

#### 🚀 理想性能指标
- API响应时间: < 200ms
- 前端加载时间: < 2秒
- 搜索响应时间: < 500ms
- AI推理时间: < 3秒
- 文件上传速度: > 10MB/s

#### ⚠️ 性能警告阈值
- API响应时间: > 1秒
- 内存使用率: > 85%
- CPU使用率: > 80%
- 磁盘使用率: > 90%

## 🛠️ 部署工具完整清单

### 📦 部署脚本 (3个)
1. `tests/install_onyx_windows.bat` - 完整安装流程
2. `tests/deploy_docker_windows.bat` - Docker容器部署
3. `tests/start_onyx.bat` - 快速启动脚本

### 🧪 验证脚本 (5个)
1. `tests/docker_container_checklist.py` - 容器状态验证
2. `tests/docker_manager.py` - 容器管理工具
3. `tests/port_checker.py` - 端口占用检查
4. `tests/health_check.py` - 系统健康检查
5. `tests/llm_config_manager.py` - LLM配置管理

### 📊 监控脚本 (3个)
1. `tests/monitor_system.py` - 实时系统监控
2. `tests/dashboard.py` - 系统状态仪表板
3. `tests/performance_test.py` - 性能基准测试

## 🎯 部署成功验证清单

### ✅ 容器验证 (10项)
- [ ] PostgreSQL数据库容器运行正常
- [ ] Redis缓存容器运行正常
- [ ] MinIO文件存储容器运行正常
- [ ] Vespa搜索引擎容器运行正常
- [ ] AI推理模型服务器运行正常
- [ ] AI索引模型服务器运行正常
- [ ] 后端API服务器运行正常
- [ ] 后台任务处理器运行正常
- [ ] 前端Web服务器运行正常
- [ ] Nginx反向代理运行正常

### ✅ 功能验证 (8项)
- [ ] 用户界面正常访问 (http://localhost)
- [ ] API文档正常访问 (http://localhost/api/docs)
- [ ] 用户认证功能正常
- [ ] 聊天功能正常工作
- [ ] 文档上传功能正常
- [ ] 搜索功能正常工作
- [ ] 助手管理功能正常
- [ ] LLM集成功能正常

### ✅ 性能验证 (5项)
- [ ] API响应时间 < 500ms
- [ ] 前端加载时间 < 3秒
- [ ] 系统内存使用 < 12GB
- [ ] 所有端口正常监听
- [ ] 容器健康检查通过

## 🚀 快速部署命令

### 一键Docker部署
```bash
# 完整Docker部署 (推荐)
tests/deploy_docker_windows.bat

# 验证部署状态
python tests/docker_container_checklist.py

# 检查端口状态
python tests/port_checker.py

# 系统健康检查
python tests/health_check.py
```

### 手动Docker部署
```bash
# 分阶段启动
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d relational_db cache minio
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d index
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d inference_model_server indexing_model_server
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d api_server background web_server
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d nginx
```

---

**📋 总结**: Onyx系统需要10个Docker容器、9个存储卷、12个网络端口，支持5个LLM提供商和75+个AI模型，总资源需求约14GB内存和65GB磁盘空间。**
