// Copyright (c) 2025 左岚. All rights reserved.
/**
 * 通用智能消息渲染器
 * 提供丝滑的用户体验，智能隐藏技术细节，渐进式展示内容
 */

import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Eye,
  EyeOff,
  Brain,
  Cog,
  CheckCircle,
  Loader2,
  ChevronDown,
  Sparkles,
  BarChart3,
  Clock
} from 'lucide-react';
import { MarkdownText } from './markdown-text';
import { cn } from '@/lib/utils';

interface ProcessedMessage {
  id: string;
  type: 'thinking' | 'working' | 'result' | 'chart';
  title: string;
  content: string;
  status: 'pending' | 'running' | 'completed';
  toolCalls?: any[];
  duration?: number;
  isImportant: boolean;
  hasChart?: boolean; // 标记是否包含图表
}

interface SmartMessageRendererProps {
  messages: any[];
  isLoading: boolean;
}

export function SmartMessageRenderer({ messages, isLoading }: SmartMessageRendererProps) {
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);

  // 智能处理消息，提取关键信息
  const processedMessages = useMemo(() => {
    const processed: ProcessedMessage[] = [];
    let currentGroup: any[] = [];
    const seenCharts = new Set<string>(); // 本次渲染周期内已展示的图表URL

    for (let i = 0; i < messages.length; i++) {
      const message = messages[i];

      // 如果是人类消息，直接添加
      if (message.type === 'human') {
        if (currentGroup.length > 0) {
          processed.push(...processAIGroup(currentGroup, isLoading, seenCharts));
          currentGroup = [];
        }
        processed.push({
          id: message.id || `human-${i}`,
          type: 'result',
          title: '用户提问',
          content: getContentString(message.content),
          status: 'completed',
          isImportant: true
        });
        continue;
      }

      // 收集AI相关消息组
      if (message.type === 'ai' || message.type === 'tool') {
        currentGroup.push(message);
      }
    }

    // 处理最后一组
    if (currentGroup.length > 0) {
      processed.push(...processAIGroup(currentGroup, isLoading, seenCharts));
    }

    return processed;
  }, [messages, isLoading]);

  return (
    <div className="space-y-4">
      {processedMessages.map((msg, index) => (
        <MessageCard
          key={msg.id}
          message={msg}
          index={index}
          showTechnicalDetails={showTechnicalDetails}
        />
      ))}

      {/* 技术细节切换按钮 */}
      {messages.some(m => m.tool_calls?.length > 0 || m.type === 'tool') && (
        <div className="flex justify-center mt-6">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-800 bg-gray-100 hover:bg-gray-200 rounded-full transition-all duration-200 shadow-sm hover:shadow-md"
          >
            {showTechnicalDetails ? (
              <>
                <EyeOff className="h-4 w-4" />
                隐藏技术细节
              </>
            ) : (
              <>
                <Eye className="h-4 w-4" />
                查看技术细节
              </>
            )}
          </motion.button>
        </div>
      )}

      {/* 技术细节面板 */}
      <AnimatePresence>
        {showTechnicalDetails && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
              <div className="flex items-center gap-2 mb-4">
                <Cog className="h-5 w-5 text-gray-600" />
                <h3 className="font-medium text-gray-900">技术执行细节</h3>
              </div>
              <div className="space-y-3 text-sm">
                {messages.map((message, index) => (
                  <TechnicalDetailItem key={index} message={message} />
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// 消息卡片组件
interface MessageCardProps {
  message: ProcessedMessage;
  index: number;
  showTechnicalDetails: boolean;
}

function MessageCard({ message, index, showTechnicalDetails }: MessageCardProps) {
  const getIcon = () => {
    switch (message.type) {
      case 'thinking':
        return <Brain className="h-5 w-5" />;
      case 'working':
        return <Cog className="h-5 w-5" />;
      case 'chart':
        return <BarChart3 className="h-5 w-5" />;
      default:
        return <Sparkles className="h-5 w-5" />;
    }
  };

  const getStatusIcon = () => {
    switch (message.status) {
      case 'running':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getCardStyle = () => {
    if (message.type === 'chart') {
      return "bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200";
    }
    if (message.isImportant) {
      return "bg-white border-gray-200 shadow-sm";
    }
    return "bg-gray-50 border-gray-100";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
      className={cn(
        "rounded-xl border p-6 transition-all duration-200",
        getCardStyle()
      )}
    >
      {/* 消息头部 */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={cn(
            "flex items-center justify-center w-10 h-10 rounded-full",
            message.type === 'chart' ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-600"
          )}>
            {getIcon()}
          </div>
          <div>
            <h3 className="font-medium text-gray-900">{message.title}</h3>
            {message.duration && (
              <p className="text-sm text-gray-500">耗时 {message.duration.toFixed(1)}s</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {getStatusIcon()}
        </div>
      </div>

      {/* 消息内容 */}
      <div className="prose prose-sm max-w-none">

        <MarkdownText disableChartRendering={message.hasChart}>
          {message.content}
        </MarkdownText>
      </div>

      {/* 图表特殊处理 */}
      {message.type === 'chart' && (
        <div className="mt-4 bg-white rounded-lg p-4 border border-blue-100">
          <ChartRenderer url={message.content.startsWith('https://') ? message.content : extractChartUrl(message.content)} />
        </div>
      )}
    </motion.div>
  );
}

// 图表渲染器
function ChartRenderer({ url }: { url: string | null }) {
  if (!url) return null;

  return (
    <div className="text-center">
      <img
        src={url}
        alt="数据可视化图表"
        className="w-full h-auto rounded-lg shadow-sm max-h-96 object-contain mx-auto"
        onError={(e) => {
          const target = e.target as HTMLImageElement;
          target.style.display = 'none';
          const fallback = target.nextElementSibling as HTMLElement;
          if (fallback) fallback.style.display = 'block';
        }}
      />
      <div style={{ display: 'none' }} className="mt-4">
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <BarChart3 className="h-4 w-4" />
          查看交互式图表
        </a>
      </div>
    </div>
  );
}

// 技术细节项
function TechnicalDetailItem({ message }: { message: any }) {
  if (message.type === 'human') return null;

  const content = getContentString(message.content);
  if (!content && !message.tool_calls?.length) return null;

  return (
    <div className="bg-white rounded-lg p-3 border border-gray-200">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">
          {message.type === 'ai' ? 'AI响应' : message.type === 'tool' ? '工具执行' : '消息'}
        </span>
        {message.tool_calls?.length > 0 && (
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded">
            {message.tool_calls.length} 个工具调用
          </span>
        )}
      </div>
      {content && (
        <div className="text-sm text-gray-700 whitespace-pre-wrap break-words">
          {content.length > 200 ? content.slice(0, 200) + '...' : content}
        </div>
      )}
    </div>
  );
}

// 辅助函数
function processAIGroup(messages: any[], isLoading = false, seenCharts?: Set<string>): ProcessedMessage[] {
  const result: ProcessedMessage[] = [];

  // 查找最终的AI响应
  const finalAIMessage = messages.filter(m => m.type === 'ai').pop();
  if (!finalAIMessage) return result;

  const content = getContentString(finalAIMessage.content);
  const hasToolCalls = messages.some(m => m.tool_calls?.length > 0 || m.type === 'tool');

  // 检测是否包含图表
  const hasChart = /https:\/\/mdn\.alipayobjects\.com|图表链接/.test(content);

  if (hasChart) {
    // 提取所有图表链接并标准化去重
    const chartUrls = extractChartUrls(content).map(normalizeChartUrl).filter(Boolean) as string[];
    const uniqueChartUrls = Array.from(new Set(chartUrls));
    const selectedChartUrl = pickPreferredChartUrl(uniqueChartUrls); // 只选一条，优先 MCP

    // 移除所有图表链接与相关提示，只保留文本内容
    const textContent = content
      .replace(/!\[[^\]]*\]\(https:\/\/[^\)]*mdn\.alipayobjects\.com[^\)]*\)/g, '')
      .replace(/图表链接[：:]\s*https:\/\/[^\s\)]+/g, '')
      .replace(/https:\/\/[^\s\)]+mdn\.alipayobjects\.com[^\s\)]+/g, '')
      .replace(/https:\/\/mdn\.alipayobjects\.com[^\s\)]+/g, '')
      .replace(/\n\s*\n/g, '\n')
      .trim();

    // 主要回答（不包含图表链接）
    result.push({
      id: `${finalAIMessage.id}-main`,
      type: 'result',
      title: hasToolCalls ? '智能分析结果' : 'AI回答',
      content: textContent,
      status: 'completed',
      isImportant: true,
      duration: hasToolCalls ? Math.random() * 3 + 2 : undefined,
      hasChart: !!selectedChartUrl
    });

    // 仅渲染一张图表（优先 MCP 链接），并在渲染周期内去重
    if (selectedChartUrl) {
      const norm = normalizeChartUrl(selectedChartUrl);
      if (!seenCharts || !seenCharts.has(norm)) {
        seenCharts?.add(norm);
        result.push({
          id: `${finalAIMessage.id}-chart-0`,
          type: 'chart',
          title: '数据可视化图表',
          content: selectedChartUrl,
          status: isLoading ? 'running' : 'completed',
          isImportant: true,
          duration: 2.5
        });
      }
    }
  } else {
    // 普通回答
    result.push({
      id: finalAIMessage.id || 'ai-result',
      type: 'result',
      title: hasToolCalls ? '智能分析结果' : 'AI回答',
      content: content,
      status: isLoading ? 'running' : 'completed',
      isImportant: true,
      duration: hasToolCalls ? Math.random() * 3 + 2 : undefined
    });
  }

  return result;
}

function getContentString(content: any): string {
  if (typeof content === 'string') return content;
  if (Array.isArray(content)) {
    return content.map(item =>
      typeof item === 'string' ? item : item.text || ''
    ).join('');
  }
  return '';
}

function extractChartUrl(content: string): string | null {
  const match = content.match(/https:\/\/mdn\.alipayobjects\.com[^\s)]+/);
  return match ? match[0] : null;
}


// 提取文本中的所有图表URL（Markdown图片、带“图表链接：”、纯URL）
function extractChartUrls(text: string): string[] {
  const urls: string[] = [];
  const mdImageRegex = /!\[[^\]]*\]\((https:\/\/mdn\.alipayobjects\.com[^\)]+)\)/g;
  const plainUrlRegex = /(https:\/\/mdn\.alipayobjects\.com[^\s\)]+)/g;
  const labeledRegex = /图表链接[：:][\s]*(https:\/\/mdn\.alipayobjects\.com[^\s\)]+)/g;

  let m: RegExpExecArray | null;
  while ((m = mdImageRegex.exec(text)) !== null) urls.push(m[1]);
  while ((m = labeledRegex.exec(text)) !== null) urls.push(m[1]);
  while ((m = plainUrlRegex.exec(text)) !== null) urls.push(m[1]);

  return urls;
}

// 规范化图表 URL（去掉查询参数等用于去重）
function normalizeChartUrl(url: string): string {
  try {
    const u = new URL(url);
    return `${u.protocol}//${u.host}${u.pathname}`;
  } catch {
    return url;
  }
}

function isMcpChartUrl(url: string): boolean {
  try { return new URL(url).hostname.includes('mdn.alipayobjects.com'); } catch { return false; }
}

// 从多个链接中挑选优先显示的链接（优先 MCP 链接）
function pickPreferredChartUrl(urls: string[]): string | null {
  if (!urls.length) return null;
  const mcp = urls.find(isMcpChartUrl);
  return mcp ?? urls[0];
}
