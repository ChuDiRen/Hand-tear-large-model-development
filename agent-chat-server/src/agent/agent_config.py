# Copyright (c) 2025 左岚. All rights reserved.
"""智能体配置管理模块 - 集中管理所有智能体、模型、工具的配置"""

import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ModelConfig:
    """模型配置类"""
    name: str  # 模型名称
    base_url: str  # API 基础 URL
    api_key: str  # API 密钥
    temperature: float = 0.1  # 温度参数
    max_tokens: int = 4096  # 最大 token 数
    timeout: int = 45  # 超时时间(秒)


@dataclass
class PromptConfig:
    """提示词配置类"""
    id: str  # 提示词 ID
    content: str  # 提示词内容
    description: str  # 提示词描述


@dataclass
class SubAgentConfig:
    """子智能体配置类"""
    name: str  # 智能体名称
    description: str  # 智能体描述
    prompt_id: str  # 使用的提示词 ID
    model_name: str  # 使用的模型名称
    tools: List[str] = field(default_factory=list)  # 可用工具列表
    enabled: bool = True  # 是否启用


@dataclass
class MCPServerConfig:
    """MCP 服务器配置类"""
    name: str  # 服务器名称
    command: str  # 启动命令
    args: List[str]  # 命令参数
    transport: str = "stdio"  # 传输协议
    enabled: bool = True  # 是否启用


@dataclass
class AgentSystemConfig:
    """智能体系统总配置类"""
    models: Dict[str, ModelConfig]  # 模型配置字典
    prompts: Dict[str, PromptConfig]  # 提示词配置字典
    sub_agents: Dict[str, SubAgentConfig]  # 子智能体配置字典
    mcp_servers: Dict[str, MCPServerConfig]  # MCP 服务器配置字典
    supervisor_model: str  # 监督智能体使用的模型名称
    enable_supervisor: bool = True  # 是否启用监督模式
    enable_mcp: bool = False  # 是否启用 MCP


def get_default_models() -> Dict[str, ModelConfig]:
    """获取默认模型配置"""
    return {
        "default": ModelConfig(
            name=os.getenv("OPENAI_MODEL", "ZhipuAI/GLM-4.5"),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api-inference.modelscope.cn/v1"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            temperature=float(os.getenv("AGENT_TEMP_DEFAULT", "0.1")),
            max_tokens=int(os.getenv("AGENT_MAX_TOKENS", "4096")),
            timeout=int(os.getenv("AGENT_TIMEOUT", "45")),
        ),
        "math": ModelConfig(
            name=os.getenv("AGENT_MODEL_MATH", os.getenv("OPENAI_MODEL", "ZhipuAI/GLM-4.5")),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api-inference.modelscope.cn/v1"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            temperature=float(os.getenv("AGENT_TEMP_MATH", "0.0")),
            max_tokens=int(os.getenv("AGENT_MAX_TOKENS", "4096")),
            timeout=int(os.getenv("AGENT_TIMEOUT", "45")),
        ),
        "research": ModelConfig(
            name=os.getenv("AGENT_MODEL_RESEARCH", os.getenv("OPENAI_MODEL", "ZhipuAI/GLM-4.5")),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api-inference.modelscope.cn/v1"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            temperature=float(os.getenv("AGENT_TEMP_RESEARCH", "0.2")),
            max_tokens=int(os.getenv("AGENT_MAX_TOKENS", "4096")),
            timeout=int(os.getenv("AGENT_TIMEOUT", "45")),
        ),
        "code": ModelConfig(
            name=os.getenv("AGENT_MODEL_CODE", os.getenv("OPENAI_MODEL", "ZhipuAI/GLM-4.5")),
            base_url=os.getenv("OPENAI_BASE_URL", "https://api-inference.modelscope.cn/v1"),
            api_key=os.getenv("OPENAI_API_KEY", ""),
            temperature=float(os.getenv("AGENT_TEMP_CODE", "0.0")),
            max_tokens=int(os.getenv("AGENT_MAX_TOKENS", "4096")),
            timeout=int(os.getenv("AGENT_TIMEOUT", "45")),
        ),
    }


def get_default_prompts() -> Dict[str, PromptConfig]:
    """获取默认提示词配置"""
    return {
        "supervisor": PromptConfig(
            id="supervisor",
            description="监督智能体提示词",
            content=(
                "你是一个智能任务协调者,负责分析用户需求并将任务分配给最合适的专业智能体。\n\n"
                "可用的专业智能体:\n"
                "- code_agent: 代码生成、代码分析、编程问题解答\n"
                "- math_agent: 数学计算、公式求解、数据分析\n"
                "- research_agent: 信息搜索、知识查询、资料检索\n"
                "- chart_agent: 数据可视化、图表生成\n"
                "- general_agent: 通用对话、时间查询、天气查询等\n\n"
                "工作流程:\n"
                "1. 分析用户请求,识别任务类型\n"
                "2. 选择最合适的智能体处理任务\n"
                "3. 一次只分配给一个智能体,不要并行调用\n"
                "4. 等待智能体完成后,整合结果回复用户\n\n"
                "注意: 你只负责任务分发,不要自己执行具体任务。"
            ),
        ),
        "code": PromptConfig(
            id="code",
            description="代码智能体提示词",
            content=(
                "你是一个专业的代码助手,擅长代码生成、代码分析和编程问题解答。\n\n"
                "核心能力:\n"
                "- 编写高质量、可维护的代码\n"
                "- 代码审查和优化建议\n"
                "- 调试和问题定位\n"
                "- 技术方案设计\n\n"
                "工作原则:\n"
                "- 代码简洁、高效、符合规范\n"
                "- 注释清晰,位于代码右侧\n"
                "- 优先考虑性能和可维护性\n"
                "- 完美支持中文环境\n\n"
                "完成任务后,直接返回结果给监督者。"
            ),
        ),
        "math": PromptConfig(
            id="math",
            description="数学智能体提示词",
            content=(
                "你是一个数学计算专家,负责处理数学表达式求值和数据分析。\n\n"
                "核心能力:\n"
                "- 数学表达式计算\n"
                "- 统计分析\n"
                "- 数值计算\n\n"
                "工作原则:\n"
                "- 只调用一次 calculate 工具\n"
                "- 表达式不明确时先澄清\n"
                "- 结果准确,格式清晰\n\n"
                "完成任务后,直接返回结果给监督者。"
            ),
        ),
        "research": PromptConfig(
            id="research",
            description="研究智能体提示词",
            content=(
                "你是一个信息检索专家,负责搜索和整理知识信息。\n\n"
                "核心能力:\n"
                "- 知识库搜索\n"
                "- 网络信息检索\n"
                "- 资料整理和总结\n\n"
                "工作原则:\n"
                "- 信息准确可靠\n"
                "- 引用来源清晰\n"
                "- 结果简洁易懂\n\n"
                "完成任务后,直接返回结果给监督者。"
            ),
        ),
        "chart": PromptConfig(
            id="chart",
            description="图表智能体提示词",
            content=(
                "你是一个数据可视化专家,负责生成各类图表。\n\n"
                "核心能力:\n"
                "- 折线图、柱状图、饼图等\n"
                "- 数据格式验证\n"
                "- 图表样式优化\n\n"
                "工作原则:\n"
                "- 只调用一次图表工具\n"
                "- 数据格式严格验证\n"
                "- 缺少数据时征得用户同意\n\n"
                "完成任务后,直接返回结果给监督者。"
            ),
        ),
        "general": PromptConfig(
            id="general",
            description="通用智能体提示词",
            content=(
                "你是一个通用助手,负责处理日常对话和基础查询。\n\n"
                "核心能力:\n"
                "- 时间查询\n"
                "- 天气查询\n"
                "- 日常对话\n\n"
                "工作原则:\n"
                "- 回答简洁准确\n"
                "- 态度友好专业\n"
                "- 中文表达流畅\n\n"
                "完成任务后,直接返回结果给监督者。"
            ),
        ),
    }


def get_default_sub_agents() -> Dict[str, SubAgentConfig]:
    """获取默认子智能体配置"""
    return {
        "code_agent": SubAgentConfig(
            name="code_agent",
            description="代码生成和分析专家",
            prompt_id="code",
            model_name="code",
            tools=[],  # 代码智能体暂不需要特定工具
            enabled=True,
        ),
        "math_agent": SubAgentConfig(
            name="math_agent",
            description="数学计算专家",
            prompt_id="math",
            model_name="math",
            tools=["calculate"],
            enabled=True,
        ),
        "research_agent": SubAgentConfig(
            name="research_agent",
            description="信息检索专家",
            prompt_id="research",
            model_name="research",
            tools=["search_knowledge"],
            enabled=True,
        ),
        "chart_agent": SubAgentConfig(
            name="chart_agent",
            description="数据可视化专家",
            prompt_id="chart",
            model_name="default",
            tools=["mcp_chart"],  # MCP 图表工具
            enabled=True,
        ),
        "general_agent": SubAgentConfig(
            name="general_agent",
            description="通用助手",
            prompt_id="general",
            model_name="default",
            tools=["get_current_time", "get_weather"],
            enabled=True,
        ),
    }


def get_default_mcp_servers() -> Dict[str, MCPServerConfig]:
    """获取默认 MCP 服务器配置"""
    # Windows 系统需要使用 cmd /c npx，其他系统直接使用 npx
    is_windows = sys.platform == "win32"

    if is_windows:
        chart_command = "cmd"
        chart_args = ["/c", "npx", "-y", "@antv/mcp-server-chart"]
        bing_command = "cmd"
        bing_args = ["/c", "npx", "-y", "bing-cn-mcp"]
    else:
        chart_command = "npx"
        chart_args = ["-y", "@antv/mcp-server-chart"]
        bing_command = "npx"
        bing_args = ["-y", "bing-cn-mcp"]

    return {
        "chart": MCPServerConfig(
            name="chart",
            command=chart_command,
            args=chart_args,
            transport="stdio",
            enabled=os.getenv("ENABLE_MCP_CHART", "1") == "1",
        ),
        "bingcn": MCPServerConfig(
            name="bingcn",
            command=bing_command,
            args=bing_args,
            transport="stdio",
            enabled=os.getenv("ENABLE_MCP_BING", "0") == "1",
        ),
    }


def get_agent_config() -> AgentSystemConfig:
    """获取完整的智能体系统配置"""
    return AgentSystemConfig(
        models=get_default_models(),
        prompts=get_default_prompts(),
        sub_agents=get_default_sub_agents(),
        mcp_servers=get_default_mcp_servers(),
        supervisor_model=os.getenv("SUPERVISOR_MODEL", "default"),
        enable_supervisor=os.getenv("ENABLE_SUPERVISOR", "1") == "1",
        enable_mcp=os.getenv("ENABLE_MCP", "1") == "1",
    )

