# Copyright (c) 2025 左岚. All rights reserved.
"""智能助手聊天图形 - 支持工具调用

使用魔塔的 GLM-4.5 大模型提供智能对话功能，支持工具调用。
"""

from __future__ import annotations

import datetime
import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# 加载环境变量
load_dotenv()


class Context(TypedDict):
    """智能助手上下文配置"""
    model_name: str


def create_llm() -> ChatOpenAI:
    """创建大模型实例"""
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "ZhipuAI/GLM-4.5"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api-inference.modelscope.cn/v1"),
        temperature=0.7,
        max_tokens=2048,
        timeout=30,
    )


@tool
def get_current_time() -> str:
    """获取当前时间"""
    now = datetime.datetime.now()
    return f"现在的时间是：{now.strftime('%Y年%m月%d日 %H:%M:%S')}"


@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息

    Args:
        city: 城市名称，如"北京"、"上海"、"广州"等
    """
    # 这里使用模拟数据，实际应用中可以接入真实的天气API
    weather_data = {
        "北京": "晴天，气温 15-25°C，微风",
        "上海": "多云，气温 18-28°C，东南风",
        "广州": "阴天，气温 22-32°C，有小雨",
        "深圳": "晴天，气温 24-34°C，南风",
        "杭州": "多云，气温 16-26°C，微风",
        "成都": "阴天，气温 12-22°C，有雾",
    }

    if city in weather_data:
        return f"{city}的天气：{weather_data[city]}"
    else:
        return f"抱歉，暂时无法获取{city}的天气信息。支持的城市有：北京、上海、广州、深圳、杭州、成都。"


@tool
def calculate(expression: str) -> str:
    """计算数学表达式

    Args:
        expression: 数学表达式，如"2+3*4"、"sqrt(16)"等
    """
    try:
        # 安全的数学计算，只允许基本运算
        import math
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round})

        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算错误：{str(e)}。请检查表达式是否正确。"


@tool
def search_knowledge(query: str) -> str:
    """搜索知识库信息

    Args:
        query: 搜索关键词
    """
    # 模拟知识库搜索
    knowledge_base = {
        "python": "Python是一种高级编程语言，由Guido van Rossum于1991年首次发布。它以简洁易读的语法著称。",
        "人工智能": "人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
        "机器学习": "机器学习是人工智能的一个子集，使计算机能够在没有明确编程的情况下学习和改进。",
        "深度学习": "深度学习是机器学习的一个子集，使用多层神经网络来模拟人脑的工作方式。",
        "langchain": "LangChain是一个用于开发由语言模型驱动的应用程序的框架，提供了构建LLM应用的工具和抽象。",
        "langgraph": "LangGraph是LangChain的一部分，用于构建有状态的、多参与者的应用程序，支持循环和条件逻辑。",
    }

    query_lower = query.lower()
    for key, value in knowledge_base.items():
        if key in query_lower or query_lower in key:
            return f"关于'{query}'的信息：{value}"

    return f"抱歉，知识库中没有找到关于'{query}'的信息。您可以尝试搜索：Python、人工智能、机器学习、深度学习、LangChain、LangGraph等主题。"


# 定义工具列表
tools = [
    get_current_time,
    get_weather,
    calculate,
    search_knowledge,
]

# 创建智能助手图形（使用 prebuilt 的 react agent）
graph = create_react_agent(
    model=create_llm(),
    tools=tools,
    prompt="""你是一个友好、专业的中文智能助手。请遵循以下原则：

1. 用中文回答问题
2. 保持友好和专业的语气
3. 当用户询问时间时，使用 get_current_time 工具
4. 当用户询问天气时，使用 get_weather 工具
5. 当用户需要计算时，使用 calculate 工具
6. 当用户询问知识问题时，使用 search_knowledge 工具
7. 如果不确定答案，请诚实说明
8. 尽量提供有用和准确的信息
9. 回答要简洁明了，避免过于冗长

你可以使用以下工具来帮助用户：
- get_current_time: 获取当前时间
- get_weather: 获取城市天气信息
- calculate: 进行数学计算
- search_knowledge: 搜索知识库信息

请根据用户的问题选择合适的工具来提供准确的答案。"""
)
