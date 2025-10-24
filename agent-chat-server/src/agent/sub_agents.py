# Copyright (c) 2025 左岚. All rights reserved.
"""子智能体系统 - 实现专业化的子智能体"""

import logging
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from agent_config import AgentSystemConfig, SubAgentConfig, ModelConfig

logger = logging.getLogger(__name__)


def create_llm_from_config(model_config: ModelConfig) -> ChatOpenAI:
    """根据配置创建 LLM 实例"""
    return ChatOpenAI(
        model=model_config.name,
        api_key=model_config.api_key,
        base_url=model_config.base_url,
        temperature=model_config.temperature,
        max_tokens=model_config.max_tokens,
        timeout=model_config.timeout,
    )


class SubAgentFactory:
    """子智能体工厂类 - 负责创建和管理子智能体"""

    def __init__(self, config: AgentSystemConfig, all_tools: Dict[str, BaseTool]):
        """初始化子智能体工厂
        
        Args:
            config: 智能体系统配置
            all_tools: 所有可用工具的字典 {tool_name: tool_instance}
        """
        self.config = config
        self.all_tools = all_tools
        self.agents: Dict[str, Any] = {}  # 存储已创建的智能体实例
        logger.info("子智能体工厂初始化完成")

    def _get_tools_for_agent(self, tool_names: List[str]) -> List[BaseTool]:
        """根据工具名称列表获取工具实例"""
        tools = []
        for tool_name in tool_names:
            if tool_name == "mcp_chart":  # MCP 图表工具特殊处理
                # 获取所有以 generate_ 开头的 MCP 工具
                mcp_tools = [t for name, t in self.all_tools.items() if name.startswith("generate_")]
                tools.extend(mcp_tools)
            elif tool_name in self.all_tools:
                tools.append(self.all_tools[tool_name])
            else:
                logger.warning(f"工具 {tool_name} 未找到,已跳过")
        return tools

    def create_sub_agent(self, agent_config: SubAgentConfig) -> Any:
        """创建单个子智能体
        
        Args:
            agent_config: 子智能体配置
            
        Returns:
            创建的智能体实例
        """
        try:
            # 获取模型配置
            model_config = self.config.models.get(agent_config.model_name)
            if not model_config:
                logger.error(f"模型配置 {agent_config.model_name} 未找到")
                return None

            # 创建 LLM
            llm = create_llm_from_config(model_config)

            # 获取提示词
            prompt_config = self.config.prompts.get(agent_config.prompt_id)
            if not prompt_config:
                logger.error(f"提示词配置 {agent_config.prompt_id} 未找到")
                return None

            # 获取工具
            tools = self._get_tools_for_agent(agent_config.tools)

            # 创建 ReAct 智能体
            agent = create_react_agent(
                model=llm,
                tools=tools,
                prompt=prompt_config.content,
                name=agent_config.name,
            )

            logger.info(
                f"✅ 子智能体 {agent_config.name} 创建成功 "
                f"(模型: {model_config.name}, 工具数: {len(tools)})"
            )
            return agent

        except Exception as e:
            logger.error(f"创建子智能体 {agent_config.name} 失败: {e}")
            return None

    def create_all_agents(self) -> Dict[str, Any]:
        """创建所有启用的子智能体
        
        Returns:
            智能体字典 {agent_name: agent_instance}
        """
        logger.info("开始创建所有子智能体...")
        
        for agent_name, agent_config in self.config.sub_agents.items():
            if not agent_config.enabled:
                logger.info(f"⏭️  子智能体 {agent_name} 已禁用,跳过创建")
                continue

            agent = self.create_sub_agent(agent_config)
            if agent:
                self.agents[agent_name] = agent

        logger.info(f"📊 子智能体创建完成,共 {len(self.agents)} 个智能体")
        return self.agents

    def get_agent(self, agent_name: str) -> Any:
        """获取指定的子智能体
        
        Args:
            agent_name: 智能体名称
            
        Returns:
            智能体实例,如果不存在则返回 None
        """
        return self.agents.get(agent_name)

    def get_all_agent_names(self) -> List[str]:
        """获取所有已创建的智能体名称列表"""
        return list(self.agents.keys())

    def get_agent_description(self, agent_name: str) -> str:
        """获取智能体的描述信息
        
        Args:
            agent_name: 智能体名称
            
        Returns:
            智能体描述,如果不存在则返回空字符串
        """
        agent_config = self.config.sub_agents.get(agent_name)
        return agent_config.description if agent_config else ""


def create_handoff_tools(agent_factory: SubAgentFactory):
    """创建智能体切换工具(用于监督智能体调用)
    
    Args:
        agent_factory: 子智能体工厂实例
        
    Returns:
        切换工具列表
    """
    from typing import Annotated
    from langchain_core.tools import tool, InjectedToolCallId
    from langgraph.prebuilt import InjectedState
    from langgraph.graph import MessagesState
    from langgraph.types import Command

    handoff_tools = []

    for agent_name in agent_factory.get_all_agent_names():
        agent_desc = agent_factory.get_agent_description(agent_name)
        
        # 动态创建切换工具
        def create_handoff_tool(name: str, description: str):
            tool_name = f"transfer_to_{name}"
            
            @tool(tool_name, description=f"将任务分配给 {description}")
            def handoff_tool(
                state: Annotated[MessagesState, InjectedState],
                tool_call_id: Annotated[str, InjectedToolCallId],
            ) -> Command:
                """切换到指定的子智能体"""
                tool_message = {
                    "role": "tool",
                    "content": f"已将任务分配给 {name}",
                    "name": tool_name,
                    "tool_call_id": tool_call_id,
                }
                return Command(
                    goto=name,  # 跳转到子智能体节点
                    update={**state, "messages": state["messages"] + [tool_message]},
                    graph=Command.PARENT,  # 在父图中导航
                )
            
            return handoff_tool

        handoff_tool = create_handoff_tool(agent_name, agent_desc)
        handoff_tools.append(handoff_tool)
        logger.info(f"✅ 创建切换工具: transfer_to_{agent_name}")

    logger.info(f"📊 切换工具创建完成,共 {len(handoff_tools)} 个工具")
    return handoff_tools

