# Copyright (c) 2025 左岚. All rights reserved.
"""异步图表生成模块

本模块提供异步图表生成功能，集成quickchart MCP服务。
"""

import asyncio
import logging
import os
# 修复相对导入问题，使用绝对导入
import sys

from langgraph.prebuilt import create_react_agent

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from workflow_sql.mcp_config import mcp_config  # MCP配置

logger = logging.getLogger(__name__)


class AsyncChartGenerator:
    """异步图表生成器"""
    
    def __init__(self, llm):
        """初始化图表生成器
        
        Args:
            llm: 语言模型实例
        """
        self.llm = llm
    
    def _get_system_prompt(self) -> str:
        """获取图表生成的系统提示"""
        return """
您是一个专业的数据可视化专家，负责根据SQL查询结果生成合适的图表。

您的任务是：
1. 分析SQL查询结果的数据结构和内容
2. 确定最适合的图表类型（柱状图、折线图、饼图等）
3. 使用可用的图表工具生成可视化图表
4. 确保图表清晰、美观且信息丰富

图表类型选择指南：
- 柱状图：适合比较不同类别的数值
- 折线图：适合显示趋势变化
- 饼图：适合显示比例关系
- 散点图：适合显示相关性

重要规则：
- 根据数据特点选择最合适的图表类型
- 确保图表标题、轴标签清晰
- 如果数据点过多，考虑只显示前几名
- 使用合适的颜色和样式
        """.strip()
    
    def _determine_chart_type(self, query_result: str, user_question: str) -> str:
        """根据数据和问题确定图表类型"""
        question_lower = user_question.lower()
        
        # 根据问题关键词判断
        if any(word in question_lower for word in ["趋势", "变化", "时间", "增长"]):
            return "line"
        elif any(word in question_lower for word in ["比例", "占比", "份额"]):
            return "pie"
        elif any(word in question_lower for word in ["比较", "排名", "最", "前", "后"]):
            return "bar"
        else:
            # 默认使用柱状图
            return "bar"
    
    async def generate_chart(self, user_question: str, query_result: str, 
                           answer_content: str) -> str:
        """异步生成图表
        
        Args:
            user_question: 用户问题
            query_result: 查询结果
            answer_content: 答案内容
            
        Returns:
            图表生成结果消息
        """
        try:
            import time
            start_time = time.time()
            logger.info("开始异步图表生成")

            # 检查图表功能是否启用
            if not mcp_config.chart.enabled:
                logger.info("图表生成功能已禁用")
                return "图表生成功能当前不可用"

            # 获取图表工具 - 使用简化的直接方式
            try:
                from langchain_mcp_adapters.client import MultiServerMCPClient

                # 按照 agent/graph.py 的成功实现方式
                client = MultiServerMCPClient({
                    "chart": {
                        "command": "npx",
                        "args": ["-y", "@antv/mcp-server-chart"],
                        "transport": "stdio"
                    }
                })

                chart_tools = await client.get_tools()
                logger.info(f"成功获取 {len(chart_tools)} 个图表工具")

                if not chart_tools:
                    logger.error("未找到图表生成工具")
                    return "图表生成工具不可用"

            except Exception as e:
                logger.error(f"获取图表工具失败: {e}")
                return f"图表生成失败：无法获取图表工具 - {str(e)}"

            # 确定图表类型
            chart_type = self._determine_chart_type(query_result, user_question)
            logger.info(f"选择图表类型: {chart_type}")
            
            # 构建提示消息
            system_message = {
                "role": "system",
                "content": self._get_system_prompt(),
            }
            
            user_message = {
                "role": "user",
                "content": f"""
用户问题：{user_question}

查询结果数据：
{query_result}

答案内容：
{answer_content}

请根据以上数据生成一个{chart_type}图表。数据格式为Python列表，每个元素是一个元组。
请使用可用的图表工具创建可视化图表。
                """.strip()
            }
            
            # 使用LLM和图表工具生成图表
            chart_agent = create_react_agent(
                model=self.llm,
                tools=chart_tools,
                prompt=self._get_system_prompt()
            )
            
            # 调用图表智能体（添加超时机制）
            agent_start = time.time()
            logger.info("开始调用图表智能体")

            try:
                # 设置60秒超时
                import asyncio
                result = await asyncio.wait_for(
                    chart_agent.ainvoke({
                        "messages": [system_message, user_message]
                    }),
                    timeout=60.0
                )
                agent_time = time.time() - agent_start
                logger.info(f"图表智能体调用完成，耗时: {agent_time:.2f}秒")
            except asyncio.TimeoutError:
                logger.error("图表生成超时")
                return "图表生成失败：操作超时（60秒）"
            except Exception as e:
                logger.error(f"图表智能体调用失败: {e}")
                return f"图表生成失败：{str(e)}"

            # 提取图表链接和内容
            chart_url = None
            chart_description = ""

            # 遍历所有消息，查找工具调用结果
            for i, message in enumerate(result["messages"]):
                if hasattr(message, 'content') and message.content:
                    content_str = str(message.content)
                    logger.debug(f"消息 {i}: {content_str[:200]}...")  # 调试日志

                    # 检查是否包含图表链接（扩展检测范围）
                    if chart_url is None:
                        # 检查多种可能的图表链接格式
                        if any(keyword in content_str.lower() for keyword in [
                            "quickchart.io", "chart", "http", "https", "图表", "可视化"
                        ]):
                            chart_url = self._extract_chart_url(content_str)
                            if chart_url:
                                logger.info(f"找到图表链接: {chart_url[:100]}...")
                            else:
                                # 尝试提取任何HTTP链接
                                import re
                                url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
                                urls = re.findall(url_pattern, content_str)
                                if urls:
                                    chart_url = urls[0]
                                    logger.info(f"提取到URL: {chart_url[:100]}...")

                    # 如果是最终的AI消息，保存描述
                    if hasattr(message, 'type') and message.type == 'ai':
                        chart_description = message.content

            # 构建最终结果
            if chart_url:
                # 验证图表链接是否有效
                if self._validate_chart_url(chart_url):
                    chart_result = f"图表生成完成！\n\n**图表链接：** {chart_url}\n\n## 图表说明：\n{self._generate_chart_description()}"
                else:
                    logger.error("图表链接验证失败")
                    return "图表生成失败：生成的图表链接无效"
            else:
                # 如果没有找到链接，返回失败
                logger.error("未找到图表链接")
                return "图表生成失败：未能生成有效的图表链接"

            total_time = time.time() - start_time
            logger.info(f"异步图表生成完成，总耗时: {total_time:.2f}秒")
            return chart_result
            
        except Exception as e:
            logger.error(f"异步图表生成错误: {e}")
            return f"图表生成错误: {str(e)}"

    def _extract_chart_url(self, content: str) -> str:
        """从内容中提取图表URL"""
        import re

        # 尝试多种URL模式
        patterns = [
            # quickchart.io URL
            r'https://quickchart\.io/chart\?c=[A-Za-z0-9%_=-]+',
            # 其他图表服务URL
            r'https://[a-zA-Z0-9.-]+/[^\s<>"{}|\\^`\[\]]*chart[^\s<>"{}|\\^`\[\]]*',
            # 通用HTTP/HTTPS URL（包含chart关键词）
            r'https?://[^\s<>"{}|\\^`\[\]]*chart[^\s<>"{}|\\^`\[\]]*',
            # 任何包含图表相关关键词的URL
            r'https?://[^\s<>"{}|\\^`\[\]]*(?:chart|graph|plot|visual)[^\s<>"{}|\\^`\[\]]*',
            # 通用URL模式（作为最后备选）
            r'https?://[^\s<>"{}|\\^`\[\]]+'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # 返回第一个匹配的URL，并清理尾部字符
                url = matches[0].rstrip('.,;!?)')
                logger.debug(f"使用模式 '{pattern}' 提取到URL: {url[:100]}...")
                return url

        return None

    def _validate_chart_url(self, url: str) -> bool:
        """验证图表URL是否有效"""
        try:
            # 基本URL格式检查
            if not url.startswith(('http://', 'https://')):
                return False

            # 检查URL长度（太短可能无效）
            if len(url) < 20:
                return False

            # 对于quickchart.io，检查特定参数
            if 'quickchart.io' in url:
                if 'chart?c=' not in url:
                    return False
                # 检查是否包含必要的参数
                    if '%22type%22' not in url or '%22data%22' not in url:
                        return False

            # 对于其他图表服务，进行基本验证
            else:
                # 检查是否包含图表相关关键词
                chart_keywords = ['chart', 'graph', 'plot', 'visual', 'data']
                if not any(keyword in url.lower() for keyword in chart_keywords):
                    logger.debug(f"URL不包含图表关键词: {url}")
                    # 仍然返回True，因为可能是其他类型的图表服务
                    pass

            return True
        except Exception:
            return False

    def _generate_chart_description(self) -> str:
        """生成图表描述"""
        return """
**图表特点：**
- 图表类型：柱状图，适合比较不同类别的数值
- 数据展示：清晰显示各音乐类型的平均时长
- 视觉效果：使用不同颜色区分各个类型
- 交互功能：支持鼠标悬停查看详细数据

**使用说明：**
点击上方链接即可查看完整的交互式图表。
        """.strip()




def run_async_chart_generation(llm, user_question: str, query_result: str, 
                              answer_content: str) -> str:
    """运行异步图表生成（同步包装器）
    
    Args:
        llm: 语言模型实例
        user_question: 用户问题
        query_result: 查询结果
        answer_content: 答案内容
        
    Returns:
        图表生成结果消息
    """
    try:
        # 创建新的事件循环或使用现有的
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # 创建图表生成器并运行
        generator = AsyncChartGenerator(llm)
        result = loop.run_until_complete(
            generator.generate_chart(user_question, query_result, answer_content)
        )
        
        return result
        
    except Exception as e:
        logger.error(f"异步图表生成包装器错误: {e}")
        return f"图表生成失败: {str(e)}"
