import { z } from "zod";

export const documentUploadSchema = z.object({
  title: z.string().min(1, { message: "Title is required" }),
  file:
    typeof window === "undefined"
      ? z.any()
      : z
          .instanceof(FileList)
          .nullable()
          .refine((file) => file !== null && file.length === 1, {
            message: "File is required"
          })
          .refine(
            (file) => {
              const allowedTypes = ["application/pdf"];
              return file !== null && allowedTypes.includes(file[0].type);
            },
            { message: "Invalid file type" }
          )
});
