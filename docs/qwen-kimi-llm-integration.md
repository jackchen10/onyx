# Onyx框架集成Qwen3、Kimi K2和DeepSeek模型指南

## 🎯 目标

在Onyx框架中添加对Qwen3、Kimi K2和DeepSeek模型的支持，利用现有的LiteLLM架构实现无缝集成。

## 🔍 现有LLM架构分析

### 📊 Onyx LLM架构概览

Onyx使用**LiteLLM**作为统一的LLM接口层，支持多种LLM提供商：

```python
# 核心架构
DefaultMultiLLM (onyx.llm.chat_llm)
    ↓
LiteLLM Library (统一接口)
    ↓
各种LLM提供商 (OpenAI, Anthropic, Azure, Bedrock, Vertex AI等)
```

### 🏗️ 关键组件

#### 1. LLM工厂 (`backend/onyx/llm/factory.py`)
```python
def get_llm(
    provider: str,           # 提供商名称
    model: str,             # 模型名称
    max_input_tokens: int,  # 最大输入token
    api_key: str | None,    # API密钥
    api_base: str | None,   # API基础URL
    # ... 其他参数
) -> LLM:
    return DefaultMultiLLM(
        model_provider=provider,
        model_name=model,
        # ... 配置参数
    )
```

#### 2. 提供商配置 (`backend/onyx/llm/llm_provider_options.py`)
```python
# 现有提供商配置示例
OPENAI_PROVIDER_NAME = "openai"
ANTHROPIC_PROVIDER_NAME = "anthropic"
BEDROCK_PROVIDER_NAME = "bedrock"
VERTEXAI_PROVIDER_NAME = "vertex_ai"

# 提供商到模型的映射
_PROVIDER_TO_MODELS_MAP = {
    OPENAI_PROVIDER_NAME: OPEN_AI_MODEL_NAMES,
    ANTHROPIC_PROVIDER_NAME: ANTHROPIC_MODEL_NAMES,
    # ...
}
```

#### 3. DefaultMultiLLM (`backend/onyx/llm/chat_llm.py`)
```python
class DefaultMultiLLM(LLM):
    def _completion(self, ...):
        return litellm.completion(
            model=f"{self.config.model_provider}/{self.config.model_name}",
            api_key=self._api_key,
            base_url=self._api_base,
            # ... 其他参数
        )
```

## 🚀 LiteLLM对Qwen和Kimi的支持

### ✅ 验证结果

通过检查LiteLLM，确认支持以下模型：

#### 🤖 Qwen模型支持
```python
# LiteLLM支持的Qwen模型 (部分列表)
qwen_models = [
    'openrouter/qwen/qwen-2.5-coder-32b-instruct',
    'openrouter/qwen/qwen-vl-plus', 
    'openrouter/qwen/qwen3-coder',
    'groq/qwen/qwen3-32b',
    'cerebras/qwen-3-32b',
    'sambanova/Qwen3-32B',
    'nscale/Qwen/Qwen2.5-Coder-32B-Instruct',
    # ... 更多模型
]
```

#### 🌙 Kimi模型支持
```python
# LiteLLM支持的Kimi模型
kimi_models = [
    'groq/moonshotai/kimi-k2-instruct',
    'moonshot/moonshot-v1-8k',
    'moonshot/moonshot-v1-32k',
    'moonshot/moonshot-v1-128k',
]
```

#### 🧠 DeepSeek模型支持
```python
# LiteLLM支持的DeepSeek模型
deepseek_models = [
    'deepseek/deepseek-r1',           # DeepSeek R1 (推理模型)
    'deepseek/deepseek-v3',           # DeepSeek V3 (最新版本)
    'deepseek/deepseek-chat',         # DeepSeek Chat
    'deepseek/deepseek-coder',        # DeepSeek Coder (代码专用)
    'deepseek/deepseek-reasoner',     # DeepSeek Reasoner (推理专用)
    'openrouter/deepseek/deepseek-r1', # 通过OpenRouter
    'azure_ai/deepseek-r1',           # 通过Azure AI
]
```

## 🔧 集成方案

### 方案1: 通过现有提供商集成 (推荐)

#### 1.1 使用OpenRouter集成Qwen3
```python
# 在llm_provider_options.py中添加
OPENROUTER_PROVIDER_NAME = "openrouter"
OPENROUTER_MODEL_NAMES = [
    "qwen/qwen3-coder",
    "qwen/qwen-2.5-coder-32b-instruct",
    "qwen/qwen-vl-plus",
]
OPENROUTER_DEFAULT_MODEL = "qwen/qwen3-coder"

# 添加到提供商映射
_PROVIDER_TO_MODELS_MAP[OPENROUTER_PROVIDER_NAME] = OPENROUTER_MODEL_NAMES
```

#### 1.2 使用Groq集成Kimi K2
```python
# 扩展现有Groq配置
GROQ_PROVIDER_NAME = "groq"  # 可能已存在
GROQ_MODEL_NAMES = [
    # 现有Groq模型...
    "moonshotai/kimi-k2-instruct",  # 添加Kimi K2
    "qwen/qwen3-32b",              # 添加Qwen3
]
```

### 方案2: 添加新的提供商

#### 2.1 添加Qwen提供商
```python
# 在llm_provider_options.py中添加
QWEN_PROVIDER_NAME = "qwen"
QWEN_MODEL_NAMES = [
    "qwen3-coder",
    "qwen-2.5-coder-32b-instruct", 
    "qwen-vl-plus",
]
QWEN_DEFAULT_MODEL = "qwen3-coder"
QWEN_DEFAULT_FAST_MODEL = "qwen3-coder"

# 添加到配置函数
def fetch_available_well_known_llms():
    return [
        # ... 现有提供商
        WellKnownLLMProviderDescriptor(
            name=QWEN_PROVIDER_NAME,
            display_name="Qwen (通义千问)",
            api_key_required=True,
            api_base_required=True,  # 需要自定义API端点
            api_version_required=False,
            custom_config_keys=[],
            model_configurations=fetch_model_configurations_for_provider(QWEN_PROVIDER_NAME),
            default_model=QWEN_DEFAULT_MODEL,
            default_fast_model=QWEN_DEFAULT_FAST_MODEL,
        ),
    ]
```

#### 2.2 添加Moonshot (Kimi)提供商
```python
MOONSHOT_PROVIDER_NAME = "moonshot"
MOONSHOT_MODEL_NAMES = [
    "kimi-k2-instruct",
    "moonshot-v1-8k",
    "moonshot-v1-32k",
    "moonshot-v1-128k",
]
MOONSHOT_DEFAULT_MODEL = "kimi-k2-instruct"
MOONSHOT_VISIBLE_MODEL_NAMES = ["kimi-k2-instruct"]
```

#### 2.3 添加DeepSeek提供商
```python
DEEPSEEK_PROVIDER_NAME = "deepseek"
DEEPSEEK_MODEL_NAMES = [
    "deepseek-r1",           # DeepSeek R1 (推理模型)
    "deepseek-v3",           # DeepSeek V3 (最新版本)
    "deepseek-chat",         # DeepSeek Chat
    "deepseek-coder",        # DeepSeek Coder (代码专用)
    "deepseek-reasoner",     # DeepSeek Reasoner (推理专用)
]
DEEPSEEK_DEFAULT_MODEL = "deepseek-r1"
DEEPSEEK_VISIBLE_MODEL_NAMES = ["deepseek-r1", "deepseek-v3", "deepseek-coder"]
```

## 📝 具体实现步骤

### 步骤1: 修改提供商配置

<function_calls>
<invoke name="view">
<parameter name="path">backend/onyx/llm/llm_provider_options.py
