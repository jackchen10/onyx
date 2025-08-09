/**
 * 企业IMAP邮箱连接器配置界面
 * 基于Gmail connector的前端实现设计
 */

import React, { useState, useEffect } from 'react';

// 模拟Onyx的UI组件 (实际实现时需要真实导入)
interface IMAPConfig {
  imap_server: string;
  imap_port: number;
  use_ssl: boolean;
  username: string;
  password: string;
  folders: string[];
  exclude_folders: string[];
  batch_size: number;
  max_attachment_size: number;
  supported_attachment_types: string[];
}

interface IMAPConnectorProps {
  onSave: (config: IMAPConfig) => void;
  onTest: (config: IMAPConfig) => Promise<boolean>;
  initialConfig?: Partial<IMAPConfig>;
}

const IMAPConnectorConfig: React.FC<IMAPConnectorProps> = ({
  onSave,
  onTest,
  initialConfig = {}
}) => {
  const [config, setConfig] = useState<IMAPConfig>({
    imap_server: '',
    imap_port: 993,
    use_ssl: true,
    username: '',
    password: '',
    folders: ['INBOX'],
    exclude_folders: ['Trash', 'Spam', 'Drafts'],
    batch_size: 100,
    max_attachment_size: 10 * 1024 * 1024, // 10MB
    supported_attachment_types: ['.pdf', '.doc', '.docx', '.txt', '.xls', '.xlsx'],
    ...initialConfig
  });

  const [isLoading, setIsLoading] = useState(false);
  const [testResult, setTestResult] = useState<{success: boolean, message: string} | null>(null);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // 预设的企业邮箱配置
  const presetConfigs = {
    'exchange': {
      name: 'Microsoft Exchange',
      imap_server: 'outlook.office365.com',
      imap_port: 993,
      use_ssl: true,
      description: 'Microsoft 365 Exchange Online'
    },
    'gmail_enterprise': {
      name: 'Google Workspace',
      imap_server: 'imap.gmail.com',
      imap_port: 993,
      use_ssl: true,
      description: 'Google Workspace Gmail'
    },
    'tencent': {
      name: '腾讯企业邮箱',
      imap_server: 'imap.exmail.qq.com',
      imap_port: 993,
      use_ssl: true,
      description: '腾讯企业邮箱'
    },
    'aliyun': {
      name: '阿里云企业邮箱',
      imap_server: 'imap.mxhichina.com',
      imap_port: 993,
      use_ssl: true,
      description: '阿里云企业邮箱'
    },
    'netease': {
      name: '网易企业邮箱',
      imap_server: 'imap.ym.163.com',
      imap_port: 993,
      use_ssl: true,
      description: '网易企业邮箱'
    },
    'custom': {
      name: '自定义配置',
      imap_server: '',
      imap_port: 993,
      use_ssl: true,
      description: '自定义IMAP服务器配置'
    }
  };

  const handlePresetChange = (presetKey: string) => {
    if (presetKey === 'custom') return;
    
    const preset = presetConfigs[presetKey];
    setConfig(prev => ({
      ...prev,
      imap_server: preset.imap_server,
      imap_port: preset.imap_port,
      use_ssl: preset.use_ssl
    }));
  };

  const handleTestConnection = async () => {
    setIsLoading(true);
    setTestResult(null);
    
    try {
      const success = await onTest(config);
      setTestResult({
        success,
        message: success ? '连接测试成功！' : '连接测试失败，请检查配置。'
      });
    } catch (error) {
      setTestResult({
        success: false,
        message: `连接测试异常: ${error.message}`
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = () => {
    onSave(config);
  };

  const updateConfig = (field: keyof IMAPConfig, value: any) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  const addFolder = () => {
    const newFolder = prompt('请输入文件夹名称:');
    if (newFolder && !config.folders.includes(newFolder)) {
      updateConfig('folders', [...config.folders, newFolder]);
    }
  };

  const removeFolder = (folder: string) => {
    updateConfig('folders', config.folders.filter(f => f !== folder));
  };

  const addExcludeFolder = () => {
    const newFolder = prompt('请输入要排除的文件夹名称:');
    if (newFolder && !config.exclude_folders.includes(newFolder)) {
      updateConfig('exclude_folders', [...config.exclude_folders, newFolder]);
    }
  };

  const removeExcludeFolder = (folder: string) => {
    updateConfig('exclude_folders', config.exclude_folders.filter(f => f !== folder));
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        🏢 企业IMAP邮箱连接器配置
      </h2>

      {/* 预设配置选择 */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          选择邮箱类型
        </label>
        <select 
          className="w-full p-3 border border-gray-300 rounded-md"
          onChange={(e) => handlePresetChange(e.target.value)}
        >
          <option value="">请选择邮箱类型</option>
          {Object.entries(presetConfigs).map(([key, preset]) => (
            <option key={key} value={key}>
              {preset.name} - {preset.description}
            </option>
          ))}
        </select>
      </div>

      {/* 基础连接配置 */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            IMAP服务器地址 *
          </label>
          <input
            type="text"
            value={config.imap_server}
            onChange={(e) => updateConfig('imap_server', e.target.value)}
            placeholder="mail.company.com"
            className="w-full p-3 border border-gray-300 rounded-md"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            IMAP端口
          </label>
          <input
            type="number"
            value={config.imap_port}
            onChange={(e) => updateConfig('imap_port', parseInt(e.target.value))}
            className="w-full p-3 border border-gray-300 rounded-md"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            邮箱用户名 *
          </label>
          <input
            type="email"
            value={config.username}
            onChange={(e) => updateConfig('username', e.target.value)}
            placeholder="user@company.com"
            className="w-full p-3 border border-gray-300 rounded-md"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            邮箱密码 *
          </label>
          <input
            type="password"
            value={config.password}
            onChange={(e) => updateConfig('password', e.target.value)}
            placeholder="应用密码或邮箱密码"
            className="w-full p-3 border border-gray-300 rounded-md"
            required
          />
        </div>
      </div>

      {/* SSL配置 */}
      <div className="mb-6">
        <label className="flex items-center">
          <input
            type="checkbox"
            checked={config.use_ssl}
            onChange={(e) => updateConfig('use_ssl', e.target.checked)}
            className="mr-2"
          />
          <span className="text-sm font-medium text-gray-700">
            使用SSL/TLS加密连接 (推荐)
          </span>
        </label>
        <p className="text-xs text-gray-500 mt-1">
          SSL端口通常为993，非SSL端口通常为143
        </p>
      </div>

      {/* 连接测试 */}
      <div className="mb-6">
        <button
          onClick={handleTestConnection}
          disabled={isLoading || !config.imap_server || !config.username || !config.password}
          className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-4 py-2 rounded-md"
        >
          {isLoading ? '测试中...' : '🔍 测试连接'}
        </button>
        
        {testResult && (
          <div className={`mt-2 p-3 rounded-md ${
            testResult.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {testResult.success ? '✅' : '❌'} {testResult.message}
          </div>
        )}
      </div>

      {/* 高级配置 */}
      <div className="mb-6">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-blue-500 hover:text-blue-600 text-sm font-medium"
        >
          {showAdvanced ? '🔼 隐藏高级配置' : '🔽 显示高级配置'}
        </button>

        {showAdvanced && (
          <div className="mt-4 p-4 bg-gray-50 rounded-md">
            {/* 文件夹配置 */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                同步文件夹
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {config.folders.map(folder => (
                  <span key={folder} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-sm">
                    {folder}
                    <button 
                      onClick={() => removeFolder(folder)}
                      className="ml-1 text-blue-600 hover:text-blue-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
                <button 
                  onClick={addFolder}
                  className="bg-gray-200 text-gray-700 px-2 py-1 rounded text-sm hover:bg-gray-300"
                >
                  + 添加文件夹
                </button>
              </div>
            </div>

            {/* 排除文件夹配置 */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                排除文件夹
              </label>
              <div className="flex flex-wrap gap-2 mb-2">
                {config.exclude_folders.map(folder => (
                  <span key={folder} className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm">
                    {folder}
                    <button 
                      onClick={() => removeExcludeFolder(folder)}
                      className="ml-1 text-red-600 hover:text-red-800"
                    >
                      ×
                    </button>
                  </span>
                ))}
                <button 
                  onClick={addExcludeFolder}
                  className="bg-gray-200 text-gray-700 px-2 py-1 rounded text-sm hover:bg-gray-300"
                >
                  + 添加排除文件夹
                </button>
              </div>
            </div>

            {/* 性能配置 */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  批处理大小
                </label>
                <input
                  type="number"
                  value={config.batch_size}
                  onChange={(e) => updateConfig('batch_size', parseInt(e.target.value))}
                  min="10"
                  max="1000"
                  className="w-full p-2 border border-gray-300 rounded-md"
                />
                <p className="text-xs text-gray-500 mt-1">每批处理的邮件数量 (10-1000)</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  最大附件大小 (MB)
                </label>
                <input
                  type="number"
                  value={Math.round(config.max_attachment_size / (1024 * 1024))}
                  onChange={(e) => updateConfig('max_attachment_size', parseInt(e.target.value) * 1024 * 1024)}
                  min="1"
                  max="100"
                  className="w-full p-2 border border-gray-300 rounded-md"
                />
                <p className="text-xs text-gray-500 mt-1">附件大小限制 (1-100MB)</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 保存按钮 */}
      <div className="flex justify-end space-x-4">
        <button
          onClick={handleSave}
          disabled={!config.imap_server || !config.username || !config.password}
          className="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-6 py-2 rounded-md"
        >
          💾 保存配置
        </button>
      </div>

      {/* 配置说明 */}
      <div className="mt-8 p-4 bg-blue-50 rounded-md">
        <h3 className="text-lg font-semibold text-blue-800 mb-2">📋 配置说明</h3>
        <div className="text-sm text-blue-700 space-y-2">
          <p><strong>IMAP服务器:</strong> 企业邮箱的IMAP服务器地址</p>
          <p><strong>端口:</strong> 993 (SSL) 或 143 (非SSL)</p>
          <p><strong>用户名:</strong> 完整的邮箱地址</p>
          <p><strong>密码:</strong> 邮箱密码或应用专用密码</p>
          <p><strong>文件夹:</strong> 要同步的邮箱文件夹</p>
        </div>
      </div>

      {/* 常见企业邮箱配置示例 */}
      <div className="mt-6 p-4 bg-gray-50 rounded-md">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">🏢 常见企业邮箱配置</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-gray-700">Microsoft Exchange</h4>
            <p className="text-gray-600">服务器: outlook.office365.com</p>
            <p className="text-gray-600">端口: 993 (SSL)</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-700">腾讯企业邮箱</h4>
            <p className="text-gray-600">服务器: imap.exmail.qq.com</p>
            <p className="text-gray-600">端口: 993 (SSL)</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-700">阿里云企业邮箱</h4>
            <p className="text-gray-600">服务器: imap.mxhichina.com</p>
            <p className="text-gray-600">端口: 993 (SSL)</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-700">网易企业邮箱</h4>
            <p className="text-gray-600">服务器: imap.ym.163.com</p>
            <p className="text-gray-600">端口: 993 (SSL)</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// 使用示例组件
const IMAPConnectorExample: React.FC = () => {
  const handleSave = (config: IMAPConfig) => {
    console.log('保存IMAP配置:', config);
    // 实际实现中调用API保存配置
  };

  const handleTest = async (config: IMAPConfig): Promise<boolean> => {
    console.log('测试IMAP连接:', config);
    // 实际实现中调用后端API测试连接
    
    // 模拟测试
    return new Promise((resolve) => {
      setTimeout(() => {
        // 简单验证
        const isValid = config.imap_server && config.username && config.password;
        resolve(isValid);
      }, 2000);
    });
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8">
      <IMAPConnectorConfig 
        onSave={handleSave}
        onTest={handleTest}
        initialConfig={{
          imap_server: 'imap.exmail.qq.com',
          username: 'demo@company.com'
        }}
      />
    </div>
  );
};

export default IMAPConnectorConfig;
export { IMAPConnectorExample };
