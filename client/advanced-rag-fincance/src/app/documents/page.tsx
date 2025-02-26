"use client";
import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Upload, FileText, Trash2, ArrowRight } from "lucide-react";
import { fetchDocuments } from "@/network/fetch-documents";
import { useQuery } from "@tanstack/react-query";

import { cn } from "@/lib/utils";
import useDocumentStore from "@/store/currentDocStore";
import Link from "next/link";
import type { Document } from "@/network/fetch-documents";

export default function Page() {
  const { setSelectedDocument } = useDocumentStore();

  const handleSelectDocumentClick = (document: Document) => {
    setSelectedDocument(document);
  };

  const { data, error, status } = useQuery({
    queryKey: ["documents"],
    queryFn: fetchDocuments
  });

  if (data?.data.length === 0) {
    return (
      <div className="flex h-dvh w-screen flex-col items-center justify-center space-y-4 lg:container lg:min-w-full">
        <p className="text-center text-lg text-gray-400">
          No RAGed documents found. Upload your first document to get started!
        </p>
        <UploadDocButton />
      </div>
    );
  }

  return (
    <div className="h-dvh w-screen lg:container lg:min-w-full">
      <div className="min-h-full bg-black p-4 md:p-6">
        <div className="mx-auto w-full max-w-4xl space-y-4 md:space-y-6">
          {/* Header */}
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
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
          {/* Document List */}

          <div className="grid w-full gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {data?.data.map(({ id, title, file_name, created_at }) => (
              <div
                onClick={() =>
                  handleSelectDocumentClick({
                    id,
                    title,
                    file_name,
                    created_at
                  })
                }
                key={id}
                className="min-w-full rounded-lg border border-input bg-background p-4 transition-colors hover:bg-accent hover:text-accent-foreground"
              >
                <Link href="/">
                  <div className="space-y-2">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <h2 className="text-lg font-medium text-white">
                          {title}
                        </h2>
                      </div>
                      <button className="text-gray-400 hover:text-red-500">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <FileText className="h-4 w-4" />
                      <span>{file_name}</span>
                    </div>

                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <span>
                        {new Date(created_at).toLocaleDateString("en-GB")}
                      </span>
                    </div>
                  </div>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function UploadDocButton({ className }: { className?: string }) {
  return (
    <Button
      variant="outline"
      className={cn("w-full gap-2 text-white sm:w-auto", className)}
    >
      <Upload className="h-4 w-4" />
      <span className="sm:inline">Upload a Document</span>
    </Button>
  );
}
