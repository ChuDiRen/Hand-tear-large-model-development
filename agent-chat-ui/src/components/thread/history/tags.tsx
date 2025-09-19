// Copyright (c) 2025 左岚. All rights reserved.

import React, { useState, useEffect } from "react";
import { Tag, Hash } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Thread } from "@langchain/langgraph-sdk";
import { cn } from "@/lib/utils";

export interface ThreadTag {
  id: string;
  name: string;
  color: string;
}

interface ThreadTagsProps {
  thread: Thread;
  onTagsChange?: (threadId: string, tags: ThreadTag[]) => void;
}

// 预定义的标签颜色
const TAG_COLORS = [
  "bg-blue-100 text-blue-800",
  "bg-green-100 text-green-800", 
  "bg-yellow-100 text-yellow-800",
  "bg-red-100 text-red-800",
  "bg-purple-100 text-purple-800",
  "bg-pink-100 text-pink-800",
  "bg-indigo-100 text-indigo-800",
  "bg-gray-100 text-gray-800",
];

// 从 localStorage 获取标签
const getStoredTags = (): ThreadTag[] => {
  try {
    const stored = localStorage.getItem('thread-tags');
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
};

// 保存标签到 localStorage
const saveStoredTags = (tags: ThreadTag[]) => {
  try {
    localStorage.setItem('thread-tags', JSON.stringify(tags));
  } catch (error) {
    console.error('Failed to save tags:', error);
  }
};

// 获取线程的标签
const getThreadTags = (threadId: string): ThreadTag[] => {
  try {
    const stored = localStorage.getItem(`thread-tags-${threadId}`);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
};

// 保存线程的标签
const saveThreadTags = (threadId: string, tags: ThreadTag[]) => {
  try {
    localStorage.setItem(`thread-tags-${threadId}`, JSON.stringify(tags));
  } catch (error) {
    console.error('Failed to save thread tags:', error);
  }
};

export function ThreadTags({ thread, onTagsChange }: ThreadTagsProps) {
  const [threadTags, setThreadTags] = useState<ThreadTag[]>([]);

  useEffect(() => {
    setThreadTags(getThreadTags(thread.thread_id));
  }, [thread.thread_id]);

  return (
    <div className="flex items-center gap-1 flex-wrap">
      {threadTags.map((tag) => (
        <Badge
          key={tag.id}
          variant="secondary"
          className={cn("text-xs", tag.color)}
        >
          <Hash className="size-2 mr-1" />
          {tag.name}
        </Badge>
      ))}
    </div>
  );
}

// 标签过滤器组件
export function TagFilter({ 
  onFilterChange 
}: { 
  onFilterChange: (selectedTags: ThreadTag[]) => void 
}) {
  const [selectedTags, setSelectedTags] = useState<ThreadTag[]>([]);
  const [availableTags, setAvailableTags] = useState<ThreadTag[]>([]);

  useEffect(() => {
    setAvailableTags(getStoredTags());
  }, []);

  const toggleTag = (tag: ThreadTag) => {
    const isSelected = selectedTags.find(t => t.id === tag.id);
    let updatedTags;
    
    if (isSelected) {
      updatedTags = selectedTags.filter(t => t.id !== tag.id);
    } else {
      updatedTags = [...selectedTags, tag];
    }
    
    setSelectedTags(updatedTags);
    onFilterChange(updatedTags);
  };

  const clearFilter = () => {
    setSelectedTags([]);
    onFilterChange([]);
  };

  if (availableTags.length === 0) return null;

  return (
    <div className="p-3 border-b">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium">按标签筛选</span>
        {selectedTags.length > 0 && (
          <Button variant="ghost" size="sm" onClick={clearFilter}>
            清除
          </Button>
        )}
      </div>
      <div className="flex flex-wrap gap-1">
        {availableTags.map((tag) => {
          const isSelected = selectedTags.find(t => t.id === tag.id);
          return (
            <Badge
              key={tag.id}
              variant={isSelected ? "default" : "outline"}
              className={cn(
                "cursor-pointer text-xs",
                isSelected ? tag.color : "hover:bg-gray-100"
              )}
              onClick={() => toggleTag(tag)}
            >
              <Hash className="size-2 mr-1" />
              {tag.name}
            </Badge>
          );
        })}
      </div>
    </div>
  );
}

// 获取所有线程的标签，用于过滤
export function getThreadsWithTags(threads: Thread[]): (Thread & { tags: ThreadTag[] })[] {
  return threads.map(thread => ({
    ...thread,
    tags: getThreadTags(thread.thread_id),
  }));
}

// 根据标签过滤线程
export function filterThreadsByTags(threads: Thread[], selectedTags: ThreadTag[]): Thread[] {
  if (selectedTags.length === 0) return threads;
  
  return threads.filter(thread => {
    const threadTags = getThreadTags(thread.thread_id);
    return selectedTags.some(selectedTag => 
      threadTags.find(threadTag => threadTag.id === selectedTag.id)
    );
  });
}
