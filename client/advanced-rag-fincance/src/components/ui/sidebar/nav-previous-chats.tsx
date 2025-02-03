"use client";

import {
  ChevronRight,
  Forward,
  MessageSquare,
  MoreHorizontal,
  Pencil,
  Trash2
} from "lucide-react";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger
} from "@/components/ui/dropdown-menu";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger
} from "@/components/ui/collapsible";

import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar
} from "@/components/ui/sidebar";

import type { PreviousChatsList } from "@/types/previous-chats-list";

export function NavPreviousChatsList({
  previousChatListProps
}: {
  previousChatListProps: PreviousChatsList[];
}) {
  const { isMobile } = useSidebar();

  return (
    <Collapsible asChild defaultOpen={true} className="group/collapsible ">
      <SidebarGroup className="group-data-[collapsible=icon]:hidden">
        <CollapsibleTrigger asChild>
          <SidebarMenuButton className="pl-0">
            <SidebarGroupLabel className="">Chats</SidebarGroupLabel>
            <ChevronRight className="size-4 ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
          </SidebarMenuButton>
        </CollapsibleTrigger>
        <CollapsibleContent className="overflow-hidden group-data-[state=open]/collapsible:animate-slideDown group-data-[state=closed]/collapsible:animate-slideUp">
          <SidebarMenu>
            {previousChatListProps.map(({ name, id }) => (
              <SidebarMenuItem key={id}>
                <SidebarMenuButton className="text-sm" asChild>
                  <a>
                    <MessageSquare />
                    <span>{name}</span>
                  </a>
                </SidebarMenuButton>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <SidebarMenuAction showOnHover>
                      <MoreHorizontal />
                      <span className="sr-only">More</span>
                    </SidebarMenuAction>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent
                    className="w-48 rounded-lg"
                    side={isMobile ? "bottom" : "right"}
                    align={isMobile ? "end" : "start"}
                  >
                    <DropdownMenuItem>
                      <Forward />
                      <span>Share</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Pencil />
                      <span>Rename</span>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem className="text-red-400 hover:text-red-500">
                      <Trash2 />
                      <span>Delete</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </SidebarMenuItem>
            ))}
            {/* TODO: Add Pagination to load more chats */}
            <SidebarMenuItem>
              <SidebarMenuButton className="text-sidebar-foreground/70">
                <MoreHorizontal className="text-sidebar-foreground/70" />
                <span>More</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </CollapsibleContent>
      </SidebarGroup>
    </Collapsible>
  );
}
