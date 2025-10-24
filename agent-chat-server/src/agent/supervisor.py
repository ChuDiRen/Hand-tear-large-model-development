# Copyright (c) 2025 左岚. All rights reserved.
"""监督智能体 - 负责任务分发和协调"""

import logging
from typing import Any, List
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from agent_config import AgentSystemConfig, ModelConfig

logger = logging.getLogger(__name__)


def create_supervisor_agent(
    config: AgentSystemConfig,
    handoff_tools: List[BaseTool],
) -> Any:
    """创建监督智能体
    
    Args:
        config: 智能体系统配置
        handoff_tools: 智能体切换工具列表
        
    Returns:
        监督智能体实例
    """
    try:
        # 获取监督智能体的模型配置
        model_name = config.supervisor_model
        model_config = config.models.get(model_name)
        
        if not model_config:
            logger.error(f"监督智能体模型配置 {model_name} 未找到")
            return None

        # 创建 LLM
        llm = ChatOpenAI(
            model=model_config.name,
            api_key=model_config.api_key,
            base_url=model_config.base_url,
            temperature=model_config.temperature,
            max_tokens=model_config.max_tokens,
            timeout=model_config.timeout,
        )

        # 获取监督智能体提示词
        prompt_config = config.prompts.get("supervisor")
        if not prompt_config:
            logger.error("监督智能体提示词配置未找到")
            return None

        # 创建监督智能体
        supervisor = create_react_agent(
            model=llm,
            tools=handoff_tools,
            prompt=prompt_config.content,
            name="supervisor",
        )

        logger.info(
            f"✅ 监督智能体创建成功 "
            f"(模型: {model_config.name}, 切换工具数: {len(handoff_tools)})"
        )
        return supervisor

    except Exception as e:
        logger.error(f"创建监督智能体失败: {e}")
        return None

