"use client";
import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowRight, Loader } from "lucide-react";
import { fetchDocuments } from "@/network/fetch-documents";
import { useQuery } from "@tanstack/react-query";
import useDocumentStore from "@/store/currentDocStore";
import type { Document } from "@/network/fetch-documents";
import UploadFormDialog from "./components/upload-form-dialog";
import DocumentCard from "./components/documents-cards";

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
            placeholder="Search uploaded documents"
            className="h-12 w-full px-4 py-2"
          />
          <Button className="absolute right-2 top-1/2 h-8 w-8 -translate-y-1/2 rounded-md">
            <ArrowRight />
          </Button>
        </div>

        {/* Loading State */}
        {status === "pending" && (
          <div className="flex w-full flex-1 items-center justify-center">
            <Loader className="size-5 animate-spin" />
          </div>
        )}

        {/* Document List */}
        {status === "success" && (
          <div className="grid h-full w-full content-start gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {data?.data.map((document) => (
              <DocumentCard
                key={document.id}
                document={document}
                onSelect={handleSelectDocumentClick}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function UploadDocButton() {
  return <UploadFormDialog />;
}
