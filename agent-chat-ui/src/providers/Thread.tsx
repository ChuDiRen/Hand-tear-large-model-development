// Copyright (c) 2025 左岚. All rights reserved.

import { validate } from "uuid";
import { getApiKey } from "@/lib/api-key";
import { Thread } from "@langchain/langgraph-sdk";
import { useQueryState } from "nuqs";
import {
  createContext,
  useContext,
  ReactNode,
  useCallback,
  useState,
  Dispatch,
  SetStateAction,
} from "react";
import { createClient } from "./client";
import { toast } from "sonner";


interface ThreadContextType {
  getThreads: () => Promise<Thread[]>;
  threads: Thread[];
  setThreads: Dispatch<SetStateAction<Thread[]>>;
  threadsLoading: boolean;
  setThreadsLoading: Dispatch<SetStateAction<boolean>>;
  deleteThread: (threadId: string) => Promise<boolean>; // 添加删除方法
  deleteThreads: (threadIds: string[]) => Promise<boolean>; // 添加批量删除方法
}

const ThreadContext = createContext<ThreadContextType | undefined>(undefined);

function getThreadSearchMetadata(
  assistantId: string,
): { graph_id: string } | { assistant_id: string } {
  if (validate(assistantId)) {
    return { assistant_id: assistantId };
  } else {
    return { graph_id: assistantId };
  }
}

export function ThreadProvider({ children }: { children: ReactNode }) {

  const [apiUrl] = useQueryState("apiUrl");
  const [assistantId] = useQueryState("assistantId");
  const [threads, setThreads] = useState<Thread[]>([]);
  const [threadsLoading, setThreadsLoading] = useState(false);

  const getThreads = useCallback(async (): Promise<Thread[]> => {
    if (!apiUrl || !assistantId) return [];
    const client = createClient(apiUrl, getApiKey() ?? undefined);

    const threads = await client.threads.search({
      metadata: {
        ...getThreadSearchMetadata(assistantId),
      },
      limit: 100,
    });

    return threads;
  }, [apiUrl, assistantId]);

  // 删除单个线程
  const deleteThread = useCallback(async (threadId: string): Promise<boolean> => {
    if (!apiUrl) return false;

    try {
      const client = createClient(apiUrl, getApiKey() ?? undefined);
      await client.threads.delete(threadId);

      // 从本地状态中移除已删除的线程
      setThreads(prev => prev.filter(thread => thread.thread_id !== threadId));

      toast.success("对话删除成功");
      return true;
    } catch (error) {
      console.error("Failed to delete thread:", error);
      toast.error("删除对话失败");
      return false;
    }
  }, [apiUrl]);

  // 批量删除线程
  const deleteThreads = useCallback(async (threadIds: string[]): Promise<boolean> => {
    if (!apiUrl || threadIds.length === 0) return false;

    try {
      const client = createClient(apiUrl, getApiKey() ?? undefined);

      // 并行删除所有线程
      const deletePromises = threadIds.map(threadId => client.threads.delete(threadId));
      await Promise.all(deletePromises);

      // 从本地状态中移除已删除的线程
      setThreads(prev => prev.filter(thread => !threadIds.includes(thread.thread_id)));

      toast.success("对话删除成功");
      return true;
    } catch (error) {
      console.error("Failed to delete threads:", error);
      toast.error("删除对话失败");
      return false;
    }
  }, [apiUrl]);

  const value = {
    getThreads,
    threads,
    setThreads,
    threadsLoading,
    setThreadsLoading,
    deleteThread,
    deleteThreads,
  };

  return (
    <ThreadContext.Provider value={value}>{children}</ThreadContext.Provider>
  );
}

export function useThreads() {
  const context = useContext(ThreadContext);
  if (context === undefined) {
    throw new Error("useThreads must be used within a ThreadProvider");
  }
  return context;
}
