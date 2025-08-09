#!/usr/bin/env python3
"""
Onyx Docker 容器清单验证脚本
验证所有必需的Docker容器是否正确部署和运行
"""

import subprocess
import json
import time
import requests
from typing import Dict, List

class DockerContainerChecker:
    def __init__(self):
        self.compose_file = "deployment/docker_compose/docker-compose.dev.yml"
        
        # 定义所有必需的容器及其验证方式
        self.containers = {
            "relational_db": {
                "name": "PostgreSQL数据库",
                "image": "postgres:15.2-alpine",
                "ports": ["5432:5432"],
                "health_check": self.check_postgres_health,
                "critical": True
            },
            "cache": {
                "name": "Redis缓存",
                "image": "redis:7.4-alpine", 
                "ports": ["6379:6379"],
                "health_check": self.check_redis_health,
                "critical": True
            },
            "minio": {
                "name": "MinIO文件存储",
                "image": "minio/minio:latest",
                "ports": ["9004:9000", "9005:9001"],
                "health_check": self.check_minio_health,
                "critical": True
            },
            "index": {
                "name": "Vespa搜索引擎",
                "image": "vespaengine/vespa:8.526.15",
                "ports": ["19071:19071", "8081:8081"],
                "health_check": self.check_vespa_health,
                "critical": True
            },
            "inference_model_server": {
                "name": "推理模型服务器",
                "image": "onyxdotapp/onyx-model-server:latest",
                "ports": ["9000:9000"],
                "health_check": self.check_inference_model_health,
                "critical": True
            },
            "indexing_model_server": {
                "name": "索引模型服务器", 
                "image": "onyxdotapp/onyx-model-server:latest",
                "ports": ["9001:9000"],
                "health_check": self.check_indexing_model_health,
                "critical": True
            },
            "api_server": {
                "name": "后端API服务器",
                "image": "onyxdotapp/onyx-backend:latest",
                "ports": ["8080:8080"],
                "health_check": self.check_api_server_health,
                "critical": True
            },
            "background": {
                "name": "后台任务处理器",
                "image": "onyxdotapp/onyx-backend:latest",
                "ports": [],
                "health_check": self.check_background_health,
                "critical": True
            },
            "web_server": {
                "name": "前端Web服务器",
                "image": "onyxdotapp/onyx-web-server:latest",
                "ports": ["3000:3000"],
                "health_check": self.check_web_server_health,
                "critical": True
            },
            "nginx": {
                "name": "Nginx反向代理",
                "image": "nginx:1.23.4-alpine",
                "ports": ["80:80"],
                "health_check": self.check_nginx_health,
                "critical": False
            }
        }
    
    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{'='*60}")
        print(f"🐳 {title}")
        print('='*60)
    
    def print_result(self, test_name: str, success: bool, details: str = ""):
        """打印测试结果"""
        status = "✅ 正常" if success else "❌ 异常"
        print(f"{status} {test_name}")
        if details:
            print(f"   详情: {details}")
    
    def check_postgres_health(self) -> tuple[bool, str]:
        """检查PostgreSQL健康状态"""
        try:
            # 使用docker exec检查PostgreSQL
            success, stdout, stderr = self.run_docker_command(
                f"docker-compose -f {self.compose_file} exec -T relational_db pg_isready -U postgres"
            )
            if success and "accepting connections" in stdout:
                return True, "数据库接受连接"
            return False, stderr or "连接检查失败"
        except Exception as e:
            return False, str(e)
    
    def check_redis_health(self) -> tuple[bool, str]:
        """检查Redis健康状态"""
        try:
            success, stdout, stderr = self.run_docker_command(
                f"docker-compose -f {self.compose_file} exec -T cache redis-cli ping"
            )
            if success and "PONG" in stdout:
                return True, "Redis响应正常"
            return False, stderr or "Redis无响应"
        except Exception as e:
            return False, str(e)
    
    def check_minio_health(self) -> tuple[bool, str]:
        """检查MinIO健康状态"""
        try:
            response = requests.get("http://localhost:9004/minio/health/live", timeout=5)
            if response.status_code == 200:
                return True, "MinIO服务正常"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def check_vespa_health(self) -> tuple[bool, str]:
        """检查Vespa健康状态"""
        try:
            response = requests.get("http://localhost:19071/ApplicationStatus", timeout=10)
            if response.status_code == 200:
                return True, "Vespa搜索引擎正常"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def check_inference_model_health(self) -> tuple[bool, str]:
        """检查推理模型服务器健康状态"""
        try:
            response = requests.get("http://localhost:9000/health", timeout=10)
            if response.status_code == 200:
                return True, "推理模型服务正常"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def check_indexing_model_health(self) -> tuple[bool, str]:
        """检查索引模型服务器健康状态"""
        try:
            response = requests.get("http://localhost:9001/health", timeout=10)
            if response.status_code == 200:
                return True, "索引模型服务正常"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def check_api_server_health(self) -> tuple[bool, str]:
        """检查API服务器健康状态"""
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            if response.status_code == 200:
                return True, "API服务器正常"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def check_background_health(self) -> tuple[bool, str]:
        """检查后台任务处理器健康状态"""
        try:
            # 检查容器是否运行
            success, stdout, stderr = self.run_docker_command(
                f"docker-compose -f {self.compose_file} ps background"
            )
            if success and "Up" in stdout:
                return True, "后台任务处理器运行中"
            return False, "后台任务处理器未运行"
        except Exception as e:
            return False, str(e)
    
    def check_web_server_health(self) -> tuple[bool, str]:
        """检查Web服务器健康状态"""
        try:
            response = requests.get("http://localhost:3000", timeout=10)
            if response.status_code == 200:
                return True, "Web服务器正常"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def check_nginx_health(self) -> tuple[bool, str]:
        """检查Nginx健康状态"""
        try:
            response = requests.get("http://localhost", timeout=5)
            if response.status_code == 200:
                return True, "Nginx代理正常"
            return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def run_full_check(self):
        """运行完整的容器检查"""
        print("🐳 Onyx Docker 容器完整检查")
        print("📅 检查时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
        
        if not self.check_docker_availability():
            return False
        
        self.print_header("容器状态检查")
        
        # 获取容器状态
        containers_status = self.get_container_status()
        
        # 检查每个容器
        all_healthy = True
        critical_failed = 0
        
        for container_id, container_info in self.containers.items():
            print(f"\n🔍 检查 {container_info['name']} ({container_id})...")
            
            # 检查容器是否运行
            if container_id in containers_status:
                container_data = containers_status[container_id]
                if container_data['state'] == 'running':
                    print(f"  ✅ 容器运行中: {container_data['status']}")
                    
                    # 运行健康检查
                    if container_info['health_check']:
                        healthy, details = container_info['health_check']()
                        self.print_result(f"{container_info['name']}健康检查", healthy, details)
                        
                        if not healthy:
                            all_healthy = False
                            if container_info['critical']:
                                critical_failed += 1
                else:
                    print(f"  ❌ 容器未运行: {container_data['state']}")
                    all_healthy = False
                    if container_info['critical']:
                        critical_failed += 1
            else:
                print(f"  ❌ 容器不存在或未启动")
                all_healthy = False
                if container_info['critical']:
                    critical_failed += 1
        
        # 生成总结报告
        self.print_header("检查总结")
        
        total_containers = len(self.containers)
        critical_containers = sum(1 for c in self.containers.values() if c['critical'])
        
        print(f"📊 容器总数: {total_containers}")
        print(f"🔥 关键容器: {critical_containers}")
        print(f"❌ 关键容器失败: {critical_failed}")
        
        if all_healthy:
            print("\n🎉 所有容器健康检查通过！")
            return True
        elif critical_failed == 0:
            print("\n✅ 关键容器正常，部分非关键容器有问题")
            return True
        else:
            print(f"\n❌ {critical_failed} 个关键容器有问题，系统可能无法正常工作")
            return False

def main():
    """主函数"""
    checker = DockerContainerChecker()
    success = checker.run_full_check()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
