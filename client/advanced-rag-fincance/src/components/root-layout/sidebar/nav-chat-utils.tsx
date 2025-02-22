import React from "react";
import {
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarGroup
} from "../../../components/ui/sidebar";
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

        <div className="ml-auto flex scale-75 items-center space-x-1 rounded-lg bg-border p-2">
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
