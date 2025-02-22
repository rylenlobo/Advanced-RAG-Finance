import { signUpSchema } from "@/app/(auth)/sign-up/schemas/signup-schema";
import { z } from "zod";

export type SignUpInput = z.infer<typeof signUpSchema>;
