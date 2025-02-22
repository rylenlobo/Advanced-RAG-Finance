import { supabase } from "@/utils/supabase/client/supabase-client";
import type { PreviousChatsList } from "../types/types";

export async function fetchPreviousChats({
  pageParam
}: {
  pageParam: number;
}): Promise<{ data: PreviousChatsList[]; nextId: number | null }> {
  const LIMIT = pageParam === 0 ? 22 : 10;

  // Fetch total conversation count
  const { count: totalCount, error: countError } = await supabase
    .from("conversations")
    .select("*", { count: "exact", head: true });

  if (countError) {
    console.error("Error fetching conversation count:", countError.message);
    throw new Error("Failed to fetch conversation count.");
  }

  const isDataAvailable = pageParam + LIMIT < (totalCount ?? 0);

  // Fetch paginated conversation data
  const { data, error } = await supabase
    .from("conversations")
    .select("*")

    .order("created_at", { ascending: true })
    .range(pageParam, pageParam + LIMIT - 1);

  if (error) {
    console.error("Error fetching conversations:", error.message);
    throw new Error("Failed to fetch conversations.");
  }

  return {
    data,
    nextId: isDataAvailable ? pageParam + LIMIT : null
  };
}
