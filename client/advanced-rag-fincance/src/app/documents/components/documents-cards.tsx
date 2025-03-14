"use client";
import { ConfirmDialog } from "@/components/ui/confirm-dialog";
import { cancelDocumentProcessing } from "@/network/cancel-document-processing";
import Link from "next/link";
import type { Document } from "@/network/fetch-documents";
import { toast } from "sonner";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { XCircle, FileText } from "lucide-react";

interface DocumentCardProps {
  document: Document;
  onSelect: (document: Document) => void;
}

export default function DocumentCard({
  document,
  onSelect
}: DocumentCardProps) {
  const {
    id = "",
    title = "",
    file_name = "",
    created_at = "",
    status = ""
  } = document;
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const queryClient = useQueryClient();

  const { mutate: cancelProcessing, isPending } = useMutation({
    mutationFn: (documentId: string) => cancelDocumentProcessing(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["documents"] });
    },
    onError: (error) => {
      toast.error(error?.message);
    }
  });

  const handleCancelClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setShowCancelConfirm(true);
  };

  const confirmCancel = () => {
    cancelProcessing(id);
    setShowCancelConfirm(false);
  };

  return (
    <>
      <Link key={id} href="/">
        <div
          onClick={() => onSelect(document)}
          className="group relative h-fit min-w-full rounded-xl border-2 border-zinc-800/50 bg-gradient-to-r from-zinc-900/50 to-zinc-800/30 p-6 transition-transform animate-in fade-in-25 hover:border-zinc-700/50 hover:bg-zinc-900/50 active:scale-95"
        >
          {/* Processing Overlay */}
          {status === "processing" && (
            <div
              className="absolute inset-0 flex items-center justify-center rounded-xl bg-black/50"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                className="flex flex-col items-center gap-2 text-white transition-colors group-hover:text-red-500"
                onClick={handleCancelClick}
              >
                <XCircle className="h-8 w-8" />
              </button>
            </div>
          )}

          {/* Document Details */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <h2 className="w-48 truncate text-lg font-medium text-primary transition-colors group-hover:text-muted-foreground">
                  {title}
                </h2>
              </div>

              {/* <Trash className="h-4 w-4 hover:text-destructive" /> */}
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <FileText className="h-4 w-4" />
              <span>{file_name}</span>
            </div>

            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>{new Date(created_at).toLocaleDateString("en-GB")}</span>
            </div>
          </div>
        </div>
      </Link>

      <ConfirmDialog
        open={showCancelConfirm}
        onOpenChange={setShowCancelConfirm}
        title="Cancel Document Processing"
        description="Are you sure you want to cancel processing this document? This action cannot be undone."
        confirmText={isPending ? "Cancelling..." : "Yes, cancel processing"}
        cancelText="No, continue processing"
        onConfirm={confirmCancel}
      />
    </>
  );
}
