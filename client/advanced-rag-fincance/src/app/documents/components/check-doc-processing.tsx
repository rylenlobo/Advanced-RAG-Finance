"use client";

import React, { useEffect } from "react";
import { supabase } from "@/utils/supabase/client/supabase-client";
import { toast } from "sonner";
import { Loader } from "lucide-react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import useModalStore from "@/store/modalStore";
import { Document } from "@/network/fetch-documents";

// Separate function for fetching processing documents
const fetchProcessingDocuments = async (): Promise<Document[]> => {
  const { data, error } = await supabase
    .from("documents")
    .select("id,title,status")
    .eq("status", "processing");

  if (error) {
    throw new Error(error.message);
  }

  return data || [];
};

export const CheckDocProcessing: React.FC = () => {
  const { toggleUploadDialog } = useModalStore();
  const queryClient = useQueryClient();

  const { data, status } = useQuery({
    queryKey: ["processingDocuments"],
    queryFn: () => fetchProcessingDocuments()
  });

  useEffect(() => {
    if (status === "success") {
      data?.forEach((doc) => {
        if (doc.status === "processing") {
          toast.info(
            <div className="flex items-center gap-2">
              <Loader className="h-4 w-4 animate-spin" />
              <span>{doc.title} is currently being processed</span>
            </div>,
            {
              id: doc.id,
              duration: 5000,
              position: "bottom-right"
            }
          );
        }
      });
    }

    supabase
      .channel("document-status-changes")
      .on(
        "postgres_changes",
        {
          event: "*",
          schema: "public",
          table: "documents"
        },
        (payload) => {
          const doc = payload.new as Document;
          if (doc) {
            queryClient.invalidateQueries({ queryKey: ["documents"] });
            if (doc.status === "processing") {
              toggleUploadDialog();
              toast.info(
                <div className="flex items-center gap-2">
                  <Loader className="h-4 w-4 animate-spin" />
                  <span>
                    <strong>{doc.title}</strong> is currently being processed
                  </span>
                </div>,
                {
                  id: doc.id,
                  duration: 5000,
                  position: "bottom-right"
                }
              );
            }
            if (doc.status === "processed") {
              toast.success(
                <span>
                  Your document <strong>{doc.title}</strong> has been processed
                  successfully you can now chat with your document
                </span>,
                {
                  id: doc.id,
                  duration: 5000,
                  position: "bottom-right"
                }
              );
            }
          }
        }
      )
      .subscribe();

    return () => {
      supabase.channel("document-status-changes").unsubscribe();
    };
  }, [data, status, queryClient, , toggleUploadDialog]);

  return null;
};
