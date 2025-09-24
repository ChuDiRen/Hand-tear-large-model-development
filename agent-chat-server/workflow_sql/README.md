# Copyright (c) 2025 左岚. All rights reserved.
# SQL智能体工作流模块

基于 LangChain 和 LangGraph 的 SQL 智能体工作流，提供自然语言到SQL查询的转换和执行功能。

## 功能特性

- 🤖 **自然语言查询**: 将自然语言问题转换为SQL查询
- 🗄️ **多数据库支持**: 支持 SQLite、PostgreSQL、MySQL 等数据库
- 📊 **图表生成**: 自动生成查询结果的可视化图表
- 🔧 **工具集成**: 集成多种SQL操作工具
- 📝 **智能验证**: 自动验证和优化SQL查询
- 🌐 **异步处理**: 支持异步图表生成和MCP服务

## 快速开始

### 1. 环境配置

创建 `.env` 文件并配置必要的环境变量：

```bash
# 必需配置 - DeepSeek API密钥
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 可选配置 - 数据库连接
DB_URI=sqlite:///path/to/your/database.db

# 可选配置 - 语言模型设置
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
LLM_TEMPERATURE=0.0

# 可选配置 - 数据库设置
DATABASE_MAX_QUERY_RESULTS=5
DATABASE_TIMEOUT_SECONDS=30

# 可选配置 - 日志设置
LOG_LEVEL=INFO
```

### 2. 安装依赖

```bash
# 安装基础依赖
pip install langchain langgraph langchain-community python-dotenv sqlalchemy

# 或者使用requirements文件
pip install -r workflow_sql/requirements.txt

# 如果遇到导入错误，请确保安装完整依赖
pip install -e .  # 从项目根目录安装
```

### 3. 启动服务

**方式一：使用启动脚本（推荐）**
```bash
# 从项目根目录启动
python start_sql.py
```

**方式二：手动设置环境变量**
```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="your_api_key_here"
python run.py

# Linux/Mac
export DEEPSEEK_API_KEY="your_api_key_here"
python run.py
```

**方式三：使用LangGraph CLI**
```bash
# 确保环境变量已设置
langgraph dev --graph workflow_sql
```

### 4. 使用示例

**通过API调用：**
```bash
curl -X POST "http://127.0.0.1:2024/workflow_sql/runs" \
  -H "Content-Type: application/json" \
  -d '{"input": {"messages": [{"role": "user", "content": "哪种音乐类型的曲目平均时长最长？"}]}}'
```

**通过Python代码：**
```python
from workflow_sql import graph

# 运行查询
question = "哪种音乐类型的曲目平均时长最长？"
result = graph.invoke({"messages": [{"role": "user", "content": question}]})
```

## 配置说明

### 环境变量配置

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `DEEPSEEK_API_KEY` | ✅ | - | DeepSeek API密钥 |
| `DB_URI` | ❌ | `sqlite:///Chinook.db` | 数据库连接字符串 |
| `LLM_PROVIDER` | ❌ | `deepseek` | 语言模型提供商 |
| `LLM_MODEL` | ❌ | `deepseek-chat` | 语言模型名称 |
| `LLM_TEMPERATURE` | ❌ | `0.0` | 模型温度参数 |
| `DATABASE_MAX_QUERY_RESULTS` | ❌ | `5` | 查询结果最大条数 |
| `DATABASE_TIMEOUT_SECONDS` | ❌ | `30` | 查询超时时间（秒） |
| `LOG_LEVEL` | ❌ | `INFO` | 日志级别 |

### 安全性说明

⚠️ **重要**: 本模块已移除所有硬编码的API密钥，所有敏感信息必须通过环境变量配置。请确保：

1. 在生产环境中妥善保管API密钥
2. 不要将包含密钥的 `.env` 文件提交到版本控制系统
3. 使用环境变量或安全的密钥管理服务

## 模块结构

```
workflow_sql/
├── __init__.py           # 模块初始化
├── agent_types.py        # 类型定义和异常类
├── config.py            # 配置管理
├── database.py          # 数据库管理
├── tools.py             # SQL工具管理
├── nodes.py             # 图节点实现
├── graph_builder.py     # 图构建器
├── graph.py             # 主图实现
├── async_chart_generator.py  # 异步图表生成
├── mcp_client.py        # MCP客户端管理
├── mcp_config.py        # MCP配置
└── logging_config.py    # 日志配置
```

## 工作流程

1. **列表表** (`ListTablesNode`): 获取数据库中的所有表
2. **获取结构** (`GetSchemaNode`): 获取相关表的结构信息
3. **生成查询** (`GenerateQueryNode`): 基于问题生成SQL查询
4. **检查查询** (`CheckQueryNode`): 验证和优化SQL查询
5. **生成答案** (`AnswerGenerationNode`): 执行查询并生成答案
6. **生成图表** (`ChartGenerationNode`): 可选的图表生成步骤

## 代码优化

本模块已进行以下优化：

### ✅ 安全性优化
- 移除所有硬编码API密钥
- 强制使用环境变量配置敏感信息
- 添加配置验证和错误提示

### ✅ 代码质量优化
- 添加版权水印到所有文件
- 统一导入方式，移除重复逻辑
- 优化日志记录格式和内容
- 改进异常处理的一致性

### ✅ 可维护性优化
- 统一注释格式（位于代码右侧）
- 增强错误日志的详细程度
- 优化成功操作的日志信息

## 使用示例

### 基本查询

```python
from workflow_sql.graph import graph

# 简单查询
question = "有多少个客户？"
result = graph.invoke({"messages": [{"role": "user", "content": question}]})

# 复杂查询
question = "按国家统计客户数量，显示前5个国家"
result = graph.invoke({"messages": [{"role": "user", "content": question}]})
```

### 自定义配置

```python
from workflow_sql.config import AgentConfig, DatabaseConfig, LLMConfig

# 自定义配置
config = AgentConfig(
    database=DatabaseConfig(uri="postgresql://user:pass@localhost/db"),
    llm=LLMConfig(provider="openai", model="gpt-4"),
    logging=LoggingConfig(level="DEBUG")
)
```

## 故障排除

### 常见问题

1. **相对导入错误**
   ```
   ImportError: attempted relative import with no known parent package
   ```
   解决方案：已修复为绝对导入，如仍有问题请安装完整依赖

2. **模块未找到错误**
   ```
   ModuleNotFoundError: No module named 'langchain_community'
   ```
   解决方案：安装缺失依赖 `pip install langchain-community`

3. **API密钥错误**
   ```
   ValueError: DEEPSEEK_API_KEY环境变量未设置
   ```
   解决方案：在 `.env` 文件中设置正确的API密钥

4. **数据库连接失败**
   ```
   DatabaseConnectionError: 数据库连接失败
   ```
   解决方案：检查数据库URI和连接权限

5. **工具未找到**
   ```
   ToolNotFoundError: 未找到必需工具
   ```
   解决方案：检查工具包初始化和依赖安装

### 临时解决方案

如果遇到依赖问题，系统会自动使用简化版本的图 (`graph_simple.py`)，该版本：
- 避免复杂依赖
- 提供基本的接口兼容性
- 返回友好的错误提示

## 开发指南

### 添加新节点

```python
from workflow_sql.agent_types import BaseNode

class CustomNode(BaseNode):
    def __init__(self, name: str):
        super().__init__(name)
    
    def execute(self, state):
        # 节点逻辑实现
        return {"messages": [...]}
```

### 扩展工具

```python
from langchain_core.tools import tool

@tool
def custom_sql_tool(query: str) -> str:
    """自定义SQL工具"""
    # 工具实现
    return result
```

## 版本历史

- **v1.1.0**: 安全性和代码质量优化
  - 移除硬编码密钥
  - 统一代码风格
  - 优化日志和异常处理
- **v1.0.0**: 初始版本
  - 基础SQL智能体功能
  - 图表生成支持

---

© 2025 左岚. All rights reserved.
