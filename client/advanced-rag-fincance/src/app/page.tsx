"use client";

import InputAI from "@/components/chat-input";

export default function ChatInterface() {
  return (
    <div className="container mx-auto flex min-h-dvh max-w-3xl items-center justify-center p-4">
      <div className="mt-auto w-full space-y-8 duration-500 animate-in fade-in-0 lg:mt-0">
        {/* Welcome Messages */}
        <div className="duration-500 animate-in fade-in-0 slide-in-from-bottom-10">
          <h1 className="mb-10 text-5xl font-thin md:text-6xl">
            Hi there,
            <br />
            How can I assist you today?
          </h1>
          <p className="max-w-2xl text-muted-foreground md:text-base">
            You can ask me anything! Whether you need financial insights,
            analysis, or recommendations, I&apos;m here to help. Let&apos;s get
            started!
          </p>
        </div>

        {/* Search Input */}
        <InputAI />
      </div>
    </div>
  );
}
