# Copyright (c) 2025 左岚. All rights reserved.
"""智能助手聊天图形 - 监督智能体架构

基于 LangGraph 的多智能体系统,采用监督智能体(Supervisor Agent)架构。
核心特性:
- 动态提示词系统:支持提示词模板的动态加载和切换
- 动态模型切换:支持多模型配置和运行时切换
- 动态工具调用:支持工具的动态注册和热插拔
- MCP 集成:支持 MCP 协议的子代码调用
- 监督智能体:主智能体负责任务分发和协调
- 子智能体系统:多个专业化子智能体处理特定任务
"""

from __future__ import annotations

import datetime
import json
import logging
from typing import Any, Dict

from dotenv import load_dotenv
from langchain_core.tools import tool, BaseTool
from langgraph.graph import StateGraph, MessagesState, START, END

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()


# ========== 导入配置和管理模块 ==========
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))  # 添加当前目录到路径

from agent_config import get_agent_config
from mcp_manager import MCPToolManager
from sub_agents import SubAgentFactory, create_handoff_tools
from supervisor import create_supervisor_agent


# ========== 工具定义 ==========
def log_tool_call(tool_name: str, args: Dict[str, Any]) -> None:
    """记录工具调用日志"""
    logger.info(f"🔧 工具调用: {tool_name}, 参数: {json.dumps(args, ensure_ascii=False, indent=2)}")


@tool
def get_current_time() -> str:
    """获取当前时间"""
    try:
        now = datetime.datetime.now()
        result = f"现在的时间是：{now.strftime('%Y年%m月%d日 %H:%M:%S')}"
        log_tool_call("get_current_time", {})
        return result
    except Exception as e:
        logger.error(f"获取时间失败: {e}")
        return f"获取时间失败：{str(e)}"


@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息

    Args:
        city: 城市名称，如"北京"、"上海"、"广州"等
    """
    try:
        log_tool_call("get_weather", {"city": city})

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
    except Exception as e:
        logger.error(f"获取天气失败: {e}")
        return f"获取天气信息失败：{str(e)}"


@tool
def calculate(expression: str) -> str:
    """计算数学表达式

    Args:
        expression: 数学表达式，如"2+3*4"、"sqrt(16)"等
    """
    try:
        log_tool_call("calculate", {"expression": expression})

        # 安全的数学计算，只允许基本运算
        import math
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({"abs": abs, "round": round})

        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        logger.error(f"计算失败: {e}")
        return f"计算错误：{str(e)}。请检查表达式是否正确。"


@tool
def search_knowledge(query: str) -> str:
    """搜索知识库信息

    Args:
        query: 搜索关键词
    """
    try:
        log_tool_call("search_knowledge", {"query": query})

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
    except Exception as e:
        logger.error(f"知识搜索失败: {e}")
        return f"知识搜索失败：{str(e)}"


# 定义本地工具列表
local_tools = [
    get_current_time,
    get_weather,
    calculate,
    search_knowledge,
]


# ========== 初始化智能体系统 ==========
logger.info("=" * 60)
logger.info("� 开始初始化监督智能体系统...")
logger.info("=" * 60)

# 1. 加载配置
config = get_agent_config()
logger.info(f"✅ 配置加载完成 (监督模式: {config.enable_supervisor}, MCP: {config.enable_mcp})")

# 2. 加载 MCP 工具
mcp_manager = MCPToolManager(config)
mcp_tools = mcp_manager.load_mcp_tools()
logger.info(f"✅ MCP 工具加载完成 (数量: {len(mcp_tools)})")

# 3. 合并所有工具
all_tools_dict: Dict[str, BaseTool] = {}
for tool in local_tools:
    all_tools_dict[tool.name] = tool
for tool in mcp_tools:
    tool_name = getattr(tool, "name", "unknown")
    all_tools_dict[tool_name] = tool

logger.info(f"📊 工具合并完成 (本地: {len(local_tools)}, MCP: {len(mcp_tools)}, 总计: {len(all_tools_dict)})")

# 4. 创建子智能体
agent_factory = SubAgentFactory(config, all_tools_dict)
sub_agents = agent_factory.create_all_agents()
logger.info(f"✅ 子智能体创建完成 (数量: {len(sub_agents)})")

# 5. 创建切换工具
handoff_tools = create_handoff_tools(agent_factory)
logger.info(f"✅ 切换工具创建完成 (数量: {len(handoff_tools)})")

# 6. 创建监督智能体
supervisor_agent = create_supervisor_agent(config, handoff_tools)
if not supervisor_agent:
    logger.error("❌ 监督智能体创建失败")
    raise RuntimeError("监督智能体创建失败")
logger.info("✅ 监督智能体创建完成")

# ========== 构建监督智能体图 ==========
logger.info("🔨 开始构建监督智能体图...")

# 创建 StateGraph
workflow = StateGraph(MessagesState)

# 添加监督智能体节点
workflow.add_node(
    "supervisor",
    supervisor_agent,
    destinations=tuple(sub_agents.keys()) + (END,)  # 可以跳转到任何子智能体或结束
)

# 添加所有子智能体节点
for agent_name, agent in sub_agents.items():
    workflow.add_node(agent_name, agent)
    # 子智能体完成后返回监督智能体
    workflow.add_edge(agent_name, "supervisor")

# 设置入口点为监督智能体
workflow.add_edge(START, "supervisor")

# 编译图
graph = workflow.compile()

logger.info("=" * 60)
logger.info("✅ 监督智能体系统初始化完成!")
logger.info(f"📊 系统统计:")
logger.info(f"  - 子智能体数量: {len(sub_agents)}")
logger.info(f"  - 工具总数: {len(all_tools_dict)}")
logger.info(f"  - MCP 工具数: {len(mcp_tools)}")
logger.info(f"  - 本地工具数: {len(local_tools)}")
logger.info("=" * 60)
