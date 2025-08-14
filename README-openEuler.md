# Onyx openEuler 20.03 LTS 双服务器集群部署指南

## 🏗️ 集群架构

### 服务器资源配置
- **主服务器 (10.0.83.30)**: CPU 8核, 内存 32GB, 磁盘 100GB
- **数据库服务器 (10.0.83.36)**: CPU 8核, 内存 32GB, 磁盘 100GB
- **网络**: 内网互通，支持跨服务器访问

### 服务分布
```
主服务器 (10.0.83.30)
├── nginx-proxy (80, 443)
├── web-frontend (3000)
├── api-backend (8080)
├── model-server (9000, 9001)
├── vespa-index (8081)
├── minio (9001, 9002)
├── celery-worker
└── scow-redis-1 (6379) [已存在，复用]

数据库服务器 (10.0.83.36)
└── postgresql (5432) [远程访问配置]
```

## 🚀 快速部署

### 前置条件
- 两台服务器都已安装Docker和Docker Compose
- 主服务器上已存在Redis容器 `scow-redis-1`
- 服务器间网络互通

### 部署步骤

#### 1. 在两台服务器上准备项目
```bash
# 在主服务器 (10.0.83.30) 和数据库服务器 (10.0.83.36) 上分别执行
git clone <repository-url> onyx
cd onyx
chmod +x deploy-openeuler-cluster.sh
```

#### 2. 设置集群环境
```bash
# 在两台服务器上分别执行
./deploy-openeuler-cluster.sh setup-cluster
```

#### 3. 配置环境变量
```bash
# 在主服务器 (10.0.83.30) 上编辑
vim .env.main
# 配置: POSTGRES_PASSWORD, GEN_AI_API_KEY, SECRET

# 在数据库服务器 (10.0.83.36) 上编辑
vim .env.db
# 配置: POSTGRES_PASSWORD (与主服务器保持一致)
```

#### 4. 部署数据库服务器
```bash
# 在数据库服务器 (10.0.83.36) 上执行
./deploy-openeuler-cluster.sh deploy-db
```

#### 5. 部署主服务器
```bash
# 在主服务器 (10.0.83.30) 上执行
./deploy-openeuler-cluster.sh deploy-main --build
```

#### 6. 验证部署
```bash
# 检查集群状态
./deploy-openeuler-cluster.sh status

# 访问应用
# 前端: http://10.0.83.30
# API文档: http://10.0.83.30/api/docs
```

## 📋 详细步骤说明

### 步骤1: 系统环境安装

```bash
# 安装Docker、Docker Compose和系统优化
./deploy-openeuler.sh install
```

这个命令会：
- 检查openEuler版本
- 安装系统依赖包
- 安装Docker CE
- 安装Docker Compose
- 配置防火墙规则
- 优化系统参数
- 配置Docker镜像加速

### 步骤2: 环境变量配置

```bash
# 编辑环境配置文件
vim .env
```

必需配置项：
```bash
# 数据库密码（必需）
POSTGRES_PASSWORD=your_secure_password_here

# AI API密钥（必需）
GEN_AI_API_KEY=your-openai-api-key-here

# 应用密钥（必需）
SECRET=your-secret-key-here

# 加密密钥（推荐）
ENCRYPTION_KEY_SECRET=your-encryption-key-here

# 认证类型（可选）
AUTH_TYPE=disabled  # 或 basic/google_oauth
```

### 步骤3: 部署应用

```bash
# 完整部署（包含构建镜像）
./deploy-openeuler.sh deploy --build
```

部署过程包括：
- 检查系统资源
- 创建必要目录
- 构建Docker镜像
- 启动基础服务（数据库、缓存等）
- 启动应用服务（API、前端等）
- 执行健康检查

## 🛠️ 常用管理命令

### 服务管理
```bash
# 查看服务状态
./deploy-openeuler.sh status

# 启动服务
./deploy-openeuler.sh start

# 停止服务
./deploy-openeuler.sh stop

# 重启服务
./deploy-openeuler.sh restart

# 查看日志
./deploy-openeuler.sh logs

# 查看特定服务日志
./deploy-openeuler.sh logs api_server
```

### 镜像管理
```bash
# 重新构建镜像
./deploy-openeuler.sh build

# 清理构建并重新构建
./deploy-openeuler.sh build --clean
```

### 数据管理
```bash
# 备份数据
./deploy-openeuler.sh backup

# 清理Docker资源
./deploy-openeuler.sh cleanup
```

### 系统验证
```bash
# 全面验证部署状态
./verify-openeuler-deployment.sh
```

## 🌐 访问应用

部署完成后，可以通过以下地址访问：

- **前端应用**: http://服务器IP
- **API文档**: http://服务器IP/api/docs
- **健康检查**: http://服务器IP/health

## 🔧 系统优化

### 防火墙配置
脚本会自动配置以下端口：
- 80/tcp - HTTP访问
- 443/tcp - HTTPS访问
- 8080/tcp - API后端（可选）
- 3000/tcp - 前端服务（可选）

### 系统参数优化
自动优化的系统参数：
```bash
vm.max_map_count=262144
net.core.somaxconn=65535
net.ipv4.tcp_max_syn_backlog=65535
fs.file-max=1000000
vm.swappiness=10
```

### Docker配置优化
- 配置国内镜像加速源
- 设置日志轮转
- 使用overlay2存储驱动

## 🐛 故障排除

### 常见问题

#### 1. Docker权限问题
```bash
# 解决方案：重新登录系统
exit
# 重新SSH登录
```

#### 2. 端口冲突
```bash
# 检查端口占用
netstat -tuln | grep :80

# 停止占用端口的服务
sudo systemctl stop nginx  # 如果有其他nginx服务
```

#### 3. 内存不足
```bash
# 检查内存使用
free -h

# 清理系统缓存
sudo sync && sudo sysctl vm.drop_caches=3
```

#### 4. 磁盘空间不足
```bash
# 检查磁盘使用
df -h

# 清理Docker资源
./deploy-openeuler.sh cleanup
```

### 日志查看
```bash
# 查看部署日志
tail -f deploy-openeuler.log

# 查看特定服务日志
./deploy-openeuler.sh logs api_server

# 查看系统日志
sudo journalctl -u docker.service -f
```

## 📊 性能监控

### 资源监控
```bash
# 查看容器资源使用
docker stats

# 查看系统资源
htop

# 查看磁盘IO
iotop
```

### 服务监控
```bash
# 检查服务健康状态
./deploy-openeuler.sh health

# 查看服务状态
./deploy-openeuler.sh status
```

## 🔒 安全配置

### 生产环境建议
1. 修改默认密码
2. 配置SSL证书
3. 限制网络访问
4. 定期备份数据
5. 监控系统日志

### 用户权限管理
```bash
# 创建专用用户
sudo useradd -r -s /bin/false onyx-app
sudo usermod -aG docker onyx-app

# 设置文件权限
sudo chown -R onyx-app:onyx-app /path/to/onyx
```

## 📚 更多资源

- [完整部署文档](docs/Linux服务器Docker部署指南.md)
- [Docker快速启动指南](docs/Docker快速启动指南.md)
- [故障排除指南](docs/故障排除指南.md)

## 🆘 获取帮助

```bash
# 查看部署脚本帮助
./deploy-openeuler.sh help

# 验证系统状态
./verify-openeuler-deployment.sh
```

如果遇到问题：
1. 查看日志文件：`deploy-openeuler.log`
2. 运行验证脚本：`./verify-openeuler-deployment.sh`
3. 查看Docker日志：`docker-compose logs`
4. 检查系统资源：`htop`, `df -h`

---

**最后更新**: 2025-02-19  
**适用版本**: Onyx v1.0+  
**系统要求**: openEuler 20.03 LTS+
