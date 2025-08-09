#!/usr/bin/env python3
"""
验证requirements.txt文件的完整性
检查所有包是否可以正常导入
"""

import sys
import importlib
import pkg_resources
from typing import List, Tuple

def read_requirements(file_path: str = None) -> List[str]:
    """读取requirements.txt文件并提取包名"""
    packages = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '==' in line:
                    package_name = line.split('==')[0]
                    packages.append(package_name)
    except FileNotFoundError:
        print(f"❌ 文件未找到: {file_path}")
        return []
    return packages

def check_package_installation(packages: List[str]) -> Tuple[List[str], List[str]]:
    """检查包是否已安装"""
    installed = []
    missing = []
    
    for package in packages:
        try:
            pkg_resources.get_distribution(package)
            installed.append(package)
        except pkg_resources.DistributionNotFound:
            missing.append(package)
    
    return installed, missing

def test_critical_imports() -> List[str]:
    """测试关键模块的导入"""
    critical_modules = [
        'fastapi',
        'sqlalchemy', 
        'redis',
        'openai',
        'langchain',
        'transformers',
        'beautifulsoup4',
        'pandas',
        'numpy'
    ]
    
    failed_imports = []
    for module in critical_modules:
        try:
            if module == 'beautifulsoup4':
                importlib.import_module('bs4')  # beautifulsoup4导入为bs4
            else:
                importlib.import_module(module)
            print(f"✅ {module} 导入成功")
        except ImportError as e:
            print(f"❌ {module} 导入失败: {e}")
            failed_imports.append(module)
    
    return failed_imports

def main():
    """主函数"""
    print("🔍 验证requirements.txt文件...")

    # 获取requirements.txt路径
    from pathlib import Path
    backend_dir = Path(__file__).parent.parent.parent / "backend"
    requirements_path = backend_dir / "requirements.txt"

    # 读取requirements.txt
    packages = read_requirements(str(requirements_path))
    print(f"📦 找到 {len(packages)} 个包")
    
    # 检查包安装状态
    installed, missing = check_package_installation(packages)
    
    print(f"\n✅ 已安装: {len(installed)} 个包")
    print(f"❌ 缺失: {len(missing)} 个包")
    
    if missing:
        print("\n缺失的包:")
        for pkg in missing:
            print(f"  - {pkg}")
    
    # 测试关键模块导入
    print("\n🧪 测试关键模块导入...")
    failed_imports = test_critical_imports()
    
    if not missing and not failed_imports:
        print("\n🎉 所有依赖验证成功！")
        return True
    else:
        print(f"\n⚠️  验证完成，发现 {len(missing)} 个缺失包，{len(failed_imports)} 个导入失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
