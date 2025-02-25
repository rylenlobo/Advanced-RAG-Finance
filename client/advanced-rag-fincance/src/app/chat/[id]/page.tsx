"use client";

import { ArrowRight, Bot, Loader, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AnimatePresence, motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { useCallback, useEffect, useRef } from "react";
import { fetchMessages } from "@/network/fetch-messages";
import { useParams } from "next/navigation";
import { useInfiniteQuery } from "@tanstack/react-query";
import { useInView } from "react-intersection-observer";
import Markdown from "react-markdown";

export default function Page() {
  const { id } = useParams<{ id: string }>();
  const bottomRef = useRef<HTMLDivElement | null>(null);

  // const bottomRef = useCallback((element: HTMLDivElement | null) => {
  //   if (element) {
  //     element.scrollIntoView({ behavior: "smooth" });
  //   }
  // }, []);

  const { ref: topOfMessagesRef, inView } = useInView();
  const { data, error, status, fetchNextPage, isFetchingNextPage } =
    useInfiniteQuery({
      queryKey: ["messages", id],
      initialPageParam: 0,
      queryFn: ({ pageParam }) => fetchMessages(pageParam, id),
      getNextPageParam: (lastPage) => lastPage.nextId
    });

  const messages = data?.pages.flatMap((page) => page.data);

  useEffect(() => {
    if (inView) {
      fetchNextPage();
    }
  }, [inView, fetchNextPage]);

  useEffect(() => {
    setTimeout(() => {
      if (bottomRef.current) {
        bottomRef.current.scrollIntoView({ behavior: "smooth" });
      }
    }, 1500);
  }, []);

  return (
    <div className="container h-dvh min-w-full">
      {/* Messages Container */}

      {status === "error" && error.message}
      {status === "pending" && (
        <div className="flex h-full w-full items-center justify-center">
          <Loader className="animate-spin" />
        </div>
      )}

      {/* Messages */}
      <div className="flex h-full w-full justify-center">
        <div className="flex flex-1 flex-col-reverse space-y-8 overflow-y-auto px-4 pb-24">
          {status === "success" &&
            messages?.map((message, index) => (
              <div
                key={index}
                className={cn(
                  "flex w-full items-start gap-3 md:gap-4 max-w-3xl mx-auto ",
                  message.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                {/* User/Assistant Avatar */}
                {message.role === "assistant" && (
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-md">
                    <Bot className="h-5 w-5" />
                  </div>
                )}

                {/* Chat Bubble */}
                <div
                  className={cn(
                    "px-4 py-2 text-sm md:text-base shadow-md",
                    message.role === "assistant"
                      ? "w-full"
                      : "bg-secondary max-w-[75%] rounded-lg "
                  )}
                >
                  <Markdown>{message.content}</Markdown>
                </div>

                {/* User Avatar (only for user messages) */}
                {message.role === "user" && (
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted shadow-md">
                    <User className="h-5 w-5" />
                  </div>
                )}
              </div>
            ))}
          <div
            ref={topOfMessagesRef}
            className="flex h-11 w-full justify-center pt-11"
          >
            {isFetchingNextPage && <Loader className="size-5 animate-spin" />}
          </div>
        </div>
      </div>

      <div className="relative mx-auto max-w-4xl">
        <div className="fixed bottom-0 w-full max-w-4xl rounded-t-xl bg-secondary px-4 py-3 lg:rounded-none lg:bg-background">
          <InputAI />
        </div>
      </div>
      <div ref={bottomRef} />
    </div>
  );
}

function InputAI({}) {
  return (
    <AnimatePresence>
      <motion.div
        viewport={{ once: true }}
        layoutId="search-input"
        className="relative"
      >
        <Input
          type="text"
          placeholder="Ask whatever you want..."
          className="h-14 w-full rounded-full bg-secondary px-4 py-4"
        />
        <Button
          size="icon"
          className="absolute bottom-0 right-3 top-1/2 -translate-y-1/2 rounded-full"
        >
          <ArrowRight className="h-4 w-4 md:h-5 md:w-5" />
        </Button>
      </motion.div>
    </AnimatePresence>
  );
}
