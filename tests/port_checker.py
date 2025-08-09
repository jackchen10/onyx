#!/usr/bin/env python3
"""
Onyx 端口检查脚本
检查所有服务端口的占用和可用性
"""

import socket
import subprocess
import sys
import time
from typing import Dict, List, Tuple

class PortChecker:
    def __init__(self):
        # 定义所有Onyx服务端口
        self.service_ports = {
            # 对外服务端口
            80: {"service": "Nginx HTTP", "type": "web", "critical": False},
            3000: {"service": "前端Web服务", "type": "web", "critical": True},
            8080: {"service": "后端API服务", "type": "api", "critical": True},
            
            # 数据库和缓存端口
            5432: {"service": "PostgreSQL数据库", "type": "database", "critical": True},
            6379: {"service": "Redis缓存", "type": "cache", "critical": True},
            
            # AI模型服务端口
            9000: {"service": "AI推理模型服务", "type": "ai", "critical": True},
            9001: {"service": "AI索引模型服务", "type": "ai", "critical": True},
            
            # 文件存储端口
            9004: {"service": "MinIO API", "type": "storage", "critical": True},
            9005: {"service": "MinIO管理控制台", "type": "storage", "critical": False},
            
            # 搜索引擎端口
            8081: {"service": "Vespa管理界面", "type": "search", "critical": False},
            19071: {"service": "Vespa应用端口", "type": "search", "critical": True},
        }
    
    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{'='*70}")
        print(f"🔌 {title}")
        print('='*70)
    
    def check_port_availability(self, port: int) -> Tuple[bool, str]:
        """检查端口是否可用"""
        try:
            # 尝试绑定端口
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                return True, "端口被占用"
            else:
                return False, "端口可用"
        except Exception as e:
            return False, f"检查异常: {e}"
    
    def get_port_process_info(self, port: int) -> str:
        """获取占用端口的进程信息"""
        try:
            if sys.platform == "win32":
                # Windows系统
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout.strip():
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if f':{port}' in line and 'LISTENING' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                
                                # 获取进程名称
                                proc_result = subprocess.run(
                                    f'tasklist /FI "PID eq {pid}" /FO CSV /NH',
                                    shell=True,
                                    capture_output=True,
                                    text=True
                                )
                                
                                if proc_result.stdout.strip():
                                    proc_info = proc_result.stdout.strip().split(',')[0].strip('"')
                                    return f"PID {pid} ({proc_info})"
                                else:
                                    return f"PID {pid}"
                
                return "未知进程"
            else:
                # Linux/Mac系统
                result = subprocess.run(
                    f'lsof -i :{port}',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout.strip():
                    lines = result.stdout.strip().split('\n')[1:]  # 跳过标题行
                    if lines:
                        parts = lines[0].split()
                        if len(parts) >= 2:
                            return f"{parts[0]} (PID {parts[1]})"
                
                return "未知进程"
        except Exception as e:
            return f"获取失败: {e}"
    
    def check_all_ports(self):
        """检查所有端口"""
        self.print_header("Onyx服务端口检查")
        
        print(f"{'端口':<6} | {'服务名称':<20} | {'类型':<8} | {'状态':<10} | {'进程信息'}")
        print("-" * 70)
        
        port_status = {}
        critical_issues = 0
        
        for port, info in sorted(self.service_ports.items()):
            occupied, status_msg = self.check_port_availability(port)
            service_name = info["service"]
            service_type = info["type"]
            is_critical = info["critical"]
            
            if occupied:
                # 端口被占用，获取进程信息
                process_info = self.get_port_process_info(port)
                status_icon = "🟢 占用"
                
                # 检查是否是预期的服务
                if any(keyword in process_info.lower() for keyword in ['python', 'node', 'nginx', 'postgres', 'redis']):
                    status_color = "🟢"
                else:
                    status_color = "🟡"
                    if is_critical:
                        critical_issues += 1
            else:
                # 端口可用
                process_info = "无"
                if is_critical:
                    status_icon = "🔴 空闲"
                    critical_issues += 1
                else:
                    status_icon = "⚪ 空闲"
                status_color = "🔴" if is_critical else "⚪"
            
            print(f"{port:<6} | {service_name:<20} | {service_type:<8} | {status_icon:<10} | {process_info}")
            
            port_status[port] = {
                "service": service_name,
                "occupied": occupied,
                "critical": is_critical,
                "process": process_info
            }
        
        return port_status, critical_issues
    
    def check_service_connectivity(self):
        """检查服务连通性"""
        self.print_header("服务连通性检查")
        
        # 定义服务健康检查端点
        health_endpoints = {
            8080: {"url": "http://localhost:8080/health", "name": "后端API"},
            3000: {"url": "http://localhost:3000", "name": "前端Web"},
            80: {"url": "http://localhost", "name": "Nginx代理"},
            9004: {"url": "http://localhost:9004/minio/health/live", "name": "MinIO API"},
            9005: {"url": "http://localhost:9005", "name": "MinIO控制台"},
            8081: {"url": "http://localhost:8081", "name": "Vespa管理"},
            19071: {"url": "http://localhost:19071/ApplicationStatus", "name": "Vespa应用"},
            9000: {"url": "http://localhost:9000/health", "name": "推理模型"},
            9001: {"url": "http://localhost:9001/health", "name": "索引模型"}
        }
        
        connectivity_results = {}
        
        for port, endpoint_info in health_endpoints.items():
            try:
                import requests
                start_time = time.time()
                response = requests.get(endpoint_info["url"], timeout=5)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    print(f"✅ {endpoint_info['name']:<15} | HTTP 200 | {response_time:.1f}ms")
                    connectivity_results[port] = {"status": "healthy", "response_time": response_time}
                else:
                    print(f"🟡 {endpoint_info['name']:<15} | HTTP {response.status_code} | {response_time:.1f}ms")
                    connectivity_results[port] = {"status": "error", "response_time": response_time}
            
            except requests.exceptions.ConnectionError:
                print(f"🔴 {endpoint_info['name']:<15} | 连接失败 | 服务未运行")
                connectivity_results[port] = {"status": "offline", "response_time": 0}
            
            except Exception as e:
                print(f"❌ {endpoint_info['name']:<15} | 检查异常 | {str(e)[:30]}...")
                connectivity_results[port] = {"status": "error", "response_time": 0}
        
        return connectivity_results
    
    def generate_port_report(self):
        """生成端口检查报告"""
        print("🔌 Onyx 端口检查报告")
        print("📅 检查时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
        
        # 检查端口占用
        port_status, critical_issues = self.check_all_ports()
        
        # 检查服务连通性
        connectivity = self.check_service_connectivity()
        
        # 生成总结
        self.print_header("检查总结")
        
        total_ports = len(self.service_ports)
        occupied_ports = sum(1 for status in port_status.values() if status["occupied"])
        critical_ports = sum(1 for info in self.service_ports.values() if info["critical"])
        
        print(f"📊 端口统计:")
        print(f"   总端口数: {total_ports}")
        print(f"   已占用端口: {occupied_ports}")
        print(f"   关键端口: {critical_ports}")
        print(f"   关键端口问题: {critical_issues}")
        
        # 服务连通性统计
        healthy_services = sum(1 for conn in connectivity.values() if conn["status"] == "healthy")
        total_services = len(connectivity)
        
        print(f"\n🌐 服务连通性:")
        print(f"   总服务数: {total_services}")
        print(f"   健康服务: {healthy_services}")
        print(f"   服务可用率: {healthy_services/total_services*100:.1f}%")
        
        # 建议
        if critical_issues == 0 and healthy_services == total_services:
            print(f"\n🎉 所有端口和服务状态正常！")
            return True
        else:
            print(f"\n⚠️  发现 {critical_issues} 个关键端口问题")
            print(f"💡 建议:")
            if critical_issues > 0:
                print(f"   1. 启动缺失的关键服务")
                print(f"   2. 检查服务配置")
            if healthy_services < total_services:
                print(f"   3. 检查服务健康状态")
                print(f"   4. 查看服务日志")
            return False

def main():
    """主函数"""
    checker = PortChecker()
    success = checker.generate_port_report()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
