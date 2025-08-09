#!/usr/bin/env python3
"""
简化的Onyx后端测试服务器
用于验证基础功能是否正常
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 设置编码
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONUTF8'] = '1'

# 创建FastAPI应用
app = FastAPI(
    title="Onyx Test API",
    description="Onyx后端测试服务器",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """根路径"""
    return {"message": "Onyx Test API is running!", "status": "ok"}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "onyx-backend",
        "version": "test"
    }

@app.get("/api/health")
async def api_health_check():
    """API健康检查"""
    return {
        "status": "healthy",
        "api_version": "v1",
        "timestamp": "2025-01-09"
    }

@app.get("/api/settings")
async def get_settings():
    """获取设置（模拟）"""
    return {
        "auth_type": "basic",
        "require_email_verification": False,
        "enable_streaming": True
    }

@app.get("/api/connectors")
async def get_connectors():
    """获取连接器列表（模拟）"""
    return {
        "connectors": [
            {
                "name": "Gmail",
                "type": "gmail",
                "status": "available",
                "description": "Gmail邮件连接器"
            },
            {
                "name": "Confluence",
                "type": "confluence",
                "status": "available",
                "description": "Confluence文档连接器"
            },
            {
                "name": "Jira",
                "type": "jira",
                "status": "available",
                "description": "Jira问题跟踪连接器"
            }
        ]
    }

@app.get("/api/manage/admin/standard-settings")
async def get_standard_settings():
    """获取标准设置（模拟）"""
    return {
        "settings": {
            "auth_type": "basic",
            "require_email_verification": False,
            "enable_streaming": True,
            "default_llm_provider": "openai"
        }
    }

@app.get("/api/assistants")
async def get_assistants():
    """获取助手列表（模拟）"""
    return {
        "assistants": [
            {
                "id": 1,
                "name": "默认助手",
                "description": "通用AI助手",
                "status": "active"
            }
        ]
    }

@app.get("/api/auth/type")
async def get_auth_type():
    """获取认证类型"""
    return {
        "auth_type": "basic",
        "requires_verification": False
    }

@app.get("/auth/type")
async def get_auth_type_direct():
    """获取认证类型（直接路径）"""
    return {
        "auth_type": "basic",
        "requires_verification": False,
        "anonymous_user_enabled": True
    }

@app.get("/settings")
async def get_settings_direct():
    """获取设置（直接路径）"""
    return {
        "auto_scroll": True,
        "application_status": "ACTIVE",
        "gpu_enabled": False,
        "maximum_chat_retention_days": None,
        "notifications": [],
        "needs_reindexing": False,
        "anonymous_user_enabled": True,
        "pro_search_enabled": True,
        "temperature_override_enabled": True,
        "query_history_type": "NORMAL"
    }

@app.get("/me")
async def get_current_user():
    """获取当前用户信息"""
    return {
        "id": "test-user",
        "email": "test@example.com",
        "is_active": True,
        "is_superuser": False,
        "is_verified": True,
        "role": "basic"
    }

@app.get("/persona")
async def get_personas():
    """获取助手/人格列表"""
    return [
        {
            "id": 1,
            "name": "默认助手",
            "description": "通用AI助手，可以帮助您处理各种任务",
            "tools": [
                {
                    "id": 1,
                    "name": "search_tool",
                    "description": "搜索工具",
                    "definition": {}
                }
            ],
            "starter_messages": [
                {
                    "name": "搜索文档",
                    "message": "帮我搜索相关文档"
                },
                {
                    "name": "总结内容",
                    "message": "请帮我总结这个内容"
                }
            ],
            "document_sets": [],
            "llm_model_provider_override": None,
            "llm_model_version_override": None,
            "uploaded_image_id": None,
            "icon_shape": 1,
            "icon_color": "#3B82F6",
            "is_public": True,
            "is_visible": True,
            "display_priority": 0,
            "is_default_persona": True,
            "builtin_persona": True,
            "labels": [],
            "owner": None
        }
    ]

@app.get("/input_prompts")
async def get_input_prompts():
    """获取输入提示"""
    return []

@app.get("/connector")
async def get_connectors_list():
    """获取连接器列表"""
    return [
        {
            "id": 1,
            "name": "Gmail",
            "source": "gmail",
            "input_type": "poll",
            "connector_specific_config": {},
            "refresh_freq": 3600,
            "prune_freq": 86400,
            "indexing_start": None,
            "disabled": False
        },
        {
            "id": 2,
            "name": "Confluence",
            "source": "confluence",
            "input_type": "poll",
            "connector_specific_config": {},
            "refresh_freq": 3600,
            "prune_freq": 86400,
            "indexing_start": None,
            "disabled": False
        },
        {
            "id": 3,
            "name": "Jira",
            "source": "jira",
            "input_type": "poll",
            "connector_specific_config": {},
            "refresh_freq": 3600,
            "prune_freq": 86400,
            "indexing_start": None,
            "disabled": False
        }
    ]

@app.get("/chat-sessions")
async def get_chat_sessions():
    """获取聊天会话"""
    return []

@app.get("/document-set")
async def get_document_sets():
    """获取文档集"""
    return []

@app.get("/tag")
async def get_tags():
    """获取标签"""
    return []

@app.get("/folder")
async def get_folders():
    """获取文件夹"""
    return []

@app.get("/llm/provider")
async def get_llm_providers():
    """获取LLM提供商"""
    return [
        {
            "name": "OpenAI",
            "provider": "openai",
            "api_key_set": False,
            "default_model_name": "gpt-3.5-turbo",
            "fast_default_model_name": "gpt-3.5-turbo",
            "is_default_provider": True,
            "model_configurations": [
                {
                    "name": "gpt-3.5-turbo",
                    "description": "GPT-3.5 Turbo",
                    "context_length": 4096,
                    "cost_per_input_token": 0.0015,
                    "cost_per_output_token": 0.002
                },
                {
                    "name": "gpt-4",
                    "description": "GPT-4",
                    "context_length": 8192,
                    "cost_per_input_token": 0.03,
                    "cost_per_output_token": 0.06
                }
            ]
        }
    ]

@app.post("/chat/create-chat-session")
async def create_chat_session():
    """创建聊天会话"""
    return {
        "id": "test-session-1",
        "name": "新聊天",
        "persona_id": 1,
        "time_created": "2025-01-09T10:00:00Z",
        "shared_status": "private",
        "folder_id": None,
        "current_alternate_model": None,
        "current_temperature_override": None,
        "messages": []
    }

@app.post("/chat/send-message")
async def send_message():
    """发送消息"""
    return {
        "message_id": "test-message-1",
        "parent_message": None,
        "latest_child_message": None,
        "message": "这是一个测试回复。Onyx系统正在正常工作！",
        "rephrased_query": None,
        "context_docs": {
            "top_documents": [],
            "predicted_flow": None,
            "predicted_search": None,
            "applied_source_filters": [],
            "applied_time_cutoff": None,
            "recency_bias_multiplier": 1.0
        },
        "message_type": "assistant",
        "time_sent": "2025-01-09T10:00:01Z",
        "citations": {},
        "files": [],
        "tool_calls": [],
        "alternate_assistant_id": None
    }

def main():
    """启动测试服务器"""
    print("🚀 启动Onyx测试服务器...")
    print("📍 服务地址: http://localhost:8080")
    print("📍 API文档: http://localhost:8080/docs")
    print("📍 健康检查: http://localhost:8080/health")
    print("🔄 按 Ctrl+C 停止服务器")
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8080,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
