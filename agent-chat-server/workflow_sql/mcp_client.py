# Copyright (c) 2025 左岚. All rights reserved.
"""MCP客户端管理模块

本模块提供MCP (Model Context Protocol) 客户端的管理功能。
"""

import logging
from typing import Dict, Any, Optional, List

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool

try:
    # 当作为模块导入时使用相对导入
    from .mcp_config import MCPServerConfig, mcp_config
    from .agent_types import ToolNotFoundError
except ImportError:
    # 当直接运行时使用绝对导入
    from mcp_config import MCPServerConfig, mcp_config
    from agent_types import ToolNotFoundError

logger = logging.getLogger(__name__)


class MCPClientManager:
    """MCP客户端管理器"""
    
    def __init__(self):
        """初始化MCP客户端管理器"""
        self._clients: Dict[str, MultiServerMCPClient] = {}
        self._tools_cache: Dict[str, List[BaseTool]] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._cache_timeout = 300  # 缓存5分钟
    
    async def get_client(self, server_name: str) -> MultiServerMCPClient:
        """获取或创建MCP客户端
        
        Args:
            server_name: 服务器名称
            
        Returns:
            MCP客户端实例
            
        Raises:
            ToolNotFoundError: 如果服务器配置不存在
        """
        if server_name not in self._clients:
            server_config = mcp_config.get_server_config(server_name)
            if not server_config:
                raise ToolNotFoundError(f"未找到MCP服务器配置: {server_name}")
            
            client_config = self._build_client_config(server_config)
            self._clients[server_name] = MultiServerMCPClient(client_config)
            logger.info(f"创建MCP客户端: {server_name}")
        
        return self._clients[server_name]
    
    def _build_client_config(self, server_config: MCPServerConfig) -> Dict[str, Dict[str, Any]]:
        """构建客户端配置
        
        Args:
            server_config: 服务器配置
            
        Returns:
            客户端配置字典
        """
        config_dict = {
            "transport": server_config.transport
        }
        
        if server_config.url:
            config_dict["url"] = server_config.url
        
        if server_config.command:
            config_dict["command"] = server_config.command
        
        if server_config.args:
            config_dict["args"] = server_config.args
        
        if server_config.env:
            config_dict["env"] = server_config.env
        
        return {server_config.name: config_dict}
    
    async def get_tools(self, server_name: str) -> List[BaseTool]:
        """获取指定服务器的工具列表

        Args:
            server_name: 服务器名称

        Returns:
            工具列表
        """
        import time
        current_time = time.time()

        # 检查缓存是否有效
        if (server_name in self._tools_cache and
            server_name in self._cache_timestamps and
            current_time - self._cache_timestamps[server_name] < self._cache_timeout):
            logger.info(f"使用缓存的工具: {server_name}")
            return self._tools_cache[server_name]

        # 获取新的工具
        client = await self.get_client(server_name)
        tools = await client.get_tools()

        # 更新缓存
        self._tools_cache[server_name] = tools
        self._cache_timestamps[server_name] = current_time
        logger.info(f"获取到 {len(tools)} 个工具: {server_name}")

        return self._tools_cache[server_name]
    
    async def get_chart_tools(self) -> List[BaseTool]:
        """获取图表生成工具
        
        Returns:
            图表工具列表
        """
        return await self.get_tools("mcp-server-chart")
    
    def clear_cache(self) -> None:
        """清除工具缓存"""
        self._tools_cache.clear()
        logger.info("MCP工具缓存已清除")
    
    async def close_all(self) -> None:
        """关闭所有客户端连接"""
        for server_name, client in self._clients.items():
            try:
                # 如果客户端有close方法，调用它
                if hasattr(client, 'close'):
                    await client.close()
                logger.info(f"关闭MCP客户端: {server_name}")
            except Exception as e:
                logger.error(f"关闭MCP客户端失败 {server_name}: {e}")
        
        self._clients.clear()
        self._tools_cache.clear()


# 全局MCP客户端管理器实例
mcp_client_manager = MCPClientManager()
