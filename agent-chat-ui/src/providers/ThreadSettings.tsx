// Copyright (c) 2025 左岚. All rights reserved.

import React, { createContext, useContext, ReactNode } from 'react';

interface ThreadSettingsContextType {
  hideToolCalls: boolean;
}

const ThreadSettingsContext = createContext<ThreadSettingsContextType | undefined>(undefined);

export function ThreadSettingsProvider({ 
  children, 
  hideToolCalls 
}: { 
  children: ReactNode;
  hideToolCalls: boolean;
}) {
  return (
    <ThreadSettingsContext.Provider value={{ hideToolCalls }}>
      {children}
    </ThreadSettingsContext.Provider>
  );
}

export function useThreadSettings() {
  const context = useContext(ThreadSettingsContext);
  if (context === undefined) {
    throw new Error('useThreadSettings must be used within a ThreadSettingsProvider');
  }
  return context;
}
