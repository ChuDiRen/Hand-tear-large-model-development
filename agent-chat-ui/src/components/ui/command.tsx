// Copyright (c) 2025 左岚. All rights reserved.

import * as React from "react";
import { cn } from "@/lib/utils";
import { Search } from "lucide-react";

interface CommandContextType {
  search: string;
  setSearch: (search: string) => void;
  filteredItems: string[];
  setFilteredItems: (items: string[]) => void;
}

const CommandContext = React.createContext<CommandContextType | undefined>(undefined);

function useCommand() {
  const context = React.useContext(CommandContext);
  if (!context) {
    throw new Error("Command components must be used within a Command");
  }
  return context;
}

interface CommandProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  value?: string;
  onValueChange?: (value: string) => void;
}

function Command({ className, children, value, onValueChange, ...props }: CommandProps) {
  const [search, setSearch] = React.useState(value || "");
  const [filteredItems, setFilteredItems] = React.useState<string[]>([]);
  
  React.useEffect(() => {
    if (value !== undefined) {
      setSearch(value);
    }
  }, [value]);
  
  const handleSearchChange = (newSearch: string) => {
    setSearch(newSearch);
    onValueChange?.(newSearch);
  };
  
  return (
    <CommandContext.Provider value={{ 
      search, 
      setSearch: handleSearchChange, 
      filteredItems, 
      setFilteredItems 
    }}>
      <div
        className={cn(
          "flex h-full w-full flex-col overflow-hidden rounded-md bg-popover text-popover-foreground",
          className
        )}
        {...props}
      >
        {children}
      </div>
    </CommandContext.Provider>
  );
}

interface CommandInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  placeholder?: string;
}

function CommandInput({ className, placeholder = "搜索...", ...props }: CommandInputProps) {
  const { search, setSearch } = useCommand();
  
  return (
    <div className="flex items-center border-b px-3" cmdk-input-wrapper="">
      <Search className="mr-2 h-4 w-4 shrink-0 opacity-50" />
      <input
        className={cn(
          "flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder={placeholder}
        {...props}
      />
    </div>
  );
}

interface CommandListProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

function CommandList({ className, children, ...props }: CommandListProps) {
  return (
    <div
      className={cn("max-h-[300px] overflow-y-auto overflow-x-hidden", className)}
      {...props}
    >
      {children}
    </div>
  );
}

interface CommandEmptyProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
}

function CommandEmpty({ className, children, ...props }: CommandEmptyProps) {
  const { search } = useCommand();
  
  if (!search) return null;
  
  return (
    <div
      className={cn("py-6 text-center text-sm text-muted-foreground", className)}
      {...props}
    >
      {children}
    </div>
  );
}

interface CommandGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  heading?: string;
}

function CommandGroup({ className, children, heading, ...props }: CommandGroupProps) {
  return (
    <div
      className={cn("overflow-hidden p-1 text-foreground", className)}
      {...props}
    >
      {heading && (
        <div className="px-2 py-1.5 text-xs font-medium text-muted-foreground">
          {heading}
        </div>
      )}
      {children}
    </div>
  );
}

interface CommandItemProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  value?: string;
  disabled?: boolean;
  onSelect?: (value: string) => void;
}

function CommandItem({ 
  className, 
  children, 
  value = "", 
  disabled = false,
  onSelect,
  ...props 
}: CommandItemProps) {
  const { search } = useCommand();
  
  const isVisible = React.useMemo(() => {
    if (!search) return true;
    const searchLower = search.toLowerCase();
    const valueLower = value.toLowerCase();
    const childrenText = typeof children === 'string' ? children.toLowerCase() : '';
    
    return valueLower.includes(searchLower) || childrenText.includes(searchLower);
  }, [search, value, children]);
  
  const handleClick = () => {
    if (disabled) return;
    onSelect?.(value);
  };
  
  if (!isVisible) return null;
  
  return (
    <div
      className={cn(
        "relative flex cursor-default select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none",
        "aria-selected:bg-accent aria-selected:text-accent-foreground",
        "hover:bg-accent hover:text-accent-foreground",
        "data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
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

type CommandSeparatorProps = React.HTMLAttributes<HTMLDivElement>;

function CommandSeparator({ className, ...props }: CommandSeparatorProps) {
  return (
    <div
      className={cn("-mx-1 h-px bg-border", className)}
      {...props}
    />
  );
}

export {
  Command,
  CommandInput,
  CommandList,
  CommandEmpty,
  CommandGroup,
  CommandItem,
  CommandSeparator,
};
