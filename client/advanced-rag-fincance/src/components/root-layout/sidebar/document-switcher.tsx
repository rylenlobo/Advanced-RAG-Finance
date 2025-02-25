"use client";

import * as React from "react";
import { ChevronsUpDown, FileText } from "lucide-react";

import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem
} from "@/components/ui/sidebar";

export function DocumentSwitcher() {
  return (
    <>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton
            size="lg"
            className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
            tooltip="Upload a file or Select a document to chat with"
          >
            <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
              <FileText className="size-5" />
            </div>
            <div className="grid flex-1 text-left leading-relaxed">
              <span className="truncate text-base font-semibold lg:text-sm">
                MS Annual report
              </span>
              <span className="truncate text-xs text-muted-foreground">
                microsoft-annual-report.pdf
              </span>
            </div>
            <ChevronsUpDown className="ml-auto" />
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </>
  );
}
