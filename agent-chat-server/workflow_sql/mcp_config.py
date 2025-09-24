# Copyright (c) 2025 左岚. All rights reserved.
"""MCP服务器配置模块

本模块提供MCP (Model Context Protocol) 服务器的配置管理功能。
"""

import os
from dataclasses import dataclass
from typing import Dict, Optional

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


@dataclass
class MCPServerConfig:
    """MCP服务器配置类"""
    
    name: str                                    # 服务器名称
    transport: str                               # 传输方式 (sse/stdio)
    url: Optional[str] = None                    # SSE连接URL
    command: Optional[str] = None                # stdio命令
    args: Optional[list] = None                  # 命令参数
    env: Optional[Dict[str, str]] = None         # 环境变量


@dataclass
class ChartConfig:
    """图表生成配置类"""
    
    enabled: bool = True                         # 是否启用图表生成
    default_chart_type: str = "bar"             # 默认图表类型
    max_data_points: int = 20                    # 最大数据点数
    chart_width: int = 800                       # 图表宽度
    chart_height: int = 600                      # 图表高度


class MCPConfig:
    """MCP配置管理类"""
    
    def __init__(self):
        """初始化MCP配置"""
        self.servers = self._load_mcp_servers_config()
        self.chart = self._load_chart_config()
    
    def _load_mcp_servers_config(self) -> Dict[str, MCPServerConfig]:
        """加载MCP服务器配置"""
        return {
            "mcp-server-chart": MCPServerConfig(
                name="mcp-server-chart",
                transport="stdio",
                command="npx",
                args=["-y", "@antv/mcp-server-chart"]
            )
        }
    
    def _load_chart_config(self) -> ChartConfig:
        """加载图表配置"""
        return ChartConfig(
            enabled=os.getenv("CHART_ENABLED", "true").lower() == "true",
            default_chart_type=os.getenv("DEFAULT_CHART_TYPE", "bar"),
            max_data_points=int(os.getenv("MAX_DATA_POINTS", "20")),
            chart_width=int(os.getenv("CHART_WIDTH", "800")),
            chart_height=int(os.getenv("CHART_HEIGHT", "600"))
        )
    
    def get_server_config(self, server_name: str) -> Optional[MCPServerConfig]:
        """获取指定服务器配置
        
        Args:
            server_name: 服务器名称
            
        Returns:
            服务器配置或None
        """
        return self.servers.get(server_name)
    
    def validate(self) -> None:
        """验证配置有效性"""
        for server_name, server_config in self.servers.items():
            if server_config.transport == "sse" and not server_config.url:
                raise ValueError(f"SSE传输方式需要URL配置: {server_name}")
            elif server_config.transport == "stdio" and not server_config.command:
                raise ValueError(f"stdio传输方式需要命令配置: {server_name}")


# 全局配置实例
mcp_config = MCPConfig()
