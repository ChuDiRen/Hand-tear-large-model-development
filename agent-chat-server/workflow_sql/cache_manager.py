# Copyright (c) 2025 左岚. All rights reserved.
"""SQL智能体缓存管理器

本模块提供高效的数据库信息缓存机制，避免重复获取相同信息。
"""

import logging
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目数据类"""
    data: Any
    timestamp: float
    access_count: int = 0
    
    def is_expired(self, ttl_seconds: int) -> bool:
        """检查缓存是否过期"""
        return time.time() - self.timestamp > ttl_seconds
    
    def access(self) -> Any:
        """访问缓存数据，更新访问计数"""
        self.access_count += 1
        return self.data


class SQLCacheManager:
    """SQL数据库信息缓存管理器"""
    
    def __init__(self, default_ttl: int = 3600, max_entries: int = 100):
        """初始化缓存管理器
        
        Args:
            default_ttl: 默认缓存生存时间（秒），默认1小时
            max_entries: 最大缓存条目数，默认100
        """
        self.default_ttl = default_ttl
        self.max_entries = max_entries
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        
        logger.info(f"SQL缓存管理器初始化 - TTL: {default_ttl}秒, 最大条目: {max_entries}")
    
    def get(self, key: str, ttl: Optional[int] = None) -> Optional[Any]:
        """获取缓存数据
        
        Args:
            key: 缓存键
            ttl: 自定义TTL，如果为None则使用默认TTL
            
        Returns:
            缓存的数据，如果不存在或已过期则返回None
        """
        with self._lock:
            if key not in self._cache:
                logger.debug(f"缓存未命中: {key}")
                return None
            
            entry = self._cache[key]
            ttl = ttl or self.default_ttl
            
            if entry.is_expired(ttl):
                logger.debug(f"缓存已过期: {key}")
                del self._cache[key]
                return None
            
            logger.debug(f"缓存命中: {key} (访问次数: {entry.access_count + 1})")
            return entry.access()
    
    def set(self, key: str, data: Any) -> None:
        """设置缓存数据
        
        Args:
            key: 缓存键
            data: 要缓存的数据
        """
        with self._lock:
            # 如果缓存已满，清理最少使用的条目
            if len(self._cache) >= self.max_entries:
                self._evict_lru()
            
            self._cache[key] = CacheEntry(
                data=data,
                timestamp=time.time(),
                access_count=0
            )
            logger.debug(f"缓存已设置: {key}")
    
    def delete(self, key: str) -> bool:
        """删除缓存条目
        
        Args:
            key: 缓存键
            
        Returns:
            是否成功删除
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"缓存已删除: {key}")
                return True
            return False
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            logger.info(f"已清空所有缓存 ({count} 个条目)")
    
    def _evict_lru(self) -> None:
        """清理最少使用的缓存条目"""
        if not self._cache:
            return
        
        # 找到访问次数最少的条目
        lru_key = min(self._cache.keys(), 
                     key=lambda k: self._cache[k].access_count)
        del self._cache[lru_key]
        logger.debug(f"LRU清理: {lru_key}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息
        
        Returns:
            包含缓存统计信息的字典
        """
        with self._lock:
            total_entries = len(self._cache)
            total_accesses = sum(entry.access_count for entry in self._cache.values())
            
            # 计算过期条目数
            current_time = time.time()
            expired_count = sum(
                1 for entry in self._cache.values()
                if entry.is_expired(self.default_ttl)
            )
            
            return {
                "total_entries": total_entries,
                "expired_entries": expired_count,
                "total_accesses": total_accesses,
                "max_entries": self.max_entries,
                "default_ttl": self.default_ttl,
                "cache_keys": list(self._cache.keys())
            }
    
    def cleanup_expired(self) -> int:
        """清理所有过期的缓存条目
        
        Returns:
            清理的条目数量
        """
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired(self.default_ttl)
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.info(f"清理了 {len(expired_keys)} 个过期缓存条目")
            
            return len(expired_keys)


# 全局缓存管理器实例
_cache_manager: Optional[SQLCacheManager] = None


def get_cache_manager() -> SQLCacheManager:
    """获取全局缓存管理器实例
    
    Returns:
        SQLCacheManager实例
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = SQLCacheManager()
    return _cache_manager


def initialize_cache(ttl: int = 3600, max_entries: int = 100) -> None:
    """初始化全局缓存管理器
    
    Args:
        ttl: 缓存生存时间（秒）
        max_entries: 最大缓存条目数
    """
    global _cache_manager
    _cache_manager = SQLCacheManager(ttl, max_entries)
    logger.info("全局SQL缓存管理器已初始化")


# 缓存键常量
class CacheKeys:
    """缓存键常量类"""
    TABLES_LIST = "tables_list"
    DATABASE_INFO = "database_info"
    
    @staticmethod
    def table_schema(table_names: str) -> str:
        """生成表结构缓存键"""
        return f"schema_{table_names}" if table_names else "schema_all"
    
    @staticmethod
    def query_result(query_hash: str) -> str:
        """生成查询结果缓存键"""
        return f"query_{query_hash}"


def cache_tables_list(tables: List[str]) -> None:
    """缓存表列表"""
    cache_manager = get_cache_manager()
    cache_manager.set(CacheKeys.TABLES_LIST, tables)


def get_cached_tables_list() -> Optional[List[str]]:
    """获取缓存的表列表"""
    cache_manager = get_cache_manager()
    return cache_manager.get(CacheKeys.TABLES_LIST)


def cache_table_schema(table_names: str, schema: str) -> None:
    """缓存表结构信息"""
    cache_manager = get_cache_manager()
    key = CacheKeys.table_schema(table_names)
    cache_manager.set(key, schema)


def get_cached_table_schema(table_names: str) -> Optional[str]:
    """获取缓存的表结构信息"""
    cache_manager = get_cache_manager()
    key = CacheKeys.table_schema(table_names)
    return cache_manager.get(key)


def cache_database_info(info: str) -> None:
    """缓存数据库信息"""
    cache_manager = get_cache_manager()
    cache_manager.set(CacheKeys.DATABASE_INFO, info)


def get_cached_database_info() -> Optional[str]:
    """获取缓存的数据库信息"""
    cache_manager = get_cache_manager()
    return cache_manager.get(CacheKeys.DATABASE_INFO)


def clear_all_cache() -> None:
    """清空所有缓存"""
    cache_manager = get_cache_manager()
    cache_manager.clear()


def get_cache_stats() -> Dict[str, Any]:
    """获取缓存统计信息"""
    cache_manager = get_cache_manager()
    return cache_manager.get_stats()
