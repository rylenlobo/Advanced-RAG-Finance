import { z } from "zod";

export const documentUploadSchema = z.object({
  title: z.string().min(1, { message: "Title is required" }),
  file:
    typeof window === "undefined"
      ? z.any()
      : z
          .instanceof(FileList)
          .nullable()
          .refine((file) => file !== null && file.length > 0, {
            message: "File is required"
          })
          .refine((file) => file && file.length === 1, {
            message: "Please upload only one file"
          })
          .refine(
            (file) => {
              if (!file || !file[0]) return false;
              const allowedTypes = ["application/pdf"];
              return allowedTypes.includes(file[0].type);
            },
            { message: "Invalid file type" }
          )
});
