# Onyx 项目结构说明

## 📁 整体项目结构

```
F:/code/onyx/
├── 📄 README.md                    # 项目主说明文档
├── 📄 LICENSE                      # 开源许可证
├── 📄 CONTRIBUTING.md              # 贡献指南
├── 📄 install_onyx_windows.bat     # Windows一键安装脚本
├── 📄 start_onyx.bat              # 系统启动脚本
├── 📄 ct.yaml                     # 配置文件
│
├── 📂 backend/                     # 后端代码目录
│   ├── 📄 requirements.txt        # 完整依赖列表 (156个包)
│   ├── 📄 pyproject.toml          # Python项目配置
│   ├── 📄 pytest.ini             # 测试配置
│   ├── 📄 alembic.ini             # 数据库迁移配置
│   ├── 📄 Dockerfile              # Docker配置
│   ├── 📂 onyx/                   # 核心业务逻辑
│   ├── 📂 alembic/                # 数据库迁移脚本
│   ├── 📂 requirements/           # 分环境依赖文件
│   ├── 📂 scripts/                # 工具脚本
│   ├── 📂 tests/                  # 后端单元测试
│   └── 📂 venv/                   # Python虚拟环境
│
├── 📂 web/                        # 前端代码目录
│   ├── 📄 package.json            # Node.js依赖配置 (93个包)
│   ├── 📄 next.config.js          # Next.js配置
│   ├── 📄 tsconfig.json           # TypeScript配置
│   ├── 📄 tailwind.config.js      # Tailwind CSS配置
│   ├── 📄 Dockerfile              # Docker配置
│   ├── 📂 src/                    # 源代码
│   ├── 📂 public/                 # 静态资源
│   ├── 📂 tests/                  # 前端测试
│   └── 📂 node_modules/           # Node.js依赖包
│
├── 📂 docs/                       # 📚 文档中心
│   ├── 📄 README.md               # 文档索引
│   ├── 📄 Windows安装指南.md       # Windows安装指南
│   ├── 📄 quick-start-guide.md    # 快速启动指南
│   ├── 📄 installation-success-report.md  # 安装成功报告
│   ├── 📄 技术架构报告.md          # 技术架构分析
│   ├── 📄 CE与EE功能对比分析.md    # 功能对比分析
│   ├── 📄 backend-dependencies-summary.md  # 后端依赖总结
│   ├── 📄 backend-dependency-guide.md      # 后端依赖指南
│   ├── 📄 frontend-dependency-guide.md     # 前端依赖指南
│   └── 📄 project-structure.md    # 项目结构说明 (本文档)
│
├── 📂 tests/                      # 🧪 测试和验证脚本
│   ├── 📄 README.md               # 测试脚本说明
│   ├── 📄 run_all_tests.py        # 完整测试运行器
│   ├── 📂 backend/                # 后端测试脚本
│   │   ├── 📄 test_import.py      # 模块导入测试
│   │   ├── 📄 validate_requirements.py  # 依赖验证
│   │   └── 📄 verify_installation.py    # 安装验证
│   ├── 📂 frontend/               # 前端测试脚本
│   │   └── 📄 verify_installation.js    # 前端安装验证
│   └── 📂 integration/            # 集成测试脚本
│       └── 📄 test_server.py      # 系统集成测试服务器
│
├── 📂 deployment/                 # 部署配置
│   ├── 📂 docker_compose/         # Docker Compose配置
│   ├── 📂 helm/                   # Kubernetes Helm配置
│   └── 📂 aws_ecs_fargate/        # AWS ECS配置
│
└── 📂 examples/                   # 示例代码
    ├── 📂 assistants-api/         # 助手API示例
    └── 📂 widget/                 # 组件示例
```

## 🎯 目录功能说明

### 📚 docs/ - 文档中心
**用途**: 存放所有项目文档  
**内容**: 安装指南、技术文档、架构分析、依赖说明  
**维护**: 随项目更新而更新

### 🧪 tests/ - 测试中心
**用途**: 存放所有测试和验证脚本  
**内容**: 
- `backend/` - 后端相关测试
- `frontend/` - 前端相关测试  
- `integration/` - 集成测试
- `run_all_tests.py` - 一键运行所有测试

### 🔧 backend/ - 后端核心
**用途**: Python FastAPI后端服务  
**关键文件**:
- `requirements.txt` - 完整依赖列表 (156个包)
- `onyx/` - 核心业务逻辑
- `alembic/` - 数据库迁移

### 🌐 web/ - 前端核心
**用途**: Next.js React前端应用  
**关键文件**:
- `package.json` - Node.js依赖 (93个包)
- `src/` - React组件和页面
- `public/` - 静态资源

## 🚀 快速操作指南

### 启动系统
```bash
# 方法1: 使用启动脚本 (推荐)
start_onyx.bat

# 方法2: 手动启动
# 终端1: 后端
cd backend && python ../tests/integration/test_server.py

# 终端2: 前端  
cd web && npm run dev
```

### 运行测试
```bash
# 运行所有测试
python tests/run_all_tests.py

# 单独测试
python tests/backend/validate_requirements.py
node tests/frontend/verify_installation.js
```

### 查看文档
```bash
# 浏览docs目录
ls docs/

# 查看特定文档
cat docs/quick-start-guide.md
```

## 📊 项目统计

### 代码规模
- **后端**: ~50,000行Python代码
- **前端**: ~30,000行TypeScript/React代码
- **文档**: 9个Markdown文档
- **测试**: 5个验证脚本

### 依赖统计
- **后端依赖**: 156个Python包
- **前端依赖**: 93个Node.js包
- **总依赖**: 249个包

### 文件统计
- **Python文件**: ~200个
- **TypeScript/JavaScript文件**: ~150个
- **配置文件**: ~20个
- **文档文件**: 9个

## 🔄 维护建议

### 定期任务
1. **依赖更新**: 定期运行`pip list --outdated`和`npm outdated`
2. **测试验证**: 定期运行`python tests/run_all_tests.py`
3. **文档更新**: 随功能变更更新相关文档

### 开发工作流
1. **新功能开发**: 在对应的backend/或web/目录中开发
2. **测试验证**: 使用tests/目录中的脚本验证
3. **文档更新**: 在docs/目录中更新相关文档

---

**最后更新**: 2025年1月9日  
**维护者**: Onyx开发团队
