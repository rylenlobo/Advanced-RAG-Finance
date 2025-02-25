"use client";

import {
  ChevronRight,
  Forward,
  Loader,
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
  SidebarMenuSkeleton,
  useSidebar
} from "@/components/ui/sidebar";
import { useInfiniteQuery } from "@tanstack/react-query";
import { fetchPreviousChats } from "@/network/fetch-previous-chats";
import { PreviousChatsList } from "../types/types";
import { useEffect } from "react";
import { useInView } from "react-intersection-observer";
import Link from "next/link";
import { motion } from "framer-motion";

import { useSearchParams } from "next/navigation";

function SkeletonLoader() {
  return (
    <>
      {Array.from({ length: 22 }).map((_, index) => (
        <SidebarMenuItem key={index}>
          <SidebarMenuSkeleton />
        </SidebarMenuItem>
      ))}
    </>
  );
}

export function NavPreviousChatsList() {
  const { ref: endOfPrevChatsListRef, inView } = useInView();
  const searchParams = useSearchParams();
  const doc_id = searchParams.get("doc_id");

  const { data, error, status, fetchNextPage, isFetchingNextPage } =
    useInfiniteQuery({
      queryKey: ["conversations"],
      initialPageParam: 0,
      queryFn: ({ pageParam }) => fetchPreviousChats(pageParam, doc_id),
      getNextPageParam: (lastPage) => lastPage.nextId
    });

  useEffect(() => {
    if (inView) {
      fetchNextPage();
    }
  }, [inView, fetchNextPage]);

  return (
    <Collapsible asChild defaultOpen={true} className="group/collapsible">
      <SidebarGroup className="group-data-[collapsible=icon]:hidden">
        <CollapsibleTrigger asChild>
          <SidebarMenuButton className="pl-0">
            <SidebarGroupLabel className="text-base">Chats</SidebarGroupLabel>
            <ChevronRight className="ml-auto size-4 transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
          </SidebarMenuButton>
        </CollapsibleTrigger>
        <CollapsibleContent className="overflow-hidden group-data-[state=closed]/collapsible:animate-slideUp group-data-[state=open]/collapsible:animate-slideDown">
          {" "}
          <SidebarMenu>
            {status === "error" && error.message}
            {status === "pending" && <SkeletonLoader />}
            {status === "success" &&
              data.pages.map((page, index) => (
                <div key={index}>
                  {page.data.map(({ name, id }, itemIndex) => (
                    <motion.div
                      key={id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{
                        delay: itemIndex * 0.05,
                        duration: 0.5,
                        ease: "easeInOut"
                      }}
                    >
                      <PreviousChat id={id} name={name} />
                    </motion.div>
                  ))}
                </div>
              ))}
            {isFetchingNextPage && (
              <SidebarMenuItem className="flex w-full justify-center py-7">
                <Loader className="size-5 animate-spin" />
              </SidebarMenuItem>
            )}
            <SidebarMenuItem ref={endOfPrevChatsListRef}></SidebarMenuItem>
          </SidebarMenu>
        </CollapsibleContent>
      </SidebarGroup>
    </Collapsible>
  );
}

function PreviousChat({ id, name }: PreviousChatsList) {
  const { isMobile } = useSidebar();
  return (
    <SidebarMenuItem key={id}>
      <SidebarMenuButton asChild className="py-5 lg:py-0">
        <Link href={`/chat/${id}`}>
          <MessageSquare />
          <p className="truncate text-base lg:text-sm">{name}</p>
        </Link>
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
  );
}
