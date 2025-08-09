#!/usr/bin/env python3
"""
Onyx 后端依赖验证脚本
验证所有必要的Python包是否正确安装
"""

import sys
import importlib
import subprocess
import pkg_resources
from typing import List, Tuple, Dict

# 关键依赖列表
CRITICAL_PACKAGES = [
    'fastapi',
    'uvicorn',
    'sqlalchemy',
    'alembic',
    'celery',
    'redis',
    'psycopg2',
    'pydantic',
    'langchain',
    'openai',
    'transformers',
    'requests',
    'boto3',
    'google.auth',
    'httpx',
    'aiohttp',
    'asyncpg',
    'bs4',
    'lxml',
    'nltk',
    'pandas',
    'numpy',
    'torch',
    'sentence_transformers',
]

# 可选依赖（不影响核心功能）
OPTIONAL_PACKAGES = [
    'playwright',
    'discord',
    'slack_sdk',
    'jira',
    'dropbox',
    'asana',
    'stripe',
    'sentry_sdk',
    'posthog',
]

def print_header(title: str):
    """打印标题"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'-'*30}")
    print(f" {title}")
    print(f"{'-'*30}")

def check_python_version() -> bool:
    """检查Python版本"""
    print_section("Python版本检查")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    print(f"当前Python版本: {version_str}")
    print(f"Python路径: {sys.executable}")
    
    if version.major != 3:
        print("❌ 错误: 需要Python 3.x版本")
        return False
    
    if version.minor < 11:
        print("❌ 错误: 需要Python 3.11或更高版本")
        print("   当前版本过低，可能导致兼容性问题")
        return False
    
    print("✅ Python版本检查通过")
    return True

def check_virtual_environment():
    """检查是否在虚拟环境中"""
    print_section("虚拟环境检查")
    
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        print("✅ 运行在虚拟环境中")
        print(f"   虚拟环境路径: {sys.prefix}")
    else:
        print("⚠️  警告: 未检测到虚拟环境")
        print("   建议在虚拟环境中运行以避免包冲突")
    
    return in_venv

def check_package(package_name: str) -> Tuple[bool, str]:
    """检查单个包是否可以导入"""
    try:
        module = importlib.import_module(package_name)
        
        # 尝试获取版本信息
        version = "未知版本"
        if hasattr(module, '__version__'):
            version = module.__version__
        elif hasattr(module, 'VERSION'):
            version = str(module.VERSION)
        elif hasattr(module, 'version'):
            version = str(module.version)
        
        return True, version
    except ImportError as e:
        return False, str(e)

def check_packages(packages: List[str], package_type: str) -> List[str]:
    """检查包列表"""
    print_section(f"{package_type}依赖检查")
    
    failed_packages = []
    success_count = 0
    
    for package in packages:
        success, info = check_package(package)
        if success:
            print(f"✅ {package:<25} ({info})")
            success_count += 1
        else:
            print(f"❌ {package:<25} - {info}")
            failed_packages.append(package)
    
    print(f"\n{package_type}依赖统计:")
    print(f"  成功: {success_count}/{len(packages)}")
    print(f"  失败: {len(failed_packages)}/{len(packages)}")
    
    return failed_packages

def get_installed_packages() -> Dict[str, str]:
    """获取已安装的包列表"""
    try:
        installed_packages = {}
        for dist in pkg_resources.working_set:
            installed_packages[dist.project_name.lower()] = dist.version
        return installed_packages
    except Exception as e:
        print(f"❌ 无法获取已安装包列表: {e}")
        return {}

def check_pip_list():
    """显示pip安装的包信息"""
    print_section("已安装包统计")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list'], 
            capture_output=True, 
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            # 去掉标题行
            package_lines = [line for line in lines if not line.startswith('-') and line.strip()]
            package_count = len(package_lines) - 1  # 减去标题行
            
            print(f"✅ 总计安装包数量: {package_count}")
            
            # 显示一些关键包的版本
            installed_packages = get_installed_packages()
            key_packages = ['fastapi', 'uvicorn', 'sqlalchemy', 'langchain', 'openai']
            
            print("\n关键包版本信息:")
            for pkg in key_packages:
                if pkg in installed_packages:
                    print(f"  {pkg}: {installed_packages[pkg]}")
            
            return True
        else:
            print(f"❌ pip list 执行失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ pip list 执行超时")
        return False
    except Exception as e:
        print(f"❌ 无法执行pip list: {e}")
        return False

def check_import_time():
    """检查关键包的导入时间"""
    print_section("导入性能测试")
    
    import time
    test_packages = ['fastapi', 'sqlalchemy', 'langchain', 'transformers']
    
    for package in test_packages:
        try:
            start_time = time.time()
            importlib.import_module(package)
            import_time = time.time() - start_time
            
            if import_time < 1.0:
                status = "✅"
            elif import_time < 3.0:
                status = "⚠️ "
            else:
                status = "❌"
            
            print(f"{status} {package:<20} 导入时间: {import_time:.2f}s")
            
        except ImportError:
            print(f"❌ {package:<20} 无法导入")

def run_basic_functionality_test():
    """运行基本功能测试"""
    print_section("基本功能测试")
    
    tests = [
        ("FastAPI应用创建", test_fastapi),
        ("SQLAlchemy连接", test_sqlalchemy),
        ("Redis连接测试", test_redis),
        ("HTTP请求测试", test_requests),
        ("JSON处理测试", test_json),
    ]
    
    passed_tests = 0
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name}")
                passed_tests += 1
            else:
                print(f"❌ {test_name}")
        except Exception as e:
            print(f"❌ {test_name}: {e}")
    
    print(f"\n功能测试结果: {passed_tests}/{len(tests)} 通过")
    return passed_tests == len(tests)

def test_fastapi() -> bool:
    """测试FastAPI基本功能"""
    try:
        from fastapi import FastAPI
        app = FastAPI()
        return True
    except Exception:
        return False

def test_sqlalchemy() -> bool:
    """测试SQLAlchemy基本功能"""
    try:
        from sqlalchemy import create_engine, text
        # 创建内存数据库进行测试
        engine = create_engine("sqlite:///:memory:")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.fetchone()[0] == 1
    except Exception:
        return False

def test_redis() -> bool:
    """测试Redis客户端"""
    try:
        import redis
        # 只测试客户端创建，不实际连接
        client = redis.Redis()
        return True
    except Exception:
        return False

def test_requests() -> bool:
    """测试HTTP请求库"""
    try:
        import requests
        import httpx
        return True
    except Exception:
        return False

def test_json() -> bool:
    """测试JSON处理"""
    try:
        import json
        from pydantic import BaseModel
        
        class TestModel(BaseModel):
            name: str
            value: int
        
        model = TestModel(name="test", value=123)
        json_str = model.model_dump_json()
        parsed = json.loads(json_str)
        return parsed["name"] == "test" and parsed["value"] == 123
    except Exception:
        return False

def generate_installation_report(failed_critical: List[str], failed_optional: List[str]):
    """生成安装报告"""
    print_section("安装建议")
    
    if failed_critical:
        print("❌ 关键依赖缺失，需要立即安装:")
        for package in failed_critical:
            print(f"   pip install {package}")
        print("\n或者重新安装所有依赖:")
        print("   pip install -r requirements/default.txt")
    
    if failed_optional:
        print("\n⚠️  可选依赖缺失（不影响核心功能）:")
        for package in failed_optional:
            print(f"   pip install {package}")
    
    if not failed_critical and not failed_optional:
        print("✅ 所有依赖都已正确安装!")

def main():
    """主函数"""
    print_header("Onyx 后端依赖验证工具")
    
    # 检查Python版本
    if not check_python_version():
        print("\n❌ Python版本不符合要求，请升级到Python 3.11+")
        sys.exit(1)
    
    # 检查虚拟环境
    check_virtual_environment()
    
    # 检查已安装包统计
    check_pip_list()
    
    # 检查关键依赖
    failed_critical = check_packages(CRITICAL_PACKAGES, "关键")
    
    # 检查可选依赖
    failed_optional = check_packages(OPTIONAL_PACKAGES, "可选")
    
    # 导入性能测试
    if not failed_critical:
        check_import_time()
        
        # 基本功能测试
        run_basic_functionality_test()
    
    # 生成报告
    generate_installation_report(failed_critical, failed_optional)
    
    # 总结
    print_header("验证结果总结")
    
    if failed_critical:
        print(f"❌ 验证失败: {len(failed_critical)} 个关键依赖缺失")
        print("请按照上述建议安装缺失的依赖包")
        sys.exit(1)
    else:
        print("✅ 验证成功: 所有关键依赖都已正确安装")
        print("Onyx后端环境准备就绪!")
        
        print("\n下一步操作:")
        print("1. 配置环境变量 (.env文件)")
        print("2. 启动数据库服务 (PostgreSQL, Redis)")
        print("3. 运行数据库迁移: alembic upgrade head")
        print("4. 启动后端服务: python -m onyx.main")

if __name__ == "__main__":
    main()
