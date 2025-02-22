import * as React from "react";
import { NavPreviousChatsList } from "@/components/root-layout/sidebar/nav-previous-chats";
import { DocumentSwitcher } from "@/components/root-layout/sidebar/document-switcher";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarProvider,
  SidebarRail
} from "@/components/ui/sidebar";

import NavChatUtils from "./nav-chat-utils";
import { NavUser } from "./nav-user";
import { ScrollArea } from "@/components/ui/scroll-area";

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <SidebarProvider>
      <Sidebar collapsible="icon" {...props}>
        <SidebarHeader>
          <DocumentSwitcher />
        </SidebarHeader>
        <SidebarContent>
          <NavChatUtils />
          <ScrollArea>
            <NavPreviousChatsList />
          </ScrollArea>
        </SidebarContent>
        <SidebarFooter>
          <NavUser />
        </SidebarFooter>
        <SidebarRail />
      </Sidebar>
    </SidebarProvider>
  );
}
