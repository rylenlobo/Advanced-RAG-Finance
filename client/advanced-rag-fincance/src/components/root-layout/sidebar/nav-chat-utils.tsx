import React from "react";
import {
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarGroup
} from "../../../components/ui/sidebar";
import { Command, Plus, MessageSquarePlus, Search } from "lucide-react";
import Link from "next/link";

interface ChatButtonProps {
  tooltip: string;
  Icon: React.ElementType;
  label: string;
  shortcut: string;
}

const ChatUtilityButton: React.FC<ChatButtonProps> = ({
  tooltip,
  Icon,
  label,
  shortcut
}) => {
  return (
    <SidebarMenuItem>
      <SidebarMenuButton tooltip={tooltip} className="pr-0">
        <Icon size={5} />
        <span className="text-base lg:text-sm">{label}</span>

        <div className="ml-auto hidden scale-75 items-center space-x-1 rounded-lg bg-border p-2 lg:flex">
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
    <Link href="/">
      <ChatUtilityButton
        tooltip="New Chat"
        Icon={MessageSquarePlus}
        label="New Chat"
        shortcut="N"
      />
    </Link>
  );
}

function SearchChatsButton() {
  return (
    <ChatUtilityButton
      tooltip="Search"
      Icon={Search}
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
