import { supabase } from "@/utils/supabase/client/supabase-client";

export type Message = {
  data?: Date;
  content: string;
  role: string;
  id: string;
  isLoading?: boolean;
};

export async function fetchMessages(
  pageParam: number,
  conversation_id: string
): Promise<{ data: Message[]; nextId: number | null }> {
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
    .select("id,role,content")
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
