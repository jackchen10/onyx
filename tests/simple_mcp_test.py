#!/usr/bin/env python3
"""
简单的MCP服务器测试
用于验证FastMCP的基本功能
"""

import asyncio
import logging
from mcp.server.fastmcp import FastMCP

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建简单的MCP服务器
app = FastMCP("Simple Test Server")

@app.tool()
def hello_world(name: str = "World") -> str:
    """
    简单的问候工具
    
    Args:
        name: 要问候的名字
    
    Returns:
        str: 问候消息
    """
    return f"Hello, {name}!"

@app.tool()
def add_numbers(a: int, b: int) -> int:
    """
    数字相加工具
    
    Args:
        a: 第一个数字
        b: 第二个数字
    
    Returns:
        int: 两数之和
    """
    return a + b

@app.resource("test://info")
def get_server_info() -> str:
    """获取服务器信息"""
    return "这是一个简单的MCP测试服务器"

if __name__ == "__main__":
    logger.info("启动简单MCP测试服务器...")
    app.run()