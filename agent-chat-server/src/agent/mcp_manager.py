# Copyright (c) 2025 左岚. All rights reserved.
"""MCP 工具管理器 - 动态加载和管理 MCP 工具"""

import os
import asyncio
import logging
from typing import Dict, List, Any
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
from agent_config import AgentSystemConfig

logger = logging.getLogger(__name__)

# 设置环境变量以支持阻塞调用
os.environ["BG_JOB_ISOLATED_LOOPS"] = "true"


class MCPToolManager:
    """MCP 工具管理器 - 负责 MCP 工具的动态加载和管理"""

    def __init__(self, config: AgentSystemConfig):
        """初始化 MCP 工具管理器
        
        Args:
            config: 智能体系统配置
        """
        self.config = config
        self.mcp_tools: List[BaseTool] = []
        self.mcp_client: Any = None
        logger.info("MCP 工具管理器初始化")

    async def _load_mcp_tools_async(self) -> List[BaseTool]:
        """异步加载 MCP 工具"""
        try:
            if not self.config.enable_mcp:
                logger.info("ℹ️  MCP 功能已禁用")
                return []

            logger.info("🔧 开始加载 MCP 工具...")

            # 构建 MCP 服务器配置
            server_configs = {}
            for server_name, server_config in self.config.mcp_servers.items():
                if not server_config.enabled:
                    logger.info(f"⏭️  MCP 服务器 {server_name} 已禁用,跳过")
                    continue

                server_configs[server_name] = {
                    "command": server_config.command,
                    "args": server_config.args,
                    "transport": server_config.transport,
                }

            if not server_configs:
                logger.info("ℹ️  没有启用的 MCP 服务器")
                return []

            # 创建 MCP 客户端
            self.mcp_client = MultiServerMCPClient(server_configs)

            # 加载工具
            tools = await self.mcp_client.get_tools()
            
            logger.info(f"✅ 成功加载 {len(tools)} 个 MCP 工具")
            for tool in tools:
                tool_name = getattr(tool, "name", "unknown")
                logger.info(f"  - {tool_name}")

            return tools

        except Exception as e:
            logger.warning(f"⚠️  MCP 工具加载失败: {e}")
            return []

    def load_mcp_tools(self) -> List[BaseTool]:
        """同步方式加载 MCP 工具
        
        Returns:
            MCP 工具列表
        """
        try:
            self.mcp_tools = asyncio.run(self._load_mcp_tools_async())
            return self.mcp_tools
        except Exception as e:
            logger.warning(f"⚠️  同步加载 MCP 工具失败: {e}")
            return []

    def get_tools(self) -> List[BaseTool]:
        """获取已加载的 MCP 工具列表"""
        return self.mcp_tools

    def get_tool_by_name(self, tool_name: str) -> BaseTool | None:
        """根据名称获取 MCP 工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具实例,如果不存在则返回 None
        """
        for tool in self.mcp_tools:
            if getattr(tool, "name", "") == tool_name:
                return tool
        return None

    def get_tools_by_prefix(self, prefix: str) -> List[BaseTool]:
        """根据前缀获取 MCP 工具列表
        
        Args:
            prefix: 工具名称前缀
            
        Returns:
            匹配的工具列表
        """
        return [
            tool for tool in self.mcp_tools
            if getattr(tool, "name", "").startswith(prefix)
        ]

    def reload_tools(self) -> List[BaseTool]:
        """重新加载 MCP 工具(热更新)
        
        Returns:
            重新加载后的工具列表
        """
        logger.info("🔄 重新加载 MCP 工具...")
        return self.load_mcp_tools()

    def get_tool_count(self) -> int:
        """获取已加载的 MCP 工具数量"""
        return len(self.mcp_tools)

    def get_tool_names(self) -> List[str]:
        """获取所有 MCP 工具的名称列表"""
        return [getattr(tool, "name", "unknown") for tool in self.mcp_tools]

