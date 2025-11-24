#!/bin/bash

# Onyx openEuler 双服务器集群部署验证脚本
# 验证主服务器 (10.0.83.30) 和数据库服务器 (10.0.83.36) 的部署状态

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

# 检查当前服务器
check_current_server() {
    log_header "服务器信息检查"
    
    log_info "当前服务器IP: $CURRENT_SERVER"
    
    if [[ "$CURRENT_SERVER" == "$MAIN_SERVER" ]]; then
        log_success "✅ 当前在主服务器 ($MAIN_SERVER)"
        echo "    角色: 应用服务器"
        echo "    配置: CPU 8核, 内存 32GB, 磁盘 100GB"
        return 0
    elif [[ "$CURRENT_SERVER" == "$DB_SERVER" ]]; then
        log_success "✅ 当前在数据库服务器 ($DB_SERVER)"
        echo "    角色: 数据库服务器"
        echo "    配置: CPU 8核, 内存 32GB, 磁盘 100GB"
        return 1
    else
        log_error "❌ 未识别的服务器IP: $CURRENT_SERVER"
        log_error "预期服务器: $MAIN_SERVER (主服务器) 或 $DB_SERVER (数据库服务器)"
        return 2
    fi
}

# 检查网络连通性
check_network_connectivity() {
    log_header "网络连通性检查"
    
    if [[ "$CURRENT_SERVER" == "$MAIN_SERVER" ]]; then
        log_info "检查主服务器到数据库服务器的连通性..."
        
        if ping -c 3 "$DB_SERVER" &> /dev/null; then
            log_success "✅ 主服务器到数据库服务器网络连通正常"
        else
            log_error "❌ 主服务器无法连接到数据库服务器 ($DB_SERVER)"
        fi
        
        # 检查数据库端口连通性
        if nc -z "$DB_SERVER" 5432 2>/dev/null; then
            log_success "✅ 数据库端口 (5432) 可访问"
        else
            log_warning "⚠️ 数据库端口 (5432) 不可访问"
        fi
        
    elif [[ "$CURRENT_SERVER" == "$DB_SERVER" ]]; then
        log_info "检查数据库服务器到主服务器的连通性..."
        
        if ping -c 3 "$MAIN_SERVER" &> /dev/null; then
            log_success "✅ 数据库服务器到主服务器网络连通正常"
        else
            log_error "❌ 数据库服务器无法连接到主服务器 ($MAIN_SERVER)"
        fi
    fi
}

# 检查主服务器服务
check_main_server_services() {
    log_header "主服务器服务检查"
    
    if [[ "$CURRENT_SERVER" != "$MAIN_SERVER" ]]; then
        log_warning "⚠️ 当前不在主服务器，跳过主服务器服务检查"
        return
    fi
    
    # 检查Redis容器
    log_info "检查已存在的Redis容器..."
    if docker ps | grep -q "scow-redis-1"; then
        log_success "✅ Redis容器 (scow-redis-1) 运行正常"
        
        # 检查Redis连接
        if docker exec scow-redis-1 redis-cli ping &> /dev/null; then
            log_success "✅ Redis连接测试通过"
        else
            log_warning "⚠️ Redis连接测试失败"
        fi
    else
        log_error "❌ Redis容器 (scow-redis-1) 未运行"
    fi
    
    # 检查主要服务容器
    local main_services=("onyx-nginx" "onyx-web-server" "onyx-api-server" "onyx-vespa" "onyx-minio")
    
    log_info "检查主要服务容器..."
    for service in "${main_services[@]}"; do
        if docker ps | grep -q "$service"; then
            log_success "✅ $service 运行正常"
        else
            log_warning "⚠️ $service 未运行"
        fi
    done
    
    # 检查端口占用
    log_info "检查关键端口占用..."
    local ports=(80 443 3000 8080 8081 9000 9001 9002)
    for port in "${ports[@]}"; do
        if netstat -tuln | grep -q ":$port "; then
            log_success "✅ 端口 $port 已占用 (服务运行中)"
        else
            log_warning "⚠️ 端口 $port 未占用"
        fi
    done
}

# 检查数据库服务器服务
check_db_server_services() {
    log_header "数据库服务器服务检查"
    
    if [[ "$CURRENT_SERVER" != "$DB_SERVER" ]]; then
        log_warning "⚠️ 当前不在数据库服务器，跳过数据库服务检查"
        return
    fi
    
    # 检查PostgreSQL容器
    log_info "检查PostgreSQL容器..."
    if docker ps | grep -q "onyx-postgres"; then
        log_success "✅ PostgreSQL容器 (onyx-postgres) 运行正常"
        
        # 检查数据库连接
        if docker exec onyx-postgres pg_isready -U onyx_user -d onyx &> /dev/null; then
            log_success "✅ PostgreSQL连接测试通过"
        else
            log_warning "⚠️ PostgreSQL连接测试失败"
        fi
        
        # 检查数据库用户和数据库
        log_info "检查数据库配置..."
        if docker exec onyx-postgres psql -U onyx_user -d onyx -c "SELECT version();" &> /dev/null; then
            log_success "✅ 数据库用户和数据库配置正确"
        else
            log_warning "⚠️ 数据库用户或数据库配置有问题"
        fi
        
    else
        log_error "❌ PostgreSQL容器 (onyx-postgres) 未运行"
    fi
    
    # 检查端口占用
    log_info "检查数据库端口..."
    if netstat -tuln | grep -q ":5432 "; then
        log_success "✅ PostgreSQL端口 (5432) 已占用"
    else
        log_warning "⚠️ PostgreSQL端口 (5432) 未占用"
    fi
}

# 检查跨服务器连接
check_cross_server_connections() {
    log_header "跨服务器连接检查"
    
    if [[ "$CURRENT_SERVER" == "$MAIN_SERVER" ]]; then
        log_info "从主服务器测试数据库连接..."
        
        # 测试PostgreSQL连接
        if command -v psql &> /dev/null; then
            if PGPASSWORD="your_secure_password_here" psql -h "$DB_SERVER" -U onyx_user -d onyx -c "SELECT 1;" &> /dev/null; then
                log_success "✅ 主服务器可以连接到数据库服务器"
            else
                log_warning "⚠️ 主服务器无法连接到数据库服务器"
                log_info "请检查数据库密码和网络配置"
            fi
        else
            log_info "主服务器未安装psql客户端，跳过数据库连接测试"
        fi
        
    elif [[ "$CURRENT_SERVER" == "$DB_SERVER" ]]; then
        log_info "从数据库服务器测试主服务器连接..."
        
        # 测试HTTP连接
        if curl -f -s "http://$MAIN_SERVER/health" &> /dev/null; then
            log_success "✅ 数据库服务器可以访问主服务器HTTP服务"
        else
            log_warning "⚠️ 数据库服务器无法访问主服务器HTTP服务"
        fi
    fi
}

# 检查应用服务健康状态
check_application_health() {
    log_header "应用服务健康检查"
    
    if [[ "$CURRENT_SERVER" == "$MAIN_SERVER" ]]; then
        log_info "检查应用服务健康状态..."
        
        # 检查前端服务
        if curl -f -s -I "http://localhost/" | grep -q "200 OK"; then
            log_success "✅ 前端服务健康检查通过"
        else
            log_warning "⚠️ 前端服务健康检查失败"
        fi
        
        # 检查API服务
        if curl -f -s "http://localhost:8080/health" &> /dev/null; then
            log_success "✅ API服务健康检查通过"
        else
            log_warning "⚠️ API服务健康检查失败"
        fi
        
        # 检查Vespa服务
        if curl -f -s "http://localhost:8081/ApplicationStatus" &> /dev/null; then
            log_success "✅ Vespa搜索引擎健康检查通过"
        else
            log_warning "⚠️ Vespa搜索引擎健康检查失败"
        fi
        
        # 检查MinIO服务
        if curl -f -s "http://localhost:9001/minio/health/live" &> /dev/null; then
            log_success "✅ MinIO对象存储健康检查通过"
        else
            log_warning "⚠️ MinIO对象存储健康检查失败"
        fi
        
    else
        log_info "当前不在主服务器，跳过应用服务健康检查"
    fi
}

# 生成部署报告
generate_deployment_report() {
    log_header "集群部署验证报告"
    
    echo ""
    log_info "🌐 访问地址:"
    echo "    前端应用: http://$MAIN_SERVER"
    echo "    API文档:  http://$MAIN_SERVER/api/docs"
    echo "    健康检查: http://$MAIN_SERVER/health"
    echo "    MinIO控制台: http://$MAIN_SERVER:9002"
    
    echo ""
    log_info "🔗 服务连接信息:"
    echo "    PostgreSQL: $DB_SERVER:5432"
    echo "    Redis: $MAIN_SERVER:6379 (scow-redis-1)"
    echo "    Vespa: $MAIN_SERVER:8081"
    echo "    MinIO: $MAIN_SERVER:9001"
    
    echo ""
    log_info "📋 下一步操作建议:"
    
    if [[ "$CURRENT_SERVER" == "$MAIN_SERVER" ]]; then
        echo "    主服务器操作:"
        echo "    1. 检查服务状态: ./deploy-openeuler-cluster.sh status"
        echo "    2. 查看服务日志: docker-compose -f deployment/docker_compose/docker-compose.main.yml logs"
        echo "    3. 重启服务: docker-compose -f deployment/docker_compose/docker-compose.main.yml restart"
        
    elif [[ "$CURRENT_SERVER" == "$DB_SERVER" ]]; then
        echo "    数据库服务器操作:"
        echo "    1. 检查数据库状态: ./deploy-openeuler-cluster.sh status"
        echo "    2. 查看数据库日志: docker-compose -f deployment/docker_compose/docker-compose.db.yml logs"
        echo "    3. 备份数据库: docker exec onyx-postgres pg_dump -U onyx_user onyx > backup.sql"
    fi
    
    echo ""
    log_info "🔧 故障排除:"
    echo "    1. 检查网络连通性: ping <目标服务器IP>"
    echo "    2. 检查端口开放: nc -z <服务器IP> <端口>"
    echo "    3. 查看容器日志: docker logs <容器名>"
    echo "    4. 重启容器: docker restart <容器名>"
    
    echo ""
    log_info "📚 更多帮助:"
    echo "    部署脚本帮助: ./deploy-openeuler-cluster.sh help"
    echo "    部署文档: docs/Linux服务器Docker部署指南.md"
}

# 主函数
main() {
    echo "Onyx openEuler 双服务器集群部署验证"
    echo "======================================"
    echo ""
    
    # 检查当前服务器
    server_type=$(check_current_server)
    server_check_result=$?
    echo ""
    
    # 检查网络连通性
    check_network_connectivity
    echo ""
    
    # 根据服务器类型检查相应服务
    if [ $server_check_result -eq 0 ]; then
        # 主服务器
        check_main_server_services
        echo ""
        check_application_health
        echo ""
    elif [ $server_check_result -eq 1 ]; then
        # 数据库服务器
        check_db_server_services
        echo ""
    fi
    
    # 检查跨服务器连接
    check_cross_server_connections
    echo ""
    
    # 生成报告
    generate_deployment_report
}

# 执行主函数
main "$@"
