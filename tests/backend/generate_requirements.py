#!/usr/bin/env python3
"""
生成完整的requirements.txt文件
"""

import subprocess
import sys

def main():
    """生成requirements文件"""
    try:
        # 获取所有已安装的包
        result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--format=freeze'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            # 写入文件
            with open('requirements_complete_new.txt', 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            
            # 统计包数量
            lines = result.stdout.strip().split('\n')
            packages = [line.split('==')[0] for line in lines if line.strip() and '==' in line]
            
            print(f"✅ 成功生成 requirements_complete_new.txt")
            print(f"📦 包含 {len(packages)} 个包")
            
            return True
        else:
            print(f"❌ pip list 执行失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return False

if __name__ == "__main__":
    main()
