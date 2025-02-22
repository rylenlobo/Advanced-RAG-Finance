"use server";

import { LoginInput } from "../types/types";

import type { Result } from "@/app/(auth)/auth-types";
import { createClient } from "@/utils/supabase/server/server";
import { loginSchema } from "../schemas/login-schema";

export async function signInUser(data: LoginInput): Promise<Result> {
  const parsed = loginSchema.safeParse(data);
  if (!parsed.success) {
    return {
      success: false,
      message: "Validation error"
    };
  }

  const { email, password } = parsed.data;

  try {
    const supabase = await createClient();

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password
    });

    if (error) {
      return {
        success: false,
        message: error.message || "Failed to login user"
      };
    }

    return {
      success: true,
      message: "User logged in successfully"
    };
  } catch {
    return {
      success: false,
      message: "Unexpected error occurred"
    };
  }
}
