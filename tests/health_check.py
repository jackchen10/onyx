#!/usr/bin/env python3
"""
Onyx 系统健康检查脚本
检查所有服务的运行状态和健康状况
"""

import requests
import time
import sys
import subprocess
import json
from typing import Dict, List, Tuple

class HealthChecker:
    def __init__(self):
        self.backend_url = "http://localhost:8080"
        self.frontend_url = "http://localhost:3000"
        self.results = []
    
    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{'='*60}")
        print(f"🏥 {title}")
        print('='*60)
    
    def print_result(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """打印测试结果"""
        status = "✅ 健康" if success else "❌ 异常"
        time_info = f" ({response_time:.2f}ms)" if response_time > 0 else ""
        print(f"{status} {test_name}{time_info}")
        if details:
            print(f"   详情: {details}")
        
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response_time": response_time
        })
    
    def check_port_availability(self, port: int, service_name: str) -> bool:
        """检查端口是否被占用"""
        try:
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout.strip():
                return True
            return False
        except Exception:
            return False
    
    def check_backend_health(self) -> bool:
        """检查后端服务健康状态"""
        self.print_header("后端服务健康检查")
        
        # 检查端口
        port_available = self.check_port_availability(8080, "后端服务")
        self.print_result("端口8080占用检查", port_available, 
                         "服务正在运行" if port_available else "端口未被占用，服务可能未启动")
        
        if not port_available:
            return False
        
        # 检查基础健康端点
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                self.print_result("健康检查端点", True, f"状态: {data.get('status', 'unknown')}", response_time)
            else:
                self.print_result("健康检查端点", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result("健康检查端点", False, str(e))
            return False
        
        # 检查API端点
        api_endpoints = [
            "/settings",
            "/auth/type", 
            "/me",
            "/persona",
            "/llm/provider"
        ]
        
        for endpoint in api_endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                response_time = (time.time() - start_time) * 1000
                
                success = response.status_code == 200
                details = f"HTTP {response.status_code}" if not success else "正常响应"
                self.print_result(f"API端点 {endpoint}", success, details, response_time)
            except Exception as e:
                self.print_result(f"API端点 {endpoint}", False, str(e))
        
        return True
    
    def check_frontend_health(self) -> bool:
        """检查前端服务健康状态"""
        self.print_header("前端服务健康检查")
        
        # 检查端口
        port_available = self.check_port_availability(3000, "前端服务")
        self.print_result("端口3000占用检查", port_available,
                         "服务正在运行" if port_available else "端口未被占用，服务可能未启动")
        
        if not port_available:
            return False
        
        # 检查前端页面
        try:
            start_time = time.time()
            response = requests.get(f"{self.frontend_url}", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                # 检查页面内容
                content = response.text
                if "Onyx" in content and "html" in content.lower():
                    self.print_result("前端页面加载", True, "页面正常加载", response_time)
                else:
                    self.print_result("前端页面加载", False, "页面内容异常")
                    return False
            else:
                self.print_result("前端页面加载", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result("前端页面加载", False, str(e))
            return False
        
        return True
    
    def check_integration(self) -> bool:
        """检查前后端集成"""
        self.print_header("前后端集成检查")
        
        # 测试CORS
        try:
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET'
            }
            response = requests.options(f"{self.backend_url}/health", headers=headers, timeout=5)
            cors_ok = 'access-control-allow-origin' in response.headers
            self.print_result("CORS配置", cors_ok, "跨域请求支持正常" if cors_ok else "CORS配置可能有问题")
        except Exception as e:
            self.print_result("CORS配置", False, str(e))
        
        return True
    
    def generate_report(self):
        """生成健康检查报告"""
        self.print_header("健康检查报告")
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r['success'])
        
        print(f"📊 总测试数: {total_tests}")
        print(f"✅ 通过测试: {passed_tests}")
        print(f"❌ 失败测试: {total_tests - passed_tests}")
        print(f"📈 成功率: {passed_tests/total_tests*100:.1f}%")
        
        # 性能统计
        response_times = [r['response_time'] for r in self.results if r['response_time'] > 0]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            print(f"⚡ 平均响应时间: {avg_time:.2f}ms")
            print(f"🐌 最慢响应时间: {max_time:.2f}ms")
        
        # 失败的测试
        failed_tests = [r for r in self.results if not r['success']]
        if failed_tests:
            print(f"\n❌ 失败的测试:")
            for test in failed_tests:
                print(f"   - {test['test']}: {test['details']}")
        
        return passed_tests == total_tests

def main():
    """主函数"""
    print("🏥 Onyx 系统健康检查")
    print("📅 检查时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    checker = HealthChecker()
    
    # 执行所有健康检查
    backend_ok = checker.check_backend_health()
    frontend_ok = checker.check_frontend_health()
    integration_ok = checker.check_integration()
    
    # 生成报告
    all_healthy = checker.generate_report()
    
    if all_healthy:
        print("\n🎉 系统完全健康！")
        return True
    else:
        print("\n⚠️  系统存在问题，请检查失败的测试项。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
