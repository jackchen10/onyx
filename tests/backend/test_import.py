#!/usr/bin/env python3
"""测试Onyx后端导入"""

import os
import sys
from pathlib import Path

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# 设置编码环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'
os.environ['LC_ALL'] = 'en_US.UTF-8'
os.environ['LANG'] = 'en_US.UTF-8'

# 设置Python默认编码
import locale
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except:
        pass

try:
    print("正在测试FastAPI应用导入...")
    from onyx.main import app
    print("✅ FastAPI应用导入成功")
    print(f"应用类型: {type(app)}")
except Exception as e:
    print(f"❌ FastAPI应用导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("✅ 后端核心模块导入测试通过！")
