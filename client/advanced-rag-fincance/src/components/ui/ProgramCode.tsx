import React, { ReactNode } from "react";
import { Copy } from "lucide-react";

interface ProgramCodeProps {
  children: ReactNode;
  language?: string;
}

export function ProgramCode({ children, language }: ProgramCodeProps) {
  const handleCopy = () => {
    navigator.clipboard.writeText(children?.toString() || "");
  };

  return (
    <div className="border-token-border-medium bg-token-sidebar-surface-primary relative rounded-md border-[0.5px] contain-inline-size dark:bg-gray-950">
      <div className="bg-token-sidebar-surface-primary dark:bg-token-main-surface-secondary text-token-text-secondary flex h-9 select-none items-center justify-between rounded-t-[5px] px-4 py-2 font-sans text-xs">
        {language}
      </div>
      <div className="relative">
        <div className="absolute bottom-0 right-2 flex h-9 items-center">
          <button
            className="text-token-text-secondary bg-token-sidebar-surface-primary dark:bg-token-main-surface-secondary flex items-center gap-1 rounded px-4 py-1 font-sans text-xs"
            aria-label="Copy"
            onClick={handleCopy}
          >
            <Copy className="icon-xs" />
            Copy
          </button>
        </div>
      </div>
      <div className="overflow-y-auto p-4" dir="ltr">
        <code className="!whitespace-pre">{children}</code>
      </div>
    </div>
  );
}
