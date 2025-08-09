#!/usr/bin/env python3
"""
Onyx 端到端测试脚本
模拟完整的用户使用流程
"""

import requests
import time
import json
import sys
from typing import Dict, Any

class E2ETestRunner:
    def __init__(self):
        self.backend_url = "http://localhost:8080"
        self.frontend_url = "http://localhost:3000"
        self.session = requests.Session()
        self.test_results = []
    
    def print_step(self, step: str):
        """打印测试步骤"""
        print(f"\n🧪 {step}")
        print("-" * 50)
    
    def print_result(self, test_name: str, success: bool, details: str = ""):
        """打印测试结果"""
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status} {test_name}")
        if details:
            print(f"   详情: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
    
    def test_user_authentication(self) -> bool:
        """测试用户认证流程"""
        self.print_step("用户认证测试")
        
        try:
            # 获取认证类型
            response = self.session.get(f"{self.backend_url}/auth/type", timeout=5)
            if response.status_code == 200:
                auth_data = response.json()
                self.print_result("获取认证类型", True, f"认证类型: {auth_data.get('auth_type', 'unknown')}")
            else:
                self.print_result("获取认证类型", False, f"HTTP {response.status_code}")
                return False
            
            # 获取当前用户信息
            response = self.session.get(f"{self.backend_url}/me", timeout=5)
            if response.status_code == 200:
                user_data = response.json()
                self.print_result("获取用户信息", True, f"用户ID: {user_data.get('id', 'unknown')}")
            else:
                self.print_result("获取用户信息", False, f"HTTP {response.status_code}")
                return False
            
            return True
        except Exception as e:
            self.print_result("用户认证流程", False, str(e))
            return False
    
    def test_assistant_management(self) -> bool:
        """测试助手管理功能"""
        self.print_step("助手管理测试")
        
        try:
            # 获取助手列表
            response = self.session.get(f"{self.backend_url}/persona", timeout=5)
            if response.status_code == 200:
                assistants = response.json()
                if isinstance(assistants, list) and len(assistants) > 0:
                    assistant = assistants[0]
                    self.print_result("获取助手列表", True, f"找到 {len(assistants)} 个助手")
                    self.print_result("助手数据完整性", 
                                    'id' in assistant and 'name' in assistant,
                                    f"助手名称: {assistant.get('name', 'unknown')}")
                else:
                    self.print_result("获取助手列表", False, "助手列表为空")
                    return False
            else:
                self.print_result("获取助手列表", False, f"HTTP {response.status_code}")
                return False
            
            return True
        except Exception as e:
            self.print_result("助手管理测试", False, str(e))
            return False
    
    def test_chat_functionality(self) -> bool:
        """测试聊天功能"""
        self.print_step("聊天功能测试")
        
        try:
            # 创建聊天会话
            response = self.session.post(f"{self.backend_url}/chat/create-chat-session", 
                                       json={"persona_id": 1}, timeout=10)
            if response.status_code == 200:
                session_data = response.json()
                session_id = session_data.get('id')
                self.print_result("创建聊天会话", True, f"会话ID: {session_id}")
            else:
                self.print_result("创建聊天会话", False, f"HTTP {response.status_code}")
                return False
            
            # 发送测试消息
            test_message = "这是一个端到端测试消息，请回复确认收到。"
            response = self.session.post(f"{self.backend_url}/chat/send-message",
                                       json={
                                           "message": test_message,
                                           "chat_session_id": session_id,
                                           "persona_id": 1
                                       }, timeout=15)
            
            if response.status_code == 200:
                message_data = response.json()
                reply_message = message_data.get('message', '')
                self.print_result("发送消息", True, f"收到回复: {reply_message[:50]}...")
            else:
                self.print_result("发送消息", False, f"HTTP {response.status_code}")
                return False
            
            return True
        except Exception as e:
            self.print_result("聊天功能测试", False, str(e))
            return False
    
    def test_llm_integration(self) -> bool:
        """测试LLM集成"""
        self.print_step("LLM集成测试")
        
        try:
            # 获取LLM提供商
            response = self.session.get(f"{self.backend_url}/llm/provider", timeout=5)
            if response.status_code == 200:
                providers = response.json()
                if isinstance(providers, list) and len(providers) > 0:
                    provider = providers[0]
                    self.print_result("获取LLM提供商", True, 
                                    f"提供商: {provider.get('name', 'unknown')}")
                    
                    # 检查模型配置
                    models = provider.get('model_configurations', [])
                    self.print_result("模型配置检查", len(models) > 0,
                                    f"可用模型: {len(models)} 个")
                else:
                    self.print_result("获取LLM提供商", False, "提供商列表为空")
                    return False
            else:
                self.print_result("获取LLM提供商", False, f"HTTP {response.status_code}")
                return False
            
            return True
        except Exception as e:
            self.print_result("LLM集成测试", False, str(e))
            return False
    
    def test_frontend_accessibility(self) -> bool:
        """测试前端可访问性"""
        self.print_step("前端可访问性测试")
        
        try:
            # 检查前端主页
            response = self.session.get(f"{self.frontend_url}", timeout=10)
            if response.status_code == 200:
                content = response.text
                
                # 检查关键元素
                checks = [
                    ("页面标题", "Onyx" in content),
                    ("React应用", "react" in content.lower() or "_next" in content),
                    ("CSS样式", "css" in content.lower() or "style" in content.lower()),
                    ("JavaScript", "script" in content.lower())
                ]
                
                for check_name, check_result in checks:
                    self.print_result(check_name, check_result)
                
                return all(result for _, result in checks)
            else:
                self.print_result("前端页面访问", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_result("前端可访问性测试", False, str(e))
            return False
    
    def run_all_tests(self) -> bool:
        """运行所有端到端测试"""
        print("🚀 Onyx 端到端测试套件")
        print("📅 测试时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
        
        # 执行所有测试
        tests = [
            self.test_user_authentication,
            self.test_assistant_management,
            self.test_llm_integration,
            self.test_chat_functionality,
            self.test_frontend_accessibility
        ]
        
        all_passed = True
        for test_func in tests:
            try:
                result = test_func()
                all_passed = all_passed and result
            except Exception as e:
                print(f"❌ 测试执行异常: {e}")
                all_passed = False
        
        # 生成总结报告
        self.print_step("测试总结")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        
        print(f"📊 测试结果: {passed_tests}/{total_tests} 通过")
        print(f"📈 成功率: {passed_tests/total_tests*100:.1f}%")
        
        if all_passed:
            print("\n🎉 所有端到端测试通过！系统运行正常。")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} 个测试失败，请检查系统状态。")
        
        return all_passed

def main():
    """主函数"""
    runner = E2ETestRunner()
    success = runner.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
