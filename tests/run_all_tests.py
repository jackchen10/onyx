#!/usr/bin/env python3
"""
Onyx 完整测试运行器
运行所有测试脚本并生成测试报告
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_command(command: str, cwd: str = None, timeout: int = 60) -> tuple[bool, str, str]:
    """运行命令并返回结果"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='ignore'  # 忽略编码错误
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"命令超时 ({timeout}秒)"
    except Exception as e:
        return False, "", str(e)

def print_section(title: str):
    """打印章节标题"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def print_result(test_name: str, success: bool, details: str = ""):
    """打印测试结果"""
    status = "✅ 成功" if success else "❌ 失败"
    print(f"{status} {test_name}")
    if details and not success:
        print(f"   详情: {details}")

def main():
    """主函数"""
    print("🚀 Onyx 完整测试套件")
    print("📅 测试时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"
    web_dir = project_root / "web"
    
    test_results = []
    
    # ===== 后端测试 =====
    print_section("后端测试")
    
    # 1. 依赖验证
    print("🔍 验证后端依赖包...")
    success, stdout, stderr = run_command(
        f"python {project_root}/tests/backend/validate_requirements.py",
        cwd=str(backend_dir)
    )
    print_result("依赖包验证", success, stderr)
    test_results.append(("后端依赖验证", success))
    
    # 2. 模块导入测试
    print("\n📦 测试模块导入...")
    success, stdout, stderr = run_command(
        f"python {project_root}/tests/backend/test_import.py",
        cwd=str(backend_dir)
    )
    print_result("模块导入测试", success, stderr)
    test_results.append(("后端模块导入", success))
    
    # 3. 后端安装验证
    print("\n🔧 验证后端安装...")
    success, stdout, stderr = run_command(
        f"python {project_root}/tests/backend/verify_installation.py",
        cwd=str(backend_dir)
    )
    print_result("后端安装验证", success, stderr)
    test_results.append(("后端安装验证", success))
    
    # ===== 前端测试 =====
    print_section("前端测试")
    
    # 4. 前端安装验证
    print("🌐 验证前端安装...")
    success, stdout, stderr = run_command(
        f"node {project_root}/tests/frontend/verify_installation.js",
        cwd=str(web_dir)
    )
    print_result("前端安装验证", success, stderr)
    test_results.append(("前端安装验证", success))
    
    # 5. 前端构建测试
    print("\n🏗️ 测试前端构建...")
    success, stdout, stderr = run_command(
        "npm run build",
        cwd=str(web_dir),
        timeout=300
    )
    print_result("前端构建测试", success, stderr)
    test_results.append(("前端构建测试", success))
    
    # ===== 扩展测试 =====
    print_section("扩展测试")

    # 6. 健康检查
    print("🏥 运行系统健康检查...")
    success, stdout, stderr = run_command(
        f"python {project_root}/tests/health_check.py",
        cwd=str(project_root)
    )
    print_result("系统健康检查", success, stderr)
    test_results.append(("系统健康检查", success))

    # 7. 端到端测试
    print("\n🔄 运行端到端测试...")
    success, stdout, stderr = run_command(
        f"python {project_root}/tests/e2e_test.py",
        cwd=str(project_root)
    )
    print_result("端到端功能测试", success, stderr)
    test_results.append(("端到端功能测试", success))

    # 8. 性能测试
    print("\n⚡ 运行性能测试...")
    success, stdout, stderr = run_command(
        f"python {project_root}/tests/performance_test.py",
        cwd=str(project_root)
    )
    print_result("性能基准测试", success, stderr)
    test_results.append(("性能基准测试", success))

    # ===== 测试总结 =====
    print_section("完整测试总结")

    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)

    print(f"📊 测试结果: {passed}/{total} 通过")
    print(f"📈 成功率: {passed/total*100:.1f}%")

    print("\n📋 详细结果:")
    for test_name, success in test_results:
        status = "✅" if success else "❌"
        print(f"  {status} {test_name}")

    # 生成测试等级
    if passed == total:
        print("\n🎉 所有测试通过！系统状态：优秀")
        grade = "优秀"
    elif passed >= total * 0.8:
        print(f"\n✅ 大部分测试通过！系统状态：良好")
        grade = "良好"
    elif passed >= total * 0.6:
        print(f"\n⚠️  部分测试失败！系统状态：需要改进")
        grade = "需要改进"
    else:
        print(f"\n❌ 多个测试失败！系统状态：需要修复")
        grade = "需要修复"

    # 保存测试报告
    report_file = project_root / "tests" / "test_report.json"
    import json
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tests": total,
        "passed_tests": passed,
        "success_rate": passed/total*100,
        "grade": grade,
        "results": [{"test": name, "success": success} for name, success in test_results]
    }

    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        print(f"\n📄 测试报告已保存: {report_file}")
    except Exception as e:
        print(f"\n⚠️  测试报告保存失败: {e}")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
