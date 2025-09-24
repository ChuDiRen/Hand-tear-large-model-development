# Copyright (c) 2025 左岚. All rights reserved.
"""SQL智能体图节点实现模块

本模块包含SQL智能体工作流中使用的所有图节点的实现。
"""

import logging
from typing import Dict, List

from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import END, MessagesState

# 修复相对导入问题，使用绝对导入
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from workflow_sql.database import SQLDatabaseManager  # 数据库管理器
from workflow_sql.tools import SQLToolManager  # SQL工具管理器
from workflow_sql.agent_types import BaseNode  # 基础节点类
from workflow_sql.mcp_config import mcp_config  # MCP配置
from workflow_sql.async_chart_generator import run_async_chart_generation  # 异步图表生成
from workflow_sql.logging_config import get_node_logger, log_node_start, log_node_complete, log_node_error  # 日志工具


# 创建不同颜色的日志记录器
logger = logging.getLogger(__name__)
list_tables_logger = get_node_logger("ListTables")
schema_logger = get_node_logger("GetSchema")
query_gen_logger = get_node_logger("QueryGeneration")
query_check_logger = get_node_logger("QueryCheck")
answer_gen_logger = get_node_logger("AnswerGeneration")
chart_gen_logger = get_node_logger("ChartGeneration")


class ListTablesNode(BaseNode):
    """列出可用数据库表的节点"""

    def __init__(self, tool_manager: SQLToolManager) -> None:
        """初始化列表表节点

        Args:
            tool_manager: SQL工具管理器实例
        """
        super().__init__("list_tables")
        self.tool_manager = tool_manager

    def execute(self, state: MessagesState) -> Dict[str, List[BaseMessage]]:
        """执行列表表操作

        Args:
            state: 当前对话状态

        Returns:
            包含表列表的更新状态
        """
        try:
            log_node_start(list_tables_logger, "ListTables", "获取数据库表列表")

            # 创建预定义的工具调用
            tool_call = {
                "name": "sql_db_list_tables",
                "args": {},
                "id": "list_tables_call",
                "type": "tool_call",
            }
            tool_call_message = AIMessage(content="", tool_calls=[tool_call])

            # 获取工具并执行
            list_tables_tool = self.tool_manager.get_list_tables_tool()
            tool_message = list_tables_tool.invoke(tool_call)

            # 创建响应消息
            response = AIMessage(f"可用表: {tool_message.content}")

            table_count = len(tool_message.content.split(', ')) if tool_message.content else 0
            log_node_complete(list_tables_logger, "ListTables", f"发现 {table_count} 个表")
            return {"messages": [tool_call_message, tool_message, response]}

        except Exception as e:
            log_node_error(list_tables_logger, "ListTables", str(e))
            error_message = AIMessage(f"获取表列表失败: {str(e)}")  # 优化错误消息
            return {"messages": [error_message]}


class GetSchemaNode(BaseNode):
    """检索数据库结构信息的节点"""

    def __init__(self, tool_manager: SQLToolManager, llm: BaseLanguageModel) -> None:
        """初始化获取结构节点

        Args:
            tool_manager: SQL工具管理器实例
            llm: 用于工具绑定的语言模型
        """
        super().__init__("get_relative_schema")
        self.tool_manager = tool_manager
        self.llm = llm

    def execute(self, state: MessagesState) -> Dict[str, List[BaseMessage]]:
        """执行结构检索操作

        Args:
            state: 当前对话状态

        Returns:
            包含结构信息的更新状态
        """
        try:
            log_node_start(schema_logger, "GetSchema", "获取数据库表结构信息")

            # 从前面的消息中查找表名信息
            table_names = []
            for message in state["messages"]:
                if hasattr(message, 'content') and "可用表:" in message.content:
                    # 从ListTablesNode的响应中提取表名
                    # 查找对应的工具消息
                    for i, msg in enumerate(state["messages"]):
                        if (hasattr(msg, 'tool_call_id') and
                            hasattr(msg, 'content') and
                            msg.content):
                            # 解析表名列表
                            content = msg.content.strip()
                            if content:
                                # 假设表名以逗号分隔或换行分隔
                                table_names = [name.strip() for name in content.replace('\n', ',').split(',') if name.strip()]
                                break
                    break

            # 如果没有从消息中找到表名，直接从数据库获取
            if not table_names:
                db_manager = self.tool_manager.db_manager
                table_names = db_manager.get_table_names()
                logger.info(f"从数据库直接获取表名列表: {table_names}")

            # 如果还是没有表名，使用空字符串（获取所有表的结构）
            table_names_str = ", ".join(table_names) if table_names else ""
            logger.info(f"使用表名字符串: '{table_names_str}'")

            # 创建预定义的工具调用，使用实际的表名
            tool_call = {
                "name": "sql_db_schema",
                "args": {"table_names": table_names_str},
                "id": "schema_call",
                "type": "tool_call",
            }
            tool_call_message = AIMessage(content="", tool_calls=[tool_call])

            # 获取工具并执行
            schema_tool = self.tool_manager.get_schema_tool()
            tool_message = schema_tool.invoke(tool_call)

            # 创建响应消息
            response = AIMessage(f"数据库结构信息已获取")

            log_node_complete(schema_logger, "GetSchema", "数据库结构信息获取成功")
            return {"messages": [tool_call_message, tool_message, response]}

        except Exception as e:
            logger.error(f"获取数据库结构失败 - 错误详情: {e}")  # 优化错误日志
            error_message = AIMessage(f"获取数据库结构失败: {str(e)}")  # 优化错误消息
            return {"messages": [error_message]}


class GenerateQueryNode(BaseNode):
    """基于用户问题生成SQL查询的节点"""

    def __init__(
        self,
        tool_manager: SQLToolManager,
        llm: BaseLanguageModel,
        db_manager: SQLDatabaseManager
    ) -> None:
        """初始化生成查询节点

        Args:
            tool_manager: SQL工具管理器实例
            llm: 用于查询生成的语言模型
            db_manager: 用于方言信息的数据库管理器
        """
        super().__init__("generate_query")
        self.tool_manager = tool_manager
        self.llm = llm
        self.db_manager = db_manager

    def _get_system_prompt(self) -> str:
        """获取查询生成的系统提示"""
        dialect = self.db_manager.get_dialect()
        max_results = self.db_manager.config.max_query_results

        return f"""
您是一个专用于与SQL数据库交互的智能体。
根据输入的问题，请生成语法正确的 {dialect.value} 查询语句，
随后查看查询结果并返回答案。除非用户明确指定要获取的示例数量，
否则请始终将查询结果限制在最多 {max_results} 条。

您可以通过相关列对结果进行排序，以返回数据库中最有价值的示例。
切勿查询特定表的所有列，仅获取问题相关的必要列。

禁止对数据库执行任何数据操作语言语句（INSERT、UPDATE、DELETE、DROP等）。
        """.strip()

    def execute(self, state: MessagesState) -> Dict[str, List[BaseMessage]]:
        """执行查询生成操作

        Args:
            state: 当前对话状态

        Returns:
            包含生成查询的更新状态
        """
        try:
            log_node_start(query_gen_logger, "QueryGeneration", "基于用户问题生成SQL查询")

            system_message = {
                "role": "system",
                "content": self._get_system_prompt(),
            }

            # 绑定查询工具但不强制使用
            query_tool = self.tool_manager.get_query_tool()
            llm_with_tools = self.llm.bind_tools([query_tool])
            response = llm_with_tools.invoke([system_message] + state["messages"])

            log_node_complete(query_gen_logger, "QueryGeneration", "SQL查询生成成功")
            return {"messages": [response]}

        except Exception as e:
            logger.error(f"生成查询节点错误: {e}")
            error_message = AIMessage(f"生成查询错误: {str(e)}")
            return {"messages": [error_message]}


class CheckQueryNode(BaseNode):
    """验证和检查SQL查询的节点"""

    def __init__(
        self,
        tool_manager: SQLToolManager,
        llm: BaseLanguageModel,
        db_manager: SQLDatabaseManager
    ) -> None:
        """初始化检查查询节点

        Args:
            tool_manager: SQL工具管理器实例
            llm: 用于查询验证的语言模型
            db_manager: 用于方言信息的数据库管理器
        """
        super().__init__("check_query")
        self.tool_manager = tool_manager
        self.llm = llm
        self.db_manager = db_manager

    def _get_system_prompt(self) -> str:
        """获取查询验证的系统提示"""
        dialect = self.db_manager.get_dialect()

        return f"""
您是一位注重细节的SQL专家。
请仔细检查 {dialect.value} 查询中的常见错误，包括：
- 在NOT IN子句中使用NULL值
- 应当使用UNION ALL时却使用了UNION
- 使用BETWEEN处理不包含边界的情况
- 谓词中的数据类型不匹配
- 正确引用标识符
- 为函数使用正确数量的参数
- 转换为正确的数据类型
- 使用合适的列进行连接

如果存在上述任何错误，请重写查询。如果没有错误，请直接返回原始查询。

完成检查后，您将调用相应的工具来执行查询。
        """.strip()

    def execute(self, state: MessagesState) -> Dict[str, List[BaseMessage]]:
        """执行查询验证操作

        Args:
            state: 当前对话状态

        Returns:
            包含验证查询的更新状态
        """
        try:
            log_node_start(query_check_logger, "QueryCheck", "验证并执行SQL查询")

            # 从最后一条消息的工具调用中获取查询
            last_message = state["messages"][-1]
            if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
                logger.error("最后一条消息中未找到工具调用")
                error_message = AIMessage("错误: 未找到要验证的查询")
                return {"messages": [error_message]}

            tool_call = last_message.tool_calls[0]

            # 更安全的参数获取方式
            if "args" not in tool_call or "query" not in tool_call["args"]:
                logger.error(f"工具调用中缺少query参数: {tool_call}")
                error_message = AIMessage("错误: 工具调用中缺少query参数")
                return {"messages": [error_message]}

            query = tool_call["args"]["query"]
            logger.info(f"获取到查询: {query}")

            system_message = {
                "role": "system",
                "content": self._get_system_prompt(),
            }

            user_message = {"role": "user", "content": query}

            # 创建预定义的工具调用来执行查询
            validated_tool_call = {
                "name": "sql_db_query",
                "args": {"query": query},
                "id": "validated_query_call",
                "type": "tool_call",
            }
            validated_tool_call_message = AIMessage(content="", tool_calls=[validated_tool_call])

            # 获取工具并执行
            query_tool = self.tool_manager.get_query_tool()
            tool_message = query_tool.invoke(validated_tool_call)

            # 创建响应消息，为AnswerGenerationNode提供清晰的信息
            response = AIMessage(f"查询执行完成: {tool_message.content}")

            log_node_complete(query_check_logger, "QueryCheck", "SQL查询执行成功")
            return {"messages": [validated_tool_call_message, tool_message, response]}

        except Exception as e:
            logger.error(f"检查查询节点错误: {e}")
            error_message = AIMessage(f"验证查询错误: {str(e)}")
            return {"messages": [error_message]}


class AnswerGenerationNode(BaseNode):
    """生成最终答案的节点"""

    def __init__(self, llm: BaseLanguageModel) -> None:
        """初始化答案生成节点

        Args:
            llm: 用于答案生成的语言模型
        """
        super().__init__("answer_generation")
        self.llm = llm

    def _get_system_prompt(self) -> str:
        """获取答案生成的系统提示"""
        return """
您是一个专业的数据分析助手，负责解释SQL查询结果并生成用户友好的答案。

您的任务是：
1. 分析用户的原始问题
2. 理解执行的SQL查询的目的
3. 解释查询结果的含义
4. 用清晰、简洁的自然语言回答用户的问题

回答要求：
- 直接回答用户的问题，不要重复查询过程
- 使用通俗易懂的语言，避免技术术语
- 如果有数值结果，要包含具体的数字和单位
- 如果有多个结果，要突出最重要的发现
- 保持回答简洁但完整
        """.strip()

    def _extract_user_question(self, messages: List[BaseMessage]) -> str:
        """从消息历史中提取用户的原始问题"""
        for message in messages:
            if hasattr(message, 'content') and message.content:
                # 确保content是字符串类型
                content = str(message.content) if not isinstance(message.content, str) else message.content
                # 查找第一个人类消息
                if not content.startswith("可用表:") and not content.startswith("数据库结构"):
                    return content
        return "用户问题"

    def _extract_query_and_result(self, messages: List[BaseMessage]) -> tuple[str, str]:
        """从消息历史中提取SQL查询和结果"""
        query = ""
        result = ""

        for message in messages:
            # 查找查询执行完成的消息
            if hasattr(message, 'content') and "查询执行完成:" in message.content:
                result = message.content.replace("查询执行完成:", "").strip()

                # 在前面的消息中查找对应的查询
                for prev_msg in reversed(messages):
                    if hasattr(prev_msg, 'tool_calls') and prev_msg.tool_calls:
                        for tool_call in prev_msg.tool_calls:
                            if tool_call.get("name") == "sql_db_query":
                                query = tool_call.get("args", {}).get("query", "")
                                break
                        if query:
                            break
                break

        return query, result

    def execute(self, state: MessagesState) -> Dict[str, List[BaseMessage]]:
        """执行答案生成操作

        Args:
            state: 当前对话状态

        Returns:
            包含最终答案的更新状态
        """
        try:
            log_node_start(answer_gen_logger, "AnswerGeneration", "生成用户友好的自然语言答案")

            # 提取用户问题、查询和结果
            user_question = self._extract_user_question(state["messages"])
            query, result = self._extract_query_and_result(state["messages"])

            logger.info(f"用户问题: {user_question}")
            logger.info(f"执行的查询: {query}")
            logger.info(f"查询结果: {result}")

            # 构建提示消息
            system_message = {
                "role": "system",
                "content": self._get_system_prompt(),
            }

            user_message = {
                "role": "user",
                "content": f"""
用户问题：{user_question}

执行的SQL查询：
{query}

查询结果：
{result}

请基于以上信息，用自然语言回答用户的问题。
                """.strip()
            }

            # 调用LLM生成答案
            response = self.llm.invoke([system_message, user_message])

            # 创建最终答案消息
            final_answer = AIMessage(content=response.content)

            log_node_complete(answer_gen_logger, "AnswerGeneration", "自然语言答案生成成功")
            return {"messages": [final_answer]}

        except Exception as e:
            logger.error(f"答案生成节点错误: {e}")
            error_message = AIMessage(f"答案生成错误: {str(e)}")
            return {"messages": [error_message]}


class ChartGenerationNode(BaseNode):
    """生成图表的节点"""

    def __init__(self, llm: BaseLanguageModel) -> None:
        """初始化图表生成节点

        Args:
            llm: 用于图表生成的语言模型
        """
        super().__init__("chart_generation")
        self.llm = llm

    def _get_system_prompt(self) -> str:
        """获取图表生成的系统提示"""
        return """
您是一个专业的数据可视化专家，负责根据SQL查询结果生成合适的图表。

您的任务是：
1. 分析SQL查询结果的数据结构和内容
2. 确定最适合的图表类型（柱状图、折线图、饼图等）
3. 使用可用的图表工具生成可视化图表
4. 确保图表清晰、美观且信息丰富

图表类型选择指南：
- 柱状图：适合比较不同类别的数值
- 折线图：适合显示趋势变化
- 饼图：适合显示比例关系
- 散点图：适合显示相关性

重要规则：
- 根据数据特点选择最合适的图表类型
- 确保图表标题、轴标签清晰
- 如果数据点过多，考虑只显示前几名
- 使用合适的颜色和样式
        """.strip()

    def _extract_chart_data(self, messages: List[BaseMessage]) -> tuple[str, str, str]:
        """从消息历史中提取图表数据

        Returns:
            (用户问题, 查询结果, 答案内容)
        """
        user_question = ""
        query_result = ""
        answer_content = ""

        for message in messages:
            if hasattr(message, 'content') and message.content:
                # 确保content是字符串类型
                content = str(message.content) if not isinstance(message.content, str) else message.content

                # 提取用户问题（第一个非系统消息）
                if not user_question and not content.startswith(("可用表:", "数据库结构", "查询执行完成")):
                    user_question = content

                # 提取查询结果
                if "查询执行完成:" in content:
                    query_result = content.replace("查询执行完成:", "").strip()

                # 提取最终答案（最后一个AI消息，不包含系统信息）
                if (not content.startswith(("可用表:", "数据库结构", "查询执行完成", "Tool Calls:")) and
                    "错误" not in content and len(content) > 20):
                    answer_content = content

        return user_question, query_result, answer_content

    def _determine_chart_type(self, query_result: str, user_question: str) -> str:
        """根据数据和问题确定图表类型"""
        question_lower = user_question.lower()

        # 根据问题关键词判断
        if any(word in question_lower for word in ["趋势", "变化", "时间", "增长"]):
            return "line"
        elif any(word in question_lower for word in ["比例", "占比", "份额"]):
            return "pie"
        elif any(word in question_lower for word in ["比较", "排名", "最", "前", "后"]):
            return "bar"
        else:
            # 默认使用柱状图
            return "bar"

    def _generate_chart_description(self, user_question: str, query_result: str,
                                   answer_content: str, chart_type: str) -> str:
        """生成图表描述"""
        try:
            # 解析查询结果
            import ast
            data = ast.literal_eval(query_result)

            if not data:
                return "数据为空，无法生成图表"

            # 根据图表类型生成描述
            if chart_type == "bar":
                return f"建议生成柱状图：横轴为{data[0][0]}等类别，纵轴为数值。显示前{len(data)}个数据点的对比。"
            elif chart_type == "pie":
                return f"建议生成饼图：显示{len(data)}个类别的比例分布。"
            elif chart_type == "line":
                return f"建议生成折线图：显示{len(data)}个数据点的趋势变化。"
            else:
                return f"建议生成{chart_type}图表，包含{len(data)}个数据点。"

        except Exception as e:
            logger.error(f"生成图表描述时出错: {e}")
            return f"建议生成{chart_type}图表来可视化查询结果。"

    def execute(self, state: MessagesState) -> Dict[str, List[BaseMessage]]:
        """执行图表生成操作

        Args:
            state: 当前对话状态

        Returns:
            包含图表信息的更新状态
        """
        try:
            log_node_start(chart_gen_logger, "ChartGeneration", "生成数据可视化图表")

            # 检查图表功能是否启用
            if not mcp_config.chart.enabled:
                logger.info("图表生成功能已禁用")
                return {"messages": [AIMessage("图表生成功能当前不可用")]}

            # 提取数据
            user_question, query_result, answer_content = self._extract_chart_data(state["messages"])

            if not query_result:
                logger.warning("未找到查询结果，跳过图表生成")
                return {"messages": [AIMessage("无法生成图表：未找到查询结果")]}

            logger.info(f"用户问题: {user_question}")
            logger.info(f"查询结果: {query_result}")

            # 尝试使用异步图表生成
            try:
                chart_result = run_async_chart_generation(
                    self.llm, user_question, query_result, answer_content
                )
                chart_response = AIMessage(chart_result)
                log_node_complete(chart_gen_logger, "ChartGeneration", "数据可视化图表生成成功")
                return {"messages": [chart_response]}
            except Exception as e:
                logger.error(f"异步图表生成失败: {e}")

                # 回退到图表描述
                chart_type = self._determine_chart_type(query_result, user_question)
                logger.info(f"回退到图表描述，建议图表类型: {chart_type}")

                chart_description = self._generate_chart_description(
                    user_question, query_result, answer_content, chart_type
                )

                chart_response = AIMessage(f"图表生成建议：{chart_description}")
                log_node_complete(chart_gen_logger, "ChartGeneration", "图表描述生成成功（备选方案）")
                return {"messages": [chart_response]}

        except Exception as e:
            logger.error(f"图表生成节点错误: {e}")
            error_message = AIMessage(f"图表生成错误: {str(e)}")
            return {"messages": [error_message]}


def should_continue(state: MessagesState):
    """确定是否继续查询验证或结束

    Args:
        state: 当前对话状态

    Returns:
        下一个节点名称或END
    """
    try:
        messages = state["messages"]
        last_message = messages[-1]

        # 检查最后一条消息是否有sql_db_query工具调用
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            tool_call = last_message.tool_calls[0]
            if tool_call.get("name") == "sql_db_query":
                logger.debug("找到sql_db_query工具调用，继续到check_query")
                return "check_query"
            else:
                logger.debug(f"找到其他工具调用: {tool_call.get('name')}，结束对话")
                return END
        else:
            logger.debug("未找到工具调用，结束对话")
            return END

    except Exception as e:
        logger.error(f"should_continue错误: {e}")
        return END
