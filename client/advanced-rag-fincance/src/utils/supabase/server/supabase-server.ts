import { createClient } from "@/utils/supabase/server/server";

export const supabase = await createClient();
