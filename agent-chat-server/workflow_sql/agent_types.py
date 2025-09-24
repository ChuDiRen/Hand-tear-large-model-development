# Copyright (c) 2025 左岚. All rights reserved.
"""SQL智能体的类型定义模块

本模块定义了SQL智能体应用中使用的核心类型、枚举和异常类。
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List

from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState


class DatabaseDialect(Enum):
    """支持的数据库方言枚举"""

    SQLITE = "sqlite"          # SQLite数据库
    POSTGRESQL = "postgresql"  # PostgreSQL数据库
    MYSQL = "mysql"           # MySQL数据库
    MSSQL = "mssql"          # SQL Server数据库
    ORACLE = "oracle"        # Oracle数据库


class BaseNode(ABC):
    """图节点的抽象基类"""

    def __init__(self, name: str) -> None:
        """初始化节点

        Args:
            name: 节点名称
        """
        self.name = name

    @abstractmethod
    def execute(self, state: MessagesState) -> Dict[str, List[BaseMessage]]:
        """执行节点逻辑

        Args:
            state: 当前对话状态

        Returns:
            包含新消息的更新状态
        """
        ...


    def __call__(self, state: MessagesState) -> Dict[str, List[BaseMessage]]:
        """使节点可调用"""
        return self.execute(state)


# 自定义异常类
class SQLAgentError(Exception):
    """SQL智能体基础异常类"""
    pass


class DatabaseConnectionError(SQLAgentError):
    """数据库连接失败时抛出"""
    pass


class QueryExecutionError(SQLAgentError):
    """查询执行失败时抛出"""
    pass


class ToolNotFoundError(SQLAgentError):
    """找不到所需工具时抛出"""
    pass
