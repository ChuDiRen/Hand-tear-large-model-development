// Copyright (c) 2025 左岚. All rights reserved.

import React from "react";
import { motion, AnimatePresence } from "framer-motion";

// 淡入动画包装器
export function FadeIn({ 
  children, 
  delay = 0,
  duration = 0.3,
  className = ""
}: { 
  children: React.ReactNode;
  delay?: number;
  duration?: number;
  className?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration, delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

// 滑入动画包装器
export function SlideIn({ 
  children, 
  direction = "left",
  delay = 0,
  duration = 0.3,
  className = ""
}: { 
  children: React.ReactNode;
  direction?: "left" | "right" | "up" | "down";
  delay?: number;
  duration?: number;
  className?: string;
}) {
  const getInitialPosition = () => {
    switch (direction) {
      case "left": return { x: -20, opacity: 0 };
      case "right": return { x: 20, opacity: 0 };
      case "up": return { y: -20, opacity: 0 };
      case "down": return { y: 20, opacity: 0 };
      default: return { x: -20, opacity: 0 };
    }
  };

  return (
    <motion.div
      initial={getInitialPosition()}
      animate={{ x: 0, y: 0, opacity: 1 }}
      exit={getInitialPosition()}
      transition={{ duration, delay }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

// 列表项动画包装器
export function ListItemAnimation({ 
  children, 
  index = 0,
  className = ""
}: { 
  children: React.ReactNode;
  index?: number;
  className?: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ 
        duration: 0.2, 
        delay: index * 0.05,
        ease: "easeOut"
      }}
      whileHover={{ 
        scale: 1.02,
        transition: { duration: 0.1 }
      }}
      whileTap={{ scale: 0.98 }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

// 搜索结果动画包装器
export function SearchResultsAnimation({ 
  children,
  resultsCount = 0
}: { 
  children: React.ReactNode;
  resultsCount?: number;
}) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={resultsCount}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -10 }}
        transition={{ duration: 0.2 }}
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

// 标签动画包装器
export function TagAnimation({ 
  children,
  isNew = false
}: { 
  children: React.ReactNode;
  isNew?: boolean;
}) {
  return (
    <motion.div
      initial={isNew ? { scale: 0, opacity: 0 } : false}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0, opacity: 0 }}
      transition={{ 
        type: "spring", 
        stiffness: 500, 
        damping: 30 
      }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      {children}
    </motion.div>
  );
}

// 侧边栏展开/收起动画
export function SidebarAnimation({ 
  children,
  isOpen = true,
  width = 320
}: { 
  children: React.ReactNode;
  isOpen?: boolean;
  width?: number;
}) {
  return (
    <motion.div
      animate={{ 
        width: isOpen ? width : 64,
        opacity: 1
      }}
      transition={{ 
        type: "spring", 
        stiffness: 300, 
        damping: 30 
      }}
      className="overflow-hidden"
    >
      {children}
    </motion.div>
  );
}

// 加载动画组件
export function LoadingDots() {
  return (
    <div className="flex space-x-1">
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          className="w-2 h-2 bg-blue-500 rounded-full"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.7, 1, 0.7],
          }}
          transition={{
            duration: 0.6,
            repeat: Infinity,
            delay: index * 0.2,
          }}
        />
      ))}
    </div>
  );
}

// 成功/错误提示动画
export function StatusAnimation({ 
  type,
  children 
}: { 
  type: "success" | "error" | "warning";
  children: React.ReactNode;
}) {
  const getColor = () => {
    switch (type) {
      case "success": return "bg-green-100 border-green-200 text-green-800";
      case "error": return "bg-red-100 border-red-200 text-red-800";
      case "warning": return "bg-yellow-100 border-yellow-200 text-yellow-800";
      default: return "bg-gray-100 border-gray-200 text-gray-800";
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9, y: -10 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.9, y: -10 }}
      transition={{ type: "spring", stiffness: 500, damping: 30 }}
      className={`p-3 rounded-lg border ${getColor()}`}
    >
      {children}
    </motion.div>
  );
}

// 悬浮按钮动画
export function FloatingButtonAnimation({ 
  children,
  className = ""
}: { 
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <motion.div
      whileHover={{ 
        scale: 1.05,
        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)"
      }}
      whileTap={{ scale: 0.95 }}
      transition={{ type: "spring", stiffness: 400, damping: 17 }}
      className={className}
    >
      {children}
    </motion.div>
  );
}
