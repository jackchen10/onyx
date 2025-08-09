#!/usr/bin/env python3
"""
Onyx 故障排除脚本
自动诊断常见问题并提供解决方案
"""

import os
import sys
import subprocess
import requests
import psutil
import time
from pathlib import Path

class TroubleshootRunner:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_dir = self.project_root / "backend"
        self.web_dir = self.project_root / "web"
        self.issues_found = []
        self.solutions = []
    
    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print('='*60)
    
    def add_issue(self, issue: str, solution: str):
        """添加问题和解决方案"""
        self.issues_found.append(issue)
        self.solutions.append(solution)
        print(f"❌ 问题: {issue}")
        print(f"💡 解决方案: {solution}")
    
    def check_environment(self):
        """检查环境配置"""
        self.print_header("环境配置检查")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version.major != 3 or python_version.minor < 11:
            self.add_issue(
                f"Python版本过低: {python_version.major}.{python_version.minor}",
                "请安装Python 3.11或更高版本"
            )
        else:
            print(f"✅ Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        # 检查Node.js版本
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                print(f"✅ Node.js版本: {node_version}")
                
                # 检查版本是否足够新
                version_num = int(node_version.replace('v', '').split('.')[0])
                if version_num < 18:
                    self.add_issue(
                        f"Node.js版本过低: {node_version}",
                        "请安装Node.js 18或更高版本"
                    )
            else:
                self.add_issue("Node.js未安装", "请安装Node.js 18+")
        except FileNotFoundError:
            self.add_issue("Node.js未找到", "请安装Node.js并添加到PATH")
        
        # 检查虚拟环境
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Python虚拟环境已激活")
        else:
            self.add_issue(
                "Python虚拟环境未激活",
                "请激活虚拟环境: cd backend && venv\\Scripts\\activate"
            )
    
    def check_dependencies(self):
        """检查依赖安装"""
        self.print_header("依赖安装检查")
        
        # 检查后端依赖
        requirements_file = self.backend_dir / "requirements.txt"
        if requirements_file.exists():
            print("✅ requirements.txt文件存在")
            
            # 运行依赖验证
            try:
                result = subprocess.run([
                    sys.executable, 
                    str(self.project_root / "tests" / "backend" / "validate_requirements.py")
                ], cwd=str(self.backend_dir), capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    print("✅ 后端依赖验证通过")
                else:
                    self.add_issue(
                        "后端依赖验证失败",
                        "运行: cd backend && pip install -r requirements.txt"
                    )
            except Exception as e:
                self.add_issue(f"依赖验证异常: {e}", "手动检查依赖安装")
        else:
            self.add_issue("requirements.txt文件缺失", "请确保requirements.txt文件存在")
        
        # 检查前端依赖
        package_json = self.web_dir / "package.json"
        node_modules = self.web_dir / "node_modules"
        
        if package_json.exists():
            print("✅ package.json文件存在")
            if node_modules.exists():
                print("✅ node_modules目录存在")
            else:
                self.add_issue(
                    "node_modules目录缺失",
                    "运行: cd web && npm install"
                )
        else:
            self.add_issue("package.json文件缺失", "请确保package.json文件存在")
    
    def check_services(self):
        """检查服务运行状态"""
        self.print_header("服务运行状态检查")
        
        # 检查后端服务
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            if response.status_code == 200:
                print("✅ 后端服务运行正常")
            else:
                self.add_issue(
                    f"后端服务响应异常: HTTP {response.status_code}",
                    "重启后端服务: cd backend && python ../tests/integration/test_server.py"
                )
        except requests.exceptions.ConnectionError:
            self.add_issue(
                "后端服务未运行",
                "启动后端服务: cd backend && python ../tests/integration/test_server.py"
            )
        except Exception as e:
            self.add_issue(f"后端服务检查异常: {e}", "检查后端服务状态")
        
        # 检查前端服务
        try:
            response = requests.get("http://localhost:3000", timeout=10)
            if response.status_code == 200:
                print("✅ 前端服务运行正常")
            else:
                self.add_issue(
                    f"前端服务响应异常: HTTP {response.status_code}",
                    "重启前端服务: cd web && npm run dev"
                )
        except requests.exceptions.ConnectionError:
            self.add_issue(
                "前端服务未运行",
                "启动前端服务: cd web && npm run dev"
            )
        except Exception as e:
            self.add_issue(f"前端服务检查异常: {e}", "检查前端服务状态")
    
    def check_ports(self):
        """检查端口占用情况"""
        self.print_header("端口占用检查")
        
        required_ports = [8080, 3000]
        
        for port in required_ports:
            try:
                result = subprocess.run(
                    f'netstat -ano | findstr :{port}',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                
                if result.stdout.strip():
                    print(f"✅ 端口 {port} 正在使用")
                    # 显示占用进程信息
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if f':{port}' in line:
                            parts = line.split()
                            if len(parts) >= 5:
                                pid = parts[-1]
                                print(f"   进程ID: {pid}")
                else:
                    service_name = "后端服务" if port == 8080 else "前端服务"
                    self.add_issue(
                        f"端口 {port} 未被占用",
                        f"启动{service_name}"
                    )
            except Exception as e:
                print(f"⚠️  端口 {port} 检查异常: {e}")
    
    def check_file_permissions(self):
        """检查文件权限"""
        self.print_header("文件权限检查")
        
        critical_files = [
            self.backend_dir / "requirements.txt",
            self.web_dir / "package.json",
            self.project_root / "tests" / "integration" / "test_server.py"
        ]
        
        for file_path in critical_files:
            if file_path.exists():
                if os.access(file_path, os.R_OK):
                    print(f"✅ {file_path.name} 可读")
                else:
                    self.add_issue(f"{file_path.name} 不可读", "检查文件权限")
            else:
                self.add_issue(f"{file_path.name} 文件缺失", f"请确保文件存在: {file_path}")
    
    def generate_report(self):
        """生成故障排除报告"""
        self.print_header("故障排除报告")
        
        if not self.issues_found:
            print("🎉 未发现任何问题！系统状态良好。")
            return True
        
        print(f"⚠️  发现 {len(self.issues_found)} 个问题:")
        print("\n📋 问题清单:")
        for i, issue in enumerate(self.issues_found, 1):
            print(f"  {i}. {issue}")
        
        print("\n💡 解决方案:")
        for i, solution in enumerate(self.solutions, 1):
            print(f"  {i}. {solution}")
        
        print("\n🔄 建议的修复顺序:")
        print("  1. 首先解决环境和依赖问题")
        print("  2. 然后启动服务")
        print("  3. 最后检查服务通信")
        
        return False

def main():
    """主函数"""
    print("🔧 Onyx 故障排除工具")
    print("📅 检查时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    troubleshooter = TroubleshootRunner()
    
    # 执行所有检查
    troubleshooter.check_environment()
    troubleshooter.check_dependencies()
    troubleshooter.check_ports()
    troubleshooter.check_services()
    troubleshooter.check_file_permissions()
    
    # 生成报告
    all_ok = troubleshooter.generate_report()
    
    return all_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
