"use client";
import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Upload, Pencil, FileText, Trash2 } from "lucide-react";
import { fetchDocuments } from "@/network/fetch-documents";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";

export default function Page() {
  const { data, errror, status } = useQuery({
    queryKey: ["documents"],
    queryFn: fetchDocuments
  });

  return (
    <div className="container h-screen min-w-full">
      <div className="min-h-full bg-black p-4 md:p-6">
        <div className="mx-auto max-w-4xl space-y-4 md:space-y-6">
          {/* Header */}
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <h1 className="text-xl font-semibold text-white md:text-2xl">
              RAG Documents
            </h1>
            <Button
              variant="outline"
              className="w-full gap-2 text-white sm:w-auto"
            >
              <Upload className="h-4 w-4" />
              <span className="sm:inline">Upload a Document</span>
            </Button>
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
          <div>
            {data?.data.map(
              ({ id, title, description, file_name, created_at }) => (
                <Link key={id} href={`/?doc_id=${id}`}>
                  <div className="mb-4 rounded-lg border border-zinc-800 bg-zinc-900 p-4">
                    <div className="space-y-2">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          <h2 className="text-lg font-medium text-white">
                            {title}
                          </h2>
                          <button className="text-gray-400 hover:text-white">
                            <Pencil className="h-4 w-4" />
                          </button>
                        </div>
                        <button className="text-gray-400 hover:text-red-500">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-400">
                        <FileText className="h-4 w-4" />
                        <span>{file_name}</span>
                      </div>
                      <p className="h-10 truncate text-sm text-gray-300">
                        {description}
                      </p>
                      <div className="flex items-center gap-2 text-sm text-gray-400">
                        <span>
                          {new Date(created_at).toLocaleDateString("en-GB")}
                        </span>
                      </div>
                    </div>
                  </div>
                </Link>
              )
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
