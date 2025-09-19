// Copyright (c) 2025 左岚. All rights reserved.

import React, { useRef, useState } from "react";
import { Download, Upload, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Thread } from "@langchain/langgraph-sdk";
import { toast } from "sonner";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { TooltipIconButton } from "../tooltip-icon-button";

interface ImportExportProps {
  threads: Thread[];
  onImport?: (threads: Thread[]) => void;
}

export function ImportExport({ threads, onImport }: ImportExportProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [menuOpen, setMenuOpen] = useState(false);

  // 导出所有对话
  const handleExportAll = () => {
    exportThreads(threads, "all");
  };

  // 导出最近的对话
  const handleExportRecent = (count: number) => {
    const recentThreads = threads
      .sort((a, b) => new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime())
      .slice(0, count);
    exportThreads(recentThreads, `recent-${count}`);
  };

  // 通用导出函数
  const exportThreads = (threadsToExport: Thread[], suffix: string) => {
    try {
      const exportData = {
        version: "1.0",
        exportDate: new Date().toISOString(),
        threads: threadsToExport.map(thread => ({
          thread_id: thread.thread_id,
          created_at: thread.created_at,
          updated_at: thread.updated_at,
          metadata: thread.metadata,
          values: thread.values,
        })),
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: "application/json",
      });

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `chat-history-${suffix}-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast.success(`已导出 ${threadsToExport.length} 个对话`);
    } catch (error) {
      console.error("Export failed:", error);
      toast.error("导出失败");
    }
  };

  // 导出单个对话
  const handleExportSingle = (thread: Thread) => {
    try {
      const exportData = {
        version: "1.0",
        exportDate: new Date().toISOString(),
        thread: {
          thread_id: thread.thread_id,
          created_at: thread.created_at,
          updated_at: thread.updated_at,
          metadata: thread.metadata,
          values: thread.values,
        },
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: "application/json",
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `chat-${thread.thread_id.slice(0, 8)}-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast.success("对话导出成功");
    } catch (error) {
      console.error("Export failed:", error);
      toast.error("导出失败");
    }
  };

  // 导入对话
  const handleImport = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // 检查文件大小（限制为 10MB）
    if (file.size > 10 * 1024 * 1024) {
      toast.error("文件太大，请选择小于 10MB 的文件");
      return;
    }

    // 检查文件类型
    if (!file.name.endsWith('.json')) {
      toast.error("请选择 JSON 格式的文件");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = e.target?.result as string;
        const importData = JSON.parse(content);

        // 验证导入数据格式
        if (!importData.version) {
          throw new Error("缺少版本信息");
        }

        // 支持单个对话和多个对话的导入
        let importedThreads: Thread[] = [];

        if (importData.threads && Array.isArray(importData.threads)) {
          // 多个对话
          importedThreads = importData.threads;
        } else if (importData.thread) {
          // 单个对话
          importedThreads = [importData.thread];
        } else {
          throw new Error("未找到有效的对话数据");
        }

        // 验证每个对话的基本结构
        const validThreads = importedThreads.filter(thread => {
          return thread.thread_id && typeof thread.thread_id === 'string';
        });

        if (validThreads.length === 0) {
          throw new Error("没有找到有效的对话");
        }

        onImport?.(validThreads);

        if (validThreads.length !== importedThreads.length) {
          toast.warning(`已导入 ${validThreads.length} 个对话，跳过了 ${importedThreads.length - validThreads.length} 个无效对话`);
        } else {
          toast.success(`已成功导入 ${validThreads.length} 个对话`);
        }
      } catch (error) {
        console.error("Import failed:", error);
        const errorMessage = error instanceof Error ? error.message : "未知错误";
        toast.error(`导入失败：${errorMessage}`);
      }
    };

    reader.onerror = () => {
      toast.error("文件读取失败");
    };

    reader.readAsText(file);

    // 清空文件输入，允许重复选择同一文件
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <>
      <div className="relative">
        <TooltipIconButton
          size="sm"
          tooltip="导入/导出"
          variant="ghost"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          <FileText className="size-4" />
        </TooltipIconButton>

        {menuOpen && (
          <div className="absolute right-0 top-8 z-50 w-48 bg-white border rounded-md shadow-lg">
            <div className="py-1">
              <button
                className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center"
                onClick={() => {
                  handleExportAll();
                  setMenuOpen(false);
                }}
              >
                <Download className="size-4 mr-2" />
                导出所有对话 ({threads.length})
              </button>
              <button
                className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center"
                onClick={() => {
                  handleExportRecent(10);
                  setMenuOpen(false);
                }}
              >
                <Download className="size-4 mr-2" />
                导出最近 10 个对话
              </button>
              <hr className="my-1" />
              <button
                className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center"
                onClick={() => {
                  handleImport();
                  setMenuOpen(false);
                }}
              >
                <Upload className="size-4 mr-2" />
                导入对话
              </button>
            </div>
          </div>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />
    </>
  );
}

// 单个对话的导出按钮
export function ThreadExportButton({ thread }: { thread: Thread }) {
  const handleExport = () => {
    try {
      const exportData = {
        version: "1.0",
        exportDate: new Date().toISOString(),
        thread: {
          thread_id: thread.thread_id,
          created_at: thread.created_at,
          updated_at: thread.updated_at,
          metadata: thread.metadata,
          values: thread.values,
        },
      };

      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: "application/json",
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `chat-${thread.thread_id.slice(0, 8)}-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      toast.success("对话导出成功");
    } catch (error) {
      console.error("Export failed:", error);
      toast.error("导出失败");
    }
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleExport}
      className="h-6 w-6 p-0"
    >
      <Download className="size-3" />
    </Button>
  );
}
