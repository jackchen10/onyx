# Onyx Docker 快速启动指南

## 🚀 一键部署

### 前提条件
- Windows 10/11 with Docker Desktop
- 最少8GB RAM，推荐16GB
- 最少20GB可用磁盘空间
- WSL2支持已启用

### 快速启动命令
```powershell
# 1. 克隆或下载项目代码
git clone <repository-url> onyx
cd onyx

# 2. 一键部署（包含构建和启动）
.\deploy.ps1 -Action deploy -Build

# 3. 访问应用
# 前端: http://localhost
# API文档: http://localhost/api/docs
```

## 📋 详细部署步骤

### 步骤1: 环境准备
```powershell
# 检查Docker Desktop是否运行
docker version

# 检查Docker Compose
docker-compose version

# 设置PowerShell执行策略（如果需要）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 步骤2: 项目配置
```powershell
# 进入项目目录
cd D:/code/onyx

# 检查项目结构
ls docker/
ls backend/
ls web/

# 创建环境配置文件（如果不存在）
cp deployment/docker_compose/env.dev.template backend/.env
# 编辑 backend/.env 文件，配置必要参数
```

### 步骤3: 构建和部署
```powershell
# 方法1: 使用部署脚本（推荐）
.\deploy.ps1 -Action deploy -Build

# 方法2: 手动执行
docker-compose build
docker-compose up -d
```

### 步骤4: 验证部署
```powershell
# 检查服务状态
.\deploy.ps1 -Action status

# 查看日志
.\deploy.ps1 -Action logs

# 测试服务
curl http://localhost/health
curl http://localhost/api/health
```

## 🛠️ 常用操作命令

### 服务管理
```powershell
# 启动所有服务
.\deploy.ps1 -Action start

# 停止所有服务
.\deploy.ps1 -Action stop

# 重启服务
.\deploy.ps1 -Action restart

# 查看服务状态
.\deploy.ps1 -Action status

# 查看日志
.\deploy.ps1 -Action logs

# 查看特定服务日志
.\deploy.ps1 -Action logs -Service api-backend
```

### 镜像管理
```powershell
# 重新构建镜像
.\deploy.ps1 -Action build -Clean

# 导出镜像包
.\export-images.ps1

# 导出并压缩
.\export-images.ps1 -Compress

# 清理所有容器和镜像
.\deploy.ps1 -Action clean
```

### 数据管理
```powershell
# 备份数据库
docker-compose exec postgres pg_dump -U onyx_user onyx > backup.sql

# 恢复数据库
docker-compose exec -T postgres psql -U onyx_user onyx < backup.sql

# 查看数据库
docker-compose exec postgres psql -U onyx_user onyx

# 查看Redis数据
docker-compose exec redis redis-cli
```

## 🔧 配置说明

### 环境变量配置 (backend/.env)
```bash
# 数据库配置
DATABASE_URL=postgresql://onyx_user:onyx_password@postgres:5432/onyx
REDIS_URL=redis://redis:6379/0

# AI模型配置
OPENAI_API_KEY=your-openai-api-key-here
MODEL_SERVER_URL=http://model-server:9000

# 安全配置
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# 日志配置
LOG_LEVEL=INFO
```

### Docker Compose服务说明
| 服务名 | 端口 | 说明 |
|--------|------|------|
| nginx-proxy | 80, 443 | 反向代理和负载均衡 |
| web-frontend | 3000 | Next.js前端应用 |
| api-backend | 8080 | FastAPI后端API |
| model-server | 9000 | AI模型推理服务 |
| postgres | 5432 | PostgreSQL数据库 |
| redis | 6379 | Redis缓存 |
| celery-worker | - | 后台任务处理 |

### 资源配置
```yaml
# 推荐的Docker Desktop配置
Memory: 8GB (最少6GB)
CPUs: 4 cores (最少2核)
Swap: 2GB
Disk: 20GB (最少)
```

## 🐛 故障排除

### 常见问题

#### 1. 容器启动失败
```powershell
# 查看详细日志
docker-compose logs [service-name]

# 检查容器状态
docker-compose ps

# 重新构建镜像
.\deploy.ps1 -Action build -Clean
```

#### 2. 端口冲突
```powershell
# 检查端口占用
netstat -an | findstr :80
netstat -an | findstr :8080

# 修改docker-compose.yml中的端口映射
# 例如: "8081:80" 替代 "80:80"
```

#### 3. 内存不足
```powershell
# 增加Docker Desktop内存限制
# Docker Desktop -> Settings -> Resources -> Memory

# 或减少并发服务
docker-compose up -d postgres redis api-backend web-frontend
```

#### 4. 数据库连接失败
```powershell
# 检查数据库容器
docker-compose exec postgres pg_isready -U onyx_user -d onyx

# 重置数据库
docker-compose down -v
docker-compose up -d postgres
```

#### 5. 前端构建失败
```powershell
# 检查yarn安装状态
cd web
yarn install

# 手动构建前端
yarn build

# 重新构建前端镜像
docker-compose build web-frontend
```

### 性能优化

#### 1. 镜像优化
```powershell
# 使用多阶段构建减少镜像大小
# 清理Docker缓存
docker system prune -af

# 查看镜像大小
docker images
```

#### 2. 资源监控
```powershell
# 查看容器资源使用
docker stats

# 查看系统资源
docker system df
```

#### 3. 网络优化
```powershell
# 检查网络配置
docker network ls
docker network inspect onyx_onyx-network
```

## 📦 镜像分发

### 创建分发包
```powershell
# 导出所有镜像
.\export-images.ps1 -Compress

# 创建完整部署包
.\create-deployment-package.ps1
```

### 在目标机器部署
```powershell
# 1. 解压部署包
Expand-Archive onyx-docker-deployment-*.zip -DestinationPath onyx-deployment

# 2. 进入目录
cd onyx-deployment

# 3. 导入镜像
cd docker-images
.\import-images.ps1

# 4. 启动服务
cd ..
docker-compose up -d
```

## 🔒 安全配置

### 生产环境安全
```bash
# 修改默认密码
POSTGRES_PASSWORD=your-secure-password
JWT_SECRET=your-secure-jwt-secret

# 启用HTTPS
# 配置SSL证书到 docker/nginx/ssl/

# 限制网络访问
# 修改docker-compose.yml中的网络配置
```

### 防火墙配置
```powershell
# Windows防火墙规则
New-NetFirewallRule -DisplayName "Onyx HTTP" -Direction Inbound -Protocol TCP -LocalPort 80
New-NetFirewallRule -DisplayName "Onyx HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443
```

## 📊 监控和日志

### 日志查看
```powershell
# 实时日志
.\deploy.ps1 -Action logs

# 特定服务日志
docker-compose logs -f api-backend

# 日志文件位置
ls logs/
```

### 健康检查
```powershell
# 检查所有服务健康状态
docker-compose ps

# 手动健康检查
curl http://localhost/health
curl http://localhost/api/health
```

## 🎯 下一步

部署成功后，您可以：

1. **配置AI模型**: 在环境变量中设置API密钥
2. **添加数据连接器**: 通过管理界面配置数据源
3. **创建用户账户**: 设置用户认证和权限
4. **自定义配置**: 根据需求调整系统参数
5. **监控和维护**: 设置日志监控和备份策略

## 📞 获取帮助

如果遇到问题：
1. 查看本文档的故障排除部分
2. 检查项目的GitHub Issues
3. 查看Docker和Docker Compose官方文档
4. 联系技术支持团队

---

**最后更新**: 2025-02-19
**适用版本**: Onyx v1.0+
**环境要求**: Windows Docker Desktop
