# Onyx 后端依赖清单和安装指南

## 系统要求

### Python 版本
- **Python 3.11** (推荐)
- 最低支持版本：Python 3.11+

### 操作系统支持
- Windows 10/11
- macOS
- Linux (Ubuntu, CentOS, etc.)

## 依赖分类

### 1. 核心运行时依赖 (default.txt)
```
aioboto3==14.0.0
aiohttp==3.11.16
alembic==1.10.4
asyncpg==0.30.0
atlassian-python-api==3.41.16
beautifulsoup4==4.12.3
boto3==1.36.23
celery==5.5.1
chardet==5.2.0
chonkie==1.0.10
dask==2023.8.1
ddtrace==3.10.0
discord.py==2.4.0
distributed==2023.8.1
fastapi==0.115.12
fastapi-users==14.0.1
fastapi-users-db-sqlalchemy==5.0.0
filelock==3.15.4
google-api-python-client==2.86.0
google-cloud-aiplatform==1.58.0
google-auth-httplib2==0.1.0
google-auth-oauthlib==1.0.0
httpcore==1.0.5
httpx[http2]==0.27.0
httpx-oauth==0.15.1
huggingface-hub==0.29.0
inflection==0.5.1
jira==3.5.1
jsonref==1.1.0
trafilatura==1.12.2
langchain==0.3.23
langchain-community==0.3.21
langchain-core==0.3.51
langchain-openai==0.2.9
langchain-text-splitters==0.3.8
langchainhub==0.1.21
langgraph==0.2.72
langgraph-checkpoint==2.0.13
langgraph-sdk==0.1.44
litellm==1.72.2
lxml==5.3.0
lxml_html_clean==0.2.2
Mako==1.2.4
msal==1.28.0
nltk==3.9.1
Office365-REST-Python-Client==2.5.9
oauthlib==3.2.2
openai==1.75.0
openpyxl==3.0.10
passlib==1.7.4
playwright==1.41.2
psutil==5.9.5
psycopg2-binary==2.9.9
puremagic==1.28
pyairtable==3.0.1
pycryptodome==3.19.1
pydantic==2.8.2
PyGithub==2.5.0
python-dateutil==2.8.2
python-gitlab==5.6.0
python-pptx==0.6.23
pypdf==5.4.0
pytest-mock==3.12.0
pytest-playwright==0.7.0
python-docx==1.1.2
python-dotenv==1.0.0
python-multipart==0.0.20
pywikibot==9.0.0
redis==5.0.8
requests==2.32.2
requests-oauthlib==1.3.1
retry==0.9.2
rfc3986==1.5.0
setfit==1.1.1
simple-salesforce==1.12.6
slack-sdk==3.20.2
SQLAlchemy[mypy]==2.0.15
starlette==0.46.1
supervisor==4.2.5
RapidFuzz==3.13.0
tiktoken==0.7.0
timeago==1.0.16
transformers==4.49.0
unstructured==0.15.1
unstructured-client==0.25.4
uvicorn==0.21.1
zulip==0.8.2
hubspot-api-client==8.1.0
asana==5.0.8
dropbox==11.36.2
boto3-stubs[s3]==1.34.133
shapely==2.0.6
stripe==10.12.0
urllib3==2.2.3
mistune==0.8.4
sentry-sdk==2.14.0
prometheus_client==0.21.0
fastapi-limiter==0.1.6
prometheus_fastapi_instrumentator==7.1.0
sendgrid==6.11.0
```

### 2. 开发依赖 (dev.txt)
```
black==25.1.0
boto3-stubs[s3]==1.34.133
celery-types==0.19.0
cohere==5.6.1
faker==37.1.0
lxml==5.3.0
lxml_html_clean==0.2.2
mypy-extensions==1.0.0
mypy==1.13.0
pandas-stubs==2.2.3.241009
pandas==2.2.3
posthog==3.7.4
pre-commit==3.2.2
pytest-asyncio==0.22.0
pytest-dotenv==0.5.2
pytest-xdist==3.6.1
pytest==8.3.5
reorder-python-imports-black==3.14.0
ruff==0.12.0
sentence-transformers==4.0.2
trafilatura==1.12.2
types-beautifulsoup4==4.12.0.3
types-html5lib==1.1.11.13
types-oauthlib==3.2.0.9
types-passlib==1.7.7.20240106
types-Pillow==10.2.0.20240822
types-psutil==5.9.5.17
types-psycopg2==2.9.21.10
types-python-dateutil==2.8.19.13
types-pytz==2023.3.1.1
types-PyYAML==6.0.12.11
types-regex==2023.3.23.1
types-requests==2.32.0.20250328
types-retry==0.9.9.3
types-setuptools==68.0.0.3
types-urllib3==1.26.25.11
voyageai==0.2.3
```

### 3. 模型服务器依赖 (model_server.txt)
```
accelerate==1.6.0
einops==0.8.1
cohere==5.6.1
fastapi==0.115.12
google-cloud-aiplatform==1.58.0
numpy==1.26.4
openai==1.75.0
pydantic==2.8.2
retry==0.9.2
safetensors==0.5.3
sentence-transformers==4.0.2
sentencepiece==0.2.0
setfit==1.1.1
torch==2.6.0
transformers==4.49.0
uvicorn==0.21.1
voyageai==0.2.3
litellm==1.72.2
sentry-sdk[fastapi,celery,starlette]==2.14.0
aioboto3==14.0.0
prometheus_fastapi_instrumentator==7.1.0
```

### 4. 企业版依赖 (ee.txt)
```
cohere==5.6.1
posthog==3.7.4
python3-saml==1.15.0
xmlsec==1.3.14
```

## Windows 安装指南

### 步骤 1: 安装 Python 3.11

1. 从 [Python官网](https://www.python.org/downloads/) 下载 Python 3.11
2. 安装时勾选 "Add Python to PATH"
3. 验证安装：
```cmd
python --version
pip --version
```

### 步骤 2: 创建虚拟环境

```cmd
# 进入项目目录
cd F:\code\onyx\backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 验证虚拟环境
where python
```

### 步骤 3: 升级 pip

```cmd
python -m pip install --upgrade pip
```

### 步骤 4: 安装依赖

#### 基础安装（仅运行时依赖）
```cmd
pip install --retries 5 --timeout 30 -r requirements/default.txt
```

#### 开发环境安装（包含开发工具）
```cmd
pip install --retries 5 --timeout 30 -r requirements/default.txt
pip install --retries 5 --timeout 30 -r requirements/dev.txt
```

#### 完整安装（包含模型服务器）
```cmd
pip install --retries 5 --timeout 30 -r requirements/default.txt
pip install --retries 5 --timeout 30 -r requirements/dev.txt
pip install --retries 5 --timeout 30 -r requirements/model_server.txt
```

#### 企业版安装
```cmd
pip install --retries 5 --timeout 30 -r requirements/default.txt
pip install --retries 5 --timeout 30 -r requirements/ee.txt
```

### 步骤 5: 验证安装

创建验证脚本 `verify_installation.py`：

```python
#!/usr/bin/env python3
"""验证 Onyx 后端依赖安装"""

import sys
import importlib
import subprocess

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
]

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major != 3 or version.minor < 11:
        print("❌ 错误: 需要Python 3.11或更高版本")
        return False
    
    print("✅ Python版本检查通过")
    return True

def check_package(package_name):
    """检查单个包是否可以导入"""
    try:
        importlib.import_module(package_name)
        print(f"✅ {package_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name}: {e}")
        return False

def check_packages():
    """检查所有关键包"""
    print("\n检查关键依赖包...")
    failed_packages = []
    
    for package in CRITICAL_PACKAGES:
        if not check_package(package):
            failed_packages.append(package)
    
    return failed_packages

def check_pip_list():
    """显示已安装的包"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                              capture_output=True, text=True)
        print(f"\n已安装包数量: {len(result.stdout.splitlines()) - 2}")
        return True
    except Exception as e:
        print(f"❌ 无法获取包列表: {e}")
        return False

def main():
    print("=== Onyx 后端依赖验证 ===\n")
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查包安装
    failed_packages = check_packages()
    
    # 显示包列表
    check_pip_list()
    
    # 总结
    print("\n=== 验证结果 ===")
    if failed_packages:
        print(f"❌ 失败: {len(failed_packages)} 个关键包未正确安装")
        print("失败的包:", ", ".join(failed_packages))
        print("\n请重新安装失败的包:")
        for package in failed_packages:
            print(f"pip install {package}")
        sys.exit(1)
    else:
        print("✅ 所有关键依赖包安装成功!")
        print("后端环境准备就绪!")

if __name__ == "__main__":
    main()
```

运行验证：
```cmd
python verify_installation.py
```

## 常见问题解决

### 1. psycopg2 安装失败
```cmd
# Windows 解决方案
pip install psycopg2-binary
```

### 2. lxml 安装失败
```cmd
# 安装 Microsoft C++ Build Tools
# 或使用预编译版本
pip install --only-binary=lxml lxml
```

### 3. torch 安装慢
```cmd
# 使用清华镜像
pip install torch -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 网络超时
```cmd
# 增加超时时间和重试次数
pip install --retries 10 --timeout 60 -r requirements/default.txt
```

## 环境变量配置

创建 `.env` 文件：
```env
# 数据库配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=onyx
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379

# API配置
API_HOST=0.0.0.0
API_PORT=8080

# 日志级别
LOG_LEVEL=INFO
```

## 下一步

安装完成后，您可以：
1. 启动后端服务：`python -m onyx.main`
2. 运行测试：`pytest`
3. 查看API文档：访问 `http://localhost:8080/docs`
