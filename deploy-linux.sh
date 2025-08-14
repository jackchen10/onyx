#!/bin/bash
# Onyx Linux服务器生产部署脚本
# 支持Ubuntu 20.04/22.04, CentOS 8+, RHEL 8+

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

echo_success() { echo -e "${GREEN}✅ $1${NC}"; }
echo_warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
echo_error() { echo -e "${RED}❌ $1${NC}"; }
echo_info() { echo -e "${CYAN}ℹ️ $1${NC}"; }
echo_header() { echo -e "${BLUE}🚀 $1${NC}"; }

# 配置参数
DEPLOYMENT_TYPE=${1:-"single"}  # single, cluster, minimal
ENVIRONMENT=${2:-"production"}   # development, staging, production

# 检测操作系统
detect_os() {
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        OS=$ID
        OS_VERSION=$VERSION_ID
        echo_info "检测到操作系统: $PRETTY_NAME"
    else
        echo_error "无法检测操作系统"
        exit 1
    fi
}

# 检查系统要求
check_system_requirements() {
    echo_header "检查系统要求"
    
    # 检查CPU核心数
    CPU_CORES=$(nproc)
    echo_info "CPU核心数: $CPU_CORES"
    
    if [[ $CPU_CORES -lt 4 ]]; then
        echo_error "CPU核心数不足，最少需要4核心"
        exit 1
    fi
    
    # 检查内存
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    echo_info "系统内存: ${MEMORY_GB}GB"
    
    case $DEPLOYMENT_TYPE in
        "minimal")
            MIN_MEMORY=8
            ;;
        "single")
            MIN_MEMORY=16
            ;;
        "cluster")
            MIN_MEMORY=32
            ;;
    esac
    
    if [[ $MEMORY_GB -lt $MIN_MEMORY ]]; then
        echo_error "内存不足，$DEPLOYMENT_TYPE 部署最少需要 ${MIN_MEMORY}GB"
        exit 1
    fi
    
    # 检查磁盘空间
    DISK_GB=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
    echo_info "可用磁盘空间: ${DISK_GB}GB"
    
    if [[ $DISK_GB -lt 50 ]]; then
        echo_error "磁盘空间不足，最少需要50GB"
        exit 1
    fi
    
    # 检查网络连接
    if ping -c 1 google.com &> /dev/null; then
        echo_success "网络连接正常"
    else
        echo_warning "网络连接可能有问题"
    fi
    
    echo_success "系统要求检查通过"
}

# 安装Docker
install_docker() {
    echo_header "安装Docker"
    
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        echo_success "Docker已安装: $DOCKER_VERSION"
        return
    fi
    
    case $OS in
        "ubuntu"|"debian")
            # 更新包索引
            sudo apt-get update
            
            # 安装必要的包
            sudo apt-get install -y \
                ca-certificates \
                curl \
                gnupg \
                lsb-release \
                software-properties-common
            
            # 添加Docker官方GPG密钥
            sudo mkdir -p /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/$OS/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            
            # 设置稳定版仓库
            echo \
                "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS \
                $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            # 安装Docker Engine
            sudo apt-get update
            sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
            
        "centos"|"rhel"|"rocky"|"almalinux")
            # 安装yum-utils
            sudo yum install -y yum-utils
            
            # 添加Docker仓库
            sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
            
            # 安装Docker
            sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
            ;;
            
        *)
            echo_error "不支持的操作系统: $OS"
            exit 1
            ;;
    esac
    
    # 启动Docker服务
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 添加当前用户到docker组
    sudo usermod -aG docker $USER
    
    echo_success "Docker安装完成"
    echo_warning "请重新登录以使docker组权限生效，或运行: newgrp docker"
}

# 安装Docker Compose
install_docker_compose() {
    echo_header "安装Docker Compose"
    
    if command -v docker-compose &> /dev/null; then
        COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f4 | cut -d',' -f1)
        echo_success "Docker Compose已安装: $COMPOSE_VERSION"
        return
    fi
    
    # 下载Docker Compose
    COMPOSE_VERSION="2.24.0"
    sudo curl -L "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 设置执行权限
    sudo chmod +x /usr/local/bin/docker-compose
    
    # 创建符号链接
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    echo_success "Docker Compose安装完成"
}

# 配置系统优化
configure_system_optimization() {
    echo_header "配置系统优化"
    
    # 配置内核参数
    cat > /tmp/onyx-sysctl.conf << EOF
# Onyx系统优化参数
vm.max_map_count=262144
vm.swappiness=10
net.core.somaxconn=65535
net.ipv4.tcp_max_syn_backlog=65535
net.core.netdev_max_backlog=5000
net.ipv4.tcp_fin_timeout=30
net.ipv4.tcp_keepalive_time=1200
fs.file-max=2097152
EOF
    
    sudo cp /tmp/onyx-sysctl.conf /etc/sysctl.d/99-onyx.conf
    sudo sysctl -p /etc/sysctl.d/99-onyx.conf
    
    # 配置文件描述符限制
    cat > /tmp/onyx-limits.conf << EOF
# Onyx文件描述符限制
* soft nofile 65535
* hard nofile 65535
* soft nproc 65535
* hard nproc 65535
EOF
    
    sudo cp /tmp/onyx-limits.conf /etc/security/limits.d/99-onyx.conf
    
    echo_success "系统优化配置完成"
}

# 创建目录结构
create_directory_structure() {
    echo_header "创建目录结构"
    
    # 创建主目录
    sudo mkdir -p /opt/onyx
    sudo chown $USER:$USER /opt/onyx
    cd /opt/onyx
    
    # 创建子目录
    directories=(
        "data/postgres_master"
        "data/postgres_slave"
        "data/redis_master"
        "data/redis_slave"
        "data/model_cache"
        "logs/nginx"
        "logs/api"
        "logs/model"
        "logs/worker"
        "docker/nginx/conf.d"
        "docker/postgres"
        "docker/redis"
        "docker/prometheus"
        "docker/grafana/dashboards"
        "docker/grafana/datasources"
        "secrets"
        "backups"
        "ssl"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        echo_info "创建目录: $dir"
    done
    
    # 设置权限
    chmod 700 secrets
    chmod 755 data logs
    
    echo_success "目录结构创建完成"
}

# 生成安全密钥
generate_secrets() {
    echo_header "生成安全密钥"
    
    # 生成数据库密码
    if [[ ! -f secrets/db_password.txt ]]; then
        openssl rand -base64 32 > secrets/db_password.txt
        echo_success "生成数据库密码"
    fi
    
    # 生成复制密码
    if [[ ! -f secrets/replication_password.txt ]]; then
        openssl rand -base64 32 > secrets/replication_password.txt
        echo_success "生成复制密码"
    fi
    
    # 生成JWT密钥
    if [[ ! -f secrets/jwt_secret.txt ]]; then
        openssl rand -hex 64 > secrets/jwt_secret.txt
        echo_success "生成JWT密钥"
    fi
    
    # 生成应用密钥
    if [[ ! -f secrets/app_secret.txt ]]; then
        openssl rand -hex 64 > secrets/app_secret.txt
        echo_success "生成应用密钥"
    fi
    
    # 设置密钥文件权限
    chmod 600 secrets/*.txt
    
    echo_success "安全密钥生成完成"
}

# 配置防火墙
configure_firewall() {
    echo_header "配置防火墙"
    
    if command -v ufw &> /dev/null; then
        # Ubuntu/Debian UFW
        sudo ufw --force enable
        sudo ufw allow ssh
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        
        # 内部服务端口（仅限本地）
        sudo ufw allow from 127.0.0.1 to any port 5432
        sudo ufw allow from 127.0.0.1 to any port 6379
        sudo ufw allow from 127.0.0.1 to any port 8080
        sudo ufw allow from 127.0.0.1 to any port 9000
        
        echo_success "UFW防火墙配置完成"
        
    elif command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL firewalld
        sudo systemctl start firewalld
        sudo systemctl enable firewalld
        
        sudo firewall-cmd --permanent --add-service=ssh
        sudo firewall-cmd --permanent --add-service=http
        sudo firewall-cmd --permanent --add-service=https
        sudo firewall-cmd --reload
        
        echo_success "firewalld防火墙配置完成"
    else
        echo_warning "未检测到防火墙，请手动配置"
    fi
}

# 部署服务
deploy_services() {
    echo_header "部署Onyx服务"
    
    # 选择部署配置
    case $DEPLOYMENT_TYPE in
        "minimal")
            COMPOSE_FILE="docker-compose.minimal.yml"
            ;;
        "single")
            COMPOSE_FILE="docker-compose.yml"
            ;;
        "cluster")
            COMPOSE_FILE="docker-compose.prod.yml"
            ;;
    esac
    
    echo_info "使用配置文件: $COMPOSE_FILE"
    
    # 拉取基础镜像
    echo_info "拉取基础镜像..."
    docker-compose -f "$COMPOSE_FILE" pull postgres redis nginx
    
    # 构建自定义镜像
    echo_info "构建自定义镜像..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    # 启动基础服务
    echo_info "启动数据库和缓存服务..."
    docker-compose -f "$COMPOSE_FILE" up -d postgres redis
    
    # 等待数据库启动
    echo_info "等待数据库启动..."
    timeout=60
    elapsed=0
    while ! docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U onyx_user -d onyx &>/dev/null; do
        sleep 2
        elapsed=$((elapsed + 2))
        if [[ $elapsed -ge $timeout ]]; then
            echo_error "数据库启动超时"
            exit 1
        fi
        echo -n "."
    done
    echo ""
    echo_success "数据库已就绪"
    
    # 启动所有服务
    echo_info "启动所有服务..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
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
        echo -n "."
    done
    echo ""
    
    if [[ $elapsed -lt $timeout ]]; then
        # 运行数据库迁移
        echo_info "运行数据库迁移..."
        docker-compose -f "$COMPOSE_FILE" exec api-backend alembic upgrade head
        echo_success "数据库迁移完成"
    fi
    
    echo_success "服务部署完成"
}

# 配置SSL证书
configure_ssl() {
    echo_header "配置SSL证书"
    
    if [[ ! -f ssl/onyx.crt ]] || [[ ! -f ssl/onyx.key ]]; then
        echo_info "生成自签名SSL证书..."
        
        # 生成私钥
        openssl genrsa -out ssl/onyx.key 2048
        
        # 生成证书签名请求
        openssl req -new -key ssl/onyx.key -out ssl/onyx.csr -subj "/C=CN/ST=State/L=City/O=Organization/CN=onyx.local"
        
        # 生成自签名证书
        openssl x509 -req -days 365 -in ssl/onyx.csr -signkey ssl/onyx.key -out ssl/onyx.crt
        
        # 合并证书和私钥 (HAProxy格式)
        cat ssl/onyx.crt ssl/onyx.key > ssl/onyx.pem
        
        # 设置权限
        chmod 600 ssl/onyx.key ssl/onyx.pem
        chmod 644 ssl/onyx.crt
        
        echo_success "SSL证书生成完成"
        echo_warning "生产环境请使用正式的SSL证书"
    else
        echo_success "SSL证书已存在"
    fi
}

# 配置监控
setup_monitoring() {
    echo_header "配置监控服务"
    
    if [[ $DEPLOYMENT_TYPE == "cluster" ]] || [[ $ENVIRONMENT == "production" ]]; then
        echo_info "启动监控服务..."
        docker-compose -f docker-compose.monitoring.yml up -d
        
        echo_info "等待监控服务启动..."
        sleep 30
        
        # 检查Prometheus
        if curl -f http://localhost:9090/-/healthy &>/dev/null; then
            echo_success "Prometheus监控已启动"
        else
            echo_warning "Prometheus启动可能有问题"
        fi
        
        # 检查Grafana
        if curl -f http://localhost:3001/api/health &>/dev/null; then
            echo_success "Grafana仪表板已启动"
        else
            echo_warning "Grafana启动可能有问题"
        fi
    else
        echo_info "跳过监控服务配置 (仅在集群或生产环境启用)"
    fi
}

# 性能测试
run_performance_test() {
    echo_header "运行性能基准测试"
    
    # 安装测试工具
    if ! command -v wrk &> /dev/null; then
        echo_info "安装性能测试工具..."
        case $OS in
            "ubuntu"|"debian")
                sudo apt-get install -y wrk
                ;;
            "centos"|"rhel"|"rocky"|"almalinux")
                sudo yum install -y epel-release
                sudo yum install -y wrk
                ;;
        esac
    fi
    
    echo_info "等待服务完全启动..."
    sleep 60
    
    # API性能测试
    echo_info "测试API性能..."
    if command -v wrk &> /dev/null; then
        wrk -t4 -c100 -d30s --timeout 30s http://localhost/api/health > /tmp/api_test.log 2>&1
        echo_success "API性能测试完成，结果保存到 /tmp/api_test.log"
    fi
    
    # 前端性能测试
    echo_info "测试前端性能..."
    if command -v wrk &> /dev/null; then
        wrk -t4 -c50 -d30s http://localhost/ > /tmp/web_test.log 2>&1
        echo_success "前端性能测试完成，结果保存到 /tmp/web_test.log"
    fi
}

# 显示部署状态
show_deployment_status() {
    echo_header "部署状态报告"
    
    # 显示容器状态
    echo_info "容器状态:"
    docker-compose ps
    
    echo ""
    echo_info "系统资源使用:"
    echo "CPU使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
    echo "内存使用: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')"
    echo "磁盘使用: $(df -h . | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')"
    
    echo ""
    echo_info "服务访问地址:"
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo "  - 前端应用: http://$SERVER_IP"
    echo "  - API文档: http://$SERVER_IP/api/docs"
    echo "  - 数据库: $SERVER_IP:5432"
    echo "  - Redis: $SERVER_IP:6379"
    
    if [[ $DEPLOYMENT_TYPE == "cluster" ]] || [[ $ENVIRONMENT == "production" ]]; then
        echo "  - Prometheus: http://$SERVER_IP:9090"
        echo "  - Grafana: http://$SERVER_IP:3001 (admin/admin123)"
    fi
    
    echo ""
    echo_info "容器资源使用:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# 创建管理脚本
create_management_scripts() {
    echo_header "创建管理脚本"
    
    # 创建服务管理脚本
    cat > manage.sh << 'EOF'
#!/bin/bash
# Onyx服务管理脚本

case $1 in
    "start")
        docker-compose up -d
        echo "✅ 服务已启动"
        ;;
    "stop")
        docker-compose down
        echo "✅ 服务已停止"
        ;;
    "restart")
        docker-compose restart
        echo "✅ 服务已重启"
        ;;
    "status")
        docker-compose ps
        ;;
    "logs")
        docker-compose logs -f ${2:-}
        ;;
    "backup")
        ./backup-prod.sh
        ;;
    "update")
        git pull
        docker-compose build --no-cache
        docker-compose up -d
        echo "✅ 服务已更新"
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|logs|backup|update}"
        exit 1
        ;;
esac
EOF
    
    chmod +x manage.sh
    echo_success "管理脚本创建完成: ./manage.sh"
    
    # 创建健康检查脚本
    cat > health-check.sh << 'EOF'
#!/bin/bash
# 健康检查脚本

echo "🔍 Onyx系统健康检查"

# 检查容器状态
echo "📊 容器状态:"
docker-compose ps

# 检查服务健康
services=("http://localhost/health" "http://localhost/api/health")
for service in "${services[@]}"; do
    if curl -f "$service" &>/dev/null; then
        echo "✅ $service - 正常"
    else
        echo "❌ $service - 异常"
    fi
done

# 检查数据库连接
if docker-compose exec -T postgres pg_isready -U onyx_user -d onyx &>/dev/null; then
    echo "✅ 数据库连接 - 正常"
else
    echo "❌ 数据库连接 - 异常"
fi

# 检查Redis连接
if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    echo "✅ Redis连接 - 正常"
else
    echo "❌ Redis连接 - 异常"
fi

echo "🎉 健康检查完成"
EOF
    
    chmod +x health-check.sh
    echo_success "健康检查脚本创建完成: ./health-check.sh"
}

# 主函数
main() {
    echo_header "Onyx Linux服务器部署脚本"
    echo_info "部署类型: $DEPLOYMENT_TYPE"
    echo_info "环境: $ENVIRONMENT"
    echo ""
    
    detect_os
    check_system_requirements
    install_docker
    install_docker_compose
    configure_system_optimization
    create_directory_structure
    generate_secrets
    configure_firewall
    configure_ssl
    deploy_services
    setup_monitoring
    create_management_scripts
    run_performance_test
    show_deployment_status
    
    echo ""
    echo_success "🎉 Onyx部署完成!"
    echo_info "💡 使用 ./manage.sh 管理服务"
    echo_info "💡 使用 ./health-check.sh 检查系统健康"
    echo_warning "⚠️ 请修改 secrets/ 目录中的默认密码"
    echo_warning "⚠️ 生产环境请配置正式的SSL证书"
}

# 显示帮助信息
show_help() {
    echo "Onyx Linux部署脚本"
    echo ""
    echo "用法: $0 [部署类型] [环境]"
    echo ""
    echo "部署类型:"
    echo "  minimal  - 最小化部署 (8GB RAM, 4核心)"
    echo "  single   - 单服务器部署 (16GB RAM, 8核心) [默认]"
    echo "  cluster  - 集群部署 (32GB+ RAM, 16+核心)"
    echo ""
    echo "环境:"
    echo "  development - 开发环境"
    echo "  staging     - 测试环境"
    echo "  production  - 生产环境 [默认]"
    echo ""
    echo "示例:"
    echo "  $0 single production    # 单服务器生产部署"
    echo "  $0 cluster production   # 集群生产部署"
    echo "  $0 minimal development  # 最小化开发部署"
}

# 参数处理
if [[ $1 == "-h" ]] || [[ $1 == "--help" ]]; then
    show_help
    exit 0
fi

# 执行主函数
main "$@"
