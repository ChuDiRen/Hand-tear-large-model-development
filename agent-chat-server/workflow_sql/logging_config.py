# Copyright (c) 2025 左岚. All rights reserved.
"""SQL智能体日志配置模块

本模块提供集中化的日志配置，支持控制台日志输出和颜色区分。
"""

import logging
import sys
import os

# 修复相对导入问题，使用绝对导入
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from workflow_sql.config import LoggingConfig  # 日志配置类


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""

    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
    }

    # 节点特定颜色
    NODE_COLORS = {
        'nodes': '\033[94m',           # 蓝色 - 节点执行
        'graph_builder': '\033[96m',   # 亮青色 - 图构建
        'database': '\033[92m',        # 亮绿色 - 数据库
        'tools': '\033[93m',           # 亮黄色 - 工具
        'mcp_client': '\033[95m',      # 亮紫色 - MCP客户端
        'async_chart_generator': '\033[91m',  # 亮红色 - 图表生成
    }

    RESET = '\033[0m'  # 重置颜色

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 检查是否支持颜色输出
        self.use_colors = (
            hasattr(sys.stdout, 'isatty') and sys.stdout.isatty() and
            os.getenv('NO_COLOR') is None and
            os.getenv('TERM') != 'dumb'
        )

    def format(self, record):
        if not self.use_colors:
            return super().format(record)

        # 获取基础格式化结果
        log_message = super().format(record)

        # 根据日志级别选择颜色
        level_color = self.COLORS.get(record.levelname, '')

        # 根据模块名选择特定颜色
        module_color = ''
        for module, color in self.NODE_COLORS.items():
            if module in record.name:
                module_color = color
                break

        # 如果有模块特定颜色，优先使用
        color = module_color or level_color

        if color:
            return f"{color}{log_message}{self.RESET}"

        return log_message


def setup_logging(config: LoggingConfig) -> None:
    """设置日志配置

    Args:
        config: 日志配置
    """
    # 获取根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.level.upper()))

    # 清除现有处理器
    root_logger.handlers.clear()

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.level.upper()))

    # 设置带颜色的格式化器
    formatter = ColoredFormatter(
        fmt=config.format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 设置特定日志记录器级别
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('langchain').setLevel(logging.WARNING)

    # 记录配置信息
    logger = logging.getLogger(__name__)
    logger.info(f"🎨 日志配置完成 - 级别: {config.level} | 颜色支持: {'✅' if formatter.use_colors else '❌'}")


def get_node_logger(node_name: str) -> logging.Logger:
    """获取节点专用日志记录器

    Args:
        node_name: 节点名称

    Returns:
        配置好的日志记录器
    """
    return logging.getLogger(f"workflow_sql.nodes.{node_name}")


def log_node_start(logger: logging.Logger, node_name: str, description: str = "") -> None:
    """记录节点开始执行

    Args:
        logger: 日志记录器
        node_name: 节点名称
        description: 描述信息
    """
    desc_text = f" - {description}" if description else ""
    logger.info(f"🚀 开始执行 {node_name} 节点{desc_text}")


def log_node_complete(logger: logging.Logger, node_name: str, result: str = "") -> None:
    """记录节点完成执行

    Args:
        logger: 日志记录器
        node_name: 节点名称
        result: 结果信息
    """
    result_text = f" - {result}" if result else ""
    logger.info(f"✅ {node_name} 节点执行完成{result_text}")


def log_node_error(logger: logging.Logger, node_name: str, error: str) -> None:
    """记录节点执行错误

    Args:
        logger: 日志记录器
        node_name: 节点名称
        error: 错误信息
    """
    logger.error(f"❌ {node_name} 节点执行失败: {error}")
