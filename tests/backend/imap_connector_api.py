#!/usr/bin/env python3
"""
企业IMAP邮箱连接器后端API实现
基于Gmail connector的API设计
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import imaplib
import ssl
from datetime import datetime
import asyncio
import logging

# 模拟Onyx的核心导入 (实际实现时需要真实导入)
logger = logging.getLogger(__name__)

class IMAPConfigModel(BaseModel):
    """IMAP配置模型"""
    imap_server: str = Field(..., description="IMAP服务器地址")
    imap_port: int = Field(default=993, description="IMAP端口")
    use_ssl: bool = Field(default=True, description="是否使用SSL")
    username: str = Field(..., description="邮箱用户名")
    password: str = Field(..., description="邮箱密码")
    folders: List[str] = Field(default=["INBOX"], description="同步文件夹")
    exclude_folders: List[str] = Field(default=["Trash", "Spam"], description="排除文件夹")
    batch_size: int = Field(default=100, ge=10, le=1000, description="批处理大小")
    max_attachment_size: int = Field(default=10485760, description="最大附件大小")
    supported_attachment_types: List[str] = Field(
        default=[".pdf", ".doc", ".docx", ".txt"], 
        description="支持的附件类型"
    )

class IMAPTestResult(BaseModel):
    """IMAP测试结果"""
    success: bool
    message: str
    server_info: Optional[Dict[str, Any]] = None
    folders: Optional[List[str]] = None
    email_count: Optional[int] = None

class IMAPSyncStatus(BaseModel):
    """IMAP同步状态"""
    is_syncing: bool
    progress: float  # 0.0 - 1.0
    current_folder: Optional[str] = None
    processed_emails: int = 0
    total_emails: int = 0
    errors: List[str] = []
    last_sync_time: Optional[datetime] = None

class IMAPConnectorAPI:
    """IMAP连接器API类"""
    
    def __init__(self):
        self.router = APIRouter(prefix="/api/manage/admin/connector/imap", tags=["IMAP Connector"])
        self._setup_routes()
        self._sync_status: Dict[str, IMAPSyncStatus] = {}
    
    def _setup_routes(self):
        """设置API路由"""
        
        @self.router.post("/test", response_model=IMAPTestResult)
        async def test_imap_connection(config: IMAPConfigModel):
            """测试IMAP连接"""
            return await self._test_connection(config)
        
        @self.router.post("/save")
        async def save_imap_config(config: IMAPConfigModel):
            """保存IMAP配置"""
            return await self._save_config(config)
        
        @self.router.get("/folders")
        async def get_imap_folders(config: IMAPConfigModel):
            """获取IMAP文件夹列表"""
            return await self._get_folders(config)
        
        @self.router.post("/sync/start")
        async def start_imap_sync(config: IMAPConfigModel, background_tasks: BackgroundTasks):
            """开始IMAP同步"""
            return await self._start_sync(config, background_tasks)
        
        @self.router.get("/sync/status/{connector_id}")
        async def get_sync_status(connector_id: str):
            """获取同步状态"""
            return self._sync_status.get(connector_id, IMAPSyncStatus(is_syncing=False, progress=0.0))
        
        @self.router.post("/sync/stop/{connector_id}")
        async def stop_sync(connector_id: str):
            """停止同步"""
            return await self._stop_sync(connector_id)
    
    async def _test_connection(self, config: IMAPConfigModel) -> IMAPTestResult:
        """测试IMAP连接"""
        try:
            # 创建SSL上下文
            if config.use_ssl:
                context = ssl.create_default_context()
                connection = imaplib.IMAP4_SSL(config.imap_server, config.imap_port, ssl_context=context)
            else:
                connection = imaplib.IMAP4(config.imap_server, config.imap_port)
            
            # 登录
            connection.login(config.username, config.password)
            
            # 获取服务器信息
            server_info = {
                "server": config.imap_server,
                "port": config.imap_port,
                "ssl": config.use_ssl,
                "capabilities": []
            }
            
            # 获取服务器能力
            try:
                status, capabilities = connection.capability()
                if status == 'OK':
                    server_info["capabilities"] = capabilities[0].decode().split()
            except:
                pass
            
            # 获取文件夹列表
            folders = []
            try:
                status, folder_list = connection.list()
                if status == 'OK':
                    for folder_info in folder_list:
                        folder_name = folder_info.decode().split('"')[-2]
                        folders.append(folder_name)
            except:
                pass
            
            # 获取INBOX邮件数量
            email_count = 0
            try:
                status, messages = connection.select('INBOX', readonly=True)
                if status == 'OK':
                    email_count = int(messages[0])
            except:
                pass
            
            # 关闭连接
            connection.logout()
            
            return IMAPTestResult(
                success=True,
                message="IMAP连接测试成功",
                server_info=server_info,
                folders=folders,
                email_count=email_count
            )
            
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP连接失败: {e}")
            return IMAPTestResult(
                success=False,
                message=f"IMAP连接失败: {str(e)}"
            )
        except Exception as e:
            logger.error(f"连接测试异常: {e}")
            return IMAPTestResult(
                success=False,
                message=f"连接测试异常: {str(e)}"
            )
    
    async def _save_config(self, config: IMAPConfigModel) -> Dict[str, Any]:
        """保存IMAP配置"""
        try:
            # 这里应该保存到数据库
            # 实际实现中需要调用Onyx的配置保存API
            
            config_dict = config.dict()
            
            # 加密敏感信息
            # config_dict['password'] = encrypt_password(config.password)
            
            # 保存到数据库
            # connector_id = save_connector_config('imap', config_dict)
            
            logger.info(f"IMAP配置已保存: {config.imap_server}")
            
            return {
                "success": True,
                "message": "IMAP配置保存成功",
                "connector_id": f"imap_{int(time.time())}"  # 模拟ID
            }
            
        except Exception as e:
            logger.error(f"保存IMAP配置失败: {e}")
            raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")
    
    async def _get_folders(self, config: IMAPConfigModel) -> Dict[str, List[str]]:
        """获取IMAP文件夹列表"""
        try:
            if config.use_ssl:
                context = ssl.create_default_context()
                connection = imaplib.IMAP4_SSL(config.imap_server, config.imap_port, ssl_context=context)
            else:
                connection = imaplib.IMAP4(config.imap_server, config.imap_port)
            
            connection.login(config.username, config.password)
            
            # 获取所有文件夹
            status, folder_list = connection.list()
            all_folders = []
            
            if status == 'OK':
                for folder_info in folder_list:
                    try:
                        # 解析文件夹名称
                        folder_line = folder_info.decode()
                        # 简单解析 (实际可能需要更复杂的解析)
                        if '"' in folder_line:
                            folder_name = folder_line.split('"')[-2]
                        else:
                            folder_name = folder_line.split()[-1]
                        all_folders.append(folder_name)
                    except:
                        continue
            
            connection.logout()
            
            # 分类文件夹
            common_folders = ['INBOX', 'Sent', 'Drafts', 'Trash', 'Spam']
            system_folders = [f for f in all_folders if f in common_folders]
            custom_folders = [f for f in all_folders if f not in common_folders]
            
            return {
                "all_folders": all_folders,
                "system_folders": system_folders,
                "custom_folders": custom_folders,
                "recommended_sync": ['INBOX', 'Sent'],
                "recommended_exclude": ['Trash', 'Spam', 'Drafts']
            }
            
        except Exception as e:
            logger.error(f"获取文件夹列表失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取文件夹失败: {str(e)}")
    
    async def _start_sync(self, config: IMAPConfigModel, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """开始IMAP同步"""
        connector_id = f"imap_{config.imap_server}_{int(time.time())}"
        
        # 初始化同步状态
        self._sync_status[connector_id] = IMAPSyncStatus(
            is_syncing=True,
            progress=0.0,
            processed_emails=0,
            total_emails=0
        )
        
        # 添加后台任务
        background_tasks.add_task(self._run_sync_task, connector_id, config)
        
        return {
            "success": True,
            "message": "IMAP同步已开始",
            "connector_id": connector_id
        }
    
    async def _run_sync_task(self, connector_id: str, config: IMAPConfigModel):
        """运行同步任务"""
        try:
            status = self._sync_status[connector_id]
            status.current_folder = "连接中..."
            
            # 创建连接
            if config.use_ssl:
                context = ssl.create_default_context()
                connection = imaplib.IMAP4_SSL(config.imap_server, config.imap_port, ssl_context=context)
            else:
                connection = imaplib.IMAP4(config.imap_server, config.imap_port)
            
            connection.login(config.username, config.password)
            
            # 计算总邮件数
            total_emails = 0
            for folder in config.folders:
                try:
                    connection.select(folder, readonly=True)
                    status_result, messages = connection.search(None, 'ALL')
                    if status_result == 'OK':
                        total_emails += len(messages[0].split())
                except:
                    continue
            
            status.total_emails = total_emails
            processed = 0
            
            # 同步每个文件夹
            for folder in config.folders:
                status.current_folder = folder
                
                try:
                    connection.select(folder, readonly=True)
                    search_status, messages = connection.search(None, 'ALL')
                    
                    if search_status == 'OK':
                        message_ids = messages[0].split()
                        
                        # 批量处理邮件
                        for i in range(0, len(message_ids), config.batch_size):
                            batch_ids = message_ids[i:i + config.batch_size]
                            
                            for msg_id in batch_ids:
                                try:
                                    # 获取邮件 (这里简化处理)
                                    fetch_status, msg_data = connection.fetch(msg_id, '(RFC822)')
                                    if fetch_status == 'OK':
                                        # 实际实现中在这里解析邮件并保存到索引
                                        processed += 1
                                        status.processed_emails = processed
                                        status.progress = processed / total_emails if total_emails > 0 else 1.0
                                        
                                        # 模拟处理时间
                                        await asyncio.sleep(0.1)
                                
                                except Exception as e:
                                    status.errors.append(f"处理邮件失败 (ID: {msg_id}): {str(e)}")
                                    continue
                
                except Exception as e:
                    status.errors.append(f"处理文件夹失败 ({folder}): {str(e)}")
                    continue
            
            connection.logout()
            
            # 完成同步
            status.is_syncing = False
            status.progress = 1.0
            status.last_sync_time = datetime.now()
            status.current_folder = None
            
            logger.info(f"IMAP同步完成: {connector_id}, 处理了 {processed} 封邮件")
            
        except Exception as e:
            logger.error(f"IMAP同步失败: {e}")
            status.is_syncing = False
            status.errors.append(f"同步失败: {str(e)}")
    
    async def _stop_sync(self, connector_id: str) -> Dict[str, Any]:
        """停止同步"""
        if connector_id in self._sync_status:
            self._sync_status[connector_id].is_syncing = False
            return {"success": True, "message": "同步已停止"}
        else:
            raise HTTPException(status_code=404, detail="同步任务不存在")

# 创建路由实例
imap_api = IMAPConnectorAPI()
router = imap_api.router

# 额外的工具函数
class IMAPConnectorUtils:
    """IMAP连接器工具类"""
    
    @staticmethod
    def validate_imap_config(config: Dict[str, Any]) -> List[str]:
        """验证IMAP配置"""
        errors = []
        
        # 检查必需字段
        required_fields = ['imap_server', 'username', 'password']
        for field in required_fields:
            if not config.get(field):
                errors.append(f"缺少必需字段: {field}")
        
        # 检查端口范围
        port = config.get('imap_port', 993)
        if not (1 <= port <= 65535):
            errors.append("端口号必须在1-65535范围内")
        
        # 检查邮箱格式
        username = config.get('username', '')
        if username and '@' not in username:
            errors.append("用户名应该是完整的邮箱地址")
        
        # 检查文件夹配置
        folders = config.get('folders', [])
        if not folders:
            errors.append("至少需要配置一个同步文件夹")
        
        return errors
    
    @staticmethod
    def get_preset_configs() -> Dict[str, Dict[str, Any]]:
        """获取预设配置"""
        return {
            "microsoft_365": {
                "name": "Microsoft 365",
                "imap_server": "outlook.office365.com",
                "imap_port": 993,
                "use_ssl": True,
                "description": "Microsoft 365 Exchange Online"
            },
            "google_workspace": {
                "name": "Google Workspace",
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "use_ssl": True,
                "description": "Google Workspace Gmail"
            },
            "tencent_exmail": {
                "name": "腾讯企业邮箱",
                "imap_server": "imap.exmail.qq.com",
                "imap_port": 993,
                "use_ssl": True,
                "description": "腾讯企业邮箱"
            },
            "aliyun_mail": {
                "name": "阿里云企业邮箱",
                "imap_server": "imap.mxhichina.com",
                "imap_port": 993,
                "use_ssl": True,
                "description": "阿里云企业邮箱"
            },
            "netease_mail": {
                "name": "网易企业邮箱",
                "imap_server": "imap.ym.163.com",
                "imap_port": 993,
                "use_ssl": True,
                "description": "网易企业邮箱"
            },
            "zimbra": {
                "name": "Zimbra",
                "imap_server": "mail.company.com",
                "imap_port": 993,
                "use_ssl": True,
                "description": "Zimbra Collaboration Suite"
            }
        }
    
    @staticmethod
    def estimate_sync_time(email_count: int, batch_size: int = 100) -> Dict[str, Any]:
        """估算同步时间"""
        # 基于经验值估算
        emails_per_minute = 60  # 每分钟处理60封邮件
        
        total_minutes = email_count / emails_per_minute
        hours = int(total_minutes // 60)
        minutes = int(total_minutes % 60)
        
        return {
            "total_emails": email_count,
            "estimated_minutes": int(total_minutes),
            "estimated_time_display": f"{hours}小时{minutes}分钟" if hours > 0 else f"{minutes}分钟",
            "batch_count": (email_count + batch_size - 1) // batch_size,
            "emails_per_minute": emails_per_minute
        }

# 测试API的示例函数
async def test_imap_api():
    """测试IMAP API"""
    print("🧪 测试企业IMAP连接器API")
    
    # 示例配置
    test_config = IMAPConfigModel(
        imap_server="imap.gmail.com",
        imap_port=993,
        use_ssl=True,
        username="test@example.com",
        password="app_password",
        folders=["INBOX"],
        exclude_folders=["Trash", "Spam"]
    )
    
    api = IMAPConnectorAPI()
    
    try:
        # 测试连接
        result = await api._test_connection(test_config)
        print(f"连接测试结果: {result}")
        
        # 测试配置验证
        errors = IMAPConnectorUtils.validate_imap_config(test_config.dict())
        print(f"配置验证: {errors if errors else '✅ 配置有效'}")
        
        # 测试预设配置
        presets = IMAPConnectorUtils.get_preset_configs()
        print(f"预设配置数量: {len(presets)}")
        
        # 测试时间估算
        time_estimate = IMAPConnectorUtils.estimate_sync_time(1000)
        print(f"同步时间估算: {time_estimate}")
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")

if __name__ == "__main__":
    import asyncio
    import time
    
    asyncio.run(test_imap_api())
