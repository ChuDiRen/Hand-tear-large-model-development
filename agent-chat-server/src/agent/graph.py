# Copyright (c) 2025 左岚. All rights reserved.
"""智能助手聊天图形 - 简化版本

提供基本的聊天功能，支持消息处理和响应生成。
"""

from __future__ import annotations

from typing import Any, Dict, List, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, MessagesState
from langgraph.runtime import Runtime


class Context(TypedDict):
    """智能助手上下文配置"""
    model_name: str


async def chat_agent(state: MessagesState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """智能助手聊天处理函数

    处理用户消息并生成回复
    """
    messages = state.get("messages", [])

    if not messages:
        return {"messages": [AIMessage(content="您好！我是智能助手，有什么可以帮助您的吗？")]}

    # 获取最后一条用户消息
    last_message = messages[-1]

    if isinstance(last_message, HumanMessage):
        user_content = last_message.content

        # 简单的回复逻辑
        if "你好" in user_content or "hello" in user_content.lower():
            response = "您好！很高兴为您服务！有什么我可以帮助您的吗？"
        elif "再见" in user_content or "bye" in user_content.lower():
            response = "再见！祝您生活愉快！"
        elif "谢谢" in user_content or "thank" in user_content.lower():
            response = "不客气！很高兴能帮助到您！"
        elif "时间" in user_content or "time" in user_content.lower():
            import datetime
            now = datetime.datetime.now()
            response = f"现在的时间是：{now.strftime('%Y年%m月%d日 %H:%M:%S')}"
        elif "天气" in user_content:
            response = "抱歉，我目前无法获取实时天气信息。建议您查看天气预报应用或网站。"
        else:
            response = f"我收到了您的消息：「{user_content}」\n\n作为智能助手，我正在不断学习中。如果您有具体问题，请告诉我，我会尽力帮助您！"

        return {"messages": [AIMessage(content=response)]}

    return {"messages": [AIMessage(content="抱歉，我无法理解这条消息。请发送文本消息。")]}


# 创建智能助手图形
graph = (
    StateGraph(MessagesState, context_schema=Context)
    .add_node("chat_agent", chat_agent)
    .add_edge("__start__", "chat_agent")
    .compile(name="智能助手聊天")
)
