"use client";
import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Upload, Pencil, FileText, Trash2 } from "lucide-react";
import { fetchDocuments } from "@/network/fetch-documents";
import { useQuery } from "@tanstack/react-query";

import { cn } from "@/lib/utils";

export default function Page() {
  const { data, error, status } = useQuery({
    queryKey: ["documents"],
    queryFn: fetchDocuments
  });

  if (data?.data.length === 0) {
    return (
      <div className="flex h-dvh w-screen flex-col items-center justify-center space-y-4 lg:container lg:min-w-full">
        <p className="text-lg text-gray-400">
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
              type="search"
              placeholder="Search your uploaded documents...."
              className="bg-zinc-900 text-white placeholder:text-gray-400"
            />
          </div>

          {/* Document List */}

          <div className="grid w-full gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {data?.data.map(({ id, title, file_name, created_at }) => (
              <div
                key={id}
                className="mb-4 min-w-full rounded-lg border border-zinc-800 bg-zinc-900 p-4 transition-transform duration-200 hover:scale-105 hover:border-zinc-700"
              >
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
