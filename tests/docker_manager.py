#!/usr/bin/env python3
"""
Onyx Docker 容器管理脚本
管理和监控所有Docker容器的状态
"""

import subprocess
import json
import time
import sys
from typing import Dict, List

class DockerManager:
    def __init__(self):
        self.compose_file = "deployment/docker_compose/docker-compose.dev.yml"
        self.required_containers = [
            "relational_db",      # PostgreSQL数据库
            "cache",              # Redis缓存
            "minio",              # MinIO文件存储
            "index",              # Vespa搜索引擎
            "inference_model_server",  # 推理模型服务器
            "indexing_model_server",   # 索引模型服务器
            "api_server",         # 后端API服务器
            "background",         # 后台任务处理器
            "web_server",         # 前端Web服务器
            "nginx"               # Nginx反向代理
        ]
    
    def run_docker_command(self, command: str) -> tuple[bool, str, str]:
        """运行Docker命令"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='ignore'
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "命令超时"
        except Exception as e:
            return False, "", str(e)
    
    def check_docker_availability(self) -> bool:
        """检查Docker是否可用"""
        print("🔍 检查Docker环境...")
        
        # 检查Docker
        success, stdout, stderr = self.run_docker_command("docker --version")
        if not success:
            print("❌ Docker 未安装或未启动")
            return False
        print(f"✅ Docker版本: {stdout.strip()}")
        
        # 检查Docker Compose
        success, stdout, stderr = self.run_docker_command("docker-compose --version")
        if not success:
            print("❌ Docker Compose 未安装")
            return False
        print(f"✅ Docker Compose版本: {stdout.strip()}")
        
        # 检查Docker守护进程
        success, stdout, stderr = self.run_docker_command("docker info")
        if not success:
            print("❌ Docker守护进程未运行")
            return False
        print("✅ Docker守护进程运行正常")
        
        return True
    
    def get_container_status(self) -> Dict:
        """获取容器状态"""
        success, stdout, stderr = self.run_docker_command(
            f"docker-compose -f {self.compose_file} ps --format json"
        )
        
        if not success:
            print(f"❌ 获取容器状态失败: {stderr}")
            return {}
        
        containers = {}
        try:
            # 解析JSON输出
            for line in stdout.strip().split('\n'):
                if line.strip():
                    container_info = json.loads(line)
                    service_name = container_info.get('Service', '')
                    containers[service_name] = {
                        'name': container_info.get('Name', ''),
                        'state': container_info.get('State', ''),
                        'status': container_info.get('Status', ''),
                        'ports': container_info.get('Publishers', [])
                    }
        except json.JSONDecodeError:
            # 如果JSON解析失败，使用传统方式
            success, stdout, stderr = self.run_docker_command(
                f"docker-compose -f {self.compose_file} ps"
            )
            print("📊 容器状态 (文本格式):")
            print(stdout)
        
        return containers
    
    def check_container_health(self) -> Dict:
        """检查容器健康状态"""
        print("🏥 检查容器健康状态...")
        
        health_status = {}
        
        # 检查每个必需的容器
        for container in self.required_containers:
            print(f"检查 {container}...")
            
            # 检查容器是否运行
            success, stdout, stderr = self.run_docker_command(
                f"docker-compose -f {self.compose_file} ps {container}"
            )
            
            if success and "Up" in stdout:
                health_status[container] = "running"
                print(f"  ✅ {container} 运行中")
            else:
                health_status[container] = "stopped"
                print(f"  ❌ {container} 未运行")
        
        return health_status
    
    def start_all_services(self):
        """启动所有服务"""
        print("🚀 启动所有Docker服务...")
        
        # 分阶段启动服务
        stages = [
            {
                "name": "基础服务",
                "services": ["relational_db", "cache", "minio"],
                "wait_time": 15
            },
            {
                "name": "搜索引擎",
                "services": ["index"],
                "wait_time": 30
            },
            {
                "name": "AI模型服务",
                "services": ["inference_model_server", "indexing_model_server"],
                "wait_time": 60
            },
            {
                "name": "应用服务",
                "services": ["api_server", "background", "web_server"],
                "wait_time": 30
            },
            {
                "name": "代理服务",
                "services": ["nginx"],
                "wait_time": 10
            }
        ]
        
        for stage in stages:
            print(f"\n🔧 启动{stage['name']}...")
            services_str = " ".join(stage["services"])
            
            success, stdout, stderr = self.run_docker_command(
                f"docker-compose -f {self.compose_file} up -d {services_str}"
            )
            
            if success:
                print(f"✅ {stage['name']}启动命令执行成功")
                print(f"⏳ 等待{stage['wait_time']}秒...")
                time.sleep(stage["wait_time"])
            else:
                print(f"❌ {stage['name']}启动失败: {stderr}")
                return False
        
        return True
    
    def stop_all_services(self):
        """停止所有服务"""
        print("🛑 停止所有Docker服务...")
        
        success, stdout, stderr = self.run_docker_command(
            f"docker-compose -f {self.compose_file} down"
        )
        
        if success:
            print("✅ 所有服务已停止")
            return True
        else:
            print(f"❌ 停止服务失败: {stderr}")
            return False
    
    def show_service_logs(self, service_name: str = None):
        """显示服务日志"""
        if service_name:
            print(f"📋 显示 {service_name} 服务日志...")
            command = f"docker-compose -f {self.compose_file} logs --tail=50 {service_name}"
        else:
            print("📋 显示所有服务日志...")
            command = f"docker-compose -f {self.compose_file} logs --tail=20"
        
        success, stdout, stderr = self.run_docker_command(command)
        
        if success:
            print(stdout)
        else:
            print(f"❌ 获取日志失败: {stderr}")
    
    def restart_service(self, service_name: str):
        """重启指定服务"""
        print(f"🔄 重启 {service_name} 服务...")
        
        success, stdout, stderr = self.run_docker_command(
            f"docker-compose -f {self.compose_file} restart {service_name}"
        )
        
        if success:
            print(f"✅ {service_name} 重启成功")
            return True
        else:
            print(f"❌ {service_name} 重启失败: {stderr}")
            return False
    
    def show_resource_usage(self):
        """显示资源使用情况"""
        print("💻 Docker资源使用情况:")
        
        success, stdout, stderr = self.run_docker_command("docker stats --no-stream --format 'table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}\\t{{.NetIO}}\\t{{.BlockIO}}'")
        
        if success:
            print(stdout)
        else:
            print(f"❌ 获取资源使用失败: {stderr}")
    
    def interactive_menu(self):
        """交互式菜单"""
        while True:
            print("\n" + "="*60)
            print("🐳 Onyx Docker 管理器")
            print("="*60)
            print("1. 检查容器状态")
            print("2. 启动所有服务")
            print("3. 停止所有服务")
            print("4. 重启指定服务")
            print("5. 查看服务日志")
            print("6. 查看资源使用")
            print("7. 健康检查")
            print("0. 退出")
            print("="*60)
            
            choice = input("请选择操作 (0-7): ").strip()
            
            if choice == "0":
                print("👋 退出Docker管理器")
                break
            elif choice == "1":
                containers = self.get_container_status()
                health = self.check_container_health()
            elif choice == "2":
                self.start_all_services()
            elif choice == "3":
                self.stop_all_services()
            elif choice == "4":
                service = input("请输入服务名称: ").strip()
                if service in self.required_containers:
                    self.restart_service(service)
                else:
                    print(f"❌ 无效的服务名称，可用服务: {', '.join(self.required_containers)}")
            elif choice == "5":
                service = input("请输入服务名称 (留空显示所有): ").strip()
                self.show_service_logs(service if service else None)
            elif choice == "6":
                self.show_resource_usage()
            elif choice == "7":
                # 运行健康检查
                import os
                os.system("python tests/health_check.py")
            else:
                print("❌ 无效选择，请重试")

def main():
    """主函数"""
    manager = DockerManager()
    
    # 检查Docker环境
    if not manager.check_docker_availability():
        print("❌ Docker环境不可用，请检查Docker Desktop")
        sys.exit(1)
    
    # 启动交互式菜单
    manager.interactive_menu()

if __name__ == "__main__":
    main()
