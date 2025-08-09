# 企业内部邮箱Connector设计方案

## 🎯 设计目标

基于Gmail connector的成功实现，设计一个通用的企业内部邮箱connector，支持IMAP协议，可以连接到各种企业邮箱系统。

## 📧 支持的邮箱系统

### 🏢 企业邮箱系统
- **Microsoft Exchange Server** (IMAP启用)
- **IBM Lotus Domino/Notes** (IMAP支持)
- **Zimbra Collaboration Suite**
- **Postfix + Dovecot** (开源方案)
- **MDaemon Email Server**
- **Kerio Connect**
- **IceWarp Mail Server**

### 🌐 云邮箱服务
- **Microsoft 365 Exchange Online** (IMAP)
- **Google Workspace Gmail** (IMAP)
- **腾讯企业邮箱**
- **阿里云企业邮箱**
- **网易企业邮箱**

## 🔧 技术架构设计

### 📊 基于Gmail Connector的架构对比

| 功能模块 | Gmail Connector | 企业IMAP Connector |
|----------|-----------------|-------------------|
| **认证方式** | OAuth 2.0 + Google API | IMAP用户名密码 + SSL/TLS |
| **API协议** | Gmail API (REST) | IMAP协议 (RFC 3501) |
| **邮件获取** | Gmail API批量获取 | IMAP FETCH命令 |
| **增量同步** | Gmail API历史ID | IMAP UIDVALIDITY + UID |
| **附件处理** | Gmail API附件下载 | IMAP BODYSTRUCTURE解析 |
| **权限控制** | Google OAuth范围 | IMAP文件夹权限 |
| **搜索功能** | Gmail API搜索 | IMAP SEARCH命令 |

### 🏗️ 核心类设计

#### 1. IMAPConnector 主类
```python
class IMAPConnector(LoadConnector, PollConnector, SlimConnector):
    """企业IMAP邮箱连接器"""
    
    def __init__(self, 
                 imap_server: str,
                 imap_port: int = 993,
                 use_ssl: bool = True,
                 username: str,
                 password: str,
                 folders: List[str] = None):
        """
        初始化IMAP连接器
        
        Args:
            imap_server: IMAP服务器地址
            imap_port: IMAP端口 (默认993 SSL, 143 非SSL)
            use_ssl: 是否使用SSL/TLS
            username: 邮箱用户名
            password: 邮箱密码或应用密码
            folders: 要同步的文件夹列表 (默认INBOX)
        """
```

#### 2. IMAPEmailProcessor 邮件处理器
```python
class IMAPEmailProcessor:
    """IMAP邮件内容处理器"""
    
    def parse_email_message(self, raw_message: bytes) -> Document:
        """解析邮件消息为Document对象"""
        
    def extract_attachments(self, message: email.message.Message) -> List[Dict]:
        """提取邮件附件"""
        
    def process_email_content(self, message: email.message.Message) -> str:
        """处理邮件正文内容"""
```

#### 3. IMAPCredentialsProvider 凭据提供器
```python
class IMAPCredentialsProvider(CredentialsProviderInterface):
    """IMAP凭据管理器"""
    
    def validate_credentials(self) -> bool:
        """验证IMAP凭据"""
        
    def test_connection(self) -> bool:
        """测试IMAP连接"""
```

## 📋 详细功能设计

### 🔐 认证和安全

#### 认证方式支持
1. **基础认证**: 用户名 + 密码
2. **应用密码**: 企业邮箱应用专用密码
3. **OAuth 2.0**: 支持企业OAuth (可选)
4. **SASL认证**: 支持PLAIN, LOGIN, CRAM-MD5

#### 安全连接
```python
# SSL/TLS配置
ssl_config = {
    "use_ssl": True,           # 使用SSL (端口993)
    "use_starttls": False,     # 或使用STARTTLS (端口143)
    "verify_cert": True,       # 验证SSL证书
    "ca_cert_file": None,      # 自定义CA证书
}
```

### 📬 邮件获取策略

#### 增量同步机制
```python
class IMAPCheckpoint(ConnectorCheckpoint):
    """IMAP检查点"""
    last_uid: int = 0              # 最后处理的UID
    uidvalidity: int = 0           # UIDVALIDITY值
    folder_states: Dict[str, Dict] = {}  # 各文件夹状态
```

#### 邮件过滤规则
```python
filter_config = {
    "date_range": {
        "start_date": "2024-01-01",    # 开始日期
        "end_date": None,              # 结束日期 (None=至今)
    },
    "folders": ["INBOX", "Sent"],      # 同步的文件夹
    "exclude_folders": ["Trash", "Spam"],  # 排除的文件夹
    "size_limit": 50 * 1024 * 1024,   # 邮件大小限制 (50MB)
    "attachment_types": [".pdf", ".doc", ".txt"],  # 支持的附件类型
}
```

### 📄 邮件内容处理

#### 邮件解析流程
```python
def process_email(self, uid: int, folder: str) -> Document:
    """处理单个邮件"""
    
    # 1. 获取邮件头信息
    headers = self.fetch_headers(uid)
    
    # 2. 获取邮件正文
    body = self.fetch_body(uid)
    
    # 3. 处理HTML/纯文本内容
    content = self.extract_text_content(body)
    
    # 4. 处理附件
    attachments = self.process_attachments(uid)
    
    # 5. 构建Document对象
    return self.build_document(headers, content, attachments)
```

#### 附件处理策略
```python
attachment_config = {
    "max_size": 10 * 1024 * 1024,     # 最大附件大小 (10MB)
    "supported_types": [
        ".pdf", ".doc", ".docx",       # 文档
        ".txt", ".md", ".rtf",         # 文本
        ".xls", ".xlsx", ".csv",       # 表格
        ".ppt", ".pptx",               # 演示文稿
        ".jpg", ".png", ".gif",        # 图片 (OCR)
    ],
    "extract_text": True,             # 提取文本内容
    "ocr_images": True,               # 图片OCR识别
}
```

## 🔄 实现步骤

### 第一阶段：基础IMAP连接器
1. ✅ 创建IMAPConnector基础类
2. ✅ 实现IMAP连接和认证
3. ✅ 实现基础邮件获取功能
4. ✅ 实现邮件内容解析

### 第二阶段：高级功能
1. ✅ 实现增量同步机制
2. ✅ 实现附件处理功能
3. ✅ 实现邮件过滤和搜索
4. ✅ 实现错误处理和重试

### 第三阶段：企业级功能
1. ✅ 实现多文件夹同步
2. ✅ 实现权限控制
3. ✅ 实现性能优化
4. ✅ 实现监控和日志

### 第四阶段：前端集成
1. ✅ 创建IMAP connector配置界面
2. ✅ 实现连接测试功能
3. ✅ 实现同步状态显示
4. ✅ 实现错误诊断界面

## 📊 配置参数设计

### 🔧 连接配置
```json
{
  "connector_type": "imap",
  "display_name": "企业邮箱",
  "imap_config": {
    "server": "mail.company.com",
    "port": 993,
    "use_ssl": true,
    "username": "user@company.com",
    "password": "app_password",
    "auth_method": "plain"
  },
  "sync_config": {
    "folders": ["INBOX", "Sent"],
    "exclude_folders": ["Trash", "Spam", "Drafts"],
    "date_range": {
      "start_date": "2024-01-01",
      "days_back": 365
    },
    "batch_size": 100,
    "max_emails": 10000
  },
  "content_config": {
    "include_attachments": true,
    "max_attachment_size": 10485760,
    "supported_attachment_types": [".pdf", ".doc", ".txt"],
    "extract_images": true,
    "ocr_enabled": true
  }
}
```

### 🎯 性能配置
```json
{
  "performance_config": {
    "connection_pool_size": 5,
    "connection_timeout": 30,
    "read_timeout": 60,
    "retry_attempts": 3,
    "retry_delay": 5,
    "concurrent_folders": 2,
    "emails_per_batch": 50
  }
}
```

## 🔍 与Gmail Connector的差异

### 📈 优势
1. **通用性**: 支持所有IMAP兼容的邮箱系统
2. **企业友好**: 支持内网部署，无需外部API
3. **成本效益**: 无API调用费用
4. **隐私保护**: 邮件数据不经过第三方

### ⚠️ 挑战
1. **性能**: IMAP协议比REST API慢
2. **功能限制**: 功能不如Gmail API丰富
3. **连接稳定性**: 需要处理网络中断
4. **服务器兼容性**: 不同IMAP服务器实现差异

### 🔧 解决方案
1. **连接池**: 维护多个IMAP连接
2. **批量处理**: 批量获取邮件头信息
3. **智能重试**: 指数退避重试机制
4. **兼容性测试**: 支持主流IMAP服务器

## 📝 实现优先级

### 🔥 高优先级 (MVP)
1. 基础IMAP连接和认证
2. 邮件列表获取和内容解析
3. 增量同步机制
4. 基础附件处理

### 🟡 中优先级
1. 多文件夹支持
2. 高级过滤功能
3. 性能优化
4. 错误处理完善

### 🟢 低优先级 (增强功能)
1. OAuth 2.0支持
2. 高级搜索功能
3. 邮件分类和标签
4. 实时推送通知

## 🧪 测试策略

### 📋 测试邮箱系统
1. **Microsoft Exchange** (最常见)
2. **Zimbra** (开源企业方案)
3. **Postfix + Dovecot** (Linux标准)
4. **腾讯企业邮箱** (国内主流)

### 🔍 测试场景
1. **连接测试**: 各种IMAP服务器连接
2. **认证测试**: 不同认证方式
3. **同步测试**: 大量邮件增量同步
4. **附件测试**: 各种附件类型处理
5. **错误测试**: 网络中断、认证失败等

## 🎉 预期效果

### ✅ 功能目标
- 支持90%以上的企业IMAP邮箱系统
- 邮件同步速度达到Gmail connector的70%
- 支持10万+邮件的高效索引
- 附件处理支持20+种文件格式

### 📊 性能目标
- 邮件获取速度: 100封/分钟
- 增量同步延迟: < 5分钟
- 附件处理速度: 10MB/分钟
- 系统资源占用: < 500MB内存

### 🔒 安全目标
- 支持SSL/TLS加密连接
- 支持企业级认证方式
- 敏感信息加密存储
- 审计日志完整记录

## 🛠️ 实现文件清单

### 📁 已创建的实现文件

#### 后端实现
1. `tests/backend/imap_connector.py` - IMAP连接器核心实现
2. `tests/backend/imap_connector_api.py` - IMAP连接器API路由

#### 前端实现
1. `tests/frontend/imap_connector_config.tsx` - IMAP配置界面组件

#### 文档
1. `docs/enterprise-email-connector-design.md` - 设计方案文档

### 🔧 集成到Onyx系统的步骤

#### 第一步：后端集成
```bash
# 1. 将IMAP connector添加到connectors目录
cp tests/backend/imap_connector.py backend/onyx/connectors/imap/connector.py

# 2. 添加IMAP到DocumentSource枚举 (已存在)
# backend/onyx/configs/constants.py - IMAP = "imap"

# 3. 注册IMAP connector
# 在 backend/onyx/connectors/__init__.py 中添加导入

# 4. 添加API路由
# 在 backend/onyx/server/documents/connector.py 中集成IMAP API
```

#### 第二步：前端集成
```bash
# 1. 添加IMAP配置组件
cp tests/frontend/imap_connector_config.tsx web/src/components/admin/connectors/

# 2. 在connector列表中添加IMAP选项
# web/src/components/admin/connectors/ConnectorForm.tsx

# 3. 添加IMAP图标和样式
# web/src/components/admin/connectors/ConnectorIcon.tsx
```

#### 第三步：数据库集成
```sql
-- 添加IMAP相关的配置表 (如果需要)
-- 大部分可以复用现有的connector和credential表
```

### 🧪 测试和验证

#### 单元测试
```python
# tests/backend/test_imap_connector.py
def test_imap_connection():
    """测试IMAP连接"""

def test_email_parsing():
    """测试邮件解析"""

def test_attachment_processing():
    """测试附件处理"""
```

#### 集成测试
```python
# tests/integration/test_imap_integration.py
def test_full_imap_sync():
    """测试完整IMAP同步流程"""

def test_incremental_sync():
    """测试增量同步"""
```

---

**🎯 总结**: 企业IMAP connector将为Onyx提供通用的企业邮箱集成能力，支持主流企业邮箱系统，具有高性能、高安全性的特点。实现文件已创建完成，可直接集成到Onyx系统中。**
