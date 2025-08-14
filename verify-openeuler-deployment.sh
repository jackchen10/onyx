#!/bin/bash

# Onyx openEuler 部署验证脚本
# 用于验证openEuler 20.03系统上的Onyx部署状态

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

# 检查系统信息
check_system_info() {
    log_header "系统信息检查"
    
    # 操作系统信息
    if [ -f /etc/os-release ]; then
        source /etc/os-release
        log_info "操作系统: $PRETTY_NAME"
        log_info "版本: $VERSION_ID"
        
        if [[ "$ID" == "openEuler" ]]; then
            log_success "✅ openEuler系统检测通过"
        else
            log_warning "⚠️ 非openEuler系统: $ID"
        fi
    else
        log_error "❌ 无法检测操作系统信息"
    fi
    
    # 内核信息
    log_info "内核版本: $(uname -r)"
    
    # 系统资源
    log_info "CPU核心数: $(nproc)"
    log_info "总内存: $(free -h | awk 'NR==2{print $2}')"
    log_info "可用内存: $(free -h | awk 'NR==2{print $7}')"
    log_info "磁盘使用: $(df -h . | awk 'NR==2{print $3"/"$2" ("$5")"}')"
}

# 检查Docker环境
check_docker_environment() {
    log_header "Docker环境检查"
    
    # Docker版本
    if command -v docker &> /dev/null; then
        log_success "✅ Docker已安装"
        log_info "Docker版本: $(docker --version)"
        
        # Docker服务状态
        if systemctl is-active --quiet docker; then
            log_success "✅ Docker服务运行中"
        else
            log_error "❌ Docker服务未运行"
        fi
        
        # Docker权限检查
        if docker ps &> /dev/null; then
            log_success "✅ Docker权限正常"
        else
            log_error "❌ Docker权限不足"
        fi
    else
        log_error "❌ Docker未安装"
    fi
    
    # Docker Compose版本
    if command -v docker-compose &> /dev/null; then
        log_success "✅ Docker Compose已安装"
        log_info "Docker Compose版本: $(docker-compose --version)"
    else
        log_error "❌ Docker Compose未安装"
    fi
    
    # Docker配置检查
    if [ -f /etc/docker/daemon.json ]; then
        log_success "✅ Docker配置文件存在"
        log_info "配置内容:"
        cat /etc/docker/daemon.json | sed 's/^/    /'
    else
        log_warning "⚠️ Docker配置文件不存在"
    fi
}

# 检查网络配置
check_network_configuration() {
    log_header "网络配置检查"
    
    # 防火墙状态
    if systemctl is-active --quiet firewalld; then
        log_success "✅ 防火墙服务运行中"
        log_info "开放的端口:"
        firewall-cmd --list-ports | sed 's/^/    /'
    else
        log_warning "⚠️ 防火墙服务未运行"
    fi
    
    # 端口占用检查
    log_info "关键端口占用检查:"
    local ports=(80 443 8080 3000 5432 6379 9000)
    for port in "${ports[@]}"; do
        if netstat -tuln | grep -q ":$port "; then
            log_warning "⚠️ 端口 $port 已被占用"
        else
            log_success "✅ 端口 $port 可用"
        fi
    done
    
    # 网络连接测试
    log_info "网络连接测试:"
    if ping -c 1 8.8.8.8 &> /dev/null; then
        log_success "✅ 外网连接正常"
    else
        log_error "❌ 外网连接失败"
    fi
}

# 检查项目文件
check_project_files() {
    log_header "项目文件检查"
    
    # 项目目录结构
    local required_dirs=("docker" "backend" "web" "deployment/docker_compose")
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            log_success "✅ 目录存在: $dir"
        else
            log_error "❌ 目录缺失: $dir"
        fi
    done
    
    # 关键文件检查
    local required_files=(
        "deployment/docker_compose/docker-compose.dev.yml"
        "docker/Dockerfile.backend"
        "docker/Dockerfile.web"
        "docker/nginx/nginx.conf"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            log_success "✅ 文件存在: $file"
        else
            log_error "❌ 文件缺失: $file"
        fi
    done
    
    # 环境配置文件
    if [ -f ".env" ]; then
        log_success "✅ 环境配置文件存在"
        
        # 检查关键配置项
        local required_vars=("POSTGRES_PASSWORD" "SECRET")
        for var in "${required_vars[@]}"; do
            if grep -q "^${var}=" .env && ! grep -q "^${var}=$" .env; then
                log_success "✅ 配置项已设置: $var"
            else
                log_warning "⚠️ 配置项未设置: $var"
            fi
        done
    else
        log_warning "⚠️ 环境配置文件不存在"
    fi
    
    # 部署脚本检查
    if [ -f "deploy-openeuler.sh" ]; then
        log_success "✅ openEuler部署脚本存在"
        if [ -x "deploy-openeuler.sh" ]; then
            log_success "✅ 部署脚本可执行"
        else
            log_warning "⚠️ 部署脚本不可执行，运行: chmod +x deploy-openeuler.sh"
        fi
    else
        log_error "❌ openEuler部署脚本不存在"
    fi
}

# 检查Docker容器状态
check_docker_containers() {
    log_header "Docker容器状态检查"
    
    local compose_file="deployment/docker_compose/docker-compose.dev.yml"
    
    if [ ! -f "$compose_file" ]; then
        log_error "❌ Docker Compose文件不存在: $compose_file"
        return 1
    fi
    
    # 检查容器状态
    if docker-compose -f "$compose_file" ps &> /dev/null; then
        log_info "容器状态:"
        docker-compose -f "$compose_file" ps
        
        # 检查运行中的容器
        local running_containers=$(docker-compose -f "$compose_file" ps --services --filter "status=running" | wc -l)
        local total_containers=$(docker-compose -f "$compose_file" ps --services | wc -l)
        
        if [ "$running_containers" -gt 0 ]; then
            log_success "✅ 有 $running_containers/$total_containers 个容器正在运行"
        else
            log_warning "⚠️ 没有容器在运行"
        fi
    else
        log_warning "⚠️ 无法获取容器状态，可能服务未启动"
    fi
}

# 检查服务健康状态
check_service_health() {
    log_header "服务健康状态检查"
    
    local server_ip=$(hostname -I | awk '{print $1}')
    
    # HTTP服务检查
    log_info "检查HTTP服务..."
    if curl -f -s http://localhost/health &> /dev/null; then
        log_success "✅ HTTP健康检查通过"
    elif curl -f -s http://$server_ip/health &> /dev/null; then
        log_success "✅ HTTP健康检查通过 (通过IP访问)"
    else
        log_warning "⚠️ HTTP健康检查失败"
    fi
    
    # API服务检查
    log_info "检查API服务..."
    if curl -f -s http://localhost/api/health &> /dev/null; then
        log_success "✅ API健康检查通过"
    elif curl -f -s http://$server_ip/api/health &> /dev/null; then
        log_success "✅ API健康检查通过 (通过IP访问)"
    else
        log_warning "⚠️ API健康检查失败"
    fi
    
    # 前端服务检查
    log_info "检查前端服务..."
    if curl -f -s -I http://localhost/ | grep -q "200 OK"; then
        log_success "✅ 前端服务正常"
    elif curl -f -s -I http://$server_ip/ | grep -q "200 OK"; then
        log_success "✅ 前端服务正常 (通过IP访问)"
    else
        log_warning "⚠️ 前端服务异常"
    fi
}

# 生成部署报告
generate_report() {
    log_header "部署验证报告"
    
    local server_ip=$(hostname -I | awk '{print $1}')
    
    echo ""
    log_info "🌐 访问地址:"
    echo "    前端应用: http://$server_ip"
    echo "    API文档:  http://$server_ip/api/docs"
    echo "    健康检查: http://$server_ip/health"
    
    echo ""
    log_info "📋 下一步操作建议:"
    
    # 检查是否需要安装系统环境
    if ! command -v docker &> /dev/null; then
        echo "    1. 运行系统环境安装: ./deploy-openeuler.sh install"
        echo "    2. 重新登录系统使Docker权限生效"
        echo "    3. 配置环境变量文件 .env"
        echo "    4. 运行完整部署: ./deploy-openeuler.sh deploy --build"
    elif [ ! -f ".env" ]; then
        echo "    1. 配置环境变量文件 .env"
        echo "    2. 运行完整部署: ./deploy-openeuler.sh deploy --build"
    elif ! docker-compose -f "deployment/docker_compose/docker-compose.dev.yml" ps | grep -q "Up"; then
        echo "    1. 启动服务: ./deploy-openeuler.sh start"
        echo "    2. 检查服务状态: ./deploy-openeuler.sh status"
    else
        echo "    ✅ 系统部署正常，可以开始使用"
        echo "    📊 查看状态: ./deploy-openeuler.sh status"
        echo "    📝 查看日志: ./deploy-openeuler.sh logs"
        echo "    💾 备份数据: ./deploy-openeuler.sh backup"
    fi
    
    echo ""
    log_info "📚 更多帮助:"
    echo "    查看部署脚本帮助: ./deploy-openeuler.sh help"
    echo "    查看部署文档: docs/Linux服务器Docker部署指南.md"
}

# 主函数
main() {
    echo "Onyx openEuler 部署验证脚本"
    echo "================================"
    echo ""
    
    check_system_info
    echo ""
    
    check_docker_environment
    echo ""
    
    check_network_configuration
    echo ""
    
    check_project_files
    echo ""
    
    check_docker_containers
    echo ""
    
    check_service_health
    echo ""
    
    generate_report
}

# 执行主函数
main "$@"
