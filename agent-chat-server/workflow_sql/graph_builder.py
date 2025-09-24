# Copyright (c) 2025 左岚. All rights reserved.
"""SQL智能体图构建器模块

本模块提供主要的图构建器类，用于构建SQL智能体工作流的LangGraph状态图。
"""

import logging
import os
# 修复相对导入问题，使用绝对导入
import sys
from typing import Any

from langchain_core.language_models import BaseLanguageModel
from langgraph.graph import START, MessagesState, StateGraph

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from workflow_sql.config import AgentConfig  # 智能体配置
from workflow_sql.database import SQLDatabaseManager  # 数据库管理器
from workflow_sql.nodes import AnswerGenerationNode, ChartGenerationNode, CheckQueryNode, GenerateQueryNode, GetSchemaNode, ListTablesNode, should_continue  # 图节点
from workflow_sql.tools import SQLToolManager  # SQL工具管理器

logger = logging.getLogger(__name__)


class SQLAgentGraphBuilder:
    """SQL智能体状态图构建器"""

    def __init__(
        self,
        config: AgentConfig,
        llm: BaseLanguageModel,
        db_manager: SQLDatabaseManager,
        tool_manager: SQLToolManager
    ) -> None:
        """初始化图构建器

        Args:
            config: 智能体配置
            llm: 语言模型实例
            db_manager: 数据库管理器实例
            tool_manager: 工具管理器实例
        """
        self.config = config
        self.llm = llm
        self.db_manager = db_manager
        self.tool_manager = tool_manager
        self.builder = StateGraph(MessagesState)

        # 初始化节点
        self.list_tables_node = ListTablesNode(tool_manager)
        self.get_schema_node = GetSchemaNode(tool_manager, llm)
        self.generate_query_node = GenerateQueryNode(tool_manager, llm, db_manager)
        self.check_query_node = CheckQueryNode(tool_manager, llm, db_manager)
        self.answer_generation_node = AnswerGenerationNode(llm)
        self.chart_generation_node = ChartGenerationNode(llm)

    def add_nodes(self) -> None:
        """向图中添加所有节点"""
        logger.info("向图中添加节点")

        # 添加自定义节点
        self.builder.add_node(self.list_tables_node.name, self.list_tables_node)
        self.builder.add_node(self.get_schema_node.name, self.get_schema_node)
        self.builder.add_node(self.generate_query_node.name, self.generate_query_node)
        self.builder.add_node(self.check_query_node.name, self.check_query_node)
        self.builder.add_node(self.answer_generation_node.name, self.answer_generation_node)
        self.builder.add_node(self.chart_generation_node.name, self.chart_generation_node)

        logger.info("所有节点添加成功")

    def add_edges(self) -> None:
        """向图中添加所有边"""
        logger.info("向图中添加边")

        # 定义完整工作流程
        self.builder.add_edge(START, "list_tables")                    # 开始 -> 列出表
        self.builder.add_edge("list_tables", "get_relative_schema")    # 列出表 -> 获取相关结构
        self.builder.add_edge("get_relative_schema", "generate_query") # 获取相关结构 -> 生成查询

        # 基于是否需要查询验证的条件边
        self.builder.add_conditional_edges(
            "generate_query",
            should_continue,
        )

        # 查询执行完成后生成最终答案，然后生成图表
        self.builder.add_edge("check_query", "answer_generation")      # 检查查询 -> 生成答案
        self.builder.add_edge("answer_generation", "chart_generation")  # 生成答案 -> 生成图表

        logger.info("所有边添加成功")

    def build_graph(self) -> Any:
        """构建并返回编译后的图

        Returns:
            编译后的LangGraph状态图
        """
        logger.info("构建SQL智能体图")

        try:
            # 构建前验证工具
            if not self.tool_manager.validate_tools():
                raise RuntimeError("所需工具不可用")

            # 添加节点和边
            self.add_nodes()
            self.add_edges()

            # 编译图
            graph = self.builder.compile()

            logger.info("图构建成功")
            return graph

        except Exception as e:
            logger.error(f"图构建失败: {e}")
            raise RuntimeError(f"图构建失败: {e}") from e


def create_sql_agent_graph(config: AgentConfig, llm: BaseLanguageModel) -> Any:
    """使用给定配置创建SQL智能体图

    Args:
        config: 智能体配置
        llm: 语言模型实例

    Returns:
        编译后的LangGraph状态图
    """
    logger.info("创建SQL智能体图")

    # 创建管理器
    db_manager = SQLDatabaseManager(config.database)
    tool_manager = SQLToolManager(db_manager, llm)

    # 创建并构建图
    builder = SQLAgentGraphBuilder(config, llm, db_manager, tool_manager)
    graph = builder.build_graph()

    logger.info("SQL智能体图创建成功")
    return graph
