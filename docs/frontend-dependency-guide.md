# Onyx 前端依赖清单和安装指南

## 系统要求

### Node.js 版本
- **Node.js 18.18.0+** (推荐 Node.js 20 LTS)
- **npm 10.8.0+** 或 **yarn 1.22.0+**

### 操作系统支持
- Windows 10/11
- macOS
- Linux (Ubuntu, CentOS, etc.)

## 技术栈概览

- **框架**: Next.js 15.2.4
- **React**: 18.3.1
- **TypeScript**: 5.0.3
- **样式**: Tailwind CSS 3.3.1
- **UI组件**: Radix UI
- **状态管理**: SWR 2.1.5
- **表单**: Formik 2.2.9 + Yup 1.4.0

## 生产依赖 (dependencies)

### 核心框架
```json
{
  "next": "^15.2.4",
  "react": "^18.3.1",
  "react-dom": "^18.3.1",
  "typescript": "5.0.3"
}
```

### UI组件库
```json
{
  "@headlessui/react": "^2.2.0",
  "@headlessui/tailwindcss": "^0.2.1",
  "@radix-ui/react-accordion": "^1.2.2",
  "@radix-ui/react-checkbox": "^1.1.2",
  "@radix-ui/react-collapsible": "^1.1.2",
  "@radix-ui/react-dialog": "^1.1.6",
  "@radix-ui/react-dropdown-menu": "^2.1.6",
  "@radix-ui/react-label": "^2.1.1",
  "@radix-ui/react-popover": "^1.1.6",
  "@radix-ui/react-radio-group": "^1.2.2",
  "@radix-ui/react-scroll-area": "^1.2.2",
  "@radix-ui/react-select": "^2.1.6",
  "@radix-ui/react-separator": "^1.1.0",
  "@radix-ui/react-slider": "^1.2.2",
  "@radix-ui/react-slot": "^1.1.2",
  "@radix-ui/react-switch": "^1.1.3",
  "@radix-ui/react-tabs": "^1.1.1",
  "@radix-ui/react-tooltip": "^1.1.3"
}
```

### 样式和图标
```json
{
  "tailwindcss": "^3.3.1",
  "tailwind-merge": "^2.5.4",
  "tailwindcss-animate": "^1.0.7",
  "autoprefixer": "^10.4.14",
  "postcss": "^8.4.31",
  "@phosphor-icons/react": "^2.0.8",
  "lucide-react": "^0.454.0",
  "react-icons": "^4.8.0"
}
```

### 状态管理和数据获取
```json
{
  "swr": "^2.1.5",
  "cookies-next": "^5.1.0",
  "js-cookie": "^3.0.5"
}
```

### 表单和验证
```json
{
  "formik": "^2.2.9",
  "yup": "^1.4.0"
}
```

### 拖拽功能
```json
{
  "@dnd-kit/core": "^6.1.0",
  "@dnd-kit/modifiers": "^7.0.0",
  "@dnd-kit/sortable": "^8.0.0",
  "@dnd-kit/utilities": "^3.2.2"
}
```

### 数据处理和工具
```json
{
  "@tanstack/react-table": "^8.21.3",
  "date-fns": "^3.6.0",
  "lodash": "^4.17.21",
  "semver": "^7.5.4",
  "uuid": "^9.0.1",
  "clsx": "^2.1.1",
  "class-variance-authority": "^0.7.0"
}
```

### Markdown和内容处理
```json
{
  "react-markdown": "^9.0.1",
  "remark-gfm": "^4.0.0",
  "remark-math": "^6.0.0",
  "rehype-katex": "^7.0.1",
  "rehype-prism-plus": "^2.0.0",
  "rehype-sanitize": "^6.0.0",
  "rehype-stringify": "^10.0.1",
  "mdast-util-find-and-replace": "^3.0.1",
  "katex": "^0.16.17",
  "prismjs": "^1.29.0"
}
```

### 第三方服务集成
```json
{
  "@sentry/nextjs": "^8.50.0",
  "@sentry/tracing": "^7.120.3",
  "posthog-js": "^1.176.0",
  "@stripe/stripe-js": "^4.6.0",
  "stripe": "^17.0.0"
}
```

### 其他工具
```json
{
  "react-datepicker": "^7.6.0",
  "react-day-picker": "^8.10.1",
  "react-dropzone": "^14.2.3",
  "react-loader-spinner": "^5.4.5",
  "react-select": "^5.8.0",
  "recharts": "^2.13.1",
  "sharp": "^0.33.5",
  "next-themes": "^0.4.4",
  "cmdk": "^1.0.0",
  "vaul": "^1.1.1",
  "favicon-fetch": "^1.0.0"
}
```

### TypeScript类型定义
```json
{
  "@types/js-cookie": "^3.0.3",
  "@types/lodash": "^4.17.0",
  "@types/node": "18.15.11",
  "@types/prismjs": "^1.26.4",
  "@types/react": "18.0.32",
  "@types/react-dom": "18.0.11",
  "@types/uuid": "^9.0.8"
}
```

## 开发依赖 (devDependencies)

### 测试工具
```json
{
  "@playwright/test": "^1.39.0",
  "@chromatic-com/playwright": "^0.10.2",
  "jest": "^29.7.0",
  "@types/jest": "^29.5.14",
  "ts-jest": "^29.2.5"
}
```

### 代码质量工具
```json
{
  "eslint": "^8.57.1",
  "eslint-config-next": "^14.1.0",
  "eslint-plugin-unused-imports": "^4.1.4",
  "prettier": "3.1.0",
  "ts-unused-exports": "^11.0.1"
}
```

### 样式工具
```json
{
  "@tailwindcss/typography": "^0.5.10"
}
```

### 其他开发工具
```json
{
  "@types/chrome": "^0.0.287",
  "chromatic": "^11.25.2"
}
```

## Windows 安装指南

### 步骤 1: 安装 Node.js

1. 从 [Node.js官网](https://nodejs.org/) 下载 LTS 版本 (推荐 20.x)
2. 运行安装程序，确保勾选 "Add to PATH"
3. 验证安装：
```cmd
node --version
npm --version
```

### 步骤 2: 配置 npm (可选)

```cmd
# 设置npm镜像源（提高下载速度）
npm config set registry https://registry.npmmirror.com

# 查看配置
npm config list
```

### 步骤 3: 安装依赖

```cmd
# 进入前端目录
cd F:\code\onyx\web

# 安装所有依赖
npm install

# 或者使用 npm ci (更快，适用于生产环境)
npm ci
```

### 步骤 4: 验证安装

创建验证脚本 `verify_installation.js`：

```javascript
#!/usr/bin/env node
/**
 * 验证 Onyx 前端依赖安装
 */

const fs = require('fs');
const path = require('path');

// 关键依赖列表
const CRITICAL_PACKAGES = [
  'next',
  'react',
  'react-dom',
  'typescript',
  'tailwindcss',
  'swr',
  'formik',
  '@radix-ui/react-dialog',
  '@headlessui/react',
  'lucide-react'
];

function checkNodeVersion() {
  const version = process.version;
  const majorVersion = parseInt(version.slice(1).split('.')[0]);
  
  console.log(`Node.js版本: ${version}`);
  
  if (majorVersion < 18) {
    console.log('❌ 错误: 需要Node.js 18.18.0或更高版本');
    return false;
  }
  
  console.log('✅ Node.js版本检查通过');
  return true;
}

function checkPackage(packageName) {
  try {
    require.resolve(packageName);
    console.log(`✅ ${packageName}`);
    return true;
  } catch (error) {
    console.log(`❌ ${packageName}: 未找到`);
    return false;
  }
}

function checkPackages() {
  console.log('\n检查关键依赖包...');
  const failedPackages = [];
  
  for (const packageName of CRITICAL_PACKAGES) {
    if (!checkPackage(packageName)) {
      failedPackages.push(packageName);
    }
  }
  
  return failedPackages;
}

function checkPackageJson() {
  try {
    const packageJsonPath = path.join(process.cwd(), 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    
    const depCount = Object.keys(packageJson.dependencies || {}).length;
    const devDepCount = Object.keys(packageJson.devDependencies || {}).length;
    
    console.log(`\npackage.json信息:`);
    console.log(`- 生产依赖: ${depCount} 个`);
    console.log(`- 开发依赖: ${devDepCount} 个`);
    console.log(`- 总计: ${depCount + devDepCount} 个`);
    
    return true;
  } catch (error) {
    console.log(`❌ 无法读取package.json: ${error.message}`);
    return false;
  }
}

function checkNodeModules() {
  const nodeModulesPath = path.join(process.cwd(), 'node_modules');
  
  if (!fs.existsSync(nodeModulesPath)) {
    console.log('❌ node_modules目录不存在');
    return false;
  }
  
  const moduleCount = fs.readdirSync(nodeModulesPath).length;
  console.log(`node_modules: ${moduleCount} 个模块`);
  return true;
}

function main() {
  console.log('=== Onyx 前端依赖验证 ===\n');
  
  // 检查Node.js版本
  if (!checkNodeVersion()) {
    process.exit(1);
  }
  
  // 检查package.json
  checkPackageJson();
  
  // 检查node_modules
  checkNodeModules();
  
  // 检查关键包
  const failedPackages = checkPackages();
  
  // 总结
  console.log('\n=== 验证结果 ===');
  if (failedPackages.length > 0) {
    console.log(`❌ 失败: ${failedPackages.length} 个关键包未正确安装`);
    console.log('失败的包:', failedPackages.join(', '));
    console.log('\n请重新安装依赖:');
    console.log('npm install');
    process.exit(1);
  } else {
    console.log('✅ 所有关键依赖包安装成功!');
    console.log('前端环境准备就绪!');
    
    console.log('\n可用的npm脚本:');
    console.log('- npm run dev     # 启动开发服务器');
    console.log('- npm run build   # 构建生产版本');
    console.log('- npm run start   # 启动生产服务器');
    console.log('- npm run lint    # 代码检查');
    console.log('- npm test        # 运行测试');
  }
}

if (require.main === module) {
  main();
}
```

运行验证：
```cmd
node verify_installation.js
```

### 步骤 5: 启动开发服务器

```cmd
# 启动开发服务器
npm run dev

# 或使用Turbo模式（更快）
npm run dev --turbo
```

访问 `http://localhost:3000` 查看应用。

## 常见问题解决

### 1. 安装速度慢
```cmd
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 或使用yarn
npm install -g yarn
yarn install
```

### 2. Sharp 安装失败
```cmd
# Windows 解决方案
npm install --platform=win32 --arch=x64 sharp
```

### 3. 权限问题
```cmd
# 以管理员身份运行命令提示符
# 或配置npm全局目录
npm config set prefix %APPDATA%\npm
```

### 4. 内存不足
```cmd
# 增加Node.js内存限制
set NODE_OPTIONS=--max-old-space-size=4096
npm install
```

### 5. 网络超时
```cmd
# 增加超时时间
npm config set timeout 60000
npm install
```

## 环境变量配置

创建 `.env.local` 文件：
```env
# API配置
INTERNAL_URL=http://localhost:8080
NEXT_PUBLIC_API_URL=http://localhost:8080

# 功能开关
NEXT_PUBLIC_DISABLE_STREAMING=false
NEXT_PUBLIC_NEW_CHAT_DIRECTS_TO_SAME_PERSONA=false

# 主题配置
NEXT_PUBLIC_THEME=default

# 开发配置
NEXT_TELEMETRY_DISABLED=1
```

## 构建和部署

### 开发环境
```cmd
npm run dev
```

### 生产构建
```cmd
npm run build
npm run start
```

### 代码检查
```cmd
npm run lint
npm run lint:fix-unused
```

### 测试
```cmd
npm test
```

## 下一步

安装完成后，您可以：
1. 启动开发服务器：`npm run dev`
2. 访问应用：`http://localhost:3000`
3. 查看Storybook：`npm run storybook`（如果配置）
4. 运行测试：`npm test`
