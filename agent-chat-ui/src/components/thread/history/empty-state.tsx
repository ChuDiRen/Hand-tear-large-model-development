// Copyright (c) 2025 左岚. All rights reserved.

import React from "react";
import { MessageCircle, Plus, Search } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  type: "no-threads" | "no-search-results" | "no-filtered-results";
  onClearSearch?: () => void;
  onClearFilters?: () => void;
}

export function EmptyState({ type, onClearSearch, onClearFilters }: EmptyStateProps) {
  const getContent = () => {
    switch (type) {
      case "no-threads":
        return {
          icon: <MessageCircle className="size-12 text-gray-300" />,
          title: "还没有对话",
          description: "点击右上角的新建按钮开始您的第一个对话吧！",
          action: null,
        };
      
      case "no-search-results":
        return {
          icon: <Search className="size-12 text-gray-300" />,
          title: "没有找到匹配的对话",
          description: "尝试使用不同的关键词搜索",
          action: (
            <Button variant="outline" onClick={onClearSearch} className="mt-4">
              清除搜索
            </Button>
          ),
        };
      
      case "no-filtered-results":
        return {
          icon: <MessageCircle className="size-12 text-gray-300" />,
          title: "没有符合条件的对话",
          description: "尝试调整筛选条件",
          action: (
            <Button variant="outline" onClick={onClearFilters} className="mt-4">
              清除筛选
            </Button>
          ),
        };
      
      default:
        return {
          icon: <MessageCircle className="size-12 text-gray-300" />,
          title: "暂无内容",
          description: "",
          action: null,
        };
    }
  };

  const content = getContent();

  return (
    <div className="flex flex-col items-center justify-center h-64 p-8 text-center">
      {content.icon}
      <h3 className="mt-4 text-lg font-medium text-gray-900">
        {content.title}
      </h3>
      {content.description && (
        <p className="mt-2 text-sm text-gray-500">
          {content.description}
        </p>
      )}
      {content.action}
    </div>
  );
}

// 加载状态组件的改进版本
export function LoadingState() {
  return (
    <div className="flex flex-col items-center justify-center h-64 p-8">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      <p className="mt-4 text-sm text-gray-500">加载对话历史...</p>
    </div>
  );
}

// 错误状态组件
export function ErrorState({ 
  error, 
  onRetry 
}: { 
  error: string; 
  onRetry?: () => void; 
}) {
  return (
    <div className="flex flex-col items-center justify-center h-64 p-8 text-center">
      <div className="rounded-full bg-red-100 p-3">
        <svg className="size-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 19.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      <h3 className="mt-4 text-lg font-medium text-gray-900">
        加载失败
      </h3>
      <p className="mt-2 text-sm text-gray-500">
        {error}
      </p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry} className="mt-4">
          重试
        </Button>
      )}
    </div>
  );
}
