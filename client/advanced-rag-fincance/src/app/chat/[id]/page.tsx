"use client";

import { ArrowRight, Loader } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AnimatePresence, motion } from "framer-motion";

import { useEffect } from "react";
import { fetchMessages } from "@/network/fetch-messages";
import { useParams } from "next/navigation";
import { useInfiniteQuery } from "@tanstack/react-query";
import { useInView } from "react-intersection-observer";
import { Message } from "../components/message";

export default function Page() {
  const { id } = useParams<{ id: string }>();

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

  return (
    <div className="h-dvh w-screen lg:container lg:min-w-full">
      {/* Error Message */}
      {status === "error" && error.message}

      {/* Loading State */}
      {status === "pending" && (
        <div className="flex h-full w-full items-center justify-center">
          <Loader className="animate-spin" />
        </div>
      )}

      {/* Messages */}
      <div className="flex h-full w-full justify-center">
        <div className="flex w-full flex-1 flex-col-reverse gap-6 overflow-y-auto px-4 pb-24">
          {status === "success" &&
            messages?.map((message) => (
              <Message key={message.id} message={message} />
            ))}
          <div
            ref={topOfMessagesRef}
            className="flex h-11 w-full justify-center pt-11"
          >
            {isFetchingNextPage && <Loader className="size-5 animate-spin" />}
          </div>
        </div>
      </div>

      {/* Message Input */}
      <div className="relative mx-auto max-w-4xl">
        <div className="fixed bottom-0 w-full max-w-4xl rounded-t-xl bg-secondary px-4 py-3 lg:rounded-none lg:bg-background">
          <InputAI />
        </div>
      </div>
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
