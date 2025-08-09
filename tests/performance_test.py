#!/usr/bin/env python3
"""
Onyx 性能测试脚本
测试系统性能指标和负载能力
"""

import requests
import time
import psutil
import threading
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

class PerformanceTestRunner:
    def __init__(self):
        self.backend_url = "http://localhost:8080"
        self.frontend_url = "http://localhost:3000"
        self.results = {}
    
    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{'='*60}")
        print(f"⚡ {title}")
        print('='*60)

    def print_result(self, test_name: str, success: bool, details: str = ""):
        """打印测试结果"""
        status = "✅ 通过" if success else "❌ 未达标"
        print(f"{status} {test_name}")
        if details:
            print(f"   详情: {details}")
    
    def get_system_metrics(self) -> Dict:
        """获取系统性能指标"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used_gb": psutil.virtual_memory().used / (1024**3),
            "disk_usage_percent": psutil.disk_usage('/').percent if sys.platform != 'win32' else psutil.disk_usage('C:').percent
        }
    
    def test_api_response_time(self) -> Dict:
        """测试API响应时间"""
        self.print_header("API响应时间测试")
        
        endpoints = [
            "/health",
            "/settings", 
            "/auth/type",
            "/me",
            "/persona",
            "/llm/provider"
        ]
        
        response_times = {}
        
        for endpoint in endpoints:
            times = []
            print(f"测试 {endpoint}...")
            
            # 每个端点测试10次
            for i in range(10):
                try:
                    start_time = time.time()
                    response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        response_time = (end_time - start_time) * 1000
                        times.append(response_time)
                    else:
                        print(f"   ❌ 请求失败: HTTP {response.status_code}")
                except Exception as e:
                    print(f"   ❌ 请求异常: {e}")
            
            if times:
                avg_time = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                median_time = statistics.median(times)
                
                response_times[endpoint] = {
                    "average": avg_time,
                    "min": min_time,
                    "max": max_time,
                    "median": median_time,
                    "samples": len(times)
                }
                
                print(f"   ✅ 平均: {avg_time:.2f}ms, 最小: {min_time:.2f}ms, 最大: {max_time:.2f}ms")
            else:
                response_times[endpoint] = None
                print(f"   ❌ 无有效响应")
        
        self.results["api_response_times"] = response_times
        return response_times
    
    def test_concurrent_requests(self, num_threads: int = 10, requests_per_thread: int = 5) -> Dict:
        """测试并发请求处理能力"""
        self.print_header(f"并发请求测试 ({num_threads} 线程, 每线程 {requests_per_thread} 请求)")
        
        def make_request(thread_id: int, request_id: int) -> Dict:
            """发送单个请求"""
            try:
                start_time = time.time()
                response = requests.get(f"{self.backend_url}/health", timeout=10)
                end_time = time.time()
                
                return {
                    "thread_id": thread_id,
                    "request_id": request_id,
                    "success": response.status_code == 200,
                    "response_time": (end_time - start_time) * 1000,
                    "status_code": response.status_code
                }
            except Exception as e:
                return {
                    "thread_id": thread_id,
                    "request_id": request_id,
                    "success": False,
                    "response_time": 0,
                    "error": str(e)
                }
        
        # 记录开始时的系统指标
        start_metrics = self.get_system_metrics()
        start_time = time.time()
        
        # 执行并发请求
        results = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for thread_id in range(num_threads):
                for request_id in range(requests_per_thread):
                    future = executor.submit(make_request, thread_id, request_id)
                    futures.append(future)
            
            for future in as_completed(futures):
                results.append(future.result())
        
        end_time = time.time()
        end_metrics = self.get_system_metrics()
        
        # 分析结果
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        total_requests = len(results)
        success_rate = len(successful_requests) / total_requests * 100
        total_time = end_time - start_time
        requests_per_second = total_requests / total_time
        
        if successful_requests:
            response_times = [r['response_time'] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        # 打印结果
        print(f"📊 总请求数: {total_requests}")
        print(f"✅ 成功请求: {len(successful_requests)}")
        print(f"❌ 失败请求: {len(failed_requests)}")
        print(f"📈 成功率: {success_rate:.1f}%")
        print(f"⚡ 请求/秒: {requests_per_second:.2f}")
        print(f"🕐 总耗时: {total_time:.2f}秒")
        print(f"⏱️  平均响应时间: {avg_response_time:.2f}ms")
        print(f"🐌 最慢响应: {max_response_time:.2f}ms")
        print(f"🚀 最快响应: {min_response_time:.2f}ms")
        
        # 系统资源使用
        print(f"\n💻 系统资源使用:")
        print(f"   CPU: {start_metrics['cpu_percent']:.1f}% → {end_metrics['cpu_percent']:.1f}%")
        print(f"   内存: {start_metrics['memory_percent']:.1f}% → {end_metrics['memory_percent']:.1f}%")
        
        concurrent_results = {
            "total_requests": total_requests,
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": success_rate,
            "requests_per_second": requests_per_second,
            "total_time": total_time,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "min_response_time": min_response_time,
            "start_metrics": start_metrics,
            "end_metrics": end_metrics
        }
        
        self.results["concurrent_test"] = concurrent_results
        return success_rate > 90  # 90%以上成功率认为通过
    
    def test_memory_usage(self) -> Dict:
        """测试内存使用情况"""
        self.print_header("内存使用测试")
        
        # 获取Python进程
        python_processes = []
        node_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cmdline']):
            try:
                if 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'test_server.py' in cmdline or 'onyx' in cmdline:
                        python_processes.append(proc)
                elif 'node' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if 'next' in cmdline or '3000' in cmdline:
                        node_processes.append(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # 计算内存使用
        total_backend_memory = sum(proc.memory_info().rss for proc in python_processes) / (1024**2)
        total_frontend_memory = sum(proc.memory_info().rss for proc in node_processes) / (1024**2)
        
        print(f"🐍 后端进程数: {len(python_processes)}")
        print(f"   内存使用: {total_backend_memory:.1f} MB")
        
        print(f"🌐 前端进程数: {len(node_processes)}")
        print(f"   内存使用: {total_frontend_memory:.1f} MB")
        
        print(f"💾 总内存使用: {total_backend_memory + total_frontend_memory:.1f} MB")
        
        # 内存使用合理性检查
        memory_ok = total_backend_memory < 1000 and total_frontend_memory < 1000  # 小于1GB
        self.print_result("内存使用合理性", memory_ok, 
                         f"总使用: {total_backend_memory + total_frontend_memory:.1f}MB")
        
        memory_results = {
            "backend_processes": len(python_processes),
            "frontend_processes": len(node_processes),
            "backend_memory_mb": total_backend_memory,
            "frontend_memory_mb": total_frontend_memory,
            "total_memory_mb": total_backend_memory + total_frontend_memory,
            "memory_reasonable": memory_ok
        }
        
        self.results["memory_usage"] = memory_results
        return memory_ok
    
    def generate_performance_report(self):
        """生成性能测试报告"""
        self.print_header("性能测试报告")
        
        # API性能总结
        if "api_response_times" in self.results:
            api_times = self.results["api_response_times"]
            valid_times = [data for data in api_times.values() if data is not None]
            
            if valid_times:
                all_avg_times = [data["average"] for data in valid_times]
                overall_avg = statistics.mean(all_avg_times)
                print(f"🚀 API整体平均响应时间: {overall_avg:.2f}ms")
                
                fastest_endpoint = min(valid_times, key=lambda x: x["average"])
                slowest_endpoint = max(valid_times, key=lambda x: x["average"])
                
                print(f"⚡ 最快端点: {fastest_endpoint['average']:.2f}ms")
                print(f"🐌 最慢端点: {slowest_endpoint['average']:.2f}ms")
        
        # 并发性能总结
        if "concurrent_test" in self.results:
            concurrent = self.results["concurrent_test"]
            print(f"🔄 并发处理能力: {concurrent['requests_per_second']:.2f} 请求/秒")
            print(f"📈 并发成功率: {concurrent['success_rate']:.1f}%")
        
        # 内存使用总结
        if "memory_usage" in self.results:
            memory = self.results["memory_usage"]
            print(f"💾 系统内存使用: {memory['total_memory_mb']:.1f}MB")
            print(f"🎯 内存使用评级: {'优秀' if memory['total_memory_mb'] < 500 else '良好' if memory['total_memory_mb'] < 1000 else '需要优化'}")

def main():
    """主函数"""
    runner = PerformanceTestRunner()
    
    print("⚡ Onyx 性能测试套件")
    print("📅 测试时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # 执行性能测试
    api_ok = runner.test_api_response_time()
    concurrent_ok = runner.test_concurrent_requests()
    memory_ok = runner.test_memory_usage()
    
    # 生成报告
    runner.generate_performance_report()
    
    all_ok = api_ok and concurrent_ok and memory_ok
    
    if all_ok:
        print("\n🎉 性能测试全部通过！")
    else:
        print("\n⚠️  部分性能测试未达标，建议优化。")
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
