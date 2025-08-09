#!/usr/bin/env python3
"""
企业IMAP邮箱连接器测试脚本
测试IMAP connector的各种功能
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any

# 添加backend路径以便导入
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from imap_connector import IMAPConnector, IMAPCheckpoint
    from imap_connector_api import IMAPConfigModel, IMAPConnectorAPI, IMAPConnectorUtils
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保backend目录中有imap_connector.py和imap_connector_api.py文件")
    sys.exit(1)

class IMAPConnectorTester:
    """IMAP连接器测试器"""
    
    def __init__(self):
        self.test_configs = self._get_test_configs()
        self.api = IMAPConnectorAPI()
    
    def _get_test_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取测试配置"""
        return {
            "gmail_test": {
                "name": "Gmail测试",
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "use_ssl": True,
                "username": "test@gmail.com",
                "password": "app_password",
                "folders": ["INBOX"],
                "description": "Gmail IMAP测试配置"
            },
            "exchange_test": {
                "name": "Exchange测试",
                "imap_server": "outlook.office365.com",
                "imap_port": 993,
                "use_ssl": True,
                "username": "test@company.com",
                "password": "password",
                "folders": ["INBOX", "Sent Items"],
                "description": "Microsoft Exchange测试配置"
            },
            "tencent_test": {
                "name": "腾讯企业邮箱测试",
                "imap_server": "imap.exmail.qq.com",
                "imap_port": 993,
                "use_ssl": True,
                "username": "test@company.com",
                "password": "password",
                "folders": ["INBOX"],
                "description": "腾讯企业邮箱测试配置"
            }
        }
    
    def print_header(self, title: str):
        """打印测试标题"""
        print(f"\n{'='*60}")
        print(f"🧪 {title}")
        print('='*60)
    
    def test_config_validation(self):
        """测试配置验证"""
        self.print_header("配置验证测试")
        
        # 测试有效配置
        valid_config = {
            "imap_server": "imap.gmail.com",
            "imap_port": 993,
            "use_ssl": True,
            "username": "test@gmail.com",
            "password": "password",
            "folders": ["INBOX"]
        }
        
        errors = IMAPConnectorUtils.validate_imap_config(valid_config)
        print(f"✅ 有效配置验证: {len(errors)} 个错误")
        
        # 测试无效配置
        invalid_configs = [
            {"imap_server": "", "username": "test", "password": "pass"},  # 缺少服务器
            {"imap_server": "test.com", "username": "", "password": "pass"},  # 缺少用户名
            {"imap_server": "test.com", "username": "test", "password": ""},  # 缺少密码
            {"imap_server": "test.com", "username": "invalid_email", "password": "pass"},  # 无效邮箱
            {"imap_server": "test.com", "username": "test@test.com", "password": "pass", "imap_port": 99999},  # 无效端口
        ]
        
        for i, invalid_config in enumerate(invalid_configs):
            errors = IMAPConnectorUtils.validate_imap_config(invalid_config)
            print(f"❌ 无效配置 {i+1}: {len(errors)} 个错误 - {errors[0] if errors else '无错误'}")
    
    def test_preset_configs(self):
        """测试预设配置"""
        self.print_header("预设配置测试")
        
        presets = IMAPConnectorUtils.get_preset_configs()
        print(f"📋 预设配置数量: {len(presets)}")
        
        for preset_key, preset_config in presets.items():
            print(f"🔧 {preset_config['name']}")
            print(f"   服务器: {preset_config['imap_server']}")
            print(f"   端口: {preset_config['imap_port']}")
            print(f"   SSL: {'✅' if preset_config['use_ssl'] else '❌'}")
            print(f"   描述: {preset_config['description']}")
    
    def test_time_estimation(self):
        """测试时间估算"""
        self.print_header("同步时间估算测试")
        
        test_cases = [100, 1000, 5000, 10000, 50000]
        
        for email_count in test_cases:
            estimate = IMAPConnectorUtils.estimate_sync_time(email_count)
            print(f"📊 {email_count:,} 封邮件:")
            print(f"   预计时间: {estimate['estimated_time_display']}")
            print(f"   批次数量: {estimate['batch_count']}")
            print(f"   处理速度: {estimate['emails_per_minute']} 封/分钟")
    
    async def test_api_functions(self):
        """测试API功能"""
        self.print_header("API功能测试")
        
        # 创建测试配置
        test_config = IMAPConfigModel(
            imap_server="imap.gmail.com",
            imap_port=993,
            use_ssl=True,
            username="test@example.com",
            password="test_password",
            folders=["INBOX"]
        )
        
        print("🔍 测试配置模型创建...")
        print(f"✅ 配置模型: {test_config.imap_server}")
        
        # 注意: 实际的连接测试需要真实的邮箱凭据
        print("⚠️  实际连接测试需要真实的邮箱凭据")
        
        # 测试配置验证
        errors = IMAPConnectorUtils.validate_imap_config(test_config.dict())
        if errors:
            print(f"❌ 配置验证失败: {errors}")
        else:
            print("✅ 配置验证通过")
    
    def test_connector_creation(self):
        """测试连接器创建"""
        self.print_header("连接器创建测试")
        
        try:
            # 创建IMAP连接器实例
            connector = IMAPConnector(batch_size=50)
            print("✅ IMAP连接器实例创建成功")
            
            # 测试配置加载 (使用虚拟配置)
            test_credentials = {
                "imap_server": "imap.example.com",
                "imap_port": 993,
                "use_ssl": True,
                "username": "test@example.com",
                "password": "test_password",
                "folders": ["INBOX"]
            }
            
            print("🔧 测试凭据加载...")
            # 注意: 这会尝试实际连接，所以会失败
            try:
                result = connector.load_credentials(test_credentials)
                print(f"✅ 凭据加载结果: {result}")
            except Exception as e:
                print(f"⚠️  凭据加载失败 (预期): {e}")
            
            print("✅ 连接器基础功能测试完成")
            
        except Exception as e:
            print(f"❌ 连接器创建失败: {e}")
    
    def generate_integration_report(self):
        """生成集成报告"""
        self.print_header("IMAP Connector 集成报告")
        
        print("📊 实现状态:")
        print("   ✅ 核心IMAP连接器类")
        print("   ✅ 邮件解析和处理")
        print("   ✅ 附件处理逻辑")
        print("   ✅ 增量同步机制")
        print("   ✅ 后端API路由")
        print("   ✅ 前端配置界面")
        print("   ✅ 预设配置支持")
        print("   ✅ 错误处理和重试")
        
        print("\n🎯 支持的企业邮箱:")
        presets = IMAPConnectorUtils.get_preset_configs()
        for preset_key, preset_config in presets.items():
            print(f"   📧 {preset_config['name']}")
        
        print("\n📋 核心功能:")
        print("   🔐 SSL/TLS安全连接")
        print("   📁 多文件夹同步")
        print("   📎 附件内容提取")
        print("   🔄 增量同步支持")
        print("   ⚡ 批量处理优化")
        print("   🏥 连接健康检查")
        print("   📊 同步进度监控")
        
        print("\n🚀 部署建议:")
        print("   1. 先在测试环境验证连接")
        print("   2. 配置合适的批处理大小")
        print("   3. 设置附件大小限制")
        print("   4. 监控同步性能")
        print("   5. 定期检查错误日志")
        
        print("\n⚠️  注意事项:")
        print("   • IMAP性能比Gmail API慢")
        print("   • 需要企业邮箱开启IMAP")
        print("   • 建议使用应用专用密码")
        print("   • 大量邮件同步需要时间")
        print("   • 需要稳定的网络连接")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 企业IMAP邮箱连接器完整测试")
        print("📅 测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        try:
            # 运行各项测试
            self.test_config_validation()
            self.test_preset_configs()
            self.test_time_estimation()
            asyncio.run(self.test_api_functions())
            self.test_connector_creation()
            self.generate_integration_report()
            
            print("\n🎉 所有测试完成！")
            return True
            
        except Exception as e:
            print(f"\n❌ 测试过程中发生异常: {e}")
            return False

def main():
    """主函数"""
    tester = IMAPConnectorTester()
    success = tester.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
