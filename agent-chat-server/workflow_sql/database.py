# Copyright (c) 2025 左岚. All rights reserved.
"""SQL智能体数据库管理模块

本模块提供数据库连接管理和SQL操作功能。
"""

import logging
from typing import List, Optional

from langchain_community.utilities import SQLDatabase

# 修复相对导入问题，使用绝对导入
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from workflow_sql.config import DatabaseConfig  # 数据库配置类
from workflow_sql.agent_types import DatabaseConnectionError, DatabaseDialect, QueryExecutionError  # 异常和类型定义


logger = logging.getLogger(__name__)


class SQLDatabaseManager:
    """SQL数据库管理器"""

    def __init__(self, config: DatabaseConfig) -> None:
        """初始化数据库管理器

        Args:
            config: 数据库配置
        """
        self.config = config
        self._db: Optional[SQLDatabase] = None
        self._dialect: Optional[DatabaseDialect] = None

    @property
    def db(self) -> SQLDatabase:
        """获取数据库连接，如果需要则创建连接"""
        if self._db is None:
            self._connect()
        return self._db

    def _connect(self) -> None:
        """建立数据库连接"""
        try:
            logger.info(f"连接数据库: {self.config.uri}")
            self._db = SQLDatabase.from_uri(
                self.config.uri,
                max_string_length=10000,      # 最大字符串长度
                include_tables=None,          # 包含所有表
                sample_rows_in_table_info=3   # 表信息中的示例行数
            )
            self._dialect = self._detect_dialect()
            logger.info(f"数据库连接成功 - 方言: {self._dialect.value}, URI: {self.config.uri}")  # 优化日志信息
        except Exception as e:
            logger.error(f"数据库连接失败 - URI: {self.config.uri}, 错误: {e}")  # 增强错误日志
            raise DatabaseConnectionError(f"数据库连接失败: {e}") from e

    def _detect_dialect(self) -> DatabaseDialect:
        """检测数据库方言"""
        if self._db is None:
            raise DatabaseConnectionError("数据库未连接")

        dialect_str = self._db.dialect.lower()

        if "sqlite" in dialect_str:
            return DatabaseDialect.SQLITE
        elif "postgresql" in dialect_str or "postgres" in dialect_str:
            return DatabaseDialect.POSTGRESQL
        elif "mysql" in dialect_str:
            return DatabaseDialect.MYSQL
        elif "mssql" in dialect_str or "sqlserver" in dialect_str:
            return DatabaseDialect.MSSQL
        elif "oracle" in dialect_str:
            return DatabaseDialect.ORACLE
        else:
            logger.warning(f"未知方言: {dialect_str}，默认使用SQLite")
            return DatabaseDialect.SQLITE

    def get_dialect(self) -> DatabaseDialect:
        """获取数据库方言"""
        if self._dialect is None:
            self._connect()
        return self._dialect

    def get_table_names(self) -> List[str]:
        """获取可用表名列表"""
        try:
            tables = self.db.get_usable_table_names()
            logger.debug(f"获取表名成功 - 共 {len(tables)} 个表: {tables}")  # 优化日志格式
            return tables
        except Exception as e:
            logger.error(f"获取表名失败 - 错误详情: {e}")  # 统一错误日志格式
            raise QueryExecutionError(f"获取表名失败: {e}") from e

    def execute_query(self, query: str) -> str:
        """执行SQL查询并返回结果

        Args:
            query: 要执行的SQL查询

        Returns:
            查询结果字符串
        """
        try:
            logger.debug(f"开始执行SQL查询: {query[:100]}...")  # 限制日志中查询长度
            result = self.db.run(query)
            logger.debug(f"SQL查询执行成功 - 结果长度: {len(str(result))} 字符")  # 优化成功日志
            return result
        except Exception as e:
            logger.error(f"SQL查询执行失败 - 查询: {query[:50]}..., 错误: {e}")  # 增强错误日志
            raise QueryExecutionError(f"查询执行失败: {e}") from e

    def get_table_schema(self, table_names: Optional[List[str]] = None) -> str:
        """获取指定表的结构信息

        Args:
            table_names: 要获取结构的表名列表，如果为None则获取所有表

        Returns:
            表结构信息字符串
        """
        try:
            if table_names is None:
                table_names = self.get_table_names()

            logger.debug(f"获取表结构: {table_names}")
            schema = self.db.get_table_info(table_names=table_names)
            logger.debug(f"表结构获取成功，长度: {len(schema)}")
            return schema
        except Exception as e:
            logger.error(f"获取表结构失败: {e}")
            raise QueryExecutionError(f"获取表结构失败: {e}") from e
