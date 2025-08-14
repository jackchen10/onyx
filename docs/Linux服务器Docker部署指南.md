# Onyx Linux服务器 Docker 双机部署完整指南
## 适用于 openEuler 20.03 LTS 双服务器架构

## 🏗️ 部署架构

### 服务器资源配置
- **主服务器 (10.0.83.30)**: CPU 8核, 内存 32GB, 磁盘 100GB
- **数据库服务器 (10.0.83.36)**: CPU 8核, 内存 32GB, 磁盘 100GB
- **网络**: 内网互通，支持跨服务器访问

### 服务分布架构
```
主服务器 (10.0.83.30)
├── nginx-proxy (80, 443)
├── web-frontend (3000)
├── api-backend (8080)
├── model-server (9000)
├── vespa-index (8081)
├── minio (9000)
├── celery-worker
└── scow-redis-1 (6379) [已存在，复用]

数据库服务器 (10.0.83.36)
└── postgresql (5432) [远程访问配置]
```

## 🚀 快速部署命令

### 主服务器 (10.0.83.30) 部署
```bash
# 1. 克隆项目代码
git clone <repository-url> onyx
cd onyx

# 2. 设置执行权限
chmod +x deploy-openeuler-cluster.sh

# 3. 配置双服务器环境
./deploy-openeuler-cluster.sh setup-cluster

# 4. 部署主服务器服务
./deploy-openeuler-cluster.sh deploy-main --build

# 5. 访问应用
# 前端: http://10.0.83.30
# API文档: http://10.0.83.30/api/docs
```

### 数据库服务器 (10.0.83.36) 部署
```bash
# 1. 克隆项目代码
git clone <repository-url> onyx
cd onyx

# 2. 部署PostgreSQL数据库
./deploy-openeuler-cluster.sh deploy-db
```

## 📋 详细部署步骤

### 步骤1: 系统环境准备

#### 1.1 更新系统包
```bash
# 更新系统包管理器
sudo yum update -y

# 安装基础工具
sudo yum install -y \
    curl \
    wget \
    git \
    vim \
    net-tools \
    firewalld \
    yum-utils \
    device-mapper-persistent-data \
    lvm2
```

#### 1.2 安装Docker
```bash
# 添加Docker官方仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 安装Docker CE
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动并启用Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 验证Docker安装
sudo docker version
sudo docker run hello-world
```

#### 1.3 安装Docker Compose
```bash
# 下载Docker Compose
COMPOSE_VERSION="2.24.0"
sudo curl -L "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 设置执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 创建软链接
sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

# 验证安装
docker-compose --version
```

#### 1.4 配置Docker用户权限
```bash
# 创建docker用户组（如果不存在）
sudo groupadd docker

# 将当前用户添加到docker组
sudo usermod -aG docker $USER

# 重新登录或执行以下命令使权限生效
newgrp docker

# 验证无sudo权限运行docker
docker ps
```

### 步骤2: 防火墙和网络配置

#### 2.1 配置防火墙
```bash
# 启动防火墙服务
sudo systemctl start firewalld
sudo systemctl enable firewalld

# 开放必要端口
sudo firewall-cmd --permanent --add-port=80/tcp      # HTTP
sudo firewall-cmd --permanent --add-port=443/tcp     # HTTPS
sudo firewall-cmd --permanent --add-port=8080/tcp    # API Backend
sudo firewall-cmd --permanent --add-port=3000/tcp    # Frontend (备用)

# 重载防火墙配置
sudo firewall-cmd --reload

# 查看开放的端口
sudo firewall-cmd --list-ports
```

#### 2.2 配置SELinux（如果启用）
```bash
# 检查SELinux状态
getenforce

# 如果是Enforcing，设置为Permissive（生产环境请谨慎）
sudo setenforce 0
sudo sed -i 's/SELINUX=enforcing/SELINUX=permissive/g' /etc/selinux/config
```

### 步骤3: 双服务器项目配置

#### 3.1 主服务器 (10.0.83.30) 配置
```bash
# 进入项目目录
cd /path/to/onyx

# 检查项目结构
ls -la docker/
ls -la backend/
ls -la web/
ls -la deployment/docker_compose/
```

#### 3.2 创建主服务器环境配置文件
```bash
# 复制环境变量模板
cp deployment/docker_compose/env.prod.template .env.main

# 编辑主服务器环境配置文件
vim .env.main
```

#### 3.3 主服务器环境变量配置
```bash
# 数据库配置（连接到远程数据库服务器）
POSTGRES_HOST=10.0.83.36
POSTGRES_PORT=5432
POSTGRES_USER=onyx_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=onyx

# AI模型配置（必需）
GEN_AI_API_KEY=your-openai-api-key-here

# 认证配置
AUTH_TYPE=disabled  # 或 basic/google_oauth
SECRET=your-secret-key-here
ENCRYPTION_KEY_SECRET=your-encryption-key-here

# Web域名配置
WEB_DOMAIN=http://10.0.83.30:3000
CORS_ALLOWED_ORIGIN=http://10.0.83.30

# Redis配置（使用已存在的容器）
REDIS_HOST=10.0.83.30
REDIS_PORT=6379
REDIS_PASSWORD=  # 无密码

# MinIO配置
S3_ENDPOINT_URL=http://10.0.83.30:9001
S3_AWS_ACCESS_KEY_ID=minioadmin
S3_AWS_SECRET_ACCESS_KEY=minioadmin

# Vespa配置
VESPA_HOST=10.0.83.30
VESPA_PORT=8081

# 日志配置
LOG_LEVEL=info
```

#### 3.4 数据库服务器 (10.0.83.36) 配置
```bash
# 创建数据库服务器环境配置文件
cp deployment/docker_compose/env.prod.template .env.db

# 编辑数据库服务器环境配置文件
vim .env.db
```

#### 3.5 数据库服务器环境变量配置
```bash
# PostgreSQL配置
POSTGRES_HOST=0.0.0.0  # 监听所有接口
POSTGRES_PORT=5432
POSTGRES_USER=onyx_user
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=onyx

# 允许远程连接
POSTGRES_HOST_AUTH_METHOD=md5
POSTGRES_INITDB_ARGS=--auth-host=md5

# 日志配置
LOG_LEVEL=info
```

### 步骤4: 构建和部署

#### 4.1 使用部署脚本（推荐）
```bash
# 赋予执行权限
chmod +x deploy-linux.sh

# 完整部署（包含构建）
./deploy-linux.sh deploy --build

# 或者分步执行
./deploy-linux.sh build    # 构建镜像
./deploy-linux.sh start    # 启动服务
```

#### 4.2 手动部署
```bash
# 构建所有镜像
docker-compose -f deployment/docker_compose/docker-compose.dev.yml build

# 启动基础服务
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d relational_db cache minio index

# 等待基础服务启动完成
sleep 30

# 启动应用服务
docker-compose -f deployment/docker_compose/docker-compose.dev.yml up -d api_server background web_server nginx
```

### 步骤5: 验证部署

#### 5.1 检查服务状态
```bash
# 查看所有容器状态
docker-compose -f deployment/docker_compose/docker-compose.dev.yml ps

# 查看服务日志
docker-compose -f deployment/docker_compose/docker-compose.dev.yml logs

# 检查特定服务日志
docker-compose -f deployment/docker_compose/docker-compose.dev.yml logs api_server
```

#### 5.2 健康检查
```bash
# 检查服务健康状态
curl -f http://localhost/health
curl -f http://localhost/api/health
curl -f http://localhost/api/docs

# 检查数据库连接
docker-compose -f deployment/docker_compose/docker-compose.dev.yml exec relational_db pg_isready -U postgres -d onyx
```

## 🛠️ 服务管理命令

### 基本操作
```bash
# 启动所有服务
./deploy-linux.sh start

# 停止所有服务
./deploy-linux.sh stop

# 重启服务
./deploy-linux.sh restart

# 查看服务状态
./deploy-linux.sh status

# 查看日志
./deploy-linux.sh logs

# 查看特定服务日志
./deploy-linux.sh logs api_server
```

### 镜像管理
```bash
# 重新构建镜像
./deploy-linux.sh build --clean

# 清理未使用的镜像
docker system prune -af

# 查看镜像大小
docker images
```

### 数据管理
```bash
# 备份数据库
docker-compose -f deployment/docker_compose/docker-compose.dev.yml exec relational_db pg_dump -U postgres onyx > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复数据库
docker-compose -f deployment/docker_compose/docker-compose.dev.yml exec -T relational_db psql -U postgres onyx < backup.sql

# 查看数据库
docker-compose -f deployment/docker_compose/docker-compose.dev.yml exec relational_db psql -U postgres onyx

# 查看Redis数据
docker-compose -f deployment/docker_compose/docker-compose.dev.yml exec cache redis-cli
```

## 🔧 系统优化配置

### 内核参数优化
```bash
# 编辑系统参数
sudo vim /etc/sysctl.conf

# 添加以下配置
vm.max_map_count=262144
net.core.somaxconn=65535
net.ipv4.tcp_max_syn_backlog=65535
fs.file-max=1000000

# 应用配置
sudo sysctl -p
```

### Docker守护进程优化
```bash
# 创建Docker配置目录
sudo mkdir -p /etc/docker

# 创建Docker配置文件
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
EOF

# 重启Docker服务
sudo systemctl restart docker
```

## 🔒 安全配置

### 生产环境安全设置
```bash
# 修改默认密码
POSTGRES_PASSWORD=your_very_secure_password_here
SECRET=your_very_secure_secret_key_here

# 限制网络访问（仅允许必要端口）
sudo firewall-cmd --permanent --remove-port=8080/tcp
sudo firewall-cmd --permanent --remove-port=3000/tcp
sudo firewall-cmd --reload

# 配置SSL证书（如果有）
mkdir -p docker/nginx/ssl/
# 将SSL证书文件放入该目录
```

### 用户权限管理
```bash
# 创建专用用户运行应用
sudo useradd -r -s /bin/false onyx-app
sudo usermod -aG docker onyx-app

# 设置文件权限
sudo chown -R onyx-app:onyx-app /path/to/onyx
sudo chmod -R 755 /path/to/onyx
```

## 📊 监控和日志

### 系统监控
```bash
# 查看系统资源使用
htop
free -h
df -h

# 查看Docker资源使用
docker stats

# 查看网络连接
netstat -tulpn | grep -E ':(80|443|8080|3000|5432|6379)'
```

### 日志管理
```bash
# 查看系统日志
sudo journalctl -u docker.service -f

# 查看应用日志
tail -f logs/*.log

# 日志轮转配置
sudo vim /etc/logrotate.d/onyx
```

## 🐛 故障排除

### 常见问题解决

#### 1. 容器启动失败
```bash
# 查看详细错误信息
docker-compose -f deployment/docker_compose/docker-compose.dev.yml logs --tail=50

# 检查端口占用
netstat -tulpn | grep :80
netstat -tulpn | grep :8080

# 重新构建镜像
docker-compose -f deployment/docker_compose/docker-compose.dev.yml build --no-cache
```

#### 2. 网络连接问题
```bash
# 检查防火墙状态
sudo firewall-cmd --list-all

# 检查Docker网络
docker network ls
docker network inspect onyx_default

# 测试内部网络连通性
docker-compose -f deployment/docker_compose/docker-compose.dev.yml exec api_server ping relational_db
```

#### 3. 权限问题
```bash
# 检查文件权限
ls -la /path/to/onyx

# 修复权限问题
sudo chown -R $USER:$USER /path/to/onyx
sudo chmod -R 755 /path/to/onyx
```

## 🎯 部署完成后的配置

### 访问验证
1. **前端应用**: http://服务器IP
2. **API文档**: http://服务器IP/api/docs
3. **健康检查**: http://服务器IP/health

### 后续配置
1. 配置域名和SSL证书
2. 设置定期备份任务
3. 配置监控告警
4. 优化性能参数

---

**最后更新**: 2025-02-19
**适用版本**: Onyx v1.0+
**系统要求**: openEuler 20.03 LTS+
