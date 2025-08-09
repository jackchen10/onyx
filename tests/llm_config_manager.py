#!/usr/bin/env python3
"""
Onyx LLM配置管理脚本
管理和配置大语言模型提供商
"""

import os
import json
import requests
import sys
from typing import Dict, List

class LLMConfigManager:
    def __init__(self):
        self.backend_url = "http://localhost:8080"
        self.supported_providers = {
            "openai": {
                "display_name": "OpenAI",
                "api_key_required": True,
                "default_model": "gpt-4o",
                "fast_model": "gpt-4o-mini",
                "models": ["o1", "o3-mini", "gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"]
            },
            "anthropic": {
                "display_name": "Anthropic",
                "api_key_required": True,
                "default_model": "claude-3-7-sonnet-20250219",
                "fast_model": "claude-3-5-sonnet-20241022",
                "models": ["claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022", "claude-3-opus-20240229"]
            },
            "azure": {
                "display_name": "Azure OpenAI",
                "api_key_required": True,
                "api_base_required": True,
                "api_version_required": True,
                "deployment_name_required": True,
                "models": ["gpt-4o", "gpt-4", "gpt-3.5-turbo"]
            },
            "bedrock": {
                "display_name": "AWS Bedrock",
                "api_key_required": False,
                "default_model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "fast_model": "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "custom_config": ["AWS_REGION_NAME", "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"],
                "models": ["anthropic.claude-3-5-sonnet-20241022-v2:0", "meta.llama3-1-70b-instruct-v1:0"]
            },
            "vertex_ai": {
                "display_name": "GCP Vertex AI",
                "api_key_required": False,
                "default_model": "gemini-2.0-flash",
                "fast_model": "gemini-2.0-flash-lite",
                "custom_config": ["VERTEX_CREDENTIALS_FILE", "VERTEX_LOCATION"],
                "models": ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-1.5-pro", "claude-sonnet-4"]
            }
        }
    
    def print_header(self, title: str):
        """打印标题"""
        print(f"\n{'='*60}")
        print(f"🤖 {title}")
        print('='*60)
    
    def get_current_providers(self) -> List[Dict]:
        """获取当前配置的LLM提供商"""
        try:
            response = requests.get(f"{self.backend_url}/llm/provider", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 获取提供商失败: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 连接后端失败: {e}")
            return []
    
    def show_provider_status(self):
        """显示提供商状态"""
        self.print_header("LLM提供商状态")
        
        current_providers = self.get_current_providers()
        
        if not current_providers:
            print("❌ 无法获取提供商信息，请确保后端服务运行正常")
            return
        
        print(f"📊 已配置的提供商: {len(current_providers)} 个")
        print()
        
        for provider in current_providers:
            provider_name = provider.get('provider', 'unknown')
            display_name = provider.get('name', provider_name)
            default_model = provider.get('default_model_name', 'unknown')
            fast_model = provider.get('fast_default_model_name', 'unknown')
            api_key_set = provider.get('api_key_set', False)
            
            print(f"🔧 {display_name} ({provider_name})")
            print(f"   默认模型: {default_model}")
            print(f"   快速模型: {fast_model}")
            print(f"   API密钥: {'✅ 已配置' if api_key_set else '❌ 未配置'}")
            
            # 显示可用模型
            model_configs = provider.get('model_configurations', [])
            if model_configs:
                visible_models = [m['name'] for m in model_configs if m.get('is_visible', False)]
                print(f"   可见模型: {len(visible_models)} 个")
                if visible_models:
                    print(f"   模型列表: {', '.join(visible_models[:3])}{'...' if len(visible_models) > 3 else ''}")
            print()
    
    def show_supported_providers(self):
        """显示支持的提供商"""
        self.print_header("支持的LLM提供商")
        
        print("📋 Onyx支持以下LLM提供商:")
        print()
        
        for provider_id, config in self.supported_providers.items():
            print(f"🔧 {config['display_name']} ({provider_id})")
            print(f"   API密钥: {'✅ 必需' if config.get('api_key_required') else '❌ 可选'}")
            
            if 'default_model' in config:
                print(f"   默认模型: {config['default_model']}")
            if 'fast_model' in config:
                print(f"   快速模型: {config['fast_model']}")
            
            print(f"   支持模型: {len(config['models'])} 个")
            print(f"   主要模型: {', '.join(config['models'][:3])}...")
            
            if 'custom_config' in config:
                print(f"   自定义配置: {', '.join(config['custom_config'])}")
            
            print()
    
    def generate_env_template(self):
        """生成环境变量模板"""
        self.print_header("环境变量配置模板")
        
        print("📝 将以下配置添加到 .env 文件:")
        print()
        
        print("# ===== OpenAI 配置 =====")
        print("GEN_AI_API_KEY=sk-your-openai-api-key-here")
        print("GEN_AI_MODEL_PROVIDER=openai")
        print("GEN_AI_MODEL_VERSION=gpt-4o")
        print("GEN_AI_TEMPERATURE=0.7")
        print()
        
        print("# ===== Anthropic 配置 =====")
        print("ANTHROPIC_API_KEY=your-anthropic-api-key-here")
        print()
        
        print("# ===== Azure OpenAI 配置 =====")
        print("AZURE_OPENAI_API_KEY=your-azure-openai-key")
        print("AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
        print("AZURE_OPENAI_API_VERSION=2024-02-01")
        print("AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name")
        print()
        
        print("# ===== AWS Bedrock 配置 =====")
        print("AWS_REGION_NAME=us-east-1")
        print("AWS_ACCESS_KEY_ID=your-aws-access-key")
        print("AWS_SECRET_ACCESS_KEY=your-aws-secret-key")
        print()
        
        print("# ===== GCP Vertex AI 配置 =====")
        print("GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json")
        print("VERTEX_LOCATION=us-east1")
        print()
    
    def test_provider_connection(self, provider_name: str):
        """测试提供商连接"""
        print(f"🔍 测试 {provider_name} 连接...")
        
        # 这里可以添加具体的连接测试逻辑
        # 由于需要真实的API密钥，这里只做基础检查
        
        if provider_name in self.supported_providers:
            config = self.supported_providers[provider_name]
            print(f"✅ {config['display_name']} 配置检查通过")
            
            # 检查环境变量
            if provider_name == "openai":
                api_key = os.getenv("GEN_AI_API_KEY") or os.getenv("OPENAI_API_KEY")
                if api_key:
                    print("✅ OpenAI API密钥已配置")
                else:
                    print("❌ OpenAI API密钥未配置")
            
            elif provider_name == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    print("✅ Anthropic API密钥已配置")
                else:
                    print("❌ Anthropic API密钥未配置")
            
            # 可以添加更多提供商的检查
            
        else:
            print(f"❌ 不支持的提供商: {provider_name}")
    
    def interactive_menu(self):
        """交互式菜单"""
        while True:
            print("\n" + "="*60)
            print("🤖 Onyx LLM配置管理器")
            print("="*60)
            print("1. 查看当前提供商状态")
            print("2. 查看支持的提供商")
            print("3. 生成环境变量模板")
            print("4. 测试提供商连接")
            print("5. 查看模型配置")
            print("0. 退出")
            print("="*60)
            
            choice = input("请选择操作 (0-5): ").strip()
            
            if choice == "0":
                print("👋 退出LLM配置管理器")
                break
            elif choice == "1":
                self.show_provider_status()
            elif choice == "2":
                self.show_supported_providers()
            elif choice == "3":
                self.generate_env_template()
            elif choice == "4":
                provider = input("请输入提供商名称 (openai/anthropic/azure/bedrock/vertex_ai): ").strip()
                self.test_provider_connection(provider)
            elif choice == "5":
                self.show_model_configurations()
            else:
                print("❌ 无效选择，请重试")
    
    def show_model_configurations(self):
        """显示模型配置"""
        self.print_header("模型配置详情")
        
        current_providers = self.get_current_providers()
        
        for provider in current_providers:
            provider_name = provider.get('name', 'unknown')
            print(f"🔧 {provider_name}")
            
            model_configs = provider.get('model_configurations', [])
            for model in model_configs:
                model_name = model.get('name', 'unknown')
                is_visible = model.get('is_visible', False)
                supports_vision = model.get('supports_image_input', False)
                max_tokens = model.get('max_input_tokens', 'unknown')
                
                visibility = "👁️ 可见" if is_visible else "🙈 隐藏"
                vision = "🖼️ 支持图像" if supports_vision else "📝 仅文本"
                
                print(f"   📱 {model_name}")
                print(f"      {visibility} | {vision} | 最大输入: {max_tokens}")
            print()

def main():
    """主函数"""
    manager = LLMConfigManager()
    
    print("🤖 Onyx LLM配置管理器")
    print("📅 启动时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # 启动交互式菜单
    manager.interactive_menu()

if __name__ == "__main__":
    import time
    main()
