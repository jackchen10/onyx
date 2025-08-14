# Vespa搜索引擎配置实践指南

## 🎯 概述

本指南提供Onyx工程中Vespa搜索引擎的详细配置说明和最佳实践，帮助开发者理解和优化混合检索系统。

## 📋 目录

1. [环境配置](#环境配置)
2. [Schema配置详解](#schema配置详解)
3. [混合检索参数调优](#混合检索参数调优)
4. [性能优化配置](#性能优化配置)
5. [监控与调试](#监控与调试)
6. [故障排除](#故障排除)

## ⚙️ 环境配置

### 基础环境变量

```bash
# Vespa连接配置
VESPA_HOST=localhost                    # Vespa主机地址
VESPA_PORT=8081                        # Vespa HTTP端口
VESPA_TENANT_PORT=19071                # Vespa管理端口

# 部署配置
VESPA_DEPLOYMENT_ZIP=/app/onyx/vespa-app.zip
VESPA_CONFIG_SERVER_HOST=localhost     # 配置服务器地址

# 性能配置
VESPA_SEARCHER_THREADS=2               # 搜索线程数
NUM_RETRIES_ON_STARTUP=10              # 启动重试次数

# 语言配置
VESPA_LANGUAGE_OVERRIDE=en             # 强制语言设置
```

### Docker Compose配置

```yaml
services:
  index:
    image: vespaengine/vespa:8.526.15
    container_name: vespa
    ports:
      - "8081:8081"     # HTTP查询端口
      - "19071:19071"   # 配置端口
    volumes:
      - vespa_data:/opt/vespa/var
    environment:
      - VESPA_CONFIGSERVERS=vespa
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/ApplicationStatus"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
```

## 🗄️ Schema配置详解

### 1. 基础文档结构

```vespa
schema onyx_chunk {
    document onyx_chunk {
        # 核心标识字段
        field document_id type string {
            indexing: summary | attribute
            rank: filter
            attribute: fast-search
        }
        
        field chunk_id type int {
            indexing: summary | attribute
        }
        
        # 文本内容字段
        field title type string {
            indexing: summary | index | attribute
            index: enable-bm25
            match: text
        }
        
        field content type string {
            indexing: summary | index
            index: enable-bm25
            match: text
        }
        
        # 向量嵌入字段
        field title_embedding type tensor<float>(x[384]) {
            indexing: attribute | index
            attribute {
                distance-metric: angular
            }
        }
        
        field embeddings type tensor<float>(t{},x[384]) {
            indexing: attribute | index
            attribute {
                distance-metric: angular
            }
        }
    }
}
```

### 2. 高级字段配置

```vespa
# 元数据字段
field source_type type string {
    indexing: summary | attribute
    rank: filter
    attribute: fast-search
}

field doc_updated_at type long {
    indexing: summary | attribute
    rank: filter
}

# 权限控制
field access_control_list type weightedset<string> {
    indexing: summary | attribute
    rank: filter
}

# 文档集合
field document_sets type weightedset<string> {
    indexing: summary | attribute
    rank: filter
}

# 提升因子
field boost type int {
    indexing: summary | attribute
    rank: filter
}
```

### 3. 知识图谱支持

```vespa
struct kg_relationship {
    field source type string {}
    field rel_type type string {}
    field target type string {}
}

field kg_relationships type array<kg_relationship> {
    indexing: summary | attribute
    struct-field source {
        indexing: attribute
        attribute: fast-search
    }
    struct-field rel_type {
        indexing: attribute
        attribute: fast-search
    }
    struct-field target {
        indexing: attribute
        attribute: fast-search
    }
}
```

## 🔍 混合检索参数调优

### 1. Alpha参数配置

```python
# 默认混合权重配置
HYBRID_ALPHA = 0.5          # 语义检索权重50%
HYBRID_ALPHA_KEYWORD = 0.4  # 关键词检索中向量权重40%

# 动态调整策略
def get_optimal_alpha(query_type: str, query_length: int) -> float:
    """根据查询类型和长度动态调整alpha值"""
    if query_type == "factual":
        return 0.3  # 事实性查询偏向关键词
    elif query_type == "conceptual":
        return 0.7  # 概念性查询偏向语义
    elif query_length < 3:
        return 0.2  # 短查询偏向关键词
    else:
        return 0.5  # 默认平衡
```

### 2. 标题内容比例调优

```python
# 标题内容权重配置
TITLE_CONTENT_RATIO = 0.3  # 标题权重30%，内容权重70%

# 根据文档类型调整
def get_title_content_ratio(source_type: str) -> float:
    """根据数据源类型调整标题内容比例"""
    ratios = {
        "confluence": 0.4,  # Wiki类文档标题更重要
        "slack": 0.2,       # 聊天消息标题不重要
        "email": 0.3,       # 邮件标题中等重要
        "pdf": 0.5,         # PDF文档标题很重要
    }
    return ratios.get(source_type, 0.3)
```

### 3. 时间衰减配置

```python
# 时间衰减参数
DOC_TIME_DECAY = 0.5  # 基础衰减因子
BASE_RECENCY_DECAY = 1.0
FAVOR_RECENT_DECAY_MULTIPLIER = 3.0

# 衰减公式: 1 / (1 + decay_factor * years_old)
def calculate_recency_bias(doc_age_years: float, decay_factor: float) -> float:
    """计算基于文档年龄的新近度偏置"""
    return 1.0 / (1.0 + decay_factor * doc_age_years)
```

## 🎯 Ranking Profile优化

### 1. 语义优先Profile

```vespa
rank-profile hybrid_search_semantic_base_384 inherits default, default_rank {
    inputs {
        query(query_embedding) tensor<float>(x[384])
        query(alpha) double: 0.5
        query(title_content_ratio) double: 0.3
        query(decay_factor) double: 0.5
    }

    function title_vector_score() {
        expression {
            max(closeness(field, embeddings), closeness(field, title_embedding))
        }
    }

    # 第一阶段：快速向量筛选
    first-phase {
        expression: query(title_content_ratio) * closeness(field, title_embedding) + (1 - query(title_content_ratio)) * closeness(field, embeddings)
    }

    # 全局阶段：精确混合评分
    global-phase {
        expression {
            (
                # 向量相似度分数
                query(alpha) * (
                    (query(title_content_ratio) * normalize_linear(title_vector_score))
                    +
                    ((1 - query(title_content_ratio)) * normalize_linear(closeness(field, embeddings)))
                )
            )
            +
            # 关键词相似度分数
            (
                (1 - query(alpha)) * (
                    (query(title_content_ratio) * normalize_linear(bm25(title)))
                    +
                    ((1 - query(title_content_ratio)) * normalize_linear(bm25(content)))
                )
            )
        }
        # 应用各种提升因子
        * document_boost
        * recency_bias
        * aggregated_chunk_boost
        
        rerank-count: 1000
    }

    # 输出匹配特征用于调试
    match-features {
        bm25(title)
        bm25(content)
        closeness(field, title_embedding)
        closeness(field, embeddings)
        document_boost
        recency_bias
        aggregated_chunk_boost
        closest(embeddings)
    }
}
```

### 2. 关键词优先Profile

```vespa
rank-profile hybrid_search_keyword_base_384 inherits default, default_rank {
    # 第一阶段：BM25关键词筛选
    first-phase {
        expression: query(title_content_ratio) * bm25(title) + (1 - query(title_content_ratio)) * bm25(content)
    }
    
    # 全局阶段：与语义Profile相同的混合评分
    global-phase {
        expression {
            # 相同的混合评分公式
        }
        rerank-count: 1000
    }
}
```

### 3. 管理员搜索Profile

```vespa
rank-profile admin_search inherits default, default_rank {
    first-phase {
        expression: bm25(content) + (5 * bm25(title))
    }
    
    # 不使用向量检索，纯关键词匹配
    # 适用于管理界面的精确搜索
}
```

## 🚀 性能优化配置

### 1. 服务配置优化

```xml
<services version="1.0">
    <container id="default" version="1.0">
        <document-api/>
        <search/>
        <http>
            <server id="default" port="8081"/>
        </http>
        <nodes>
            <node hostalias="vespa-node"/>
        </nodes>
        <!-- 调优配置 -->
        <config name="container.qr">
            <filedistributor>
                <maxpendingbytes>134217728</maxpendingbytes>
            </filedistributor>
        </config>
    </container>
    
    <content id="onyx_index" version="1.0">
        <redundancy>1</redundancy>
        <documents>
            <document type="onyx_chunk" mode="index"/>
        </documents>
        <nodes>
            <node hostalias="vespa-node" distribution-key="0"/>
        </nodes>
        
        <!-- 性能调优 -->
        <tuning>
            <resource-limits>
                <disk>0.85</disk>
                <memory>0.8</memory>
            </resource-limits>
        </tuning>
        
        <engine>
            <proton>
                <tuning>
                    <searchnode>
                        <requestthreads>
                            <persearch>4</persearch>
                        </requestthreads>
                        <flushstrategy>
                            <native>
                                <total>
                                    <maxmemorygain>134217728</maxmemorygain>
                                </total>
                            </native>
                        </flushstrategy>
                    </searchnode>
                </tuning>
            </proton>
        </engine>
        
        <!-- 摘要配置 -->
        <config name="vespa.config.search.summary.juniperrc">
            <max_matches>3</max_matches>
            <length>750</length>
            <surround_max>350</surround_max>
            <min_length>300</min_length>
        </config>
    </content>
</services>
```

### 2. 查询优化参数

```python
# 查询参数优化
VESPA_TIMEOUT = 30  # 查询超时时间
MAX_ID_SEARCH_QUERY_SIZE = 1000  # 批量查询最大大小

# 目标命中数动态调整
def calculate_target_hits(num_to_retrieve: int) -> int:
    """动态计算目标命中数"""
    return max(10 * num_to_retrieve, 1000)

# 查询参数构建
def build_query_params(
    query: str,
    query_embedding: list[float],
    hybrid_alpha: float,
    num_hits: int,
    ranking_profile: str
) -> dict:
    """构建优化的查询参数"""
    return {
        "yql": build_yql_query(query),
        "query": query,
        "input.query(query_embedding)": str(query_embedding),
        "input.query(alpha)": hybrid_alpha,
        "hits": num_hits,
        "ranking.profile": ranking_profile,
        "timeout": VESPA_TIMEOUT,
        # 性能优化参数
        "presentation.timing": True,
        "model.defaultIndex": "content",
        "model.type": "weakAnd",
    }
```

### 3. 索引优化策略

```python
# 批量索引配置
NUM_THREADS = 8  # 索引线程数
BATCH_SIZE = 100  # 批量大小

def optimize_indexing_performance():
    """索引性能优化配置"""
    return {
        "max_workers": NUM_THREADS,
        "batch_size": BATCH_SIZE,
        "timeout": 300,  # 5分钟超时
        "retry_attempts": 3,
        "backoff_factor": 2,
    }

# 文档预处理优化
def preprocess_document(content: str) -> str:
    """文档预处理优化"""
    # 移除无效Unicode字符
    content = remove_invalid_unicode_chars(content)
    # 限制文档长度
    if len(content) > 50000:
        content = content[:50000] + "..."
    return content
```

## 📊 监控与调试

### 1. 查询性能监控

```python
# 启用详细时间信息
LOG_VESPA_TIMING_INFORMATION = True

# 查询监控装饰器
def monitor_query_performance(func):
    """查询性能监控装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"Query completed in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Query failed after {duration:.3f}s: {e}")
            raise
    return wrapper

# 性能指标收集
class VespaMetrics:
    def __init__(self):
        self.query_count = 0
        self.total_time = 0.0
        self.error_count = 0
    
    def record_query(self, duration: float, success: bool):
        self.query_count += 1
        self.total_time += duration
        if not success:
            self.error_count += 1
    
    def get_stats(self) -> dict:
        return {
            "avg_latency": self.total_time / max(self.query_count, 1),
            "error_rate": self.error_count / max(self.query_count, 1),
            "total_queries": self.query_count,
        }
```

### 2. 匹配特征分析

```python
def analyze_match_features(vespa_response: dict) -> dict:
    """分析Vespa返回的匹配特征"""
    features = {}
    for hit in vespa_response.get("root", {}).get("children", []):
        match_features = hit.get("fields", {}).get("matchfeatures", {})
        features[hit["id"]] = {
            "bm25_title": match_features.get("bm25(title)", 0),
            "bm25_content": match_features.get("bm25(content)", 0),
            "vector_title": match_features.get("closeness(field,title_embedding)", 0),
            "vector_content": match_features.get("closeness(field,embeddings)", 0),
            "document_boost": match_features.get("document_boost", 1),
            "recency_bias": match_features.get("recency_bias", 1),
        }
    return features

# 评分分析
def analyze_scoring_distribution(features: dict) -> dict:
    """分析评分分布"""
    bm25_scores = [f["bm25_content"] for f in features.values()]
    vector_scores = [f["vector_content"] for f in features.values()]
    
    return {
        "bm25_avg": sum(bm25_scores) / len(bm25_scores),
        "bm25_max": max(bm25_scores),
        "vector_avg": sum(vector_scores) / len(vector_scores),
        "vector_max": max(vector_scores),
    }
```

## 🔧 故障排除

### 1. 常见问题诊断

```python
# 连接问题诊断
def diagnose_vespa_connection():
    """诊断Vespa连接问题"""
    try:
        response = requests.get(f"http://{VESPA_HOST}:{VESPA_PORT}/ApplicationStatus")
        if response.status_code == 200:
            logger.info("Vespa connection OK")
            return True
        else:
            logger.error(f"Vespa returned status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Failed to connect to Vespa: {e}")
        return False

# 索引问题诊断
def diagnose_indexing_issues(document_id: str):
    """诊断索引问题"""
    try:
        # 检查文档是否存在
        response = requests.get(
            f"http://{VESPA_HOST}:{VESPA_PORT}/document/v1/default/onyx_chunk/docid/{document_id}"
        )
        if response.status_code == 200:
            logger.info(f"Document {document_id} indexed successfully")
        else:
            logger.error(f"Document {document_id} not found in index")
    except Exception as e:
        logger.error(f"Error checking document {document_id}: {e}")

# 查询问题诊断
def diagnose_query_issues(query: str, expected_results: int):
    """诊断查询问题"""
    # 简单查询测试
    simple_params = {
        "yql": f"select * from onyx_chunk where userInput('{query}')",
        "hits": expected_results,
    }
    
    try:
        response = requests.post(
            f"http://{VESPA_HOST}:{VESPA_PORT}/search/",
            json=simple_params
        )
        result = response.json()
        actual_hits = len(result.get("root", {}).get("children", []))
        
        logger.info(f"Query '{query}' returned {actual_hits} hits (expected {expected_results})")
        
        if actual_hits == 0:
            logger.warning("No results found - check indexing and query syntax")
        
        return actual_hits
    except Exception as e:
        logger.error(f"Query diagnosis failed: {e}")
        return 0
```

### 2. 性能问题解决

```python
# 慢查询分析
def analyze_slow_queries(threshold_ms: int = 1000):
    """分析慢查询"""
    slow_queries = []
    
    # 从日志中提取慢查询
    # 实际实现需要根据日志格式调整
    
    for query in slow_queries:
        logger.warning(f"Slow query detected: {query}")
        # 分析查询复杂度
        # 建议优化方案
    
    return slow_queries

# 内存使用优化
def optimize_memory_usage():
    """优化内存使用"""
    recommendations = []
    
    # 检查索引大小
    # 检查查询缓存
    # 检查文档大小
    
    return recommendations
```

---

**文档版本**: v1.0  
**最后更新**: 2025-02-19  
**适用版本**: Onyx v1.0+
