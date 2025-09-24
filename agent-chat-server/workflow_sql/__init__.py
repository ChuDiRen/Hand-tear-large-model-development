# Copyright (c) 2025 左岚. All rights reserved.
"""SQL智能体工作流模块

本模块提供SQL智能体的核心功能。
"""

# 修复相对导入问题，使用绝对导入
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 导入图和配置
try:
    from workflow_sql.graph import graph
    from workflow_sql.config import get_config, AgentConfig
    __all__ = ["graph", "get_config", "AgentConfig"]
except ImportError as e:
    # 如果导入失败，只导出配置功能
    from workflow_sql.config import get_config, AgentConfig
    __all__ = ["get_config", "AgentConfig"]
    print(f"Warning: Could not import graph: {e}")
