# Onyx 大模型配置完整分析

## 🤖 支持的LLM提供商

基于对 `backend/onyx/llm/llm_provider_options.py` 的分析，Onyx系统支持以下LLM提供商：

### 📊 LLM提供商总览

| 提供商 | 显示名称 | API密钥 | API Base | API版本 | 部署名称 | 默认模型 | 快速模型 |
|--------|----------|---------|----------|---------|----------|----------|----------|
| **openai** | OpenAI | ✅ 必需 | ❌ 可选 | ❌ 可选 | ❌ 不需要 | gpt-4o | gpt-4o-mini |
| **anthropic** | Anthropic | ✅ 必需 | ❌ 可选 | ❌ 可选 | ❌ 不需要 | claude-3-7-sonnet-20250219 | claude-3-5-sonnet-20241022 |
| **azure** | Azure OpenAI | ✅ 必需 | ✅ 必需 | ✅ 必需 | ✅ 必需 | - | - |
| **bedrock** | AWS Bedrock | ❌ 可选 | ❌ 可选 | ❌ 可选 | ❌ 不需要 | claude-3-5-sonnet-20241022-v2:0 | claude-3-5-sonnet-20241022-v2:0 |
| **vertex_ai** | GCP Vertex AI | ❌ 不需要 | ❌ 可选 | ❌ 可选 | ❌ 不需要 | gemini-2.0-flash | gemini-2.0-flash-lite |

## 🔧 详细提供商配置

### 1. OpenAI 配置
```yaml
提供商名称: openai
显示名称: OpenAI
配置要求:
  - API密钥: 必需
  - API Base: 可选 (默认: https://api.openai.com/v1)
  - API版本: 可选

支持的模型 (25个):
主要模型:
  - o4-mini, o3-mini, o1-mini, o3, o1
  - gpt-4, gpt-4.1, gpt-4o, gpt-4o-mini
  - gpt-4-turbo, gpt-4-turbo-preview
  - gpt-3.5-turbo 系列

默认可见模型:
  - o1, o3-mini, gpt-4o, gpt-4o-mini

默认配置:
  - 主模型: gpt-4o
  - 快速模型: gpt-4o-mini
```

### 2. Anthropic 配置
```yaml
提供商名称: anthropic
显示名称: Anthropic
配置要求:
  - API密钥: 必需
  - API Base: 可选
  - API版本: 可选

支持的模型:
  - claude-3-7-sonnet-20250219
  - claude-3-5-sonnet-20241022
  - claude-3-opus-20240229
  - claude-3-haiku-20240307

默认可见模型:
  - claude-3-5-sonnet-20241022
  - claude-3-7-sonnet-20250219

默认配置:
  - 主模型: claude-3-7-sonnet-20250219
  - 快速模型: claude-3-5-sonnet-20241022
```

### 3. Azure OpenAI 配置
```yaml
提供商名称: azure
显示名称: Azure OpenAI
配置要求:
  - API密钥: 必需
  - API Base: 必需 (Azure端点URL)
  - API版本: 必需 (如: 2024-02-01)
  - 部署名称: 必需

特殊配置:
  - 单模型支持: 每个部署只支持一个模型
  - 部署名称必需: 需要Azure部署名称

支持的模型:
  - 所有OpenAI模型 (通过Azure部署)
```

### 4. AWS Bedrock 配置
```yaml
提供商名称: bedrock
显示名称: AWS Bedrock
配置要求:
  - API密钥: 可选 (可使用IAM角色)
  - AWS区域: 必需
  - AWS访问密钥: 可选
  - AWS秘密密钥: 可选

自定义配置:
  - AWS_REGION_NAME: 必需
  - AWS_ACCESS_KEY_ID: 可选
  - AWS_SECRET_ACCESS_KEY: 可选

支持的模型:
  - anthropic.claude-3-5-sonnet-20241022-v2:0
  - meta.llama3-1-70b-instruct-v1:0
  - meta.llama3-1-8b-instruct-v1:0
  - mistral.mistral-large-2402-v1:0

默认配置:
  - 主模型: anthropic.claude-3-5-sonnet-20241022-v2:0
  - 快速模型: anthropic.claude-3-5-sonnet-20241022-v2:0
```

### 5. GCP Vertex AI 配置
```yaml
提供商名称: vertex_ai
显示名称: GCP Vertex AI
配置要求:
  - 凭据文件: 必需 (JSON格式)
  - 位置: 可选 (默认: us-east1)

自定义配置:
  - VERTEX_CREDENTIALS_FILE: 必需 (JSON凭据文件)
  - VERTEX_LOCATION: 可选 (默认: us-east1)

支持的模型 (18个):
Gemini 2.5 Pro:
  - gemini-2.5-pro-preview-06-05
  - gemini-2.5-pro-preview-05-06

Gemini 2.0 Flash:
  - gemini-2.0-flash
  - gemini-2.0-flash-lite
  - gemini-2.0-flash-001
  - gemini-2.0-flash-exp

Gemini 1.5:
  - gemini-1.5-pro, gemini-1.5-pro-001, gemini-1.5-pro-002
  - gemini-1.5-flash, gemini-1.5-flash-001, gemini-1.5-flash-002

Claude (通过Vertex):
  - claude-sonnet-4, claude-opus-4
  - claude-3-7-sonnet@20250219

默认配置:
  - 主模型: gemini-2.0-flash
  - 快速模型: gemini-2.0-flash-lite
```

## 🎯 模型选择策略

### 按用途分类

#### 💬 聊天对话 (主模型)
- **OpenAI**: gpt-4o, o1, o3
- **Anthropic**: claude-3-7-sonnet-20250219
- **Vertex AI**: gemini-2.0-flash
- **Bedrock**: anthropic.claude-3-5-sonnet-20241022-v2:0

#### ⚡ 快速响应 (快速模型)
- **OpenAI**: gpt-4o-mini, o3-mini
- **Anthropic**: claude-3-5-sonnet-20241022
- **Vertex AI**: gemini-2.0-flash-lite
- **Bedrock**: anthropic.claude-3-5-sonnet-20241022-v2:0

#### 🖼️ 视觉理解
- **OpenAI**: gpt-4-vision-preview, gpt-4o
- **Anthropic**: claude-3-opus-20240229
- **Vertex AI**: gemini-1.5-pro, gemini-2.0-flash

## 🔑 API密钥配置

### 配置方式
1. **环境变量**: 在 `.env` 文件中配置
2. **管理界面**: 通过Web界面配置
3. **数据库**: 存储在PostgreSQL中

### 环境变量示例
```bash
# OpenAI
GEN_AI_API_KEY=sk-your-openai-api-key
GEN_AI_MODEL_PROVIDER=openai
GEN_AI_MODEL_VERSION=gpt-4o

# Anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-01

# AWS Bedrock
AWS_REGION_NAME=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# GCP Vertex AI
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
VERTEX_LOCATION=us-east1
```

## 🎛️ 模型配置参数

### 通用参数
```yaml
temperature: 0.7          # 创造性 (0.0-2.0)
max_tokens: 4096          # 最大输出长度
timeout: 60               # 请求超时 (秒)
max_input_tokens: 128000  # 最大输入长度
```

### 提供商特定参数
```yaml
OpenAI:
  - top_p: 1.0
  - frequency_penalty: 0.0
  - presence_penalty: 0.0

Anthropic:
  - top_p: 1.0
  - top_k: 40

Azure OpenAI:
  - deployment_name: 必需
  - api_version: 必需

Bedrock:
  - region: 必需
  - aws_access_key_id: 可选
  - aws_secret_access_key: 可选

Vertex AI:
  - location: us-east1
  - credentials_file: 必需
```

## 📈 成本分析

### 按提供商的成本结构

#### OpenAI 成本 (USD/1M tokens)
```
gpt-4o:
  - 输入: $2.50
  - 输出: $10.00

gpt-4o-mini:
  - 输入: $0.15
  - 输出: $0.60

o1:
  - 输入: $15.00
  - 输出: $60.00
```

#### Anthropic 成本 (USD/1M tokens)
```
claude-3-7-sonnet:
  - 输入: $3.00
  - 输出: $15.00

claude-3-5-sonnet:
  - 输入: $3.00
  - 输出: $15.00
```

#### 其他提供商
- **Azure**: 与OpenAI相同，但可能有企业折扣
- **Bedrock**: 按AWS定价，通常比直接API便宜
- **Vertex AI**: 按Google Cloud定价

## 🔄 模型切换和配置

### 动态模型切换
- ✅ 支持运行时切换模型
- ✅ 支持按用户/助手配置不同模型
- ✅ 支持A/B测试不同模型
- ✅ 支持成本优化的模型选择

### 配置优先级
1. **用户覆盖** - 用户选择的模型
2. **助手配置** - 助手特定的模型
3. **全局默认** - 系统默认模型

### 配置管理
- **Web界面**: `/admin/configuration/llm`
- **API端点**: `/api/admin/llm/provider`
- **数据库表**: `llm_provider`, `model_configuration`

---

**🎯 总结**: Onyx支持5个主要LLM提供商，75+个模型，支持动态配置和切换，具有完整的成本控制和管理功能。
