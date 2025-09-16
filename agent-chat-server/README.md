# 智能助手聊天服务器

基于 LangGraph 的简化版智能助手聊天服务器。

## 功能特性

- 🤖 智能对话处理
- 💬 支持基本聊天功能
- 🕐 时间查询
- 🌟 友好的中文交互
- 🚀 简单易用的启动方式

## 快速开始

### 1. 安装依赖

```bash
pip install -e .
```

### 2. 启动服务器

```bash
python run.py
```

或者直接使用：

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

在 `.env` 文件中可以配置：

```bash
LANGSMITH_PROJECT=agent-chat-server
# LANGSMITH_API_KEY=your_api_key_here
```

## 使用方法

启动服务器后，可以通过以下方式与智能助手交互：

1. **前端界面**: 使用配套的 agent-chat-ui 前端应用
2. **API 调用**: 直接调用 REST API
3. **Studio UI**: 使用 LangGraph Studio 进行调试

## 支持的对话

- 问候语：你好、hello
- 告别语：再见、bye
- 感谢语：谢谢、thank you
- 时间查询：现在几点、时间
- 天气查询：天气怎么样
- 其他任意文本对话

## 开发说明

智能助手的核心逻辑在 `src/agent/graph.py` 文件中，可以根据需要修改对话处理逻辑。

---

© 2025 左岚. All rights reserved.
