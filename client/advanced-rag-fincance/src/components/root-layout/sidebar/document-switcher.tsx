"use client";

import * as React from "react";
import { ChevronsUpDown, FileText } from "lucide-react";

import {
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem
} from "@/components/ui/sidebar";
import Link from "next/link";
import useDocumentStore from "@/store/currentDocStore";
import { Skeleton } from "@/components/ui/skeleton";

export function DocumentSwitcher() {
  const { selectedDocumentDetails } = useDocumentStore();
  const [isClient, setIsClient] = React.useState(false);

  // Ensure this component only renders client-side
  React.useEffect(() => {
    setIsClient(true);
  }, []);

  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <SidebarMenuButton
          size="lg"
          className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
          tooltip="Upload a file or Select a document to chat with"
          asChild
        >
          <Link href="/documents">
            <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary text-sidebar-primary-foreground">
              <FileText className="size-5" />
            </div>
            <div className="grid flex-1 text-left leading-relaxed">
              {isClient ? (
                selectedDocumentDetails ? (
                  <>
                    <span className="truncate text-base font-semibold lg:text-sm">
                      {selectedDocumentDetails.title}
                    </span>
                    <span className="truncate text-xs text-muted-foreground">
                      {selectedDocumentDetails.file_name}
                    </span>
                  </>
                ) : (
                  <>
                    <span className="truncate text-base font-semibold lg:text-sm">
                      No document selected
                    </span>
                    <span className="truncate text-xs text-muted-foreground">
                      Click to choose a document
                    </span>
                  </>
                )
              ) : (
                <>
                  <span className="truncate text-base font-semibold lg:text-sm">
                    <Skeleton className="h-3" />
                  </span>
                  <span className="mt-1 truncate text-base font-semibold lg:text-sm">
                    <Skeleton className="h-3" />
                  </span>
                </>
              )}
            </div>
            <ChevronsUpDown className="ml-auto" />
          </Link>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
