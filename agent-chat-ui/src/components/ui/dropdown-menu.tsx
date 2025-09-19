// Copyright (c) 2025 左岚. All rights reserved.

import * as React from "react";
import { cn } from "@/lib/utils";

interface DropdownMenuContextType {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const DropdownMenuContext = React.createContext<DropdownMenuContextType | undefined>(undefined);

function useDropdownMenu() {
  const context = React.useContext(DropdownMenuContext);
  if (!context) {
    throw new Error("DropdownMenu components must be used within a DropdownMenu");
  }
  return context;
}

interface DropdownMenuProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

function DropdownMenu({ open = false, onOpenChange, children }: DropdownMenuProps) {
  const [internalOpen, setInternalOpen] = React.useState(false);
  const isControlled = open !== undefined && onOpenChange !== undefined;
  const isOpen = isControlled ? open : internalOpen;
  const setOpen = isControlled ? onOpenChange : setInternalOpen;

  return (
    <DropdownMenuContext.Provider value={{ open: isOpen, onOpenChange: setOpen }}>
      {children}
    </DropdownMenuContext.Provider>
  );
}

interface DropdownMenuTriggerProps {
  asChild?: boolean;
  children: React.ReactNode;
  className?: string;
}

function DropdownMenuTrigger({ asChild, children, className }: DropdownMenuTriggerProps) {
  const { open, onOpenChange } = useDropdownMenu();
  
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

interface DropdownMenuContentProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  align?: "start" | "center" | "end";
  side?: "top" | "right" | "bottom" | "left";
}

function DropdownMenuContent({ 
  className, 
  children, 
  align = "start",
  side = "bottom",
  ...props 
}: DropdownMenuContentProps) {
  const { open, onOpenChange } = useDropdownMenu();
  const contentRef = React.useRef<HTMLDivElement>(null);
  
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (contentRef.current && !contentRef.current.contains(event.target as Node)) {
        onOpenChange(false);
      }
    };
    
    if (open) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [open, onOpenChange]);
  
  if (!open) return null;
  
  return (
    <div
      ref={contentRef}
      className={cn(
        "absolute z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md",
        "data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
        {
          "top-full mt-1": side === "bottom",
          "bottom-full mb-1": side === "top",
          "left-full ml-1": side === "right",
          "right-full mr-1": side === "left",
        },
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

interface DropdownMenuItemProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  disabled?: boolean;
}

function DropdownMenuItem({ 
  className, 
  children, 
  disabled = false,
  onClick,
  ...props 
}: DropdownMenuItemProps) {
  const { onOpenChange } = useDropdownMenu();
  
  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (disabled) return;
    onClick?.(e);
    onOpenChange(false);
  };
  
  return (
    <div
      className={cn(
        "relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors",
        "focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
        "hover:bg-accent hover:text-accent-foreground",
        disabled && "pointer-events-none opacity-50",
        className
      )}
      onClick={handleClick}
      {...props}
    >
      {children}
    </div>
  );
}

function DropdownMenuSeparator({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("-mx-1 my-1 h-px bg-muted", className)}
      {...props}
    />
  );
}

interface DropdownMenuLabelProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

function DropdownMenuLabel({ className, children, ...props }: DropdownMenuLabelProps) {
  return (
    <div
      className={cn("px-2 py-1.5 text-sm font-semibold", className)}
      {...props}
    >
      {children}
    </div>
  );
}

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuLabel,
};
