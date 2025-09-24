# Copyright (c) 2025 左岚. All rights reserved.
"""SQL智能体ReAct图实现模块

本模块提供基于ReAct Agent的SQL智能体实现，支持智能工具选择和调用。
"""

import logging
import os
# 修复相对导入问题
import sys
from typing import Any

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from langchain_core.language_models import BaseLanguageModel
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState

from workflow_sql.config import AgentConfig
from workflow_sql.database import SQLDatabaseManager
from workflow_sql.tools import SQLToolManager
from workflow_sql.react_tools import (
    initialize_sql_tools, 
    get_sql_tools, 
    get_sql_system_prompt
)
from workflow_sql.cache_manager import initialize_cache
from workflow_sql.async_chart_generator import run_async_chart_generation

logger = logging.getLogger(__name__)


class SQLReActAgent:
    """基于ReAct模式的SQL智能体"""
    
    def __init__(
        self,
        config: AgentConfig,
        llm: BaseLanguageModel,
        db_manager: SQLDatabaseManager,
        tool_manager: SQLToolManager
    ):
        """初始化SQL ReAct智能体
        
        Args:
            config: 智能体配置
            llm: 语言模型实例
            db_manager: 数据库管理器
            tool_manager: SQL工具管理器
        """
        self.config = config
        self.llm = llm
        self.db_manager = db_manager
        self.tool_manager = tool_manager
        
        # 初始化缓存
        initialize_cache(ttl=3600, max_entries=100)
        
        # 初始化SQL工具
        initialize_sql_tools(db_manager, tool_manager)
        
        # 获取工具列表
        self.tools = get_sql_tools()
        
        # 创建ReAct智能体
        self.agent = self._create_react_agent()
        
        logger.info(f"SQL ReAct智能体初始化完成 - 工具数量: {len(self.tools)}")
    
    def _create_react_agent(self) -> Any:
        """创建ReAct智能体
        
        Returns:
            编译后的ReAct智能体图
        """
        try:
            # 获取系统提示词
            system_prompt = get_sql_system_prompt()
            
            # 创建ReAct智能体
            agent = create_react_agent(
                model=self.llm,
                tools=self.tools,
                prompt=system_prompt
            )
            
            logger.info("ReAct智能体创建成功")
            return agent
            
        except Exception as e:
            logger.error(f"ReAct智能体创建失败: {e}")
            raise RuntimeError(f"ReAct智能体创建失败: {e}") from e
    
    def invoke(self, state: MessagesState) -> MessagesState:
        """调用智能体处理用户请求
        
        Args:
            state: 包含用户消息的状态
            
        Returns:
            包含智能体响应的更新状态
        """
        try:
            logger.info("开始处理SQL查询请求")
            
            # 调用ReAct智能体
            result = self.agent.invoke(state)
            
            # 检查是否需要生成图表
            should_generate_chart = self._should_generate_chart(result)
            
            if should_generate_chart:
                logger.info("检测到需要生成图表，启动异步图表生成")
                chart_result = self._generate_chart_async(result)
                if chart_result:
                    # 将图表结果添加到响应中
                    result = self._append_chart_result(result, chart_result)
            
            logger.info("SQL查询请求处理完成")
            return result
            
        except Exception as e:
            logger.error(f"处理SQL查询请求失败: {e}")
            # 返回错误消息
            from langchain_core.messages import AIMessage
            error_message = AIMessage(content=f"处理请求时出错: {str(e)}")
            return {"messages": state.get("messages", []) + [error_message]}
    
    def stream(self, state: MessagesState, **kwargs):
        """流式处理用户请求

        Args:
            state: 包含用户消息的状态
            **kwargs: 额外的流式处理参数

        Yields:
            流式响应数据
        """
        try:
            logger.info("开始流式处理SQL查询请求")

            # 收集所有流式响应
            final_result = None

            # 使用ReAct智能体的流式处理
            for chunk in self.agent.stream(state, **kwargs):
                final_result = chunk  # 保存最后的结果
                yield chunk

            # 检查是否需要生成图表
            if final_result:
                should_generate_chart = self._should_generate_chart(final_result)

                if should_generate_chart:
                    logger.info("检测到需要生成图表，启动异步图表生成")
                    chart_result = self._generate_chart_async(final_result)
                    if chart_result:
                        # 将图表结果作为额外的流式响应返回
                        chart_chunk = self._append_chart_result(final_result, chart_result)
                        yield chart_chunk

        except Exception as e:
            logger.error(f"流式处理SQL查询请求失败: {e}")
            # 返回错误消息
            from langchain_core.messages import AIMessage
            error_message = AIMessage(content=f"流式处理时出错: {str(e)}")
            yield {"messages": state.get("messages", []) + [error_message]}
    
    def _should_generate_chart(self, result: MessagesState) -> bool:
        """判断是否需要生成图表
        
        Args:
            result: 智能体的响应结果
            
        Returns:
            是否需要生成图表
        """
        try:
            # 检查最后一条消息是否包含数据查询结果
            messages = result.get("messages", [])
            if not messages:
                return False
            
            last_message = messages[-1]
            if not hasattr(last_message, 'content'):
                return False
            
            content = last_message.content.lower()
            
            # 检查是否包含数据相关的关键词
            chart_keywords = [
                '查询结果', '数据', '统计', '分析', '对比', 
                'select', 'count', 'sum', 'avg', 'max', 'min',
                '平均', '总计', '最大', '最小', '排序'
            ]
            
            return any(keyword in content for keyword in chart_keywords)
            
        except Exception as e:
            logger.error(f"判断是否生成图表时出错: {e}")
            return False
    
    def _generate_chart_async(self, result: MessagesState) -> str:
        """异步生成图表
        
        Args:
            result: 智能体的响应结果
            
        Returns:
            图表生成结果
        """
        try:
            # 提取用户问题和查询结果
            user_question, query_result, answer_content = self._extract_chart_data(result["messages"])
            
            if not user_question or not query_result:
                logger.warning("无法提取图表生成所需的数据")
                return ""
            
            # 调用异步图表生成
            chart_result = run_async_chart_generation(
                user_question=user_question,
                query_result=query_result,
                answer_content=answer_content,
                llm=self.llm
            )
            
            return chart_result
            
        except Exception as e:
            logger.error(f"异步图表生成失败: {e}")
            return f"图表生成失败: {str(e)}"
    
    def _extract_chart_data(self, messages):
        """从消息中提取图表生成所需的数据
        
        Args:
            messages: 消息列表
            
        Returns:
            (用户问题, 查询结果, 答案内容)
        """
        user_question = ""
        query_result = ""
        answer_content = ""
        
        try:
            for message in messages:
                if not hasattr(message, 'content'):
                    continue
                
                content = str(message.content) if not isinstance(message.content, str) else message.content
                
                # 提取用户问题（第一个人类消息）
                if hasattr(message, 'type') and message.type == 'human' and not user_question:
                    user_question = content
                
                # 提取查询结果（包含SQL执行结果的消息）
                if 'SELECT' in content.upper() or '查询结果' in content:
                    query_result = content
                
                # 提取最终答案（最后一个AI消息）
                if hasattr(message, 'type') and message.type == 'ai':
                    answer_content = content
            
            return user_question, query_result, answer_content
            
        except Exception as e:
            logger.error(f"提取图表数据失败: {e}")
            return "", "", ""
    
    def _append_chart_result(self, result: MessagesState, chart_result: str) -> MessagesState:
        """将图表结果添加到响应中
        
        Args:
            result: 原始响应结果
            chart_result: 图表生成结果
            
        Returns:
            包含图表结果的更新响应
        """
        try:
            from langchain_core.messages import AIMessage
            
            # 创建图表消息
            chart_message = AIMessage(content=f"\n\n📊 数据可视化：\n{chart_result}")
            
            # 添加到消息列表
            messages = result.get("messages", [])
            messages.append(chart_message)
            
            return {"messages": messages}
            
        except Exception as e:
            logger.error(f"添加图表结果失败: {e}")
            return result


def create_sql_react_agent(config: AgentConfig, llm: BaseLanguageModel) -> SQLReActAgent:
    """创建SQL ReAct智能体
    
    Args:
        config: 智能体配置
        llm: 语言模型实例
        
    Returns:
        SQL ReAct智能体实例
    """
    logger.info("创建SQL ReAct智能体")
    
    try:
        # 创建管理器
        db_manager = SQLDatabaseManager(config.database)
        tool_manager = SQLToolManager(db_manager, llm)
        
        # 创建智能体
        agent = SQLReActAgent(config, llm, db_manager, tool_manager)
        
        logger.info("SQL ReAct智能体创建成功")
        return agent
        
    except Exception as e:
        logger.error(f"SQL ReAct智能体创建失败: {e}")
        raise RuntimeError(f"SQL ReAct智能体创建失败: {e}") from e
