#!/usr/bin/env python3
"""
企业IMAP邮箱连接器实现
基于Gmail connector设计，支持通用IMAP协议的企业邮箱系统
"""

import imaplib
import email
import ssl
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Iterator, Optional, Tuple
from email.message import Message
from email.header import decode_header
import base64
import re

# 模拟Onyx的核心导入 (实际实现时需要真实导入)
class DocumentSource:
    IMAP = "imap"

class Document:
    def __init__(self, id: str, semantic_identifier: str, sections: List, 
                 source: str, metadata: Dict, doc_updated_at: datetime = None,
                 primary_owners: List = None, secondary_owners: List = None):
        self.id = id
        self.semantic_identifier = semantic_identifier
        self.sections = sections
        self.source = source
        self.metadata = metadata
        self.doc_updated_at = doc_updated_at
        self.primary_owners = primary_owners or []
        self.secondary_owners = secondary_owners or []

class TextSection:
    def __init__(self, text: str, link: str = None):
        self.text = text
        self.link = link

class BasicExpertInfo:
    def __init__(self, email: str, first_name: str = None, last_name: str = None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

class ConnectorCheckpoint:
    def __init__(self, has_more: bool = True):
        self.has_more = has_more

class IMAPCheckpoint(ConnectorCheckpoint):
    """IMAP连接器检查点"""
    def __init__(self, last_uid: int = 0, uidvalidity: int = 0, 
                 folder_states: Dict[str, Dict] = None):
        super().__init__()
        self.last_uid = last_uid
        self.uidvalidity = uidvalidity
        self.folder_states = folder_states or {}

class IMAPConnector:
    """企业IMAP邮箱连接器"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self._connection: Optional[imaplib.IMAP4_SSL] = None
        self._config: Dict[str, Any] = {}
        
    def load_credentials(self, credentials: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """加载IMAP凭据"""
        self._config = credentials
        
        # 验证必需的配置参数
        required_fields = ['imap_server', 'username', 'password']
        for field in required_fields:
            if field not in credentials:
                raise ValueError(f"Missing required field: {field}")
        
        # 测试连接
        if self._test_connection():
            return {"status": "success", "message": "IMAP connection successful"}
        else:
            return {"status": "error", "message": "IMAP connection failed"}
    
    def _test_connection(self) -> bool:
        """测试IMAP连接"""
        try:
            connection = self._create_connection()
            connection.logout()
            return True
        except Exception as e:
            print(f"IMAP连接测试失败: {e}")
            return False
    
    def _create_connection(self) -> imaplib.IMAP4_SSL:
        """创建IMAP连接"""
        server = self._config['imap_server']
        port = self._config.get('imap_port', 993)
        use_ssl = self._config.get('use_ssl', True)
        username = self._config['username']
        password = self._config['password']
        
        if use_ssl:
            # 创建SSL上下文
            context = ssl.create_default_context()
            if not self._config.get('verify_cert', True):
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            connection = imaplib.IMAP4_SSL(server, port, ssl_context=context)
        else:
            connection = imaplib.IMAP4(server, port)
            if self._config.get('use_starttls', False):
                connection.starttls()
        
        # 登录
        connection.login(username, password)
        return connection
    
    def _get_connection(self) -> imaplib.IMAP4_SSL:
        """获取IMAP连接 (带连接池)"""
        if self._connection is None:
            self._connection = self._create_connection()
        
        # 测试连接是否还活着
        try:
            self._connection.noop()
        except:
            # 连接断开，重新创建
            self._connection = self._create_connection()
        
        return self._connection
    
    def _get_folders(self) -> List[str]:
        """获取要同步的文件夹列表"""
        configured_folders = self._config.get('folders', ['INBOX'])
        exclude_folders = self._config.get('exclude_folders', ['Trash', 'Spam', 'Drafts'])
        
        connection = self._get_connection()
        
        # 获取所有可用文件夹
        status, folder_list = connection.list()
        if status != 'OK':
            return configured_folders
        
        available_folders = []
        for folder_info in folder_list:
            # 解析文件夹名称
            folder_name = folder_info.decode().split('"')[-2]
            if folder_name not in exclude_folders:
                available_folders.append(folder_name)
        
        # 返回配置的文件夹与可用文件夹的交集
        if configured_folders == ['INBOX']:
            return ['INBOX'] if 'INBOX' in available_folders else available_folders[:1]
        else:
            return [f for f in configured_folders if f in available_folders]
    
    def _decode_header(self, header_value: str) -> str:
        """解码邮件头"""
        if not header_value:
            return ""
        
        decoded_parts = decode_header(header_value)
        decoded_string = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    try:
                        decoded_string += part.decode(encoding)
                    except (UnicodeDecodeError, LookupError):
                        decoded_string += part.decode('utf-8', errors='ignore')
                else:
                    decoded_string += part.decode('utf-8', errors='ignore')
            else:
                decoded_string += str(part)
        
        return decoded_string
    
    def _extract_email_addresses(self, header_value: str) -> List[Tuple[str, str]]:
        """提取邮件地址和显示名称"""
        if not header_value:
            return []
        
        # 简单的邮件地址提取 (可以使用更复杂的解析器)
        email_pattern = r'([^<>]+)?<([^<>]+@[^<>]+)>|([^<>\s]+@[^<>\s]+)'
        matches = re.findall(email_pattern, header_value)
        
        emails = []
        for match in matches:
            if match[1]:  # 格式: "Name <email@domain.com>"
                name = match[0].strip(' "') if match[0] else ""
                email_addr = match[1].strip()
                emails.append((email_addr, name))
            elif match[2]:  # 格式: "email@domain.com"
                email_addr = match[2].strip()
                emails.append((email_addr, ""))
        
        return emails
    
    def _parse_email_message(self, raw_message: bytes, uid: int, folder: str) -> Optional[Document]:
        """解析邮件消息为Document对象"""
        try:
            # 解析邮件
            message = email.message_from_bytes(raw_message)
            
            # 提取基础信息
            subject = self._decode_header(message.get('Subject', ''))
            if not subject:
                subject = "(no subject)"
            
            from_header = self._decode_header(message.get('From', ''))
            to_header = self._decode_header(message.get('To', ''))
            cc_header = self._decode_header(message.get('Cc', ''))
            date_header = message.get('Date', '')
            message_id = message.get('Message-ID', f"{uid}@{folder}")
            
            # 解析日期
            doc_updated_at = None
            if date_header:
                try:
                    doc_updated_at = email.utils.parsedate_to_datetime(date_header)
                    if doc_updated_at.tzinfo is None:
                        doc_updated_at = doc_updated_at.replace(tzinfo=timezone.utc)
                except:
                    pass
            
            # 提取邮件正文
            body_text = self._extract_email_body(message)
            
            # 构建邮件元数据
            metadata_text = f"Subject: {subject}\n"
            metadata_text += f"From: {from_header}\n"
            if to_header:
                metadata_text += f"To: {to_header}\n"
            if cc_header:
                metadata_text += f"Cc: {cc_header}\n"
            metadata_text += f"Date: {date_header}\n"
            metadata_text += f"Folder: {folder}\n"
            
            # 组合完整内容
            full_content = metadata_text + "\n" + body_text
            
            # 创建文档链接 (企业邮箱可能没有web界面)
            doc_link = f"imap://{self._config['imap_server']}/{folder}/{uid}"
            
            # 创建文档段落
            sections = [TextSection(text=full_content, link=doc_link)]
            
            # 处理附件
            attachments = self._process_attachments(message)
            for attachment in attachments:
                sections.append(TextSection(text=attachment['content'], 
                                          link=attachment.get('link', doc_link)))
            
            # 提取邮件地址信息
            from_emails = self._extract_email_addresses(from_header)
            other_emails = self._extract_email_addresses(to_header + " " + cc_header)
            
            # 构建所有者信息
            primary_owners = [BasicExpertInfo(email=email, first_name=name.split()[0] if name else None,
                                            last_name=" ".join(name.split()[1:]) if name and len(name.split()) > 1 else None)
                            for email, name in from_emails]
            
            secondary_owners = [BasicExpertInfo(email=email, first_name=name.split()[0] if name else None,
                                              last_name=" ".join(name.split()[1:]) if name and len(name.split()) > 1 else None)
                              for email, name in other_emails]
            
            # 创建Document对象
            return Document(
                id=f"{folder}_{uid}",
                semantic_identifier=subject,
                sections=sections,
                source=DocumentSource.IMAP,
                metadata={
                    'folder': folder,
                    'uid': uid,
                    'message_id': message_id,
                    'from': from_header,
                    'to': to_header,
                    'cc': cc_header,
                    'date': date_header,
                    'server': self._config['imap_server']
                },
                doc_updated_at=doc_updated_at,
                primary_owners=primary_owners,
                secondary_owners=secondary_owners
            )
            
        except Exception as e:
            print(f"解析邮件失败 (UID: {uid}): {e}")
            return None
    
    def _extract_email_body(self, message: Message) -> str:
        """提取邮件正文"""
        body_text = ""
        
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))
                
                # 跳过附件
                if "attachment" in content_disposition:
                    continue
                
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            charset = part.get_content_charset() or 'utf-8'
                            body_text += payload.decode(charset, errors='ignore')
                    except:
                        pass
                elif content_type == "text/html":
                    # 如果没有纯文本，使用HTML (需要HTML到文本的转换)
                    if not body_text:
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                charset = part.get_content_charset() or 'utf-8'
                                html_content = payload.decode(charset, errors='ignore')
                                # 简单的HTML标签移除 (实际应使用BeautifulSoup)
                                body_text += re.sub(r'<[^>]+>', '', html_content)
                        except:
                            pass
        else:
            # 非multipart邮件
            try:
                payload = message.get_payload(decode=True)
                if payload:
                    charset = message.get_content_charset() or 'utf-8'
                    body_text = payload.decode(charset, errors='ignore')
            except:
                pass
        
        return body_text.strip()
    
    def _process_attachments(self, message: Message) -> List[Dict[str, Any]]:
        """处理邮件附件"""
        attachments = []
        
        if not message.is_multipart():
            return attachments
        
        for part in message.walk():
            content_disposition = str(part.get("Content-Disposition", ""))
            
            if "attachment" in content_disposition:
                filename = part.get_filename()
                if filename:
                    filename = self._decode_header(filename)
                    
                    # 检查文件类型是否支持
                    supported_types = self._config.get('supported_attachment_types', 
                                                     ['.pdf', '.doc', '.docx', '.txt'])
                    
                    file_ext = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
                    if file_ext not in supported_types:
                        continue
                    
                    # 检查文件大小
                    max_size = self._config.get('max_attachment_size', 10 * 1024 * 1024)  # 10MB
                    payload = part.get_payload(decode=True)
                    if payload and len(payload) > max_size:
                        continue
                    
                    # 提取附件内容 (这里简化处理，实际需要根据文件类型处理)
                    content = f"附件: {filename}\n"
                    if file_ext == '.txt':
                        try:
                            content += payload.decode('utf-8', errors='ignore')
                        except:
                            content += "无法解析附件内容"
                    else:
                        content += f"文件类型: {file_ext}, 大小: {len(payload)} bytes"
                    
                    attachments.append({
                        'filename': filename,
                        'content': content,
                        'size': len(payload) if payload else 0,
                        'type': file_ext
                    })
        
        return attachments
    
    def _fetch_emails_from_folder(self, folder: str, 
                                 start_uid: int = 1, 
                                 end_uid: Optional[int] = None) -> Iterator[List[Document]]:
        """从指定文件夹获取邮件"""
        connection = self._get_connection()
        
        try:
            # 选择文件夹
            status, messages = connection.select(folder, readonly=True)
            if status != 'OK':
                print(f"无法选择文件夹 {folder}: {messages}")
                return
            
            # 获取文件夹中的邮件数量
            num_messages = int(messages[0])
            if num_messages == 0:
                return
            
            print(f"文件夹 {folder} 包含 {num_messages} 封邮件")
            
            # 构建UID范围
            if end_uid is None:
                uid_range = f"{start_uid}:*"
            else:
                uid_range = f"{start_uid}:{end_uid}"
            
            # 搜索邮件UID
            status, uid_data = connection.uid('search', None, 'ALL')
            if status != 'OK':
                return
            
            uids = uid_data[0].split()
            if not uids:
                return
            
            # 过滤UID范围
            filtered_uids = [uid for uid in uids if int(uid) >= start_uid]
            if end_uid:
                filtered_uids = [uid for uid in filtered_uids if int(uid) <= end_uid]
            
            print(f"处理 {len(filtered_uids)} 封邮件 (UID范围: {uid_range})")
            
            # 批量处理邮件
            doc_batch = []
            for i, uid in enumerate(filtered_uids):
                try:
                    # 获取邮件内容
                    status, msg_data = connection.uid('fetch', uid, '(RFC822)')
                    if status != 'OK':
                        continue
                    
                    raw_message = msg_data[0][1]
                    doc = self._parse_email_message(raw_message, int(uid), folder)
                    
                    if doc:
                        doc_batch.append(doc)
                    
                    # 批量返回
                    if len(doc_batch) >= self.batch_size:
                        yield doc_batch
                        doc_batch = []
                    
                    # 进度显示
                    if (i + 1) % 10 == 0:
                        print(f"已处理 {i + 1}/{len(filtered_uids)} 封邮件")
                
                except Exception as e:
                    print(f"处理邮件失败 (UID: {uid}): {e}")
                    continue
            
            # 返回剩余的邮件
            if doc_batch:
                yield doc_batch
                
        except Exception as e:
            print(f"获取文件夹 {folder} 邮件失败: {e}")
        finally:
            try:
                connection.close()
            except:
                pass
    
    def load_from_state(self) -> Iterator[List[Document]]:
        """从状态加载所有邮件 (完整同步)"""
        print("🔄 开始IMAP邮件完整同步...")
        
        folders = self._get_folders()
        print(f"📁 同步文件夹: {folders}")
        
        total_docs = 0
        for folder in folders:
            print(f"\n📂 处理文件夹: {folder}")
            
            for doc_batch in self._fetch_emails_from_folder(folder):
                total_docs += len(doc_batch)
                yield doc_batch
        
        print(f"\n✅ 完整同步完成，共处理 {total_docs} 封邮件")
    
    def poll_source(self, start: float, end: float) -> Iterator[List[Document]]:
        """轮询源获取增量邮件"""
        print(f"🔄 开始IMAP邮件增量同步 (时间范围: {start} - {end})...")
        
        # 将时间戳转换为日期
        start_date = datetime.fromtimestamp(start, tz=timezone.utc)
        end_date = datetime.fromtimestamp(end, tz=timezone.utc)
        
        print(f"📅 同步时间范围: {start_date} 到 {end_date}")
        
        folders = self._get_folders()
        total_docs = 0
        
        for folder in folders:
            print(f"\n📂 增量同步文件夹: {folder}")
            
            # 这里简化处理，实际应该使用IMAP SEARCH命令按日期过滤
            for doc_batch in self._fetch_emails_from_folder(folder):
                # 过滤时间范围内的邮件
                filtered_docs = []
                for doc in doc_batch:
                    if (doc.doc_updated_at and 
                        start_date <= doc.doc_updated_at <= end_date):
                        filtered_docs.append(doc)
                
                if filtered_docs:
                    total_docs += len(filtered_docs)
                    yield filtered_docs
        
        print(f"\n✅ 增量同步完成，共处理 {total_docs} 封新邮件")
    
    def close(self):
        """关闭连接"""
        if self._connection:
            try:
                self._connection.logout()
            except:
                pass
            self._connection = None

# 测试函数
def test_imap_connector():
    """测试IMAP连接器"""
    print("🧪 测试企业IMAP邮箱连接器")
    
    # 示例配置 (需要真实的邮箱配置)
    test_config = {
        'imap_server': 'imap.gmail.com',  # 示例服务器
        'imap_port': 993,
        'use_ssl': True,
        'username': 'test@example.com',   # 需要真实邮箱
        'password': 'app_password',       # 需要真实密码
        'folders': ['INBOX'],
        'exclude_folders': ['Trash', 'Spam'],
        'batch_size': 10,
        'max_attachment_size': 5 * 1024 * 1024,  # 5MB
        'supported_attachment_types': ['.pdf', '.txt', '.doc']
    }
    
    connector = IMAPConnector(batch_size=10)
    
    try:
        # 测试凭据加载
        result = connector.load_credentials(test_config)
        print(f"凭据测试结果: {result}")
        
        if result and result.get('status') == 'success':
            print("✅ IMAP连接器测试成功")
            
            # 可以进行更多测试
            # for doc_batch in connector.load_from_state():
            #     print(f"获取到 {len(doc_batch)} 封邮件")
            #     break  # 只测试第一批
        else:
            print("❌ IMAP连接器测试失败")
    
    except Exception as e:
        print(f"❌ 测试异常: {e}")
    
    finally:
        connector.close()

if __name__ == "__main__":
    test_imap_connector()
