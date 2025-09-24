# Copyright (c) 2025 左岚. All rights reserved.
"""SQL智能体ReAct工具集合

本模块将SQL操作转换为独立的工具函数，支持LLM智能选择和调用。
"""

import logging
from typing import Dict, List, Optional, Any
from langchain_core.tools import tool
from langchain_core.language_models import BaseLanguageModel

# 修复相对导入问题
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from workflow_sql.database import SQLDatabaseManager
from workflow_sql.tools import SQLToolManager
from workflow_sql.cache_manager import (
    get_cached_tables_list, cache_tables_list,
    get_cached_table_schema, cache_table_schema,
    get_cached_database_info, cache_database_info,
    clear_all_cache, get_cache_stats
)

logger = logging.getLogger(__name__)

# 全局变量，用于管理器实例
_db_manager: Optional[SQLDatabaseManager] = None
_tool_manager: Optional[SQLToolManager] = None


def initialize_sql_tools(db_manager: SQLDatabaseManager, tool_manager: SQLToolManager) -> None:
    """初始化SQL工具的全局管理器
    
    Args:
        db_manager: 数据库管理器实例
        tool_manager: SQL工具管理器实例
    """
    global _db_manager, _tool_manager
    _db_manager = db_manager
    _tool_manager = tool_manager
    logger.info("SQL工具管理器初始化完成")


@tool
def get_database_tables() -> str:
    """获取数据库中所有可用的表列表

    Returns:
        包含所有表名的字符串，用逗号分隔
    """
    global _tool_manager

    # 检查缓存
    cached_tables = get_cached_tables_list()
    if cached_tables is not None:
        logger.info(f"使用缓存的表列表: {cached_tables}")
        return ", ".join(cached_tables)

    if _tool_manager is None:
        return "错误: SQL工具管理器未初始化"

    try:
        # 调用底层工具
        list_tables_tool = _tool_manager.get_list_tables_tool()
        tool_call = {
            "name": "sql_db_list_tables",
            "args": {},
            "id": "get_tables_call",
            "type": "tool_call",
        }
        result = list_tables_tool.invoke(tool_call)

        # 缓存结果
        if result.content:
            tables_list = [table.strip() for table in result.content.split(',')]
            cache_tables_list(tables_list)
            logger.info(f"获取并缓存表列表: {tables_list}")
            return result.content
        else:
            return "未找到任何表"

    except Exception as e:
        logger.error(f"获取表列表失败: {e}")
        return f"获取表列表失败: {str(e)}"


@tool
def get_table_schema(table_names: str = "") -> str:
    """获取指定表的结构信息

    Args:
        table_names: 要获取结构的表名，多个表用逗号分隔。如果为空，获取所有表的结构

    Returns:
        表结构信息的详细描述
    """
    global _tool_manager

    # 检查缓存
    cached_schema = get_cached_table_schema(table_names)
    if cached_schema is not None:
        logger.info(f"使用缓存的表结构: {table_names or 'all_tables'}")
        return cached_schema

    if _tool_manager is None:
        return "错误: SQL工具管理器未初始化"

    try:
        # 调用底层工具
        schema_tool = _tool_manager.get_schema_tool()
        tool_call = {
            "name": "sql_db_schema",
            "args": {"table_names": table_names},
            "id": "get_schema_call",
            "type": "tool_call",
        }
        result = schema_tool.invoke(tool_call)

        # 缓存结果
        if result.content:
            cache_table_schema(table_names, result.content)
            logger.info(f"获取并缓存表结构: {table_names or 'all_tables'}")
            return result.content
        else:
            return "未找到表结构信息"

    except Exception as e:
        logger.error(f"获取表结构失败: {e}")
        return f"获取表结构失败: {str(e)}"


@tool
def execute_sql_query(query: str) -> str:
    """执行SQL查询并返回结果
    
    Args:
        query: 要执行的SQL查询语句
        
    Returns:
        查询结果，如果出错则返回错误信息
    """
    global _tool_manager, _db_manager
    
    if _tool_manager is None:
        return "错误: SQL工具管理器未初始化"
    
    if not query.strip():
        return "错误: 查询语句不能为空"
    
    try:
        logger.info(f"执行SQL查询: {query}")
        
        # 调用底层工具
        query_tool = _tool_manager.get_query_tool()
        tool_call = {
            "name": "sql_db_query",
            "args": {"query": query},
            "id": "execute_query_call",
            "type": "tool_call",
        }
        result = query_tool.invoke(tool_call)
        
        if result.content:
            logger.info("SQL查询执行成功")
            return result.content
        else:
            return "查询执行成功，但没有返回结果"
            
    except Exception as e:
        logger.error(f"SQL查询执行失败: {e}")
        return f"查询执行失败: {str(e)}"


@tool
def get_database_info() -> str:
    """获取数据库的基本信息

    Returns:
        数据库类型、连接状态等基本信息
    """
    global _db_manager

    # 检查缓存
    cached_info = get_cached_database_info()
    if cached_info is not None:
        logger.info("使用缓存的数据库信息")
        return cached_info

    if _db_manager is None:
        return "错误: 数据库管理器未初始化"

    try:
        dialect = _db_manager.get_dialect()
        table_count = len(_db_manager.get_table_names())

        info = f"""数据库信息:
- 类型: {dialect.value}
- 表数量: {table_count}
- 连接状态: 正常
- 最大查询结果数: {_db_manager.config.max_query_results}"""

        # 缓存结果
        cache_database_info(info)
        logger.info("获取并缓存数据库信息")
        return info

    except Exception as e:
        logger.error(f"获取数据库信息失败: {e}")
        return f"获取数据库信息失败: {str(e)}"


@tool
def clear_cache() -> str:
    """清除所有缓存的数据库信息

    Returns:
        清除操作的结果
    """
    clear_all_cache()
    logger.info("数据库信息缓存已清除")
    return "缓存已清除，下次查询将重新获取最新信息"


@tool
def get_cache_status() -> str:
    """获取缓存状态信息

    Returns:
        缓存统计信息
    """
    stats = get_cache_stats()

    status = f"""缓存状态:
- 总条目数: {stats['total_entries']}
- 过期条目数: {stats['expired_entries']}
- 总访问次数: {stats['total_accesses']}
- 最大容量: {stats['max_entries']}
- 默认TTL: {stats['default_ttl']}秒
- 缓存键: {', '.join(stats['cache_keys'])}"""

    return status


def get_sql_tools() -> List[Any]:
    """获取所有SQL相关的工具列表

    Returns:
        SQL工具列表
    """
    return [
        analyze_query_complexity,
        get_database_tables,
        get_table_schema,
        execute_sql_query,
        get_database_info,
        clear_cache,
        get_cache_status,
    ]


@tool
def analyze_query_complexity(question: str) -> str:
    """分析用户问题的复杂度，帮助决定查询策略

    Args:
        question: 用户的自然语言问题

    Returns:
        问题复杂度分析和建议的查询策略
    """
    question_lower = question.lower()

    # 简单查询关键词
    simple_keywords = ['多少', 'count', '总数', '数量', '有几个', '列出', 'list', 'show']
    # 复杂查询关键词
    complex_keywords = ['平均', 'average', '最大', 'max', '最小', 'min', '分组', 'group',
                       '排序', 'order', '连接', 'join', '比较', '分析', '统计']

    simple_score = sum(1 for keyword in simple_keywords if keyword in question_lower)
    complex_score = sum(1 for keyword in complex_keywords if keyword in question_lower)

    if simple_score > complex_score and simple_score > 0:
        strategy = "简单查询策略：可以直接构造SQL查询，可能需要基本的表信息"
        complexity = "简单"
    elif complex_score > 0:
        strategy = "复杂查询策略：需要了解表结构和关系，可能需要多表连接或聚合函数"
        complexity = "复杂"
    else:
        strategy = "中等查询策略：建议先了解相关表的结构信息"
        complexity = "中等"

    return f"问题复杂度: {complexity}\n建议策略: {strategy}"


def get_sql_system_prompt() -> str:
    """获取SQL智能体的系统提示词

    Returns:
        专门为SQL查询优化的系统提示词
    """
    return """# SQL数据库智能助手 v2.0

你是一个高度智能的SQL数据库助手，专门设计用于高效、准确地处理各种复杂度的数据库查询任务。

## 🎯 核心使命
- 理解自然语言问题并转换为精确的SQL查询
- 智能选择最优的工具组合和执行策略
- 提供深入的数据分析和业务洞察

## 🛠️ 专业工具集
1. **analyze_query_complexity**: 智能分析问题复杂度，制定最优查询策略
2. **get_database_tables**: 获取数据库表列表（自动缓存）
3. **get_table_schema**: 获取表结构信息（支持多表，自动缓存）
4. **execute_sql_query**: 执行SQL查询并返回结果
5. **get_database_info**: 获取数据库基本信息和配置
6. **get_cache_status**: 查看缓存状态和统计信息
7. **clear_cache**: 清除缓存（强制获取最新信息）

## 📋 智能决策流程

### 🔍 第一步：问题理解与策略制定
**必须执行**：使用 `analyze_query_complexity` 分析用户问题
- 识别问题类型（简单计数、复杂分析、多表关联等）
- 确定所需信息范围（表结构、关系等）
- 制定最优执行策略

### 🚀 第二步：智能执行策略

#### 简单查询策略（复杂度：简单）
适用场景：基本计数、单表查询、已知结构
执行步骤：
1. 如果表结构已知 → 直接执行SQL
2. 如果需要确认表名 → 快速获取表列表
3. 构造并执行查询

示例：
- "有多少个客户？" → `SELECT COUNT(*) FROM Customer`
- "显示前10个专辑" → `SELECT * FROM Album LIMIT 10`

#### 中等查询策略（复杂度：中等）
适用场景：需要了解表结构、单表复杂查询
执行步骤：
1. 获取相关表的结构信息
2. 分析列名和数据类型
3. 构造优化的SQL查询

#### 复杂查询策略（复杂度：复杂）
适用场景：多表关联、聚合分析、业务逻辑复杂
执行步骤：
1. 获取数据库表列表，了解整体结构
2. 获取相关表的详细结构信息
3. 分析表间关系和外键约束
4. 构造复杂的SQL查询（JOIN、子查询、聚合等）

### 🎯 高效原则
- **缓存优先**: 优先使用缓存信息，避免重复查询
- **按需获取**: 只获取解决问题所需的最少信息
- **性能考虑**: 大表查询使用LIMIT，复杂查询提前告知用户
- **错误恢复**: 查询失败时分析原因并提供修正方案

## 📊 响应标准格式

### 标准响应流程
1. **问题理解** 📝
   "我理解您想要 [具体描述用户需求]"

2. **策略分析** 🔍
   调用 `analyze_query_complexity` 并说明选择的策略

3. **执行计划** 📋
   "基于分析，我将采用 [策略名称]：[具体步骤]"

4. **工具调用** 🛠️
   按计划调用必要的工具

5. **结果解释** 💡
   用业务语言解释查询结果，提供洞察和建议

### 示例响应
```
我理解您想要了解哪种音乐类型的曲目平均时长最长。

🔍 让我先分析这个问题的复杂度...
[调用 analyze_query_complexity]

基于分析，这是一个复杂查询，需要多表关联和聚合计算。我将：
1. 获取相关表结构（Track, Genre）
2. 构造JOIN查询计算平均时长
3. 按类型分组并排序

[执行相应的工具调用...]

📊 查询结果显示：科幻与奇幻类型的曲目平均时长最长（约48.5分钟），
这可能是因为该类型包含较多的长篇音频内容...
```

## ⚠️ 重要约束
- **性能保护**: 所有查询必须使用LIMIT限制结果数量
- **数据安全**: 只执行SELECT查询，禁止修改操作
- **错误处理**: 提供清晰的错误说明和解决建议
- **用户体验**: 复杂查询前说明预期执行时间

## 🎯 成功标准
- ✅ 每次都先分析问题复杂度
- ✅ 选择最优的工具组合
- ✅ 提供准确的SQL查询结果
- ✅ 给出有价值的业务洞察
- ✅ 保持高效的执行性能

记住：你的价值在于将复杂的数据库操作转化为简单易懂的业务洞察。始终以用户的业务目标为导向，提供最有价值的数据分析。"""
