// Copyright (c) 2025 左岚. All rights reserved.

import React, { useState, useMemo } from "react";
import { Search, X } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Thread } from "@langchain/langgraph-sdk";
import { getContentString } from "../utils";

interface ThreadSearchProps {
  threads: Thread[];
  onFilteredThreadsChange: (filteredThreads: Thread[]) => void;
  isOpen: boolean;
}

export function ThreadSearch({ threads, onFilteredThreadsChange, isOpen }: ThreadSearchProps) {
  const [searchQuery, setSearchQuery] = useState("");

  // 搜索过滤逻辑
  const filteredThreads = useMemo(() => {
    if (!searchQuery.trim()) {
      return threads;
    }

    const query = searchQuery.toLowerCase();
    return threads.filter((thread) => {
      // 搜索线程ID
      if (thread.thread_id.toLowerCase().includes(query)) {
        return true;
      }

      // 搜索消息内容
      if (
        typeof thread.values === "object" &&
        thread.values &&
        "messages" in thread.values &&
        Array.isArray(thread.values.messages)
      ) {
        return thread.values.messages.some((message: any) => {
          const content = getContentString(message.content);
          return content.toLowerCase().includes(query);
        });
      }

      return false;
    });
  }, [threads, searchQuery]);

  // 当过滤结果改变时通知父组件
  React.useEffect(() => {
    onFilteredThreadsChange(filteredThreads);
  }, [filteredThreads, onFilteredThreadsChange]);

  if (!isOpen) return null;

  return (
    <div className="p-3 border-b">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 size-4" />
        <Input
          placeholder="搜索对话..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 pr-10"
        />
        {searchQuery && (
          <Button
            variant="ghost"
            size="sm"
            className="absolute right-1 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
            onClick={() => setSearchQuery("")}
          >
            <X className="size-3" />
          </Button>
        )}
      </div>
      {searchQuery && (
        <div className="mt-2 text-xs text-gray-500">
          找到 {filteredThreads.length} 个结果
        </div>
      )}
    </div>
  );
}
