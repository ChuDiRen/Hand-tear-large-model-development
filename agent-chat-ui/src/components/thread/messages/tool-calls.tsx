// Copyright (c) 2025 左岚. All rights reserved.

import { AIMessage, ToolMessage } from "@langchain/langgraph-sdk";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronUp, Check } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function isComplexValue(value: any): boolean {
  return Array.isArray(value) || (typeof value === "object" && value !== null);
}

// 检查是否是图表数据
function isChartData(toolCall: AIMessage["tool_calls"][0]): boolean {
  return toolCall.name.includes('chart') || toolCall.name.includes('graph') || toolCall.name.includes('plot');
}

// 图表组件
function ChartDisplay({ toolCall }: { toolCall: AIMessage["tool_calls"][0] }) {
  const args = toolCall.args as any;

  // 模拟图表数据（实际应用中应该从工具结果中获取）
  const chartData = [
    { date: '2025-09-15', price: 117.16, label: '收盘价' },
    { date: '2025-09-16', price: 120.48, label: '收盘价' },
    { date: '2025-09-17', price: 119.11, label: '收盘价' },
    { date: '2025-09-18', price: 119.01, label: '收盘价' },
    { date: '2025-09-19', price: 120.59, label: '收盘价' },
  ];

  return (
    <div className="p-6 bg-white">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        {args.title || '滴起科技最近5天股价走势'}
      </h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis
              dataKey="date"
              stroke="#666"
              fontSize={12}
              tickFormatter={(value) => value.slice(5)} // 只显示月-日
            />
            <YAxis
              stroke="#666"
              fontSize={12}
              domain={['dataMin - 1', 'dataMax + 1']}
            />
            <Tooltip
              formatter={(value: any, name: string) => [value, '收盘价']}
              labelFormatter={(label) => `日期: ${label}`}
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #ccc',
                borderRadius: '4px'
              }}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#2563eb"
              strokeWidth={2}
              dot={{ fill: '#2563eb', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#2563eb', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// 单个工具调用组件
function ToolCallItem({ toolCall, index }: { toolCall: AIMessage["tool_calls"][0]; index: number }) {
  const args = toolCall.args as Record<string, any>;
  const hasArgs = Object.keys(args).length > 0;
  const isChart = isChartData(toolCall);

  // 简单的本地状态管理
  const [isExpanded, setIsExpanded] = useState(false); // 默认折叠

  // 切换展开状态
  const handleToggle = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: index * 0.05 }}
      className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm"
    >
      {/* 工具调用标题栏 */}
      <div
        className="flex items-center justify-between px-4 py-3 cursor-pointer select-none hover:bg-gray-50 transition-colors"
        onClick={handleToggle}
        role="button"
        aria-expanded={isExpanded}
        aria-label={`${isExpanded ? '折叠' : '展开'}工具调用 ${toolCall.name}`}
      >
        <div className="flex items-center gap-3">
          {/* 绿色勾选标记 */}
          <div className="flex items-center justify-center w-5 h-5 bg-green-500 rounded-full">
            <Check className="h-3 w-3 text-white" />
          </div>
          <span className="font-medium text-gray-900">
            {toolCall.name}
          </span>
          <code className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
            {toolCall.id?.replace(/^call_\w+_/, '').slice(0, 16) || '2d8c48f28a426688'}
          </code>
        </div>
        <motion.div
          animate={{ rotate: isExpanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="h-4 w-4 text-gray-400" />
        </motion.div>
      </div>

      {/* 工具调用参数内容 */}
      <AnimatePresence initial={false}>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
            className="overflow-hidden border-t border-gray-200"
          >
            {hasArgs ? (
              <div className="p-4 bg-gray-50">
                <div className="space-y-2">
                  {Object.entries(args).map(([key, value], argIdx) => (
                    <div key={argIdx} className="flex items-start gap-3">
                      <span className="text-sm font-medium text-gray-700 min-w-0 flex-shrink-0">
                        {key}:
                      </span>
                      <span className="text-sm text-gray-600 break-words">
                        {isComplexValue(value) ? (
                          <code className="rounded bg-white px-2 py-1 font-mono text-xs border">
                            {JSON.stringify(value, null, 2)}
                          </code>
                        ) : (
                          String(value)
                        )}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="p-4 bg-gray-50">
                <code className="text-sm text-gray-500">无参数</code>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function ToolCalls({
  toolCalls,
}: {
  toolCalls: AIMessage["tool_calls"];
}) {
  if (!toolCalls || toolCalls.length === 0) return null;

  return (
    <div className="mx-auto grid max-w-3xl grid-rows-[1fr_auto] gap-3">
      {toolCalls.map((tc, idx) => (
        <ToolCallItem
          key={tc.id || `tool-${idx}`}
          toolCall={tc}
          index={idx}
        />
      ))}
    </div>
  );
}

export function ToolResult({ message }: { message: ToolMessage }) {
  const [isExpanded, setIsExpanded] = useState(true); // 默认展开以显示图表

  let parsedContent: any;
  let isJsonContent = false;
  let isChartResult = false;

  try {
    if (typeof message.content === "string") {
      parsedContent = JSON.parse(message.content);
      isJsonContent = isComplexValue(parsedContent);
    }
  } catch {
    // Content is not JSON, use as is
    parsedContent = message.content;
  }

  // 检查是否是图表相关的工具结果
  isChartResult = message.name?.includes('chart') || message.name?.includes('graph') || message.name?.includes('plot') || false;

  const contentStr = isJsonContent
    ? JSON.stringify(parsedContent, null, 2)
    : String(message.content);
  const contentLines = contentStr.split("\n");
  const shouldTruncate = contentLines.length > 4 || contentStr.length > 500;
  const displayedContent =
    shouldTruncate && !isExpanded
      ? contentStr.length > 500
        ? contentStr.slice(0, 500) + "..."
        : contentLines.slice(0, 4).join("\n") + "\n..."
      : contentStr;

  return (
    <div className="mx-auto grid max-w-3xl grid-rows-[1fr_auto] gap-2">
      <div className="overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
        {/* 工具结果标题栏 */}
        <div
          className="flex items-center justify-between px-4 py-3 cursor-pointer select-none hover:bg-gray-50 transition-colors"
          onClick={() => setIsExpanded(!isExpanded)}
          role="button"
          aria-expanded={isExpanded}
          aria-label={`${isExpanded ? '折叠' : '展开'}工具结果`}
        >
          <div className="flex items-center gap-3">
            {/* 绿色勾选标记 */}
            <div className="flex items-center justify-center w-5 h-5 bg-green-500 rounded-full">
              <Check className="h-3 w-3 text-white" />
            </div>
            <span className="font-medium text-gray-900">
              工具结果: {message.name || 'unknown'}
            </span>
            <code className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
              {message.tool_call_id?.replace(/^call_\w+_/, '').slice(0, 16) || '2d8c48f28a426688'}
            </code>
          </div>
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronUp className="h-4 w-4 text-gray-400" />
          </motion.div>
        </div>
        {/* 工具结果内容 */}
        <AnimatePresence initial={false}>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="overflow-hidden border-t border-gray-200"
            >
              {isChartResult ? (
                <ChartDisplay toolCall={{ name: message.name || 'chart', args: {}, id: message.tool_call_id }} />
              ) : (
                <div className="bg-white p-4">
                  <pre className="whitespace-pre-wrap break-words text-sm text-gray-700">
                    {displayedContent}
                  </pre>
                  {shouldTruncate && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setIsExpanded(!isExpanded);
                      }}
                      className="mt-2 text-sm text-blue-600 hover:text-blue-800"
                    >
                      {isExpanded ? "显示更少" : "显示更多"}
                    </button>
                  )}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
