#!/usr/bin/env python3
"""
Onyx 系统状态仪表板
实时显示系统状态、性能指标和服务健康状况
"""

import os
import sys
import time
import json
import requests
import psutil
from datetime import datetime
from pathlib import Path

class OnyxDashboard:
    def __init__(self):
        self.backend_url = "http://localhost:8080"
        self.frontend_url = "http://localhost:3000"
        self.project_root = Path(__file__).parent.parent
        
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_service_status(self):
        """获取服务状态"""
        services = {
            "backend": {"url": self.backend_url + "/health", "status": "unknown", "response_time": 0},
            "frontend": {"url": self.frontend_url, "status": "unknown", "response_time": 0}
        }
        
        for service_name, service_info in services.items():
            try:
                start_time = time.time()
                response = requests.get(service_info["url"], timeout=3)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    services[service_name]["status"] = "healthy"
                    services[service_name]["response_time"] = response_time
                else:
                    services[service_name]["status"] = "error"
                    services[service_name]["response_time"] = response_time
            except Exception:
                services[service_name]["status"] = "offline"
        
        return services
    
    def get_system_metrics(self):
        """获取系统指标"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory": psutil.virtual_memory(),
            "disk": psutil.disk_usage('C:' if os.name == 'nt' else '/'),
            "network": psutil.net_io_counters(),
            "boot_time": psutil.boot_time()
        }
    
    def get_process_info(self):
        """获取Onyx进程信息"""
        processes = {"backend": [], "frontend": []}
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'cmdline', 'create_time']):
            try:
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                
                if 'python' in proc.info['name'].lower() and ('test_server.py' in cmdline or 'onyx' in cmdline):
                    processes["backend"].append({
                        "pid": proc.info['pid'],
                        "memory_mb": proc.info['memory_info'].rss / (1024**2),
                        "cpu_percent": proc.info['cpu_percent'],
                        "uptime": time.time() - proc.info['create_time']
                    })
                elif 'node' in proc.info['name'].lower() and ('next' in cmdline or '3000' in cmdline):
                    processes["frontend"].append({
                        "pid": proc.info['pid'],
                        "memory_mb": proc.info['memory_info'].rss / (1024**2),
                        "cpu_percent": proc.info['cpu_percent'],
                        "uptime": time.time() - proc.info['create_time']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
    
    def format_uptime(self, seconds):
        """格式化运行时间"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours:02d}:{minutes:02d}"
    
    def format_bytes(self, bytes_value):
        """格式化字节数"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024:
                return f"{bytes_value:.1f}{unit}"
            bytes_value /= 1024
        return f"{bytes_value:.1f}TB"
    
    def display_dashboard(self):
        """显示仪表板"""
        while True:
            try:
                self.clear_screen()
                
                # 标题
                print("=" * 80)
                print("🖥️  ONYX 系统状态仪表板")
                print("=" * 80)
                print(f"📅 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print()
                
                # 服务状态
                services = self.get_service_status()
                print("🔧 服务状态:")
                for service_name, service_data in services.items():
                    status = service_data["status"]
                    response_time = service_data.get("response_time", 0)
                    
                    if status == "healthy":
                        icon = "🟢"
                        status_text = f"正常 ({response_time:.1f}ms)"
                    elif status == "error":
                        icon = "🟡"
                        status_text = f"错误 ({response_time:.1f}ms)"
                    else:
                        icon = "🔴"
                        status_text = "离线"
                    
                    service_display = "后端API" if service_name == "backend" else "前端Web"
                    print(f"  {icon} {service_display:8} | {status_text}")
                
                print()
                
                # 系统指标
                metrics = self.get_system_metrics()
                print("💻 系统性能:")
                print(f"  🔥 CPU使用率    | {metrics['cpu_percent']:5.1f}%")
                print(f"  💾 内存使用率   | {metrics['memory'].percent:5.1f}% ({self.format_bytes(metrics['memory'].used)}/{self.format_bytes(metrics['memory'].total)})")
                print(f"  💿 磁盘使用率   | {metrics['disk'].percent:5.1f}% (剩余 {self.format_bytes(metrics['disk'].free)})")
                print(f"  🌐 网络发送     | {self.format_bytes(metrics['network'].bytes_sent)}")
                print(f"  📥 网络接收     | {self.format_bytes(metrics['network'].bytes_recv)}")
                
                print()
                
                # 进程信息
                processes = self.get_process_info()
                print("🔄 Onyx进程:")
                
                if processes["backend"]:
                    total_backend_memory = sum(p["memory_mb"] for p in processes["backend"])
                    backend_proc = processes["backend"][0]  # 主进程
                    uptime = self.format_uptime(backend_proc["uptime"])
                    print(f"  🐍 后端进程     | PID:{backend_proc['pid']} | 内存:{total_backend_memory:.1f}MB | 运行:{uptime}")
                else:
                    print(f"  🔴 后端进程     | 未运行")
                
                if processes["frontend"]:
                    total_frontend_memory = sum(p["memory_mb"] for p in processes["frontend"])
                    frontend_proc = processes["frontend"][0]  # 主进程
                    uptime = self.format_uptime(frontend_proc["uptime"])
                    print(f"  🌐 前端进程     | PID:{frontend_proc['pid']} | 内存:{total_frontend_memory:.1f}MB | 运行:{uptime}")
                else:
                    print(f"  🔴 前端进程     | 未运行")
                
                print()
                
                # 快速操作
                print("🛠️  快速操作:")
                print("  [H] 运行健康检查    [T] 故障排除    [P] 性能测试")
                print("  [E] 端到端测试      [M] 启动监控    [Q] 退出")
                
                print()
                print("🔄 自动刷新中... (按任意键进行操作)")
                
                # 等待用户输入或自动刷新
                import msvcrt
                start_time = time.time()
                while time.time() - start_time < 5:  # 5秒自动刷新
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8').upper()
                        return self.handle_user_input(key)
                    time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\n\n🛑 仪表板已停止")
                return True
            except Exception as e:
                print(f"\n❌ 仪表板错误: {e}")
                time.sleep(2)
    
    def handle_user_input(self, key: str):
        """处理用户输入"""
        if key == 'Q':
            print("\n👋 退出仪表板")
            return True
        elif key == 'H':
            print("\n🏥 运行健康检查...")
            os.system(f"python {self.project_root}/tests/health_check.py")
            input("\n按回车键返回仪表板...")
        elif key == 'T':
            print("\n🔧 运行故障排除...")
            os.system(f"python {self.project_root}/tests/troubleshoot.py")
            input("\n按回车键返回仪表板...")
        elif key == 'P':
            print("\n⚡ 运行性能测试...")
            os.system(f"python {self.project_root}/tests/performance_test.py")
            input("\n按回车键返回仪表板...")
        elif key == 'E':
            print("\n🔄 运行端到端测试...")
            os.system(f"python {self.project_root}/tests/e2e_test.py")
            input("\n按回车键返回仪表板...")
        elif key == 'M':
            print("\n📊 启动系统监控...")
            os.system(f"python {self.project_root}/tests/monitor_system.py")
            input("\n按回车键返回仪表板...")
        
        return False

def main():
    """主函数"""
    dashboard = OnyxDashboard()
    dashboard.display_dashboard()

if __name__ == "__main__":
    main()
