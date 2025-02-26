import { supabase } from "@/utils/supabase/client/supabase-client";

export type PreviousChatsList = {
  id: string;
  name: string;
  date?: Date;
  index: number;
};

export async function fetchPreviousChats(
  pageParam: number,
  doc_id: string | undefined
): Promise<{ data: PreviousChatsList[]; nextId: number | null }> {
  const LIMIT = pageParam === 0 ? 22 : 10;

  // Fetch total conversation count
  const { count: totalCount, error: countError } = await supabase
    .from("conversations")
    .select("*", { count: "exact", head: true });
  // .eq("document_id", doc_id);

  if (countError) {
    throw new Error("Failed to fetch conversation count.");
  }

  const isDataAvailable = pageParam + LIMIT < (totalCount ?? 0);

  // Fetch paginated conversation data
  const { data, error } = await supabase
    .from("conversations")
    .select("*")
    .eq("document_id", doc_id)
    .order("created_at", { ascending: true })
    .range(pageParam, pageParam + LIMIT - 1);

  if (error) {
    throw new Error("Failed to fetch conversations.");
  }

  return {
    data,
    nextId: isDataAvailable ? pageParam + LIMIT : null
  };
}
