# Copyright (c) 2025 左岚. All rights reserved.
"""SQL智能体工具管理模块

本模块提供SQL数据库工具和其他实用程序的管理功能。
"""

import logging
from typing import List, Optional

from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.language_models import BaseLanguageModel
from langchain_core.tools import BaseTool
from langgraph.prebuilt import ToolNode

# 修复相对导入问题，使用绝对导入
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from workflow_sql.database import SQLDatabaseManager  # 数据库管理器
from workflow_sql.agent_types import ToolNotFoundError  # 工具异常类型


logger = logging.getLogger(__name__)


class SQLToolManager:
    """SQL数据库工具和工具节点管理器"""

    def __init__(self, db_manager: SQLDatabaseManager, llm: BaseLanguageModel) -> None:
        """初始化工具管理器

        Args:
            db_manager: 数据库管理器实例
            llm: 用于工具操作的语言模型
        """
        self.db_manager = db_manager
        self.llm = llm
        self._toolkit: Optional[SQLDatabaseToolkit] = None
        self._tools: Optional[List[BaseTool]] = None
        self._tool_nodes: dict[str, ToolNode] = {}

    @property
    def toolkit(self) -> SQLDatabaseToolkit:
        """获取SQL数据库工具包，如果需要则创建"""
        if self._toolkit is None:
            self._create_toolkit()
        return self._toolkit

    def _create_toolkit(self) -> None:
        """创建SQL数据库工具包"""
        try:
            logger.info("开始创建SQL数据库工具包...")  # 优化开始日志
            self._toolkit = SQLDatabaseToolkit(
                db=self.db_manager.db,
                llm=self.llm
            )
            self._tools = self._toolkit.get_tools()
            tool_names = [tool.name for tool in self._tools]  # 获取工具名称列表
            logger.info(f"SQL工具包创建成功 - 包含 {len(self._tools)} 个工具: {tool_names}")  # 增强成功日志
        except Exception as e:
            logger.error(f"SQL工具包创建失败 - 错误详情: {e}")  # 统一错误日志格式
            raise ToolNotFoundError(f"创建SQL工具包失败: {e}") from e

    def get_all_tools(self) -> List[BaseTool]:
        """获取所有可用工具"""
        if self._tools is None:
            self._create_toolkit()
        return self._tools

    def get_tool_by_name(self, name: str) -> Optional[BaseTool]:
        """按名称获取特定工具

        Args:
            name: 要检索的工具名称

        Returns:
            如果找到则返回工具，否则返回None
        """
        tools = self.get_all_tools()
        for tool in tools:
            if tool.name == name:
                logger.debug(f"找到工具: {name}")
                return tool

        logger.warning(f"未找到工具: {name}")
        return None

    def get_required_tool(self, name: str) -> BaseTool:
        """按名称获取必需工具，如果未找到则抛出错误

        Args:
            name: 要检索的工具名称

        Returns:
            工具

        Raises:
            ToolNotFoundError: 如果未找到工具
        """
        tool = self.get_tool_by_name(name)
        if tool is None:
            available_tools = [t.name for t in self.get_all_tools()]
            logger.error(f"工具查找失败 - 目标工具: '{name}', 可用工具: {available_tools}")  # 添加错误日志
            raise ToolNotFoundError(
                f"未找到必需工具 '{name}'。可用工具: {available_tools}"
            )
        logger.debug(f"工具获取成功 - 工具名称: '{name}'")  # 添加成功日志
        return tool

    def get_schema_tool(self) -> BaseTool:
        """获取结构检索工具"""
        return self.get_required_tool("sql_db_schema")

    def get_query_tool(self) -> BaseTool:
        """获取查询执行工具"""
        return self.get_required_tool("sql_db_query")

    def get_list_tables_tool(self) -> BaseTool:
        """获取表列表工具"""
        return self.get_required_tool("sql_db_list_tables")

    def get_tool_node(self, tool_name: str, node_name: Optional[str] = None) -> ToolNode:
        """获取特定工具的工具节点

        Args:
            tool_name: 工具名称
            node_name: 节点的可选名称（默认为tool_name）

        Returns:
            ToolNode实例
        """
        if node_name is None:
            node_name = tool_name

        if node_name not in self._tool_nodes:
            tool = self.get_required_tool(tool_name)
            self._tool_nodes[node_name] = ToolNode([tool], name=node_name)
            logger.debug(f"创建工具节点: {node_name}")

        return self._tool_nodes[node_name]

    def get_schema_node(self) -> ToolNode:
        """获取结构工具节点"""
        return self.get_tool_node("sql_db_schema", "get_schema")

    def get_query_node(self) -> ToolNode:
        """获取查询工具节点"""
        return self.get_tool_node("sql_db_query", "run_query")

    def list_available_tools(self) -> List[str]:
        """获取可用工具名称列表

        Returns:
            工具名称列表
        """
        tools = self.get_all_tools()
        tool_names = [tool.name for tool in tools]
        logger.debug(f"可用工具: {tool_names}")
        return tool_names

    def validate_tools(self) -> bool:
        """验证所有必需工具是否可用

        Returns:
            如果所有必需工具都可用则返回True，否则返回False
        """
        required_tools = ["sql_db_schema", "sql_db_query", "sql_db_list_tables"]
        available_tools = self.list_available_tools()

        missing_tools = [tool for tool in required_tools if tool not in available_tools]

        if missing_tools:
            logger.error(f"缺少必需工具: {missing_tools}")
            return False

        logger.info("所有必需工具都可用")
        return True
