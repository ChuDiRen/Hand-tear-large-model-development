# Copyright (c) 2025 左岚. All rights reserved.
"""SQL智能体图实现模块

本模块提供SQL智能体的主要图实现，整合所有组件为一个可工作的LangGraph应用。
"""

import logging
import os

# 修复相对导入问题，使用绝对导入
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 使用绝对导入
from workflow_sql.config import get_config  # 配置获取函数
from workflow_sql.react_graph import create_sql_react_agent  # ReAct智能体
from workflow_sql.logging_config import setup_logging  # 日志配置


# 初始化配置
config = get_config()

# 设置日志
setup_logging(config.logging)
logger = logging.getLogger(__name__)

# 设置API密钥到环境变量
if config.llm.api_key:
    os.environ[f"{config.llm.provider.upper()}_API_KEY"] = config.llm.api_key

# 真实的模型初始化函数
def init_chat_model(model_string: str):
    """初始化聊天模型"""
    try:
        # 尝试导入并初始化模型
        from langchain_openai import ChatOpenAI

        # 解析模型字符串
        provider, model = model_string.split(":", 1)

        if provider.lower() == "deepseek":
            # 使用DeepSeek API
            return ChatOpenAI(
                model=model,
                api_key=config.llm.api_key,
                base_url="https://api.deepseek.com",
                temperature=config.llm.temperature,
                max_tokens=config.llm.max_tokens
            )
        else:
            logger.warning(f"不支持的模型提供商: {provider}")
            return None

    except ImportError:
        logger.warning("langchain_openai 未安装，使用模拟模型")
        # 创建一个模拟的LLM对象
        class MockLLM:
            def __init__(self):
                self.model_name = model_string

            def invoke(self, messages):
                return "模拟响应：请安装 langchain_openai 以使用真实模型"

        return MockLLM()
    except Exception as e:
        logger.error(f"模型初始化失败: {e}")
        return None

# 初始化语言模型
try:
    llm = init_chat_model(f"{config.llm.provider}:{config.llm.model}")
    if llm:
        logger.info(f"语言模型初始化成功: {config.llm.provider}:{config.llm.model}")
    else:
        logger.warning("语言模型初始化失败，将使用模拟模型")
except Exception as e:
    logger.error(f"语言模型初始化失败: {e}")
    llm = None

# 创建ReAct智能体
try:
    if llm is not None:
        react_agent = create_sql_react_agent(config, llm)
        # 将ReAct智能体包装为兼容的图接口
        graph = react_agent.agent
        logger.info("SQL ReAct智能体创建成功")
    else:
        logger.error("无法创建智能体：语言模型未初始化")
        # 创建一个简单的错误图
        from langgraph.graph import StateGraph, MessagesState, START, END
        from langchain_core.messages import AIMessage

        def error_node(state):
            response = AIMessage(content="SQL工作流暂时不可用，请检查模型配置")
            return {"messages": state.get("messages", []) + [response]}

        workflow = StateGraph(MessagesState)
        workflow.add_node("error", error_node)
        workflow.set_entry_point("error")
        workflow.add_edge("error", END)
        graph = workflow.compile()
        logger.info("创建了错误处理图")

except Exception as e:
    logger.error(f"智能体创建失败: {e}")
    # 最后的备用方案
    from langgraph.graph import StateGraph, MessagesState, START, END
    from langchain_core.messages import AIMessage

    def fallback_node(state):
        response = AIMessage(content=f"SQL工作流创建失败: {str(e)}")
        return {"messages": state.get("messages", []) + [response]}

    workflow = StateGraph(MessagesState)
    workflow.add_node("fallback", fallback_node)
    workflow.set_entry_point("fallback")
    workflow.add_edge("fallback", END)
    graph = workflow.compile()
    logger.info("创建了备用图")


# 导出图供LangGraph CLI使用
__all__ = ["graph", "config"]


def run_example() -> None:
    """运行示例查询来测试工作流"""
    question = "哪种音乐类型的曲目平均时长最长？"

    logger.info(f"运行示例查询: {question}")

    try:
        for step in graph.stream(
            {"messages": [{"role": "user", "content": question}]},
            stream_mode="values",
        ):
            step["messages"][-1].pretty_print()
    except Exception as e:
        logger.error(f"运行示例时出错: {e}")
        raise


if __name__ == "__main__":
    run_example()