# 智能助手聊天服务器

基于 LangGraph 和魔塔大模型的智能助手聊天服务器。

## 功能特性

- 🤖 基于 GLM-4.5 大模型的智能对话
- 🛠️ **工具调用支持** - 使用 LangGraph ReAct Agent
- 💬 支持复杂问题回答和多轮对话
- 🌐 使用魔塔 API 服务，稳定可靠
- 🔧 OpenAI 兼容格式，易于集成
- 🌟 友好的中文交互体验
- 🚀 简单易用的启动方式

## 快速开始

### 1. 安装依赖

```bash
pip install -e .
```

### 2. 启动服务器

**推荐方式（自动配置环境）：**
```bash
python start.py
```

**或者手动启动：**
```bash
python run.py
```

**或者直接使用：**
```bash
langgraph dev
```

### 3. 访问服务

- **API 服务**: http://localhost:2024
- **API 文档**: http://localhost:2024/docs
- **Studio UI**: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

## 项目结构

```
agent-chat-server/
├── src/agent/
│   ├── __init__.py
│   └── graph.py          # 智能助手核心逻辑
├── .env                  # 环境配置
├── langgraph.json        # LangGraph 配置
├── pyproject.toml        # 项目配置
├── run.py               # 启动脚本
└── README.md            # 说明文档
```

## 配置说明

在 `.env` 文件中配置魔塔大模型：

```bash
# 魔塔大模型配置 (OpenAI 兼容格式)
OPENAI_API_KEY=ms-0e0e7c95-62f5-4c6b-bf9b-15b0f2240a17
OPENAI_BASE_URL=https://api-inference.modelscope.cn/v1
OPENAI_MODEL=ZhipuAI/GLM-4.5

# LangSmith 配置 (可选)
LANGSMITH_PROJECT=agent-chat-server
# LANGSMITH_API_KEY=lsv2_your_api_key_here
```

### 配置参数说明

- **OPENAI_API_KEY**: 魔塔平台的 API 密钥
- **OPENAI_BASE_URL**: 魔塔 API 的基础 URL
- **OPENAI_MODEL**: 使用的模型名称（GLM-4.5）
- **LANGSMITH_PROJECT**: LangSmith 项目名称（用于追踪）

## 使用方法

启动服务器后，可以通过以下方式与智能助手交互：

1. **前端界面**: 使用配套的 agent-chat-ui 前端应用
2. **API 调用**: 直接调用 REST API
3. **Studio UI**: 使用 LangGraph Studio 进行调试

## 支持的对话和工具

基于 GLM-4.5 大模型和 ReAct Agent，支持：

### 🛠️ 内置工具

- ⏰ **时间查询** (`get_current_time`): 获取当前时间
- 🌤️ **天气查询** (`get_weather`): 获取城市天气信息
- 🧮 **数学计算** (`calculate`): 进行数学表达式计算
- 📚 **知识搜索** (`search_knowledge`): 搜索内置知识库

### 🌐 MCP 扩展工具

- 🔍 **网络搜索** (`bing_search`): 必应中文实时搜索，获取最新信息
- 📊 **数据可视化** (`generate_*_chart`): 支持柱状图、折线图、面积图等多种图表类型

### 💬 对话能力

- 📝 **通用问答**: 各种知识问题、学习辅导
- 💼 **工作助手**: 文档写作、邮件起草、方案制定
- 🧮 **逻辑推理**: 数学计算、逻辑分析、问题解决
- 🌍 **多领域知识**: 科技、历史、文化、生活常识
- 💬 **多轮对话**: 上下文理解，连续对话
- 🎯 **任务执行**: 代码编写、文本处理、创意写作

### 🔧 工具调用示例

**本地工具：**
- "现在几点了？" → 自动调用时间工具
- "北京天气怎么样？" → 自动调用天气工具
- "计算 2+3*4" → 自动调用计算工具
- "什么是人工智能？" → 自动调用知识搜索工具

**网络搜索：**
- "今天的新闻有什么？" → 自动调用必应搜索
- "最新的AI技术发展" → 自动调用必应搜索
- "2024年经济形势" → 自动调用必应搜索

**数据可视化：**
- "帮我画个销售数据的柱状图" → 自动调用图表生成工具
- "生成产品对比的条形图" → 自动调用图表生成工具

## 开发说明

- **核心逻辑**: `src/agent/graph.py` - 基于 LangChain 和 LangGraph 的智能助手实现
- **大模型集成**: 使用 `langchain-openai` 连接魔塔 API
- **错误处理**: 包含完善的异常处理和错误提示
- **系统提示**: 内置中文友好的系统提示词

## 技术架构

- **LangGraph ReAct Agent**: 支持工具调用的智能代理
- **LangChain Tools**: 工具抽象和管理
- **LangChain**: 大模型抽象层
- **魔塔 API**: GLM-4.5 大模型服务
- **OpenAI 兼容**: 标准化 API 接口

## 工具扩展

可以轻松添加新的工具：

```python
@tool
def your_custom_tool(param: str) -> str:
    """工具描述"""
    # 工具实现
    return "结果"

# 添加到工具列表
tools.append(your_custom_tool)
```

---

© 2025 左岚. All rights reserved.
