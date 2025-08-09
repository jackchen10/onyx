#!/usr/bin/env node
/**
 * Onyx 前端依赖验证脚本
 * 验证所有必要的Node.js包是否正确安装
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

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
  'lucide-react',
  '@phosphor-icons/react',
  'yup',
  'js-cookie',
  'date-fns',
  'lodash'
];

// 可选依赖（不影响核心功能）
const OPTIONAL_PACKAGES = [
  '@sentry/nextjs',
  'posthog-js',
  '@stripe/stripe-js',
  '@playwright/test',
  'jest',
  'prettier',
  'eslint'
];

function printHeader(title) {
  console.log(`\n${'='.repeat(50)}`);
  console.log(` ${title}`);
  console.log(`${'='.repeat(50)}`);
}

function printSection(title) {
  console.log(`\n${'-'.repeat(30)}`);
  console.log(` ${title}`);
  console.log(`${'-'.repeat(30)}`);
}

function checkNodeVersion() {
  printSection('Node.js版本检查');
  
  const version = process.version;
  const majorVersion = parseInt(version.slice(1).split('.')[0]);
  const minorVersion = parseInt(version.slice(1).split('.')[1]);
  
  console.log(`当前Node.js版本: ${version}`);
  console.log(`Node.js路径: ${process.execPath}`);
  
  if (majorVersion < 18) {
    console.log('❌ 错误: 需要Node.js 18.18.0或更高版本');
    return false;
  }
  
  if (majorVersion === 18 && minorVersion < 18) {
    console.log('❌ 错误: 需要Node.js 18.18.0或更高版本');
    return false;
  }
  
  console.log('✅ Node.js版本检查通过');
  return true;
}

function checkNpmVersion() {
  printSection('npm版本检查');
  
  try {
    const npmVersion = execSync('npm --version', { encoding: 'utf8' }).trim();
    console.log(`npm版本: ${npmVersion}`);
    
    const majorVersion = parseInt(npmVersion.split('.')[0]);
    if (majorVersion < 8) {
      console.log('⚠️  警告: 建议使用npm 8.0.0或更高版本');
    } else {
      console.log('✅ npm版本检查通过');
    }
    
    return true;
  } catch (error) {
    console.log('❌ 无法获取npm版本信息');
    return false;
  }
}

function checkPackageJson() {
  printSection('package.json检查');

  try {
    // 获取web目录的package.json路径
    const webDir = path.join(__dirname, '..', '..', 'web');
    const packageJsonPath = path.join(webDir, 'package.json');
    
    if (!fs.existsSync(packageJsonPath)) {
      console.log('❌ package.json文件不存在');
      return false;
    }
    
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    
    const depCount = Object.keys(packageJson.dependencies || {}).length;
    const devDepCount = Object.keys(packageJson.devDependencies || {}).length;
    
    console.log('✅ package.json文件存在');
    console.log(`   项目名称: ${packageJson.name || '未知'}`);
    console.log(`   项目版本: ${packageJson.version || '未知'}`);
    console.log(`   生产依赖: ${depCount} 个`);
    console.log(`   开发依赖: ${devDepCount} 个`);
    console.log(`   总计依赖: ${depCount + devDepCount} 个`);
    
    return { packageJson, depCount, devDepCount };
  } catch (error) {
    console.log(`❌ 无法读取package.json: ${error.message}`);
    return false;
  }
}

function checkNodeModules() {
  printSection('node_modules检查');

  const webDir = path.join(__dirname, '..', '..', 'web');
  const nodeModulesPath = path.join(webDir, 'node_modules');
  
  if (!fs.existsSync(nodeModulesPath)) {
    console.log('❌ node_modules目录不存在');
    console.log('   请运行: npm install');
    return false;
  }
  
  try {
    const modules = fs.readdirSync(nodeModulesPath);
    const moduleCount = modules.filter(name => !name.startsWith('.')).length;
    
    console.log('✅ node_modules目录存在');
    console.log(`   已安装模块: ${moduleCount} 个`);
    
    // 检查关键目录
    const keyDirs = ['.bin', '@types', '@radix-ui', '@headlessui'];
    keyDirs.forEach(dir => {
      if (modules.includes(dir)) {
        console.log(`   ✅ ${dir} 目录存在`);
      }
    });
    
    return true;
  } catch (error) {
    console.log(`❌ 无法读取node_modules: ${error.message}`);
    return false;
  }
}

function checkPackage(packageName) {
  try {
    // 使用web目录的node_modules检查
    const webDir = path.join(__dirname, '..', '..', 'web');
    const packagePath = path.join(webDir, 'node_modules', packageName);

    if (!fs.existsSync(packagePath)) {
      return { success: false, error: `Package directory not found: ${packagePath}` };
    }

    // 尝试获取版本信息
    let version = '未知版本';
    try {
      const packageJsonPath = path.join(packagePath, 'package.json');
      if (fs.existsSync(packageJsonPath)) {
        const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
        version = packageJson.version;
      }
    } catch (e) {
      // 忽略版本获取错误
    }

    return { success: true, version, path: packagePath };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

function checkPackages(packages, packageType) {
  printSection(`${packageType}依赖检查`);
  
  const failedPackages = [];
  let successCount = 0;
  
  packages.forEach(packageName => {
    const result = checkPackage(packageName);
    
    if (result.success) {
      console.log(`✅ ${packageName.padEnd(30)} (${result.version})`);
      successCount++;
    } else {
      console.log(`❌ ${packageName.padEnd(30)} - ${result.error}`);
      failedPackages.push(packageName);
    }
  });
  
  console.log(`\n${packageType}依赖统计:`);
  console.log(`  成功: ${successCount}/${packages.length}`);
  console.log(`  失败: ${failedPackages.length}/${packages.length}`);
  
  return failedPackages;
}

function checkImportTime() {
  printSection('导入性能测试');
  
  const testPackages = ['next', 'react', 'tailwindcss', 'swr'];
  
  testPackages.forEach(packageName => {
    try {
      const startTime = Date.now();
      require(packageName);
      const importTime = Date.now() - startTime;
      
      let status;
      if (importTime < 100) {
        status = '✅';
      } else if (importTime < 500) {
        status = '⚠️ ';
      } else {
        status = '❌';
      }
      
      console.log(`${status} ${packageName.padEnd(20)} 导入时间: ${importTime}ms`);
    } catch (error) {
      console.log(`❌ ${packageName.padEnd(20)} 无法导入`);
    }
  });
}

function runBasicFunctionalityTest() {
  printSection('基本功能测试');
  
  const tests = [
    { name: 'Next.js配置检查', test: testNextConfig },
    { name: 'TypeScript配置检查', test: testTypeScriptConfig },
    { name: 'Tailwind配置检查', test: testTailwindConfig },
    { name: 'React组件测试', test: testReactComponent },
    { name: 'JSON处理测试', test: testJsonProcessing }
  ];
  
  let passedTests = 0;
  
  tests.forEach(({ name, test }) => {
    try {
      if (test()) {
        console.log(`✅ ${name}`);
        passedTests++;
      } else {
        console.log(`❌ ${name}`);
      }
    } catch (error) {
      console.log(`❌ ${name}: ${error.message}`);
    }
  });
  
  console.log(`\n功能测试结果: ${passedTests}/${tests.length} 通过`);
  return passedTests === tests.length;
}

function testNextConfig() {
  const webDir = path.join(__dirname, '..', '..', 'web');
  const configPath = path.join(webDir, 'next.config.js');
  return fs.existsSync(configPath);
}

function testTypeScriptConfig() {
  const webDir = path.join(__dirname, '..', '..', 'web');
  const configPath = path.join(webDir, 'tsconfig.json');
  return fs.existsSync(configPath);
}

function testTailwindConfig() {
  const webDir = path.join(__dirname, '..', '..', 'web');
  const configPath = path.join(webDir, 'tailwind.config.js');
  return fs.existsSync(configPath);
}

function testReactComponent() {
  try {
    const React = require('react');
    // 简单的组件创建测试
    const element = React.createElement('div', null, 'test');
    return element.type === 'div';
  } catch (error) {
    return false;
  }
}

function testJsonProcessing() {
  try {
    const testObj = { name: 'test', value: 123 };
    const jsonStr = JSON.stringify(testObj);
    const parsed = JSON.parse(jsonStr);
    return parsed.name === 'test' && parsed.value === 123;
  } catch (error) {
    return false;
  }
}

function generateInstallationReport(failedCritical, failedOptional) {
  printSection('安装建议');
  
  if (failedCritical.length > 0) {
    console.log('❌ 关键依赖缺失，需要立即安装:');
    failedCritical.forEach(pkg => {
      console.log(`   npm install ${pkg}`);
    });
    console.log('\n或者重新安装所有依赖:');
    console.log('   npm install');
  }
  
  if (failedOptional.length > 0) {
    console.log('\n⚠️  可选依赖缺失（不影响核心功能）:');
    failedOptional.forEach(pkg => {
      console.log(`   npm install ${pkg}`);
    });
  }
  
  if (failedCritical.length === 0 && failedOptional.length === 0) {
    console.log('✅ 所有依赖都已正确安装!');
  }
}

function checkScripts() {
  printSection('可用脚本检查');

  try {
    const webDir = path.join(__dirname, '..', '..', 'web');
    const packageJsonPath = path.join(webDir, 'package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const scripts = packageJson.scripts || {};
    
    const importantScripts = ['dev', 'build', 'start', 'lint', 'test'];
    
    console.log('可用的npm脚本:');
    importantScripts.forEach(script => {
      if (scripts[script]) {
        console.log(`✅ npm run ${script.padEnd(8)} - ${scripts[script]}`);
      } else {
        console.log(`❌ npm run ${script.padEnd(8)} - 未定义`);
      }
    });
    
    return true;
  } catch (error) {
    console.log('❌ 无法检查脚本配置');
    return false;
  }
}

function main() {
  printHeader('Onyx 前端依赖验证工具');
  
  // 检查Node.js版本
  if (!checkNodeVersion()) {
    console.log('\n❌ Node.js版本不符合要求，请升级到Node.js 18.18.0+');
    process.exit(1);
  }
  
  // 检查npm版本
  checkNpmVersion();
  
  // 检查package.json
  const packageInfo = checkPackageJson();
  if (!packageInfo) {
    console.log('\n❌ package.json检查失败');
    process.exit(1);
  }
  
  // 检查node_modules
  if (!checkNodeModules()) {
    console.log('\n❌ node_modules检查失败，请运行 npm install');
    process.exit(1);
  }
  
  // 检查关键依赖
  const failedCritical = checkPackages(CRITICAL_PACKAGES, '关键');
  
  // 检查可选依赖
  const failedOptional = checkPackages(OPTIONAL_PACKAGES, '可选');
  
  // 如果关键依赖都安装了，进行进一步测试
  if (failedCritical.length === 0) {
    checkImportTime();
    runBasicFunctionalityTest();
  }
  
  // 检查脚本配置
  checkScripts();
  
  // 生成报告
  generateInstallationReport(failedCritical, failedOptional);
  
  // 总结
  printHeader('验证结果总结');
  
  if (failedCritical.length > 0) {
    console.log(`❌ 验证失败: ${failedCritical.length} 个关键依赖缺失`);
    console.log('请按照上述建议安装缺失的依赖包');
    process.exit(1);
  } else {
    console.log('✅ 验证成功: 所有关键依赖都已正确安装');
    console.log('Onyx前端环境准备就绪!');
    
    console.log('\n下一步操作:');
    console.log('1. 配置环境变量 (.env.local文件)');
    console.log('2. 启动开发服务器: npm run dev');
    console.log('3. 访问应用: http://localhost:3000');
    console.log('4. 构建生产版本: npm run build');
  }
}

if (require.main === module) {
  main();
}
