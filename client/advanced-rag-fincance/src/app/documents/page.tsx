"use client";
import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Upload, FileText, ArrowRight, Loader, Trash } from "lucide-react";
import { fetchDocuments } from "@/network/fetch-documents";
import { useQuery } from "@tanstack/react-query";

import { cn } from "@/lib/utils";
import useDocumentStore from "@/store/currentDocStore";
import Link from "next/link";
import type { Document } from "@/network/fetch-documents";

export default function Page() {
  const { setSelectedDocument } = useDocumentStore();

  // TODO: Add error hnaadling and status

  const handleSelectDocumentClick = (document: Document) => {
    setSelectedDocument(document);
  };

  const { data, status } = useQuery({
    queryKey: ["documents"],
    queryFn: fetchDocuments
  });

  if (data?.data.length === 0) {
    return (
      <div className="flex h-dvh w-screen flex-col items-center justify-center space-y-4 animate-in lg:container lg:min-w-full">
        <p className="text-center text-lg text-gray-400">
          You haven’t uploaded any documents yet. Upload your first document to
          get started!
        </p>
        <UploadDocButton />
      </div>
    );
  }

  return (
    <div className="h-dvh w-screen p-4 lg:container md:p-6 lg:min-w-full">
      <div className="mx-auto flex h-full w-full max-w-4xl flex-col space-y-4 md:space-y-6">
        {/* Header */}
        <div className="flex justify-between gap-4 sm:flex-row">
          <h1 className="text-xl font-semibold text-white md:text-2xl">
            RAG Documents
          </h1>
          <UploadDocButton />
        </div>

        {/* Search Bar */}
        <div className="relative">
          <Input
            type="text"
            placeholder="Ask whatever you want..."
            className="h-12 w-full px-4 py-2"
          />
          <Button className="absolute right-2 top-1/2 h-8 w-8 -translate-y-1/2 rounded-md">
            <ArrowRight />
          </Button>
        </div>

        {status === "pending" && (
          <div className="flex w-full flex-1 items-center justify-center">
            <Loader className="size-5 animate-spin" />
          </div>
        )}

        {/* Document List */}

        {status === "success" && (
          <div className="grid h-full w-full content-start gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {data?.data.map(({ id, title, file_name, created_at }) => (
              <Link key={id} href="/">
                <div
                  onClick={() =>
                    handleSelectDocumentClick({
                      id,
                      title,
                      file_name,
                      created_at
                    })
                  }
                  className="group h-fit min-w-full rounded-xl border-2 border-zinc-800/50 bg-gradient-to-r from-zinc-900/50 to-zinc-800/30 p-6 transition-transform animate-in fade-in-25 hover:border-zinc-700/50 hover:bg-zinc-900/50 active:scale-95"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <h2 className="text-lg font-medium text-primary transition-colors group-hover:text-muted-foreground">
                          {title}
                        </h2>
                      </div>

                      <Trash className="h-4 w-4 hover:text-destructive" />
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <FileText className="h-4 w-4" />
                      <span>{file_name}</span>
                    </div>

                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span>
                        {new Date(created_at).toLocaleDateString("en-GB")}
                      </span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function UploadDocButton({ className }: { className?: string }) {
  return (
    <Button
      variant="outline"
      className={cn("gap-2 text-white sm:w-auto", className)}
      asChild
    >
      <Link href="/documents/upload">
        <Upload className="h-4 w-4" />
        <span className="sm:inline">Upload a Document</span>
      </Link>
    </Button>
  );
}
