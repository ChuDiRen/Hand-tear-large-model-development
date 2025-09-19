// Copyright (c) 2025 左岚. All rights reserved.

import * as React from "react";
import { cn } from "@/lib/utils";

interface PopoverContextType {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const PopoverContext = React.createContext<PopoverContextType | undefined>(undefined);

function usePopover() {
  const context = React.useContext(PopoverContext);
  if (!context) {
    throw new Error("Popover components must be used within a Popover");
  }
  return context;
}

interface PopoverProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

function Popover({ open = false, onOpenChange, children }: PopoverProps) {
  const [internalOpen, setInternalOpen] = React.useState(false);
  const isControlled = open !== undefined && onOpenChange !== undefined;
  const isOpen = isControlled ? open : internalOpen;
  const setOpen = isControlled ? onOpenChange : setInternalOpen;

  return (
    <PopoverContext.Provider value={{ open: isOpen, onOpenChange: setOpen }}>
      <div className="relative inline-block">
        {children}
      </div>
    </PopoverContext.Provider>
  );
}

interface PopoverTriggerProps {
  asChild?: boolean;
  children: React.ReactNode;
  className?: string;
}

function PopoverTrigger({ asChild, children, className }: PopoverTriggerProps) {
  const { open, onOpenChange } = usePopover();
  
  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onOpenChange(!open);
  };
  
  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children, {
      onClick: handleClick,
      className: cn(className, children.props.className),
    });
  }
  
  return (
    <button onClick={handleClick} className={className}>
      {children}
    </button>
  );
}

interface PopoverContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  align?: "start" | "center" | "end";
  side?: "top" | "right" | "bottom" | "left";
  sideOffset?: number;
}

function PopoverContent({ 
  className, 
  children, 
  align = "center",
  side = "bottom",
  sideOffset = 4,
  ...props 
}: PopoverContentProps) {
  const { open, onOpenChange } = usePopover();
  const contentRef = React.useRef<HTMLDivElement>(null);
  
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (contentRef.current && !contentRef.current.contains(event.target as Node)) {
        onOpenChange(false);
      }
    };
    
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onOpenChange(false);
      }
    };
    
    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
        document.removeEventListener('keydown', handleEscape);
      };
    }
  }, [open, onOpenChange]);
  
  if (!open) return null;
  
  const getPositionClasses = () => {
    const baseClasses = "absolute z-50";
    
    switch (side) {
      case "top":
        return `${baseClasses} bottom-full mb-${sideOffset}`;
      case "bottom":
        return `${baseClasses} top-full mt-${sideOffset}`;
      case "left":
        return `${baseClasses} right-full mr-${sideOffset}`;
      case "right":
        return `${baseClasses} left-full ml-${sideOffset}`;
      default:
        return `${baseClasses} top-full mt-${sideOffset}`;
    }
  };
  
  const getAlignClasses = () => {
    switch (align) {
      case "start":
        return side === "top" || side === "bottom" ? "left-0" : "top-0";
      case "end":
        return side === "top" || side === "bottom" ? "right-0" : "bottom-0";
      case "center":
      default:
        return side === "top" || side === "bottom" ? "left-1/2 -translate-x-1/2" : "top-1/2 -translate-y-1/2";
    }
  };
  
  return (
    <div
      ref={contentRef}
      className={cn(
        getPositionClasses(),
        getAlignClasses(),
        "w-72 rounded-md border bg-popover p-4 text-popover-foreground shadow-md outline-none",
        "data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export {
  Popover,
  PopoverTrigger,
  PopoverContent,
};
