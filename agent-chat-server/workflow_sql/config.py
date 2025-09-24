# Copyright (c) 2025 左岚. All rights reserved.
"""SQL智能体配置管理模块

本模块提供集中化的配置管理，支持环境变量和默认值。
"""

import logging
import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# 创建logger
logger = logging.getLogger(__name__)

# 获取当前文件所在目录的绝对路径
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 构建数据库文件的绝对路径
_DEFAULT_DB_PATH = os.path.join(_CURRENT_DIR, "Chinook.db")


@dataclass
class DatabaseConfig:
    """数据库配置类"""

    uri: str = f"sqlite:///{_DEFAULT_DB_PATH}"  # 数据库连接字符串（绝对路径）
    max_query_results: int = 5         # 查询结果最大条数
    timeout_seconds: int = 30          # 查询超时时间（秒）


@dataclass
class LLMConfig:
    """语言模型配置类"""

    provider: str = "deepseek"                                    # 模型提供商
    model: str = "deepseek-chat"                                 # 模型名称
    api_key: str = ""                                            # API密钥（从环境变量获取）
    temperature: float = 0.0                                     # 温度参数
    max_tokens: Optional[int] = None                             # 最大token数


@dataclass
class LoggingConfig:
    """日志配置类"""

    level: str = "INFO"                                          # 日志级别
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # 日志格式


@dataclass
class AgentConfig:
    """SQL智能体主配置类"""

    database: DatabaseConfig
    llm: LLMConfig
    logging: LoggingConfig

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """从环境变量创建配置

        Returns:
            从环境变量加载的AgentConfig实例
        """
        # 尝试加载.env文件
        try:
            # 查找.env文件的可能位置
            env_paths = [
                os.path.join(os.path.dirname(__file__), ".env"),  # workflow_sql/.env
                os.path.join(os.path.dirname(__file__), "..", ".env"),  # agent-chat-server/.env
                ".env"  # 当前目录
            ]

            for env_path in env_paths:
                if os.path.exists(env_path):
                    load_dotenv(env_path)
                    logger.info(f"✅ 加载环境变量文件: {env_path}")
                    break
            else:
                logger.warning("⚠️ 未找到.env文件，使用系统环境变量")
                load_dotenv()  # 尝试默认加载

        except Exception as e:
            logger.warning(f"⚠️ 加载.env文件失败: {e}")
            load_dotenv()  # 尝试默认加载

        # 数据库配置
        db_config = DatabaseConfig(
            uri=os.getenv("DB_URI", f"sqlite:///{_DEFAULT_DB_PATH}"),
            max_query_results=int(os.getenv("DATABASE_MAX_QUERY_RESULTS", "5")),
            timeout_seconds=int(os.getenv("DATABASE_TIMEOUT_SECONDS", "30"))
        )

        # 语言模型配置
        api_key = os.getenv("DEEPSEEK_API_KEY")  # 从环境变量获取API密钥
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY环境变量未设置，请在.env文件或系统环境变量中配置")

        llm_config = LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "deepseek"),
            model=os.getenv("LLM_MODEL", "deepseek-chat"),
            api_key=api_key,
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.0")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS")) if os.getenv("LLM_MAX_TOKENS") else None
        )

        # 日志配置
        logging_config = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )

        return cls(
            database=db_config,
            llm=llm_config,
            logging=logging_config
        )


def get_config() -> AgentConfig:
    """获取全局配置实例

    Returns:
        从环境变量加载的AgentConfig实例
    """
    return AgentConfig.from_env()
