# Onyx 快速启动指南

## 🚀 快速启动

### 前提条件
- Python 3.11.9 已安装
- Node.js 20.18.1 已安装
- Git 已安装

### 1. 启动后端服务器

```bash
# 进入后端目录
cd F:/code/onyx/backend

# 激活虚拟环境 (如果需要)
# python -m venv venv
# venv\Scripts\activate

# 启动测试服务器
python test_server.py
```

**后端服务器将启动在**: http://localhost:8080

### 2. 启动前端服务器

```bash
# 打开新的终端窗口
# 进入前端目录
cd F:/code/onyx/web

# 启动开发服务器
npm run dev
```

**前端应用将启动在**: http://localhost:3000

### 3. 访问应用

打开浏览器访问: http://localhost:3000

## 🎯 功能测试

### 基本聊天功能
1. 在输入框中输入消息
2. 按回车发送
3. 查看AI助手回复

### 助手功能
- 点击"默认助手"查看助手信息
- 使用"搜索文档"和"总结内容"快捷按钮

### 模型选择
- 点击"GPT 3.5 Turbo"按钮选择不同的AI模型

## 🔧 配置文件

### 后端配置 (.env)
```env
# 数据库配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=onyx
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# API配置
API_HOST=0.0.0.0
API_PORT=8080

# 开发模式
DEV_MODE=true
DISABLE_TELEMETRY=true
```

### 前端配置 (.env.local)
```env
# API配置
INTERNAL_URL=http://localhost:8080
NEXT_PUBLIC_API_URL=http://localhost:8080

# 功能开关
NEXT_PUBLIC_DISABLE_STREAMING=false
NEXT_TELEMETRY_DISABLED=1
```

## 🛠️ 故障排除

### 后端问题
- **端口占用**: 确保8080端口未被占用
- **依赖缺失**: 运行 `pip install -r requirements/default.txt`
- **Python版本**: 确保使用Python 3.11+

### 前端问题
- **端口占用**: 确保3000端口未被占用
- **依赖缺失**: 运行 `npm install`
- **构建失败**: 检查Node.js版本是否为20.x

### 常见错误
1. **404错误**: 确保后端服务器正在运行
2. **CORS错误**: 检查后端CORS配置
3. **连接失败**: 确认防火墙设置

## 📚 API文档

访问 http://localhost:8080/docs 查看完整的API文档

## 🔄 开发工作流

### 修改后端代码
1. 编辑Python文件
2. 重启后端服务器
3. 测试API变更

### 修改前端代码
1. 编辑React/TypeScript文件
2. 前端会自动热重载
3. 测试界面变更

## 📞 支持

如果遇到问题，请检查：
1. 控制台错误信息
2. 浏览器开发者工具
3. 服务器日志输出

## 🎉 下一步

现在您可以：
- 自定义助手配置
- 添加新的API端点
- 集成外部服务
- 配置数据库连接
