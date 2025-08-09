#!/usr/bin/env python3
"""
基于现有IMAP Connector的管理工具
正确使用Onyx现有的IMAP connector实现
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List

# 添加backend路径以便正确导入Onyx模块
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

try:
    # 正确的Onyx导入
    from onyx.configs.constants import DocumentSource
    from onyx.connectors.imap.connector import ImapConnector, ImapCheckpoint
    from onyx.connectors.imap.models import EmailHeaders
    from onyx.connectors.credentials_provider import OnyxStaticCredentialsProvider
    from onyx.connectors.models import Document, TextSection, BasicExpertInfo
    
    print("✅ 成功导入Onyx IMAP connector模块")
    
except ImportError as e:
    print(f"❌ 导入Onyx模块失败: {e}")
    print("请确保在Onyx工程根目录下运行此脚本")
    sys.exit(1)

class IMAPConnectorManager:
    """基于现有IMAP Connector的管理工具"""
    
    def __init__(self):
        self.connector: ImapConnector = None
        self.enterprise_presets = self._get_enterprise_presets()
    
    def _get_enterprise_presets(self) -> Dict[str, Dict[str, Any]]:
        """获取企业邮箱预设配置"""
        return {
            "microsoft_365": {
                "name": "Microsoft 365",
                "host": "outlook.office365.com",
                "port": 993,
                "description": "Microsoft 365 Exchange Online",
                "setup_notes": "需要启用IMAP并使用应用密码"
            },
            "tencent_exmail": {
                "name": "腾讯企业邮箱",
                "host": "imap.exmail.qq.com", 
                "port": 993,
                "description": "腾讯企业邮箱服务",
                "setup_notes": "需要在管理后台启用IMAP/SMTP"
            },
            "aliyun_mail": {
                "name": "阿里云企业邮箱",
                "host": "imap.mxhichina.com",
                "port": 993,
                "description": "阿里云企业邮箱服务",
                "setup_notes": "默认支持IMAP协议"
            },
            "netease_mail": {
                "name": "网易企业邮箱",
                "host": "imap.ym.163.com",
                "port": 993,
                "description": "网易企业邮箱服务",
                "setup_notes": "需要开启IMAP功能"
            },
            "zimbra": {
                "name": "Zimbra Collaboration",
                "host": "mail.company.com",
                "port": 993,
                "description": "Zimbra企业邮件平台",
                "setup_notes": "自定义服务器地址"
            }
        }
    
    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{'='*60}")
        print(f"📧 {title}")
        print('='*60)
    
    def show_existing_implementation(self):
        """显示现有IMAP实现信息"""
        self.print_header("Onyx现有IMAP Connector分析")
        
        print("🔍 发现: Onyx已有完整的IMAP connector实现!")
        print()
        print("📁 实现位置:")
        print("   backend/onyx/connectors/imap/connector.py (485行)")
        print("   backend/onyx/connectors/imap/models.py (76行)")
        print("   backend/onyx/connectors/imap/__init__.py")
        print()
        
        print("🏗️ 核心架构:")
        print("   ✅ ImapConnector - 主连接器类")
        print("   ✅ ImapCheckpoint - 检查点机制")
        print("   ✅ EmailHeaders - 邮件头模型")
        print("   ✅ CurrentMailbox - 当前邮箱状态")
        print()
        
        print("🔧 已实现功能:")
        print("   ✅ IMAP SSL连接")
        print("   ✅ 用户名密码认证")
        print("   ✅ 多邮箱支持")
        print("   ✅ 增量同步机制")
        print("   ✅ 邮件头解析")
        print("   ✅ HTML邮件处理")
        print("   ✅ 权限管理")
        print("   ✅ 错误处理")
        print()
        
        print("📊 技术特点:")
        print("   🔐 使用imaplib.IMAP4_SSL")
        print("   📄 继承标准Onyx connector接口")
        print("   🔄 实现CheckpointedConnectorWithPermSync")
        print("   🏥 包含完整的错误处理")
        print("   📝 使用BeautifulSoup处理HTML")
    
    def create_connector_instance(self, host: str, username: str, password: str, 
                                 mailboxes: List[str] = None, port: int = 993):
        """创建IMAP connector实例"""
        try:
            # 创建connector实例
            self.connector = ImapConnector(
                host=host,
                port=port,
                mailboxes=mailboxes
            )
            
            # 设置凭据
            credentials = {
                "imap_username": username,
                "imap_password": password
            }
            
            credentials_provider = OnyxStaticCredentialsProvider(
                tenant_id=None,
                connector_name=DocumentSource.IMAP,
                credential_json=credentials
            )
            
            self.connector.set_credentials_provider(credentials_provider)
            
            print(f"✅ IMAP connector实例创建成功")
            print(f"   服务器: {host}:{port}")
            print(f"   用户: {username}")
            print(f"   邮箱: {mailboxes or '自动检测'}")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建IMAP connector失败: {e}")
            return False
    
    def test_connector_validation(self):
        """测试connector验证功能"""
        self.print_header("IMAP Connector验证测试")
        
        if not self.connector:
            print("❌ 请先创建connector实例")
            return
        
        try:
            # 调用现有的验证方法
            self.connector.validate_connector_settings()
            print("✅ IMAP connector验证通过")
            
        except Exception as e:
            print(f"❌ IMAP connector验证失败: {e}")
    
    def demonstrate_checkpoint_mechanism(self):
        """演示检查点机制"""
        self.print_header("IMAP检查点机制演示")
        
        if not self.connector:
            print("❌ 请先创建connector实例")
            return
        
        try:
            # 创建虚拟检查点
            dummy_checkpoint = self.connector.build_dummy_checkpoint()
            print("✅ 虚拟检查点创建成功")
            print(f"   类型: {type(dummy_checkpoint).__name__}")
            print(f"   has_more: {dummy_checkpoint.has_more}")
            print(f"   todo_mailboxes: {dummy_checkpoint.todo_mailboxes}")
            print(f"   current_mailbox: {dummy_checkpoint.current_mailbox}")
            
            # 演示检查点JSON序列化
            checkpoint_json = dummy_checkpoint.model_dump_json()
            print(f"   JSON长度: {len(checkpoint_json)} 字符")
            
            # 演示检查点验证
            validated_checkpoint = self.connector.validate_checkpoint_json(checkpoint_json)
            print("✅ 检查点JSON验证通过")
            
        except Exception as e:
            print(f"❌ 检查点机制演示失败: {e}")
    
    def show_enterprise_presets(self):
        """显示企业邮箱预设配置"""
        self.print_header("企业邮箱预设配置")
        
        print(f"📋 支持的企业邮箱: {len(self.enterprise_presets)} 种")
        print()
        
        for preset_key, preset_info in self.enterprise_presets.items():
            print(f"🏢 {preset_info['name']}")
            print(f"   服务器: {preset_info['host']}")
            print(f"   端口: {preset_info['port']}")
            print(f"   描述: {preset_info['description']}")
            print(f"   配置说明: {preset_info['setup_notes']}")
            print()
    
    def generate_usage_example(self):
        """生成使用示例"""
        self.print_header("现有IMAP Connector使用示例")
        
        print("📝 正确的使用方式:")
        print()
        
        example_code = '''
# 1. 导入现有的IMAP connector
from onyx.connectors.imap.connector import ImapConnector
from onyx.connectors.credentials_provider import OnyxStaticCredentialsProvider
from onyx.configs.constants import DocumentSource

# 2. 创建connector实例
connector = ImapConnector(
    host="imap.exmail.qq.com",
    port=993,
    mailboxes=["INBOX", "Sent"]  # 可选，不指定则自动检测
)

# 3. 设置凭据
credentials_provider = OnyxStaticCredentialsProvider(
    tenant_id=None,
    connector_name=DocumentSource.IMAP,
    credential_json={
        "imap_username": "user@company.com",
        "imap_password": "your_password"
    }
)
connector.set_credentials_provider(credentials_provider)

# 4. 验证连接
connector.validate_connector_settings()

# 5. 创建检查点并开始同步
checkpoint = connector.build_dummy_checkpoint()
result = connector.load_from_checkpoint(
    start=0,
    end=time.time(),
    checkpoint=checkpoint
)

# 6. 处理同步结果
for document in result.documents:
    print(f"邮件: {document.title}")
'''
        
        print(example_code)
    
    def interactive_demo(self):
        """交互式演示"""
        while True:
            print("\n" + "="*60)
            print("📧 Onyx IMAP Connector管理器")
            print("="*60)
            print("1. 查看现有实现分析")
            print("2. 显示企业邮箱预设")
            print("3. 创建connector实例 (需要真实凭据)")
            print("4. 测试connector验证")
            print("5. 演示检查点机制")
            print("6. 生成使用示例")
            print("0. 退出")
            print("="*60)
            
            choice = input("请选择操作 (0-6): ").strip()
            
            if choice == "0":
                print("👋 退出IMAP Connector管理器")
                break
            elif choice == "1":
                self.show_existing_implementation()
            elif choice == "2":
                self.show_enterprise_presets()
            elif choice == "3":
                host = input("请输入IMAP服务器地址: ").strip()
                username = input("请输入邮箱用户名: ").strip()
                password = input("请输入邮箱密码: ").strip()
                if host and username and password:
                    self.create_connector_instance(host, username, password)
                else:
                    print("❌ 请提供完整的连接信息")
            elif choice == "4":
                self.test_connector_validation()
            elif choice == "5":
                self.demonstrate_checkpoint_mechanism()
            elif choice == "6":
                self.generate_usage_example()
            else:
                print("❌ 无效选择，请重试")

def main():
    """主函数"""
    print("📧 基于现有IMAP Connector的管理工具")
    print("📅 启动时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    print("🔍 重要发现: Onyx已经有完整的IMAP connector实现!")
    print("📁 位置: backend/onyx/connectors/imap/")
    print("📊 状态: 生产就绪，功能完整")
    
    manager = IMAPConnectorManager()
    manager.interactive_demo()

if __name__ == "__main__":
    main()
