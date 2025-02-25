import { supabase } from "@/utils/supabase/client/supabase-client";

type Messages = {
  data?: Date;
  content: string;
  role: string;
};

export async function fetchMessages(
  pageParam: number,
  conversation_id: string
): Promise<{ data: Messages[]; nextId: number | null }> {
  const LIMIT = 12;

  // Fetch total conversation count
  const { count: totalMessagesCount, error: countError } = await supabase
    .from("messages")
    .select("*", { count: "exact", head: true })
    .eq("conversation_id", conversation_id);

  if (countError) {
    throw new Error("Failed to fetch messages count.");
  }

  const isDataAvailable = pageParam + LIMIT < (totalMessagesCount ?? 0);

  // Fetch paginated conversation data
  const { data, error } = await supabase
    .from("messages")
    .select("*")
    .eq("conversation_id", conversation_id)
    .order("created_at", { ascending: false })
    .range(pageParam, pageParam + LIMIT - 1);

  if (error) {
    throw new Error("Failed to fetch messages.");
  }

  return {
    data,
    nextId: isDataAvailable ? pageParam + LIMIT : null
  };
}
