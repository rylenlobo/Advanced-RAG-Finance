import { z } from "zod";
import { loginSchema } from "../schemas/login-schema";

export type LoginInput = z.infer<typeof loginSchema>;
