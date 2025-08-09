# Onyx Windows 安装指南

## 概述

本指南提供了在 Windows 10/11 环境下安装和配置 Onyx 项目的完整步骤。我们已经为您准备了详细的依赖清单、验证脚本和自动化安装工具。

## 文件结构

```
onyx/
├── install_onyx_windows.bat          # Windows 自动安装脚本
├── backend/
│   ├── 依赖清单和安装指南.md         # 后端依赖详细说明
│   └── verify_installation.py        # 后端依赖验证脚本
├── web/
│   ├── 依赖清单和安装指南.md         # 前端依赖详细说明
│   └── verify_installation.js        # 前端依赖验证脚本
└── docs/
    ├── 技术架构报告.md               # 技术架构分析
    ├── CE与EE功能对比分析.md         # 版本功能对比
    └── Windows安装指南.md            # 本文档
```

## 快速开始

### 方法一：自动安装（推荐）

1. **以管理员身份运行命令提示符**
2. **进入项目目录**：
   ```cmd
   cd F:\code\onyx
   ```
3. **运行自动安装脚本**：
   ```cmd
   install_onyx_windows.bat
   ```

脚本将自动完成以下操作：
- ✅ 检查系统环境（Python 3.11+, Node.js 18.18.0+）
- ✅ 创建 Python 虚拟环境
- ✅ 安装所有后端依赖
- ✅ 安装所有前端依赖
- ✅ 验证安装结果
- ✅ 创建配置文件

### 方法二：手动安装

如果自动安装遇到问题，可以按照以下步骤手动安装：

#### 1. 系统要求检查

**Python 要求**：
- Python 3.11 或更高版本
- pip 最新版本

**Node.js 要求**：
- Node.js 18.18.0 或更高版本（推荐 20.x LTS）
- npm 8.0.0 或更高版本

#### 2. 后端安装

```cmd
# 进入后端目录
cd F:\code\onyx\backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 升级 pip
python -m pip install --upgrade pip

# 安装依赖
pip install --retries 5 --timeout 60 -r requirements/default.txt
pip install --retries 5 --timeout 60 -r requirements/dev.txt

# 验证安装
python verify_installation.py
```

#### 3. 前端安装

```cmd
# 进入前端目录
cd F:\code\onyx\web

# 配置 npm 镜像（可选，提高下载速度）
npm config set registry https://registry.npmmirror.com

# 安装依赖
npm install

# 验证安装
node verify_installation.js
```

## 依赖详情

### 后端依赖（Python）

**核心框架**：
- FastAPI 0.115.12 - Web 框架
- Uvicorn 0.21.1 - ASGI 服务器
- SQLAlchemy 2.0.15 - ORM
- Alembic 1.10.4 - 数据库迁移

**AI/ML 库**：
- LangChain 0.3.23 - AI 应用框架
- OpenAI 1.75.0 - OpenAI API 客户端
- Transformers 4.49.0 - Hugging Face 模型
- Sentence-Transformers 4.0.2 - 句子嵌入

**数据库和缓存**：
- psycopg2-binary 2.9.9 - PostgreSQL 驱动
- Redis 5.0.8 - Redis 客户端
- AsyncPG 0.30.0 - 异步 PostgreSQL 驱动

**连接器**：
- Google API 客户端 - Google 服务集成
- Slack SDK 3.20.2 - Slack 集成
- Jira 3.5.1 - Jira 集成
- Office365 REST 客户端 - Office 365 集成

### 前端依赖（Node.js）

**核心框架**：
- Next.js 15.2.4 - React 框架
- React 18.3.1 - UI 库
- TypeScript 5.0.3 - 类型系统

**UI 组件**：
- Radix UI - 无障碍组件库
- Tailwind CSS 3.3.1 - 样式框架
- Headless UI - 无样式组件

**状态管理**：
- SWR 2.1.5 - 数据获取和缓存
- Formik 2.2.9 - 表单处理

**工具库**：
- Lodash 4.17.21 - 工具函数
- Date-fns 3.6.0 - 日期处理
- React Markdown 9.0.1 - Markdown 渲染

## 验证脚本说明

### 后端验证脚本 (`backend/verify_installation.py`)

功能：
- ✅ Python 版本检查
- ✅ 虚拟环境检测
- ✅ 关键依赖包验证
- ✅ 导入性能测试
- ✅ 基本功能测试

运行方式：
```cmd
cd backend
venv\Scripts\activate
python verify_installation.py
```

### 前端验证脚本 (`web/verify_installation.js`)

功能：
- ✅ Node.js 版本检查
- ✅ npm 版本检查
- ✅ package.json 验证
- ✅ node_modules 检查
- ✅ 关键依赖包验证
- ✅ 配置文件检查

运行方式：
```cmd
cd web
node verify_installation.js
```

## 常见问题解决

### 1. Python 相关问题

**问题**：`psycopg2` 安装失败
```cmd
# 解决方案：使用二进制版本
pip install psycopg2-binary
```

**问题**：`lxml` 安装失败
```cmd
# 解决方案：安装 Microsoft C++ Build Tools
# 或使用预编译版本
pip install --only-binary=lxml lxml
```

**问题**：虚拟环境激活失败
```cmd
# 解决方案：检查执行策略
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Node.js 相关问题

**问题**：`sharp` 安装失败
```cmd
# 解决方案：指定平台
npm install --platform=win32 --arch=x64 sharp
```

**问题**：权限错误
```cmd
# 解决方案：配置 npm 全局目录
npm config set prefix %APPDATA%\npm
```

**问题**：网络超时
```cmd
# 解决方案：增加超时时间
npm config set timeout 60000
npm install
```

### 3. 内存不足问题

```cmd
# 增加 Node.js 内存限制
set NODE_OPTIONS=--max-old-space-size=4096
npm install
```

## 环境配置

### 后端环境变量 (`.env`)

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

# 认证配置
AUTH_TYPE=basic
REQUIRE_EMAIL_VERIFICATION=false

# 禁用遥测
DISABLE_TELEMETRY=true
```

### 前端环境变量 (`.env.local`)

```env
# API配置
INTERNAL_URL=http://localhost:8080
NEXT_PUBLIC_API_URL=http://localhost:8080

# 功能开关
NEXT_PUBLIC_DISABLE_STREAMING=false
NEXT_PUBLIC_NEW_CHAT_DIRECTS_TO_SAME_PERSONA=false

# 开发配置
NEXT_TELEMETRY_DISABLED=1
```

## 启动服务

### 1. 启动数据库服务

**选项 A：使用 Docker Compose（推荐）**
```cmd
cd deployment/docker_compose
docker-compose -f docker-compose.dev.yml up -d relational_db cache
```

**选项 B：本地安装**
- 安装 PostgreSQL 15+
- 安装 Redis 7+
- 创建数据库：`onyx`

### 2. 初始化数据库

```cmd
cd backend
venv\Scripts\activate
alembic upgrade head
```

### 3. 启动后端服务

```cmd
cd backend
venv\Scripts\activate
python -m onyx.main
```

后端服务将在 `http://localhost:8080` 启动

### 4. 启动前端服务

```cmd
cd web
npm run dev
```

前端服务将在 `http://localhost:3000` 启动

## 验证安装

1. **访问前端应用**：http://localhost:3000
2. **访问 API 文档**：http://localhost:8080/docs
3. **检查服务状态**：http://localhost:8080/health

## 下一步

安装完成后，您可以：

1. **配置连接器**：
   - Gmail 连接器
   - Confluence 连接器
   - Jira 连接器

2. **设置认证**：
   - 基本认证
   - OIDC/SAML（企业版）

3. **自定义配置**：
   - LLM 提供商
   - 搜索设置
   - UI 主题

4. **开发和测试**：
   - 运行测试套件
   - 添加自定义连接器
   - 扩展功能

## 技术支持

如果遇到问题：

1. **查看日志**：检查终端输出和错误信息
2. **运行验证脚本**：确认依赖安装正确
3. **查看文档**：参考详细的依赖清单和安装指南
4. **社区支持**：访问 Onyx GitHub 仓库获取帮助

## 总结

通过本指南，您应该能够在 Windows 环境下成功安装和运行 Onyx 项目。我们提供的自动化脚本和验证工具可以大大简化安装过程，确保所有依赖都正确安装。

关键优势：
- ✅ 完全免费的社区版
- ✅ 支持 40+ 种连接器
- ✅ 包含您需要的 Gmail、Confluence、Jira 连接器
- ✅ 现代化的技术架构
- ✅ 详细的安装和验证工具
