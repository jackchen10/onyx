# Onyx 测试和验证脚本

## 📁 目录结构

```
tests/
├── backend/                 # 后端测试脚本
│   ├── test_import.py      # 后端模块导入测试
│   ├── validate_requirements.py  # 依赖包验证
│   └── verify_installation.py    # 后端安装验证
├── frontend/               # 前端测试脚本
│   └── verify_installation.js    # 前端安装验证
├── integration/            # 集成测试脚本
│   └── test_server.py     # 完整系统测试服务器
└── README.md              # 本文档
```

## 🧪 测试脚本说明

### 后端测试 (backend/)

#### test_import.py
- **功能**: 测试Onyx后端核心模块导入
- **用途**: 验证Python环境和依赖是否正确配置
- **运行**: `cd backend && python ../tests/backend/test_import.py`

#### validate_requirements.py
- **功能**: 验证requirements.txt中所有依赖包
- **用途**: 检查156个依赖包的安装状态和导入能力
- **运行**: `cd backend && python ../tests/backend/validate_requirements.py`

#### verify_installation.py
- **功能**: 完整的后端安装验证
- **用途**: 验证后端环境、依赖和配置
- **运行**: `cd backend && python ../tests/backend/verify_installation.py`

### 前端测试 (frontend/)

#### verify_installation.js
- **功能**: 前端安装和构建验证
- **用途**: 验证Node.js环境、依赖和构建过程
- **运行**: `cd web && node ../tests/frontend/verify_installation.js`

### 集成测试 (integration/)

#### test_server.py
- **功能**: 完整的系统集成测试服务器
- **用途**: 提供模拟API端点，测试前后端集成
- **运行**: `cd backend && python ../tests/integration/test_server.py`
- **服务地址**: http://localhost:8080
- **API文档**: http://localhost:8080/docs

## 🚀 快速测试流程

### 1. 验证后端环境
```bash
cd backend
python ../tests/backend/validate_requirements.py
python ../tests/backend/test_import.py
```

### 2. 验证前端环境
```bash
cd web
node ../tests/frontend/verify_installation.js
```

### 3. 启动集成测试
```bash
# 终端1: 启动后端测试服务器
cd backend
python ../tests/integration/test_server.py

# 终端2: 启动前端开发服务器
cd web
npm run dev

# 浏览器访问: http://localhost:3000
```

## ✅ 预期结果

### 后端测试成功标志
- ✅ 所有156个依赖包验证通过
- ✅ FastAPI应用导入成功
- ✅ 核心模块导入无错误

### 前端测试成功标志
- ✅ Next.js构建成功
- ✅ 所有npm依赖安装完成
- ✅ TypeScript编译无错误

### 集成测试成功标志
- ✅ 后端API服务器启动成功
- ✅ 前端应用正常加载
- ✅ 聊天功能正常工作
- ✅ API通信正常

## 🔧 故障排除

### 常见问题
1. **Python模块导入失败**: 检查虚拟环境是否激活
2. **依赖包缺失**: 运行 `pip install -r requirements.txt`
3. **Node.js构建失败**: 运行 `npm install` 重新安装依赖
4. **端口占用**: 检查8080和3000端口是否被占用

### 调试命令
```bash
# 检查Python环境
python --version
pip list

# 检查Node.js环境
node --version
npm list

# 检查端口占用
netstat -ano | findstr :8080
netstat -ano | findstr :3000
```

## 📊 测试覆盖范围

- ✅ 依赖包完整性
- ✅ 模块导入能力
- ✅ API服务器启动
- ✅ 前端构建和运行
- ✅ 前后端通信
- ✅ 基础聊天功能
