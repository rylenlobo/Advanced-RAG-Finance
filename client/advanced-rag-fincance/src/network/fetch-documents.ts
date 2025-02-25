import { supabase } from "@/utils/supabase/client/supabase-client";

type Document = {
  id: string;
  file_name: string;
  title: string;
  created_at: Date;
};

export async function fetchDocuments(): Promise<{ data: Document[] }> {
  const { data, error } = await supabase
    .from("documents")
    .select("*")
    .order("created_at", { ascending: true });

  if (error) {
    throw new Error("Failed to get documents");
  }

  return {
    data
  };
}
