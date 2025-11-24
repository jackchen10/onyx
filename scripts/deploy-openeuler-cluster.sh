#!/bin/bash

# Onyx openEuler 20.03 LTS 双服务器集群部署脚本
# 主服务器: 10.0.83.30 (CPU:8核, 内存:32G, 磁盘:100G)
# 数据库服务器: 10.0.83.36 (CPU:8核, 内存:32G, 磁盘:100G)

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 服务器配置
MAIN_SERVER="10.0.83.30"
DB_SERVER="10.0.83.36"
CURRENT_SERVER=$(hostname -I | awk '{print $1}')

# 项目配置
PROJECT_NAME="onyx"
MAIN_COMPOSE_FILE="deployment/docker_compose/docker-compose.main.yml"
DB_COMPOSE_FILE="deployment/docker_compose/docker-compose.db.yml"
LOG_FILE="deploy-cluster.log"

# 服务列表
MAIN_SERVICES=("minio" "index" "inference_model_server" "indexing_model_server" "api_server" "background" "web_server" "nginx")
DB_SERVICES=("relational_db")

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_header() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

# 检查当前服务器
check_current_server() {
    log_info "当前服务器IP: $CURRENT_SERVER"
    
    if [[ "$CURRENT_SERVER" == "$MAIN_SERVER" ]]; then
        log_success "当前在主服务器 ($MAIN_SERVER)"
        return 0
    elif [[ "$CURRENT_SERVER" == "$DB_SERVER" ]]; then
        log_success "当前在数据库服务器 ($DB_SERVER)"
        return 1
    else
        log_error "未识别的服务器IP: $CURRENT_SERVER"
        log_error "请在指定的服务器 ($MAIN_SERVER 或 $DB_SERVER) 上运行此脚本"
        exit 1
    fi
}

# 检查网络连通性
check_network_connectivity() {
    log_info "检查服务器间网络连通性..."
    
    if [[ "$CURRENT_SERVER" == "$MAIN_SERVER" ]]; then
        if ping -c 3 "$DB_SERVER" &> /dev/null; then
            log_success "主服务器到数据库服务器网络连通正常"
        else
            log_error "主服务器无法连接到数据库服务器 ($DB_SERVER)"
            exit 1
        fi
    elif [[ "$CURRENT_SERVER" == "$DB_SERVER" ]]; then
        if ping -c 3 "$MAIN_SERVER" &> /dev/null; then
            log_success "数据库服务器到主服务器网络连通正常"
        else
            log_error "数据库服务器无法连接到主服务器 ($MAIN_SERVER)"
            exit 1
        fi
    fi
}

# 检查已存在的Redis容器
check_existing_redis() {
    log_info "检查已存在的Redis容器..."
    
    if docker ps | grep -q "scow-redis-1"; then
        log_success "发现已存在的Redis容器: scow-redis-1"
        
        # 检查Redis连接
        if docker exec scow-redis-1 redis-cli ping &> /dev/null; then
            log_success "Redis容器运行正常"
        else
            log_warning "Redis容器存在但无法连接"
        fi
    else
        log_error "未找到Redis容器 scow-redis-1"
        log_error "请确保Redis容器已启动"
        exit 1
    fi
}

# 创建Docker Compose配置文件
create_main_compose_file() {
    log_info "创建主服务器Docker Compose配置文件..."
    
    mkdir -p deployment/docker_compose
    
    cat > "$MAIN_COMPOSE_FILE" << 'EOF'
version: '3.8'

services:
  # MinIO对象存储
  minio:
    image: minio/minio:RELEASE.2024-01-16T16-07-38Z
    container_name: onyx-minio
    ports:
      - "9001:9000"
      - "9002:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Vespa搜索引擎
  index:
    image: vespaengine/vespa:8.526.15
    container_name: onyx-vespa
    ports:
      - "8081:8081"
      - "19071:19071"
    volumes:
      - vespa_data:/opt/vespa/var
    environment:
      - VESPA_CONFIGSERVERS=index
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/ApplicationStatus"]
      interval: 30s
      timeout: 10s
      retries: 3

  # 推理模型服务器
  inference_model_server:
    build:
      context: .
      dockerfile: docker/Dockerfile.model_server
    container_name: onyx-inference-model
    ports:
      - "9000:9000"
    environment:
      - MODEL_SERVER_HOST=0.0.0.0
      - MODEL_SERVER_PORT=9000
    env_file:
      - .env.main
    restart: unless-stopped
    depends_on:
      - index

  # 索引模型服务器
  indexing_model_server:
    build:
      context: .
      dockerfile: docker/Dockerfile.model_server
    container_name: onyx-indexing-model
    ports:
      - "9001:9000"
    environment:
      - MODEL_SERVER_HOST=0.0.0.0
      - MODEL_SERVER_PORT=9000
    env_file:
      - .env.main
    restart: unless-stopped
    depends_on:
      - index

  # API后端服务
  api_server:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    container_name: onyx-api-server
    ports:
      - "8080:8080"
    environment:
      - POSTGRES_HOST=10.0.83.36
      - REDIS_HOST=10.0.83.30
      - VESPA_HOST=10.0.83.30
    env_file:
      - .env.main
    restart: unless-stopped
    depends_on:
      - inference_model_server
      - indexing_model_server
      - minio

  # 后台任务处理
  background:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    container_name: onyx-background
    command: python -m onyx.background.celery.celery_app
    environment:
      - POSTGRES_HOST=10.0.83.36
      - REDIS_HOST=10.0.83.30
      - VESPA_HOST=10.0.83.30
    env_file:
      - .env.main
    restart: unless-stopped
    depends_on:
      - api_server

  # Web前端服务
  web_server:
    build:
      context: .
      dockerfile: docker/Dockerfile.web
    container_name: onyx-web-server
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://10.0.83.30:8080
    restart: unless-stopped
    depends_on:
      - api_server

  # Nginx反向代理
  nginx:
    build:
      context: .
      dockerfile: docker/Dockerfile.nginx
    container_name: onyx-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./docker/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./docker/nginx/conf.d:/etc/nginx/conf.d:ro
    restart: unless-stopped
    depends_on:
      - web_server
      - api_server

volumes:
  minio_data:
  vespa_data:

networks:
  default:
    name: onyx_network
    driver: bridge
EOF

    log_success "主服务器Docker Compose配置文件创建完成"
}

# 创建数据库服务器配置文件
create_db_compose_file() {
    log_info "创建数据库服务器Docker Compose配置文件..."
    
    mkdir -p deployment/docker_compose
    
    cat > "$DB_COMPOSE_FILE" << 'EOF'
version: '3.8'

services:
  # PostgreSQL数据库
  relational_db:
    image: postgres:15-alpine
    container_name: onyx-postgres
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: onyx_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: onyx
      POSTGRES_HOST_AUTH_METHOD: md5
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
      - ./docker/postgres/postgresql.conf:/etc/postgresql/postgresql.conf:ro
      - ./docker/postgres/pg_hba.conf:/etc/postgresql/pg_hba.conf:ro
    command: >
      postgres
      -c config_file=/etc/postgresql/postgresql.conf
      -c hba_file=/etc/postgresql/pg_hba.conf
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U onyx_user -d onyx"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:

networks:
  default:
    name: onyx_db_network
    driver: bridge
EOF

    log_success "数据库服务器Docker Compose配置文件创建完成"
}

# 创建PostgreSQL配置文件
create_postgres_config() {
    log_info "创建PostgreSQL配置文件..."
    
    mkdir -p docker/postgres
    
    # 创建postgresql.conf
    cat > docker/postgres/postgresql.conf << 'EOF'
# PostgreSQL配置文件
listen_addresses = '*'
port = 5432
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
min_wal_size = 1GB
max_wal_size = 4GB

# 日志配置
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'all'
log_min_duration_statement = 1000

# 时区
timezone = 'Asia/Shanghai'
EOF

    # 创建pg_hba.conf
    cat > docker/postgres/pg_hba.conf << 'EOF'
# PostgreSQL客户端认证配置文件
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# 本地连接
local   all             all                                     trust
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5

# 允许主服务器连接
host    all             onyx_user       10.0.83.30/32           md5

# 允许内网连接
host    all             onyx_user       10.0.83.0/24            md5

# 允许所有连接（生产环境请谨慎使用）
host    all             all             0.0.0.0/0               md5
EOF

    # 创建初始化SQL
    cat > docker/postgres/init.sql << 'EOF'
-- 创建Onyx数据库用户和数据库
CREATE USER onyx_user WITH PASSWORD 'your_secure_password_here';
CREATE DATABASE onyx OWNER onyx_user;
GRANT ALL PRIVILEGES ON DATABASE onyx TO onyx_user;

-- 创建必要的扩展
\c onyx;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- 授权
GRANT ALL ON SCHEMA public TO onyx_user;
EOF

    log_success "PostgreSQL配置文件创建完成"
}

# 设置集群环境
setup_cluster() {
    log_header "设置双服务器集群环境"
    
    check_current_server
    check_network_connectivity
    
    if [[ "$CURRENT_SERVER" == "$MAIN_SERVER" ]]; then
        log_info "在主服务器上设置环境..."
        check_existing_redis
        create_main_compose_file
        
        # 创建主服务器环境配置
        if [ ! -f ".env.main" ]; then
            cp deployment/docker_compose/env.prod.template .env.main
            log_warning "请编辑 .env.main 文件配置必要参数"
        fi
        
    elif [[ "$CURRENT_SERVER" == "$DB_SERVER" ]]; then
        log_info "在数据库服务器上设置环境..."
        create_db_compose_file
        create_postgres_config
        
        # 创建数据库服务器环境配置
        if [ ! -f ".env.db" ]; then
            cp deployment/docker_compose/env.prod.template .env.db
            log_warning "请编辑 .env.db 文件配置数据库参数"
        fi
    fi
    
    log_success "集群环境设置完成"
}

# 部署主服务器
deploy_main() {
    log_header "部署主服务器服务"
    
    if [[ "$CURRENT_SERVER" != "$MAIN_SERVER" ]]; then
        log_error "请在主服务器 ($MAIN_SERVER) 上运行此命令"
        exit 1
    fi
    
    local build_images=false
    if [ "$1" = "--build" ]; then
        build_images=true
    fi
    
    check_existing_redis
    
    if [ "$build_images" = true ]; then
        log_info "构建Docker镜像..."
        docker-compose -f "$MAIN_COMPOSE_FILE" build --parallel
    fi
    
    log_info "启动主服务器服务..."
    docker-compose -f "$MAIN_COMPOSE_FILE" up -d
    
    log_success "主服务器部署完成"
    log_info "访问地址:"
    log_info "  前端: http://$MAIN_SERVER"
    log_info "  API文档: http://$MAIN_SERVER/api/docs"
}

# 部署数据库服务器
deploy_db() {
    log_header "部署数据库服务器"
    
    if [[ "$CURRENT_SERVER" != "$DB_SERVER" ]]; then
        log_error "请在数据库服务器 ($DB_SERVER) 上运行此命令"
        exit 1
    fi
    
    log_info "启动PostgreSQL数据库..."
    docker-compose -f "$DB_COMPOSE_FILE" --env-file .env.db up -d
    
    # 等待数据库启动
    log_info "等待数据库启动..."
    sleep 30
    
    # 检查数据库连接
    if docker-compose -f "$DB_COMPOSE_FILE" exec -T relational_db pg_isready -U onyx_user -d onyx; then
        log_success "数据库启动成功"
    else
        log_error "数据库启动失败"
        exit 1
    fi
    
    log_success "数据库服务器部署完成"
    log_info "数据库连接信息:"
    log_info "  主机: $DB_SERVER"
    log_info "  端口: 5432"
    log_info "  数据库: onyx"
    log_info "  用户: onyx_user"
}

# 显示集群状态
show_cluster_status() {
    log_header "集群状态"
    
    if [[ "$CURRENT_SERVER" == "$MAIN_SERVER" ]]; then
        log_info "主服务器服务状态:"
        docker-compose -f "$MAIN_COMPOSE_FILE" ps
        
        log_info "Redis容器状态:"
        docker ps | grep scow-redis-1 || log_warning "Redis容器未运行"
        
    elif [[ "$CURRENT_SERVER" == "$DB_SERVER" ]]; then
        log_info "数据库服务器状态:"
        docker-compose -f "$DB_COMPOSE_FILE" ps
    fi
}

# 显示帮助信息
show_help() {
    echo "Onyx openEuler 20.03 LTS 双服务器集群部署脚本"
    echo ""
    echo "服务器配置:"
    echo "  主服务器: $MAIN_SERVER (CPU:8核, 内存:32G, 磁盘:100G)"
    echo "  数据库服务器: $DB_SERVER (CPU:8核, 内存:32G, 磁盘:100G)"
    echo ""
    echo "用法: $0 <命令> [选项]"
    echo ""
    echo "集群管理命令:"
    echo "  setup-cluster       设置双服务器集群环境"
    echo "  deploy-main [--build]  部署主服务器服务"
    echo "  deploy-db           部署数据库服务器"
    echo "  status              显示集群状态"
    echo ""
    echo "示例:"
    echo "  # 在两台服务器上分别设置环境"
    echo "  $0 setup-cluster"
    echo ""
    echo "  # 在主服务器上部署应用服务"
    echo "  $0 deploy-main --build"
    echo ""
    echo "  # 在数据库服务器上部署数据库"
    echo "  $0 deploy-db"
}

# 主函数
main() {
    local command="$1"
    local option="$2"
    
    touch "$LOG_FILE"
    
    case "$command" in
        "setup-cluster")
            setup_cluster
            ;;
        "deploy-main")
            deploy_main "$option"
            ;;
        "deploy-db")
            deploy_db
            ;;
        "status")
            show_cluster_status
            ;;
        "help"|"--help"|"-h"|"")
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
