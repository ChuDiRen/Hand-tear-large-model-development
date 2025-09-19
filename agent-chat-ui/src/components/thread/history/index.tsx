// Copyright (c) 2025 左岚. All rights reserved.

import { Button } from "@/components/ui/button";
import { useThreads } from "@/providers/Thread";
import { Thread } from "@langchain/langgraph-sdk";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";


import { getContentString } from "../utils";

/**
 * 生成对话总结
 * 基于第一个用户问题和对话内容生成简洁的标题
 */
function generateConversationSummary(firstUserMessage: string, messages: any[]): string {
  // 清理和截断第一个用户消息
  let summary = firstUserMessage.trim();

  // 移除常见的无意义前缀
  const prefixesToRemove = [
    "你好", "请问", "能否", "可以", "帮我", "我想", "我需要", "请帮助"
  ];

  for (const prefix of prefixesToRemove) {
    if (summary.startsWith(prefix)) {
      summary = summary.substring(prefix.length).trim();
      break;
    }
  }

  // 如果消息太长，智能截断
  if (summary.length > 50) {
    // 尝试在句号、问号、感叹号处截断
    const sentenceEnd = summary.search(/[。？！.?!]/);
    if (sentenceEnd > 10 && sentenceEnd < 50) {
      summary = summary.substring(0, sentenceEnd + 1);
    } else {
      // 在词边界截断
      summary = summary.substring(0, 47) + "...";
    }
  }

  // 如果总结为空或太短，使用默认值
  if (!summary || summary.length < 3) {
    summary = "新对话";
  }

  return summary;
}
import { useQueryState, parseAsBoolean } from "nuqs";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { PanelRightOpen, PanelRightClose, Trash2, Edit, MoreHorizontal, Loader2, Plus, Search, Tag } from "lucide-react";
import { TooltipIconButton } from "../tooltip-icon-button";
import { ThreadSearch } from "./search";
import { ImportExport } from "./import-export";
import { ThreadTags, TagFilter, filterThreadsByTags } from "./tags";
import type { ThreadTag } from "./tags";

import { EmptyState, LoadingState, ErrorState } from "./empty-state";
import { ListItemAnimation, SearchResultsAnimation } from "./animations";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

function ThreadList({
  threads,
  onThreadClick,
}: {
  threads: Thread[];
  onThreadClick?: (threadId: string) => void;
}) {

  const [threadId, setThreadId] = useQueryState("threadId");
  const { deleteThread } = useThreads();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [threadToDelete, setThreadToDelete] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (threadId: string) => {
    setThreadToDelete(threadId);
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (threadToDelete) {
      setIsDeleting(true);
      try {
        const success = await deleteThread(threadToDelete);
        if (success) {
          // 如果删除的是当前显示的对话，清空 threadId
          if (threadToDelete === threadId) {
            setThreadId(null);
          }
          setDeleteDialogOpen(false);
          setThreadToDelete(null);
        }
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <>
      <SearchResultsAnimation resultsCount={threads.length}>
        <div className="flex h-full w-full flex-col items-start justify-start gap-2 overflow-y-scroll [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-gray-300 [&::-webkit-scrollbar-track]:bg-transparent">
        {threads.map((t, index) => {
          let itemText = t.thread_id;

          // 尝试从thread的values中获取消息
          if (
            typeof t.values === "object" &&
            t.values &&
            "messages" in t.values &&
            Array.isArray(t.values.messages) &&
            t.values.messages?.length > 0
          ) {
            // 查找第一个人类消息
            const firstHumanMessage = t.values.messages.find(msg => msg.type === "human");
            if (firstHumanMessage) {
              const content = getContentString(firstHumanMessage.content);
              if (content && content.trim() && content !== t.thread_id) {
                // 生成智能总结
                itemText = generateConversationSummary(content, t.values.messages);
              }
            }
          }

          // 如果仍然是thread_id，尝试使用更友好的显示
          if (itemText === t.thread_id) {
            itemText = "新对话";
          }
          return (
            <ListItemAnimation
              key={t.thread_id}
              index={index}
              className="w-full px-1"
            >
              <ContextMenu>
                <ContextMenuTrigger asChild>
                  <div className="w-[280px] relative group">
                    <div className="w-full">
                      <Button
                        variant="ghost"
                        className={cn(
                          "w-full items-start justify-start text-left font-normal pr-8 h-auto py-2 transition-all duration-200",
                          "hover:bg-gray-50 hover:shadow-sm",
                          t.thread_id === threadId && "bg-blue-50 border-l-2 border-blue-500"
                        )}
                        onClick={(e) => {
                          e.preventDefault();
                          onThreadClick?.(t.thread_id);
                          if (t.thread_id === threadId) return;
                          setThreadId(t.thread_id);
                        }}
                      >
                        <div className="flex flex-col items-start gap-1 w-full">
                          <p className="truncate text-ellipsis">{itemText}</p>
                        </div>
                      </Button>
                    </div>
                    {/* 悬浮显示的删除按钮 */}
                    <div
                      className="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-all duration-200 h-8 w-8 flex items-center justify-center rounded-md hover:bg-red-50 hover:scale-110 cursor-pointer"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteClick(t.thread_id);
                      }}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </div>
                  </div>
                </ContextMenuTrigger>
                <ContextMenuContent>
                  <ContextMenuItem
                    onClick={() => handleDeleteClick(t.thread_id)}
                    className="text-red-600 focus:text-red-600"
                  >
                    <Trash2 className="mr-2 h-4 w-4" />
                    删除
                  </ContextMenuItem>
                </ContextMenuContent>
              </ContextMenu>
            </ListItemAnimation>
          );
        })}
        </div>
      </SearchResultsAnimation>

      {/* 删除确认对话框 */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>删除对话</AlertDialogTitle>
            <AlertDialogDescription>
              确定要删除这个对话吗？此操作无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700 disabled:opacity-50"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  删除中...
                </>
              ) : (
                "确认删除"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}

function ThreadHistoryLoading() {
  return (
    <div className="flex h-full w-full flex-col items-start justify-start gap-2 overflow-y-scroll [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-gray-300 [&::-webkit-scrollbar-track]:bg-transparent">
      {Array.from({ length: 30 }).map((_, i) => (
        <Skeleton
          key={`skeleton-${i}`}
          className="h-10 w-[280px]"
        />
      ))}
    </div>
  );
}

export default function ThreadHistory() {

  const isLargeScreen = useMediaQuery("(min-width: 1024px)");
  const [chatHistoryOpen, setChatHistoryOpen] = useQueryState(
    "chatHistoryOpen",
    parseAsBoolean.withDefault(true), // 默认打开侧边栏
  );
  const [searchOpen, setSearchOpen] = useState(false);
  const [tagFilterOpen, setTagFilterOpen] = useState(false);
  const [filteredThreads, setFilteredThreads] = useState<Thread[]>([]);
  const [selectedTags, setSelectedTags] = useState<ThreadTag[]>([]);
  const [error, setError] = useState<string | null>(null);

  const { getThreads, threads, setThreads, threadsLoading, setThreadsLoading } =
    useThreads();

  useEffect(() => {
    if (typeof window === "undefined") return;
    setThreadsLoading(true);
    setError(null);
    getThreads()
      .then(setThreads)
      .catch((error) => {
        console.error("Failed to load threads:", error);
        setError("加载对话历史失败，请稍后重试");
      })
      .finally(() => setThreadsLoading(false));
  }, []);

  // 重试加载
  const handleRetry = () => {
    setThreadsLoading(true);
    setError(null);
    getThreads()
      .then(setThreads)
      .catch((error) => {
        console.error("Failed to load threads:", error);
        setError("加载对话历史失败，请稍后重试");
      })
      .finally(() => setThreadsLoading(false));
  };

  // 初始化过滤的线程列表
  useEffect(() => {
    let filtered = threads;

    // 应用标签过滤
    if (selectedTags.length > 0) {
      filtered = filterThreadsByTags(filtered, selectedTags);
    }

    setFilteredThreads(filtered);
  }, [threads, selectedTags]);



  // 处理搜索过滤结果
  const handleSearchFilter = (searchFiltered: Thread[]) => {
    let filtered = searchFiltered;

    // 应用标签过滤
    if (selectedTags.length > 0) {
      filtered = filterThreadsByTags(filtered, selectedTags);
    }

    setFilteredThreads(filtered);
  };

  return (
    <>
      <div className="flex h-full w-full flex-col">
        {/* 侧边栏头部 */}
        <div className={cn(
          "flex items-center justify-between p-4 border-b",
          chatHistoryOpen ? "px-4" : "px-2"
        )}>
          {chatHistoryOpen ? (
            <>
              <h1 className="text-lg font-semibold tracking-tight">
                聊天历史
              </h1>
              <div className="flex items-center gap-2">
                <TooltipIconButton
                  size="sm"
                  tooltip="搜索对话"
                  variant="ghost"
                  onClick={() => setSearchOpen(!searchOpen)}
                >
                  <Search className="size-4" />
                </TooltipIconButton>
                <TooltipIconButton
                  size="sm"
                  tooltip="标签筛选"
                  variant="ghost"
                  onClick={() => setTagFilterOpen(!tagFilterOpen)}
                >
                  <Tag className="size-4" />
                </TooltipIconButton>
                <ImportExport
                  threads={threads}
                  onImport={(importedThreads) => {
                    // 这里可以添加导入逻辑，比如合并到现有线程中
                    setThreads(prev => [...prev, ...importedThreads]);
                  }}
                />


                <TooltipIconButton
                  size="sm"
                  tooltip="收起侧边栏"
                  variant="ghost"
                  onClick={() => setChatHistoryOpen(false)}
                >
                  <PanelRightOpen className="size-4" />
                </TooltipIconButton>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center gap-2 w-full">
              <TooltipIconButton
                size="sm"
                tooltip="展开侧边栏"
                variant="ghost"
                onClick={() => setChatHistoryOpen(true)}
              >
                <PanelRightClose className="size-4" />
              </TooltipIconButton>
            </div>
          )}
        </div>

        {/* 搜索功能 */}
        {chatHistoryOpen && (
          <ThreadSearch
            threads={threads}
            onFilteredThreadsChange={handleSearchFilter}
            isOpen={searchOpen}
          />
        )}

        {/* 标签过滤 */}
        {chatHistoryOpen && tagFilterOpen && (
          <TagFilter onFilterChange={setSelectedTags} />
        )}

        {/* 侧边栏内容 */}
        <div className="flex-1 overflow-hidden flex flex-col">
          <div className="flex-1 overflow-hidden">
            {chatHistoryOpen && (
              threadsLoading ? (
                <LoadingState />
              ) : error ? (
                <ErrorState error={error} onRetry={handleRetry} />
              ) : filteredThreads.length === 0 ? (
                threads.length === 0 ? (
                  <EmptyState
                    type="no-threads"
                  />
                ) : (
                  <EmptyState
                    type={searchOpen ? "no-search-results" : "no-filtered-results"}
                    onClearSearch={() => {
                      setSearchOpen(false);
                      // 清除搜索输入
                      const searchInput = document.querySelector('input[placeholder*="搜索"]') as HTMLInputElement;
                      if (searchInput) {
                        searchInput.value = '';
                        searchInput.dispatchEvent(new Event('input', { bubbles: true }));
                      }
                    }}
                    onClearFilters={() => {
                      setSelectedTags([]);
                      setTagFilterOpen(false);
                    }}
                  />
                )
              ) : (
                <ThreadList threads={filteredThreads} />
              )
            )}
          </div>


        </div>
      </div>
      <div className="lg:hidden">
        <Sheet
          open={!!chatHistoryOpen && !isLargeScreen}
          onOpenChange={(open) => {
            if (isLargeScreen) return;
            setChatHistoryOpen(open);
          }}
        >
          <SheetContent
            side="left"
            className="flex lg:hidden"
          >
            <SheetHeader>
              <SheetTitle>聊天历史</SheetTitle>
            </SheetHeader>
            <ThreadList
              threads={threads}
              onThreadClick={() => setChatHistoryOpen((o) => !o)}
            />
          </SheetContent>
        </Sheet>
      </div>
    </>
  );
}
