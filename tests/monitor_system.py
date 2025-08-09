#!/usr/bin/env python3
"""
Onyx 系统监控脚本
实时监控系统状态和性能指标
"""

import requests
import time
import psutil
import json
import sys
from datetime import datetime
from typing import Dict, List

class SystemMonitor:
    def __init__(self, interval: int = 30):
        self.backend_url = "http://localhost:8080"
        self.frontend_url = "http://localhost:3000"
        self.interval = interval
        self.monitoring = True
        self.metrics_history = []
    
    def get_service_status(self) -> Dict:
        """获取服务状态"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "backend": {"status": "unknown", "response_time": 0},
            "frontend": {"status": "unknown", "response_time": 0}
        }
        
        # 检查后端
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                status["backend"] = {"status": "healthy", "response_time": response_time}
            else:
                status["backend"] = {"status": "error", "response_time": response_time}
        except Exception as e:
            status["backend"] = {"status": "offline", "error": str(e)}
        
        # 检查前端
        try:
            start_time = time.time()
            response = requests.get(f"{self.frontend_url}", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                status["frontend"] = {"status": "healthy", "response_time": response_time}
            else:
                status["frontend"] = {"status": "error", "response_time": response_time}
        except Exception as e:
            status["frontend"] = {"status": "offline", "error": str(e)}
        
        return status
    
    def get_system_metrics(self) -> Dict:
        """获取系统性能指标"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory": {
                "percent": psutil.virtual_memory().percent,
                "used_gb": psutil.virtual_memory().used / (1024**3),
                "available_gb": psutil.virtual_memory().available / (1024**3)
            },
            "disk": {
                "percent": psutil.disk_usage('C:').percent,
                "free_gb": psutil.disk_usage('C:').free / (1024**3)
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            }
        }
    
    def get_process_metrics(self) -> Dict:
        """获取Onyx相关进程指标"""
        python_processes = []
        node_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'test_server.py' in cmdline or 'onyx' in cmdline:
                        python_processes.append({
                            "pid": proc.info['pid'],
                            "memory_mb": proc.info['memory_info'].rss / (1024**2),
                            "cpu_percent": proc.info['cpu_percent']
                        })
                elif 'node' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'next' in cmdline or '3000' in cmdline:
                        node_processes.append({
                            "pid": proc.info['pid'],
                            "memory_mb": proc.info['memory_info'].rss / (1024**2),
                            "cpu_percent": proc.info['cpu_percent']
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            "timestamp": datetime.now().isoformat(),
            "backend_processes": python_processes,
            "frontend_processes": node_processes,
            "total_backend_memory": sum(p["memory_mb"] for p in python_processes),
            "total_frontend_memory": sum(p["memory_mb"] for p in node_processes)
        }
    
    def print_status_line(self, metrics: Dict):
        """打印状态行"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 服务状态
        backend_status = metrics["services"]["backend"]["status"]
        frontend_status = metrics["services"]["frontend"]["status"]
        
        backend_icon = "🟢" if backend_status == "healthy" else "🔴" if backend_status == "offline" else "🟡"
        frontend_icon = "🟢" if frontend_status == "healthy" else "🔴" if frontend_status == "offline" else "🟡"
        
        # 性能指标
        cpu = metrics["system"]["cpu_percent"]
        memory = metrics["system"]["memory"]["percent"]
        
        # 响应时间
        backend_time = metrics["services"]["backend"].get("response_time", 0)
        frontend_time = metrics["services"]["frontend"].get("response_time", 0)
        
        print(f"[{timestamp}] {backend_icon}后端 {frontend_icon}前端 | "
              f"CPU: {cpu:5.1f}% | 内存: {memory:5.1f}% | "
              f"响应: 后端{backend_time:6.1f}ms 前端{frontend_time:6.1f}ms")
    
    def monitor_loop(self):
        """监控循环"""
        print("🖥️  Onyx 系统实时监控")
        print("📅 开始时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("⏱️  监控间隔:", self.interval, "秒")
        print("🛑 按 Ctrl+C 停止监控")
        print("\n" + "="*80)
        print("时间     | 服务状态 | 系统性能 | 响应时间")
        print("="*80)
        
        try:
            while self.monitoring:
                # 收集指标
                service_status = self.get_service_status()
                system_metrics = self.get_system_metrics()
                process_metrics = self.get_process_metrics()
                
                # 合并指标
                combined_metrics = {
                    "services": service_status,
                    "system": system_metrics,
                    "processes": process_metrics
                }
                
                # 保存历史
                self.metrics_history.append(combined_metrics)
                
                # 只保留最近100条记录
                if len(self.metrics_history) > 100:
                    self.metrics_history.pop(0)
                
                # 显示状态
                self.print_status_line(combined_metrics)
                
                # 检查异常情况
                self.check_alerts(combined_metrics)
                
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 监控已停止")
            self.generate_monitoring_report()
    
    def check_alerts(self, metrics: Dict):
        """检查告警条件"""
        # CPU使用率过高
        if metrics["system"]["cpu_percent"] > 80:
            print(f"⚠️  [告警] CPU使用率过高: {metrics['system']['cpu_percent']:.1f}%")
        
        # 内存使用率过高
        if metrics["system"]["memory"]["percent"] > 85:
            print(f"⚠️  [告警] 内存使用率过高: {metrics['system']['memory']['percent']:.1f}%")
        
        # 服务离线
        if metrics["services"]["backend"]["status"] == "offline":
            print("🚨 [告警] 后端服务离线！")
        
        if metrics["services"]["frontend"]["status"] == "offline":
            print("🚨 [告警] 前端服务离线！")
        
        # 响应时间过长
        backend_time = metrics["services"]["backend"].get("response_time", 0)
        if backend_time > 1000:  # 超过1秒
            print(f"⚠️  [告警] 后端响应时间过长: {backend_time:.1f}ms")
    
    def generate_monitoring_report(self):
        """生成监控报告"""
        if not self.metrics_history:
            print("📊 无监控数据")
            return
        
        print("\n" + "="*60)
        print("📊 监控报告")
        print("="*60)
        
        # 计算平均值
        total_records = len(self.metrics_history)
        
        # 服务可用性
        backend_healthy = sum(1 for m in self.metrics_history 
                            if m["services"]["backend"]["status"] == "healthy")
        frontend_healthy = sum(1 for m in self.metrics_history 
                             if m["services"]["frontend"]["status"] == "healthy")
        
        backend_uptime = backend_healthy / total_records * 100
        frontend_uptime = frontend_healthy / total_records * 100
        
        print(f"🔧 后端可用性: {backend_uptime:.1f}% ({backend_healthy}/{total_records})")
        print(f"🌐 前端可用性: {frontend_uptime:.1f}% ({frontend_healthy}/{total_records})")
        
        # 平均性能指标
        avg_cpu = sum(m["system"]["cpu_percent"] for m in self.metrics_history) / total_records
        avg_memory = sum(m["system"]["memory"]["percent"] for m in self.metrics_history) / total_records
        
        print(f"💻 平均CPU使用率: {avg_cpu:.1f}%")
        print(f"💾 平均内存使用率: {avg_memory:.1f}%")
        
        # 响应时间统计
        backend_times = [m["services"]["backend"].get("response_time", 0) 
                        for m in self.metrics_history 
                        if m["services"]["backend"].get("response_time", 0) > 0]
        
        if backend_times:
            avg_backend_time = sum(backend_times) / len(backend_times)
            max_backend_time = max(backend_times)
            print(f"⚡ 后端平均响应时间: {avg_backend_time:.1f}ms")
            print(f"🐌 后端最慢响应: {max_backend_time:.1f}ms")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print("❌ 无效的监控间隔，使用默认值30秒")
            interval = 30
    else:
        interval = 30
    
    monitor = SystemMonitor(interval)
    monitor.monitor_loop()

if __name__ == "__main__":
    main()
