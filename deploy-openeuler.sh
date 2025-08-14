#!/bin/bash

# Onyx openEuler 20.03 LTS 专用部署脚本
# 针对openEuler 20.03 LTS优化的Docker部署方案
# 作者: Onyx Team
# 版本: 1.0

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="onyx"
COMPOSE_FILE="deployment/docker_compose/docker-compose.dev.yml"
ENV_FILE=".env"
LOG_FILE="deploy-openeuler.log"

# 服务列表
BASIC_SERVICES=("relational_db" "cache" "minio" "index")
APP_SERVICES=("inference_model_server" "indexing_model_server" "api_server" "background" "web_server" "nginx")
ALL_SERVICES=("${BASIC_SERVICES[@]}" "${APP_SERVICES[@]}")

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

# 检查openEuler版本
check_openeuler() {
    log_info "检查openEuler版本..."
    
    if [ ! -f /etc/os-release ]; then
        log_error "无法检测操作系统版本"
        exit 1
    fi
    
    source /etc/os-release
    
    if [[ "$ID" != "openEuler" ]]; then
        log_error "此脚本专为openEuler设计，当前系统: $PRETTY_NAME"
        exit 1
    fi
    
    log_success "检测到openEuler系统: $PRETTY_NAME"
    
    # 检查版本
    if [[ "$VERSION_ID" < "20.03" ]]; then
        log_warning "建议使用openEuler 20.03 LTS或更高版本"
    fi
}

# 安装系统依赖
install_dependencies() {
    log_info "安装系统依赖..."
    
    # 更新系统
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
        lvm2 \
        htop \
        tree \
        unzip
    
    log_success "系统依赖安装完成"
}

# 安装Docker
install_docker() {
    log_info "安装Docker..."
    
    # 检查Docker是否已安装
    if command -v docker &> /dev/null; then
        log_info "Docker已安装，版本: $(docker --version)"
        return 0
    fi
    
    # 添加Docker仓库
    sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    
    # 安装Docker CE
    sudo yum install -y docker-ce docker-ce-cli containerd.io
    
    # 启动Docker服务
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 配置Docker用户组
    sudo groupadd docker || true
    sudo usermod -aG docker $USER
    
    log_success "Docker安装完成"
    log_warning "请重新登录以使Docker用户组权限生效"
}

# 安装Docker Compose
install_docker_compose() {
    log_info "安装Docker Compose..."
    
    # 检查是否已安装
    if command -v docker-compose &> /dev/null; then
        log_info "Docker Compose已安装，版本: $(docker-compose --version)"
        return 0
    fi
    
    # 下载Docker Compose
    COMPOSE_VERSION="2.24.0"
    sudo curl -L "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    # 设置执行权限
    sudo chmod +x /usr/local/bin/docker-compose
    
    # 创建软链接
    sudo ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
    
    log_success "Docker Compose安装完成"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    # 启动防火墙服务
    sudo systemctl start firewalld
    sudo systemctl enable firewalld
    
    # 开放必要端口
    sudo firewall-cmd --permanent --add-port=80/tcp      # HTTP
    sudo firewall-cmd --permanent --add-port=443/tcp     # HTTPS
    sudo firewall-cmd --permanent --add-port=8080/tcp    # API Backend (可选)
    sudo firewall-cmd --permanent --add-port=3000/tcp    # Frontend (可选)
    
    # 重载防火墙配置
    sudo firewall-cmd --reload
    
    log_success "防火墙配置完成"
    log_info "开放的端口: $(sudo firewall-cmd --list-ports)"
}

# 优化系统参数
optimize_system() {
    log_info "优化系统参数..."
    
    # 创建系统优化配置
    sudo tee /etc/sysctl.d/99-onyx.conf > /dev/null <<EOF
# Onyx系统优化参数
vm.max_map_count=262144
net.core.somaxconn=65535
net.ipv4.tcp_max_syn_backlog=65535
fs.file-max=1000000
vm.swappiness=10
EOF
    
    # 应用配置
    sudo sysctl -p /etc/sysctl.d/99-onyx.conf
    
    # 配置Docker守护进程
    sudo mkdir -p /etc/docker
    sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF
    
    # 重启Docker服务
    sudo systemctl restart docker
    
    log_success "系统优化完成"
}

# 检查系统资源
check_resources() {
    log_info "检查系统资源..."
    
    # 检查内存
    TOTAL_MEM=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    if [ "$TOTAL_MEM" -lt 6144 ]; then
        log_warning "系统内存不足6GB，当前: ${TOTAL_MEM}MB，建议至少8GB"
    else
        log_success "内存检查通过: ${TOTAL_MEM}MB"
    fi
    
    # 检查磁盘空间
    AVAILABLE_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt 20 ]; then
        log_warning "磁盘空间不足20GB，当前可用: ${AVAILABLE_SPACE}GB"
    else
        log_success "磁盘空间检查通过: ${AVAILABLE_SPACE}GB可用"
    fi
    
    # 检查CPU核心数
    CPU_CORES=$(nproc)
    if [ "$CPU_CORES" -lt 2 ]; then
        log_warning "CPU核心数较少，当前: ${CPU_CORES}核，建议至少4核"
    else
        log_success "CPU检查通过: ${CPU_CORES}核"
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    local directories=(
        "logs"
        "data/postgres"
        "data/redis"
        "data/minio"
        "data/vespa"
        "docker/nginx/conf.d"
        "docker/nginx/ssl"
        "temp"
        "backups"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log_success "创建目录: $dir"
        fi
    done
    
    # 设置权限
    chmod -R 755 logs data temp backups
}

# 配置环境变量
setup_environment() {
    log_info "配置环境变量..."
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "deployment/docker_compose/env.prod.template" ]; then
            log_info "复制环境配置模板..."
            cp deployment/docker_compose/env.prod.template "$ENV_FILE"
            
            # 自动配置一些基本参数
            SERVER_IP=$(hostname -I | awk '{print $1}')
            sed -i "s|WEB_DOMAIN=.*|WEB_DOMAIN=http://${SERVER_IP}:3000|g" "$ENV_FILE"
            sed -i "s|CORS_ALLOWED_ORIGIN=.*|CORS_ALLOWED_ORIGIN=http://${SERVER_IP}|g" "$ENV_FILE"
            
            log_success "环境配置文件已创建: $ENV_FILE"
            log_warning "请编辑 $ENV_FILE 文件配置以下必要参数:"
            log_warning "  - POSTGRES_PASSWORD (数据库密码)"
            log_warning "  - GEN_AI_API_KEY (AI API密钥)"
            log_warning "  - SECRET (应用密钥)"
        else
            log_error "环境配置模板不存在"
            exit 1
        fi
    else
        log_info "环境配置文件已存在: $ENV_FILE"
    fi
}

# 构建镜像
build_images() {
    local clean_build=false
    if [ "$1" = "--clean" ]; then
        clean_build=true
    fi
    
    log_info "开始构建Docker镜像..."
    
    if [ "$clean_build" = true ]; then
        log_info "清理旧镜像..."
        docker-compose -f "$COMPOSE_FILE" down --rmi all --volumes --remove-orphans || true
        docker system prune -af || true
    fi
    
    # 构建镜像
    log_info "构建应用镜像..."
    if docker-compose -f "$COMPOSE_FILE" build --parallel; then
        log_success "镜像构建完成"
    else
        log_error "镜像构建失败"
        exit 1
    fi
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 启动基础服务
    log_info "启动基础服务..."
    for service in "${BASIC_SERVICES[@]}"; do
        log_info "启动服务: $service"
        docker-compose -f "$COMPOSE_FILE" up -d "$service"
        
        case $service in
            "relational_db") sleep 15 ;;
            "cache") sleep 5 ;;
            "minio") sleep 10 ;;
            "index") sleep 30 ;;
        esac
    done
    
    # 启动应用服务
    log_info "启动应用服务..."
    for service in "${APP_SERVICES[@]}"; do
        log_info "启动服务: $service"
        docker-compose -f "$COMPOSE_FILE" up -d "$service"
        
        case $service in
            "inference_model_server"|"indexing_model_server") sleep 20 ;;
            "api_server") sleep 15 ;;
            *) sleep 5 ;;
        esac
    done
    
    log_success "所有服务启动完成"
}

# 健康检查
health_check() {
    log_info "执行健康检查..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "健康检查尝试 $attempt/$max_attempts"
        
        # 检查容器状态
        local unhealthy_containers=()
        for service in "${ALL_SERVICES[@]}"; do
            if ! docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "Up"; then
                unhealthy_containers+=("$service")
            fi
        done
        
        if [ ${#unhealthy_containers[@]} -eq 0 ]; then
            log_success "所有服务运行正常"
            
            # 检查HTTP服务
            if curl -f http://localhost/health &> /dev/null; then
                log_success "HTTP健康检查通过"
                return 0
            else
                log_warning "HTTP健康检查失败，但容器运行正常"
            fi
            
            return 0
        else
            log_warning "以下服务未正常运行: ${unhealthy_containers[*]}"
        fi
        
        sleep 10
        ((attempt++))
    done
    
    log_error "健康检查失败"
    return 1
}

# 显示服务状态
show_status() {
    log_info "服务状态:"
    docker-compose -f "$COMPOSE_FILE" ps

    echo ""
    log_info "系统资源使用:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

    echo ""
    log_info "访问地址:"
    SERVER_IP=$(hostname -I | awk '{print $1}')
    echo "  前端: http://${SERVER_IP}"
    echo "  API文档: http://${SERVER_IP}/api/docs"
    echo "  健康检查: http://${SERVER_IP}/health"
}

# 显示日志
show_logs() {
    local service="$1"
    local lines="${2:-50}"

    if [ -n "$service" ]; then
        log_info "显示服务 $service 的日志 (最近 $lines 行):"
        docker-compose -f "$COMPOSE_FILE" logs --tail="$lines" "$service"
    else
        log_info "显示所有服务日志 (最近 $lines 行):"
        docker-compose -f "$COMPOSE_FILE" logs --tail="$lines"
    fi
}

# 停止服务
stop_services() {
    log_info "停止所有服务..."
    docker-compose -f "$COMPOSE_FILE" down
    log_success "服务已停止"
}

# 重启服务
restart_services() {
    log_info "重启所有服务..."
    stop_services
    sleep 5
    start_services
    health_check
    log_success "服务重启完成"
}

# 备份数据
backup_data() {
    log_info "备份数据..."

    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    # 备份数据库
    log_info "备份PostgreSQL数据库..."
    docker-compose -f "$COMPOSE_FILE" exec -T relational_db pg_dump -U postgres onyx > "$backup_dir/postgres_backup.sql"

    # 备份环境配置
    cp "$ENV_FILE" "$backup_dir/"

    # 备份日志
    cp -r logs "$backup_dir/" 2>/dev/null || true

    log_success "数据备份完成: $backup_dir"
}

# 清理资源
cleanup() {
    log_info "清理Docker资源..."
    docker-compose -f "$COMPOSE_FILE" down --volumes --remove-orphans
    docker system prune -af
    log_success "清理完成"
}

# 系统环境安装
install_system() {
    log_info "开始系统环境安装..."

    check_openeuler
    install_dependencies
    install_docker
    install_docker_compose
    configure_firewall
    optimize_system

    log_success "系统环境安装完成"
    log_warning "请重新登录以使Docker用户组权限生效，然后运行部署命令"
}

# 完整部署
full_deploy() {
    local build_images=false
    if [ "$1" = "--build" ]; then
        build_images=true
    fi

    log_info "开始完整部署..."

    check_openeuler
    check_resources
    create_directories
    setup_environment

    if [ "$build_images" = true ]; then
        build_images
    fi

    start_services
    health_check
    show_status

    log_success "部署完成!"

    SERVER_IP=$(hostname -I | awk '{print $1}')
    log_info "访问地址:"
    log_info "  前端: http://${SERVER_IP}"
    log_info "  API文档: http://${SERVER_IP}/api/docs"
}

# 显示帮助信息
show_help() {
    echo "Onyx openEuler 20.03 LTS 专用部署脚本"
    echo ""
    echo "用法: $0 <命令> [选项]"
    echo ""
    echo "系统安装命令:"
    echo "  install             安装系统环境 (Docker, Docker Compose等)"
    echo ""
    echo "部署命令:"
    echo "  deploy [--build]    完整部署 (可选择是否构建镜像)"
    echo "  build [--clean]     构建镜像 (可选择清理旧镜像)"
    echo "  start              启动所有服务"
    echo "  stop               停止所有服务"
    echo "  restart            重启所有服务"
    echo ""
    echo "管理命令:"
    echo "  status             显示服务状态"
    echo "  logs [service]     显示日志"
    echo "  health             执行健康检查"
    echo "  backup             备份数据"
    echo "  cleanup            清理Docker资源"
    echo ""
    echo "示例:"
    echo "  $0 install                    # 首次安装系统环境"
    echo "  $0 deploy --build            # 构建镜像并完整部署"
    echo "  $0 logs api_server           # 查看API服务器日志"
    echo "  $0 status                    # 查看服务状态"
    echo "  $0 backup                    # 备份数据"
    echo ""
    echo "注意:"
    echo "  - 首次使用请先运行 'install' 命令安装系统环境"
    echo "  - 安装完成后需要重新登录以使Docker权限生效"
    echo "  - 部署前请确保编辑 .env 文件配置必要参数"
}

# 主函数
main() {
    local command="$1"
    local option="$2"

    # 创建日志文件
    touch "$LOG_FILE"

    case "$command" in
        "install")
            install_system
            ;;
        "deploy")
            full_deploy "$option"
            ;;
        "build")
            build_images "$option"
            ;;
        "start")
            start_services
            health_check
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$option"
            ;;
        "health")
            health_check
            ;;
        "backup")
            backup_data
            ;;
        "cleanup")
            cleanup
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

# 执行主函数
main "$@"
