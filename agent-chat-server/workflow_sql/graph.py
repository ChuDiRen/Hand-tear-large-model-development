"""SQL智能体图实现模块

本模块提供SQL智能体的主要图实现，整合所有组件为一个可工作的LangGraph应用。
"""

import logging
import os

from langchain.chat_models import init_chat_model

try:
    # 当作为模块导入时使用相对导入
    from .config import get_config
    from .graph_builder import create_sql_agent_graph
    from .logging_config import setup_logging
except ImportError:
    # 当直接运行时使用绝对导入
    from config import get_config
    from graph_builder import create_sql_agent_graph
    from logging_config import setup_logging


# 初始化配置
config = get_config()

# 设置日志
setup_logging(config.logging)
logger = logging.getLogger(__name__)

# 设置API密钥到环境变量
if config.llm.api_key:
    os.environ[f"{config.llm.provider.upper()}_API_KEY"] = config.llm.api_key

# 初始化语言模型
try:
    llm = init_chat_model(f"{config.llm.provider}:{config.llm.model}")
    logger.info(f"初始化语言模型: {config.llm.provider}:{config.llm.model}")
except Exception as e:
    logger.error(f"语言模型初始化失败: {e}")
    raise

# 创建图
try:
    graph = create_sql_agent_graph(config, llm)
    logger.info("SQL智能体图创建成功")
except Exception as e:
    logger.error(f"图创建失败: {e}")
    raise


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