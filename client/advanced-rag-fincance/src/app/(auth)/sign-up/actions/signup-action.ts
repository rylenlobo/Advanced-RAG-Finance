"use server";

import { signUpSchema } from "../schemas/signup-schema";
import { SignUpInput } from "../types/types";

import type { Result } from "@/app/(auth)/auth-types";
import { createClient } from "@/utils/supabase/server/server";

export async function signUpUser(data: SignUpInput): Promise<Result> {
  const parsed = signUpSchema.safeParse(data);
  if (!parsed.success) {
    return {
      success: false,
      message: "Validation error"
    };
  }

  const { firstName, lastName, email, password } = parsed.data;

  try {
    const supabase = await createClient();

    // const checkIfUserExistsByEmail = async (
    //   email: string
    // ): Promise<boolean> => {
    //   const { data, error } = await supabase.rpc("check_email_exists", {
    //     user_email: email
    //   });

    //   if (error) {
    //     console.error("Error checking user existence:", error);
    //     throw error;
    //   }

    //   return data;
    // };

    // const userExists = await checkIfUserExistsByEmail(email);
    // if (userExists) {
    //   return {
    //     success: false,
    //     message: "User with this email already exists."
    //   };
    // }

    const { error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          first_name: firstName,
          last_name: lastName
        }
      }
    });

    if (error) {
      return {
        success: false,
        message: error.message || "Failed to sign up user"
      };
    }

    console.log(data);
    return {
      success: true,
      message: "User signed up successfully"
    };
  } catch {
    return {
      success: false,
      message: "Unexpected error occurred"
    };
  }
}
