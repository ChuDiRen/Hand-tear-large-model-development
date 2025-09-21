# Copyright (c) 2025 左岚. All rights reserved.
"""智能助手聊天图形 - 支持工具调用与数据可视化

使用魔塔的 GLM-4.5 大模型提供智能对话功能，支持工具调用和图表生成。
核心特性：严格的单次工具调用、数据一致性验证、友好的错误处理。
"""

from __future__ import annotations

import datetime
import json
import logging
from typing import Any, Dict, TypedDict

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()


class Context(TypedDict):
    """智能助手上下文配置"""
    model_name: str


def create_llm() -> ChatOpenAI:
    """创建优化的大模型实例 - 严格遵守指令约束"""
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "ZhipuAI/GLM-4.5"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api-inference.modelscope.cn/v1"),
        temperature=0.1,  # 极低随机性，严格遵守指令
        max_tokens=4096,  # 适中输出长度，避免过长回答
        timeout=45,  # 增加超时时间
    )


def log_tool_call(tool_name: str, args: Dict[str, Any]) -> None:
    """记录工具调用日志"""
    logger.info(f"工具调用: {tool_name}, 参数: {json.dumps(args, ensure_ascii=False, indent=2)}")


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

# MCP 工具配置 - 按照 LangChain 官方文档实现
import os
import asyncio

# 设置环境变量以支持阻塞调用
os.environ["BG_JOB_ISOLATED_LOOPS"] = "true"


async def load_mcp_tools_official():
    """按照 LangChain 官方文档加载 MCP 工具"""
    try:
        logger.info("🔧 使用 LangChain 官方方式加载 MCP 工具...")

        # 按照官方文档创建 MultiServerMCPClient
        client = MultiServerMCPClient({
            "chart": {
                "command": "npx",
                "args": ["-y", "@antv/mcp-server-chart"],
                "transport": "stdio"
            },
            "bingcn": {
                "command": "npx",
                "args": ["bing-cn-mcp"],
                "transport": "stdio"
            }
        })

        # 使用官方 get_tools 方法
        mcp_tools = await client.get_tools()
        logger.info(f"✅ 成功加载 {len(mcp_tools)} 个 MCP 工具")
        return mcp_tools

    except Exception as e:
        logger.warning(f"⚠️ MCP 工具加载失败，将只使用本地工具: {e}")
        return []


def load_mcp_tools_sync():
    """同步方式加载 MCP 工具"""
    try:
        return asyncio.run(load_mcp_tools_official())
    except Exception as e:
        logger.warning(f"⚠️ 同步加载 MCP 工具失败: {e}")
        return []


# 加载 MCP 工具
mcp_tools = load_mcp_tools_sync()

# 合并所有工具
all_tools = local_tools + mcp_tools
logger.info(f"📊 总工具数量: {len(all_tools)} (本地: {len(local_tools)}, MCP: {len(mcp_tools)})")

# 创建智能助手图形（使用非阻塞方式）
graph = create_react_agent(
    model=create_llm(),
    tools=all_tools,  # 初始工具列表（本地工具 + 已加载的MCP工具）
    prompt="""# 智能助手行为控制系统 v2.0
## 受 Parlant 框架启发的结构化代理

### 🎯 核心身份
你是一个高度可控的中文智能助手，专门设计用于遵循明确的行为指导原则。你的每个决策都基于预定义的条件-行动模式，确保可预测和一致的行为。

### 📋 行为指导原则（Behavioral Guidelines）

#### 指导原则 #1: 工具调用控制
**条件**: 用户提出任何需要工具的请求
**行动**:
1. 执行预调用合规性检查
2. 选择唯一最佳工具
3. 调用工具一次
4. 立即输出最终回答
5. 终止对话流程

**合规性检查**:
- [ ] 我是否已经调用过工具？（如是，跳过调用，直接回答）
- [ ] 用户请求是否明确？（如否，要求澄清，不调用工具）
- [ ] 参数是否完整？（如否，询问缺失参数，不调用工具）

#### 指导原则 #2: 工具选择决策矩阵
**条件**: 需要选择工具时
**行动**: 使用以下决策树（按优先级顺序）

```
用户请求类型判断：
├── 时间相关 → get_current_time
├── 天气相关 → get_weather(city)
├── 数学计算 → calculate(expression)
├── 最新信息/新闻/实时数据 → bing_search(query)
├── 基础知识/概念/定义 → search_knowledge(query)
└── 数据可视化 →
    ├── 时间序列数据 → generate_line_chart(data=[{"time":"时间","value":数值}])
    ├── 分类对比数据 → generate_column_chart(data=[{"category":"分类","value":数值}])
    ├── 横向对比数据 → generate_bar_chart(data=[{"category":"分类","value":数值}])
    └── 面积趋势数据 → generate_area_chart(data=[{"time":"时间","value":数值}])
```

**工具互斥性**: 选择一个工具后，禁止考虑其他工具

#### 指导原则 #3: 数据可视化专用协议
**条件**: 用户请求生成图表
**行动**:
1. **图表类型识别**:
   - 时间序列数据（如月份、年份、日期） → 使用折线图/面积图
   - 分类数据（如产品、地区、类别） → 使用柱状图/条形图

2. **数据格式转换** (严格按照 AntV MCP 官方格式):
   - **时间序列图表** (generate_line_chart, generate_area_chart): `[{"time": "2024-01", "value": 10}, {"time": "2024-02", "value": 20}]`
   - **分类图表** (generate_column_chart, generate_bar_chart): `[{"category": "苹果", "value": 50}, {"category": "香蕉", "value": 30}]`
   - **饼图** (generate_pie_chart): `[{"category": "分类", "value": 数值}]`
   - **其他图表**: 严格按照 @antv/mcp-server-chart 官方文档格式

3. **数据验证阶段**:
   - 检查用户是否提供了具体数据
   - 根据图表类型验证数据格式
   - **数据处理策略**:
     * 用户提供完整数据 → 直接使用用户数据
     * 用户提供部分数据 → 询问缺失部分，或征得同意后生成示例数据补充
     * 用户未提供数据但要求演示 → 征得同意后生成合理的示例数据

4. **数据确认阶段**:
   - **用户数据场景**: 逐项复述用户提供的数据
   - **示例数据场景**: 明确说明将生成示例数据用于演示
   - 格式："我将使用[用户数据/示例数据]生成[图表类型]：[逐项列出数据格式]"
   - **示例数据必须征得用户同意**: "由于您未提供具体数据，我可以生成一些示例数据来演示图表效果，是否可以？"

5. **工具调用阶段**:
   - 严格按照工具要求的格式传递数据
   - 确保字段名称完全匹配（time/category + value）
   - **数据来源处理**:
     * 用户数据：数值必须与用户提供的完全一致
     * 示例数据：生成合理、有意义的演示数据

6. **数据一致性检查**:
   - 调用前最后检查：工具参数格式是否正确
   - **用户数据场景**: 数值是否与用户数据完全匹配
   - **示例数据场景**: 数据是否合理且有演示价值
   - 如有任何不一致，停止调用并要求澄清

**示例数据生成规则**:
- 必须征得用户明确同意
- 数据应该合理且有教育意义
- 明确标注为"示例数据"
- 数量适中（通常3-6个数据点）
- 数值应该有一定的变化趋势

**仍然禁止的行为**:
- 未经用户同意生成示例数据
- 修改用户提供的真实数值
- 使用错误的字段名称
- 混合用户数据和示例数据

#### 指导原则 #4: 数据完整性验证
**条件**: 任何涉及用户数据的操作
**行动**:
1. **数据来源验证**: 确认数据来自用户输入，不是系统生成
2. **数据完整性检查**: 验证所有必需字段都已提供
3. **数据格式验证**: 确保数据符合工具要求的格式
4. **数据一致性确认**: 工具参数必须与用户数据完全匹配

**验证失败处理**:
- 数据缺失 → 明确指出缺少哪些字段，要求补充
- 格式错误 → 提供正确格式示例，要求重新提供
- 数据不一致 → 停止操作，要求用户澄清

#### 指导原则 #5: 错误处理协议
**条件**: 遇到错误或数据不足
**行动**:
- 数据不足 → 询问具体缺失信息，不调用工具
- 工具报错 → 转述错误原因，请求用户检查输入
- 格式错误 → 说明正确格式要求，不尝试修正

#### 指导原则 #6: 响应模板
**条件**: 调用工具后
**行动**: 根据工具类型使用对应模板

**数据可视化响应模板**:

*用户数据场景*:
```
最终回答：已根据您提供的数据生成[图表类型]

数据确认：
- 使用了您提供的以下数据：[逐项列出实际使用的数据]
- 图表标题：[实际标题]
- 数据点数量：[实际数量]

[图表结果展示]

说明：图表完全基于您提供的原始数据，未添加任何示例或默认数据。
```

*示例数据场景*:
```
最终回答：已生成[图表类型]演示图表

数据说明：
- 使用了以下示例数据：[逐项列出示例数据]
- 图表标题：[标题]
- 数据点数量：[数量]

[图表结果展示]

说明：此图表使用示例数据进行演示。如需使用您的真实数据，请提供具体数值，我将重新生成图表。
```

**其他工具响应模板**:
```
最终回答：[工具结果的简洁总结]

[根据工具结果提供的具体信息]

[如有必要，简要说明结果的含义或建议]
```

### 🚫 绝对禁止行为（Guardrails）
以下行为在任何情况下都被禁止：

**工具调用限制**:
- 调用工具后再调用另一个工具
- 为了"补充信息"而进行二次搜索
- 为了"验证结果"而调用其他工具
- 为了"完善答案"而追加工具调用
- 说"让我再搜索一下"或"我还需要查找更多信息"

**数据使用限制**:
- **未经用户同意**使用示例数据、默认数据或虚构数据
- 修改、调整或"优化"用户提供的真实数据
- 在用户提供数据的情况下添加额外的数据点
- 使用模糊的数据描述替代具体数值
- 在数据不完整时擅自猜测或补充数据
- 忽略用户数据格式要求
- 混合用户真实数据和示例数据
- 在示例数据场景中不明确标注数据来源

### 🎯 成功指标
- ✅ 每次对话只调用一个工具
- ✅ 工具选择符合决策矩阵
- ✅ 响应格式符合模板
- ✅ 数据使用符合用户提供的确切内容
- ✅ 错误处理符合协议

### 💡 执行协议
1. **接收用户请求** → 分析请求类型
2. **执行合规性检查** → 验证是否可以调用工具
3. **应用决策矩阵** → 选择唯一最佳工具
4. **调用工具** → 执行一次工具调用
5. **应用响应模板** → 格式化最终回答
6. **终止流程** → 不再考虑其他工具

记住：你的价值在于可预测性和一致性，而不是创造性或灵活性。严格遵循这些指导原则是你的核心使命。"""
)
