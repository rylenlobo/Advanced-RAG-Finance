"use client";

import { ArrowRight, MessageSquareText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motion } from "framer-motion";

export default function ChatInterface() {
  const suggestions = [
    "What are the key financial trends in the report?",
    "Can you summarize the investment opportunities discussed?",
    "How does this document explain risk management strategies?"
  ];

  return (
    <div className="container mx-auto flex min-h-dvh max-w-3xl items-center justify-center p-4">
      <div className="mt-auto w-full space-y-8 lg:mt-0">
        {/* Welcome Messages */}
        <div className="space-y-4">
          <h1 className="mb-12 text-5xl font-thin duration-1000 animate-in fade-in slide-in-from-top-10 md:text-6xl">
            Hi there,
            <br />
            How can I assist you today?
          </h1>
          <p className="max-w-2xl text-muted-foreground duration-1000 animate-in fade-in-0 md:text-base">
            You can ask me anything! Whether you need financial insights,
            analysis, or recommendations, I&apos;m here to help. Let&apos;s get
            started!
          </p>
        </div>

        {/* Suggestion Cards */}
        <div className="flex flex-col items-center gap-5 duration-1000 animate-in fade-in-0 lg:h-28 lg:flex-row">
          {suggestions.map((suggestion, index) => (
            <Button
              key={index}
              variant="outline"
              className="flex h-auto w-full flex-col items-start justify-between whitespace-normal break-words rounded-xl px-4 py-3 text-left text-sm font-medium leading-normal transition-all duration-300 hover:-translate-y-1 hover:animate-in md:w-3/4 lg:h-full"
            >
              {suggestion}

              <MessageSquareText className="text-muted-foreground" />
            </Button>
          ))}
        </div>

        {/* Search Input */}
        <motion.div
          layoutId="search-input"
          className="relative duration-1000 animate-in fade-in slide-in-from-bottom-10"
        >
          <Input
            type="text"
            placeholder="Ask whatever you want..."
            className="bg-bg-secondary h-14 w-full rounded-full px-4 py-4"
          />
          <Button
            size="icon"
            className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full"
          >
            <ArrowRight className="h-4 w-4 md:h-5 md:w-5" />
          </Button>
        </motion.div>
      </div>
    </div>
  );
}
