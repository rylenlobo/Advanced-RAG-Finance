import React from "react";
import {
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarGroup
} from "../sidebar";
import { Command, Plus, MessageSquarePlus, Search } from "lucide-react";

interface ChatButtonProps {
  tooltip: string;
  icon: React.ReactNode;
  label: string;
  shortcut: string;
}

const ChatUtilityButton: React.FC<ChatButtonProps> = ({
  tooltip,
  icon,
  label,
  shortcut
}) => {
  return (
    <SidebarMenuItem>
      <SidebarMenuButton tooltip={tooltip} className="pr-0">
        {icon}
        <span className="truncate">{label}</span>

        <div className="flex space-x-1 p-2 items-center bg-border rounded-lg ml-auto scale-75">
          <Command className="size-3" />
          <Plus className="size-2.5" />
          <p className="text-xs">{shortcut}</p>
        </div>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
};

function NewChatButton() {
  return (
    <ChatUtilityButton
      tooltip="New Chat"
      icon={<MessageSquarePlus />}
      label="New Chat"
      shortcut="N"
    />
  );
}

function SearchChatsButton() {
  return (
    <ChatUtilityButton
      tooltip="Search"
      icon={<Search />}
      label="Search"
      shortcut="K"
    />
  );
}

export default function NavChatUtils() {
  return (
    <div>
      <SidebarGroup>
        <SidebarMenu>
          <SearchChatsButton />
          <NewChatButton />
        </SidebarMenu>
      </SidebarGroup>
    </div>
  );
}
