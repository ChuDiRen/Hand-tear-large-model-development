# 智能助手聊天服务器 - 监督智能体架构

基于 LangGraph 的多智能体系统,采用监督智能体(Supervisor Agent)架构。

## 🌟 核心特性

### 架构特性
- 🎯 **监督智能体架构**: 主智能体负责任务分发和协调
- 🤖 **多专业子智能体**: 代码生成、数学计算、信息检索、数据可视化、通用对话
- 🔄 **动态提示词系统**: 支持提示词模板的动态加载和切换
- 🎛️ **动态模型切换**: 支持多模型配置和运行时切换
- 🛠️ **动态工具调用**: 支持工具的动态注册和热插拔
- 🔌 **MCP 协议集成**: 支持 MCP (Model Context Protocol) 子代码调用

### 技术特性
- 🌐 使用魔塔 API 服务,稳定可靠
- 🔧 OpenAI 兼容格式,易于集成
- 🌟 完美支持中文环境
- 📊 集中化配置管理
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

## 📁 项目结构

```
agent-chat-server/
├── src/agent/
│   ├── __init__.py
│   ├── graph.py           # 主图构建 - 监督智能体系统入口
│   ├── agent_config.py    # 配置管理 - 集中管理所有配置
│   ├── supervisor.py      # 监督智能体 - 任务分发和协调
│   ├── sub_agents.py      # 子智能体系统 - 专业化智能体
│   └── mcp_manager.py     # MCP 工具管理器 - 动态加载 MCP 工具
├── .env                   # 环境配置
├── langgraph.json         # LangGraph 配置
├── pyproject.toml         # 项目配置
├── run.py                 # 启动脚本
└── README.md              # 说明文档
```

## 🏗️ 系统架构

### 监督智能体架构图

```
用户请求
    ↓
┌─────────────────────┐
│  Supervisor Agent   │  ← 主智能体(任务分发)
│  (监督智能体)       │
└─────────────────────┘
    ↓ (分发任务)
    ├─→ Code Agent      (代码生成/分析)
    ├─→ Math Agent      (数学计算)
    ├─→ Research Agent  (信息检索)
    ├─→ Chart Agent     (数据可视化)
    └─→ General Agent   (通用对话)
         ↓ (返回结果)
    ┌─────────────────────┐
    │  Supervisor Agent   │
    └─────────────────────┘
         ↓
      用户响应
```

### 工作流程

1. **用户请求** → 监督智能体接收
2. **任务分析** → 监督智能体分析任务类型
3. **智能体选择** → 选择最合适的子智能体
4. **任务执行** → 子智能体执行具体任务
5. **结果整合** → 监督智能体整合结果
6. **用户响应** → 返回最终结果

### 子智能体说明

| 智能体 | 职责 | 工具 | 模型温度 |
|--------|------|------|----------|
| **Code Agent** | 代码生成、代码分析、编程问题解答 | - | 0.0 |
| **Math Agent** | 数学计算、公式求解、数据分析 | calculate | 0.0 |
| **Research Agent** | 信息搜索、知识查询、资料检索 | search_knowledge | 0.2 |
| **Chart Agent** | 数据可视化、图表生成 | MCP 图表工具 | 0.1 |
| **General Agent** | 通用对话、时间查询、天气查询 | get_current_time, get_weather | 0.1 |

## ⚙️ 配置说明

### 基础配置

在 `.env` 文件中配置系统参数:

```bash
# ========== 基础模型配置 ==========
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api-inference.modelscope.cn/v1
OPENAI_MODEL=ZhipuAI/GLM-4.5

# ========== 监督智能体系统配置 ==========
ENABLE_SUPERVISOR=1          # 是否启用监督模式 (1=启用, 0=禁用)
SUPERVISOR_MODEL=default     # 监督智能体使用的模型

# ========== 子智能体模型配置 ==========
# 各子智能体可以使用不同的模型
# AGENT_MODEL_CODE=ZhipuAI/GLM-4.5
# AGENT_MODEL_MATH=ZhipuAI/GLM-4.5
# AGENT_MODEL_RESEARCH=ZhipuAI/GLM-4.5

# ========== 模型温度参数配置 ==========
AGENT_TEMP_DEFAULT=0.1
AGENT_TEMP_CODE=0.0
AGENT_TEMP_MATH=0.0
AGENT_TEMP_RESEARCH=0.2

# ========== MCP 配置 ==========
ENABLE_MCP=1                 # 是否启用 MCP 功能
ENABLE_MCP_CHART=1           # 是否启用图表服务器
ENABLE_MCP_BING=0            # 是否启用必应搜索
```

### 配置参数说明

#### 基础配置
- **OPENAI_API_KEY**: 魔塔平台的 API 密钥
- **OPENAI_BASE_URL**: 魔塔 API 的基础 URL
- **OPENAI_MODEL**: 默认使用的模型名称

#### 监督智能体配置
- **ENABLE_SUPERVISOR**: 是否启用监督模式 (1=启用, 0=禁用)
- **SUPERVISOR_MODEL**: 监督智能体使用的模型配置名称

#### 子智能体配置
- **AGENT_MODEL_XXX**: 各子智能体可以配置不同的模型
- **AGENT_TEMP_XXX**: 各子智能体的温度参数 (0.0-1.0)

#### MCP 配置
- **ENABLE_MCP**: 是否启用 MCP 功能
- **ENABLE_MCP_CHART**: 是否启用 AntV 图表服务器
- **ENABLE_MCP_BING**: 是否启用必应搜索服务器

## 💡 使用方法

### 基本使用

启动服务器后,可以通过以下方式与智能助手交互:

1. **前端界面**: 使用配套的 agent-chat-ui 前端应用
2. **API 调用**: 直接调用 REST API
3. **Studio UI**: 使用 LangGraph Studio 进行调试

### 使用示例

#### 代码相关任务
```
用户: 帮我写一个 Python 函数,实现快速排序
→ Supervisor 分发给 Code Agent
→ Code Agent 生成代码并返回
```

#### 数学计算任务
```
用户: 计算 (3 + 5) * 7 的结果
→ Supervisor 分发给 Math Agent
→ Math Agent 调用 calculate 工具并返回结果
```

#### 信息检索任务
```
用户: 什么是 LangGraph?
→ Supervisor 分发给 Research Agent
→ Research Agent 搜索知识库并返回信息
```

#### 数据可视化任务
```
用户: 帮我画一个销售数据的柱状图
→ Supervisor 分发给 Chart Agent
→ Chart Agent 调用 MCP 图表工具生成图表
```

#### 通用对话任务
```
用户: 现在几点了?
→ Supervisor 分发给 General Agent
→ General Agent 调用 get_current_time 工具返回时间
```

## 🛠️ 支持的工具

### 内置工具

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

## 🔧 扩展开发

### 添加新的子智能体

1. 在 `agent_config.py` 中添加提示词配置
2. 添加子智能体配置
3. 更新监督智能体提示词

### 添加新的工具

在 `graph.py` 中定义工具函数并添加到 `local_tools` 列表

### 添加新的 MCP 服务器

在 `agent_config.py` 中添加 MCP 服务器配置

## 🐛 故障排除

**Q: 监督智能体无法正确分发任务?**
A: 检查监督智能体的提示词配置

**Q: MCP 工具加载失败?**
A: 检查 Node.js 是否已安装,查看日志中的详细错误信息

**Q: 如何禁用监督模式?**
A: 在 `.env` 中设置 `ENABLE_SUPERVISOR=0`

## 📚 技术栈

- **LangGraph**: 多智能体工作流框架
- **LangChain**: 大模型抽象层
- **LangChain MCP Adapters**: MCP 协议适配器
- **魔塔 API**: GLM-4.5 大模型服务

## 📄 许可证

MIT License - Copyright (c) 2025 左岚

---

欢迎提交 Issue 和 Pull Request!
