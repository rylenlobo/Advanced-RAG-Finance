"use client";

import React from "react";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage
} from "@/components/ui/form";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { documentUploadSchema } from "@/app/documents/schemas/file-upload-schema";
import { z } from "zod";
import { supabase } from "@/utils/supabase/client/supabase-client";
import { uploadProcessDocument } from "@/network/upload-process-document";
import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";
import { Loader } from "lucide-react";

export default function UploadForm() {
  const { mutate, status, error } = useMutation({
    mutationFn: uploadProcessDocument,
    onError: () => {
      toast.error(
        error?.message ||
          "An unexpected error occurred while processing the documents"
      );
    }
  });

  const form = useForm<z.infer<typeof documentUploadSchema>>({
    resolver: zodResolver(documentUploadSchema),
    defaultValues: {
      title: "",
      file: null
    }
  });

  const { formState } = form;
  const fileRef = form.register("file");

  async function onSubmit(values: z.infer<typeof documentUploadSchema>) {
    const {
      data: { user }
    } = await supabase.auth.getUser();

    const formData = new FormData();

    if (values.file && values.file.length > 0) {
      formData.append("file", values.file[0]);
    }

    formData.append("title", values.title);

    if (user) {
      formData.append("user_id", user.id);
    }

    mutate(formData);
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <div className="mt-2 flex flex-col justify-start gap-6 text-left">
          <FormField
            control={form.control}
            name="title"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Title</FormLabel>
                <FormControl>
                  <Input
                    placeholder="A title describing the document"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="file"
            render={() => (
              <FormItem>
                <FormLabel>File</FormLabel>
                <FormControl>
                  <Input type="file" placeholder="Upload a PDF" {...fileRef} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <Button
            type="submit"
            className="mt-2"
            disabled={
              !formState.isValid ||
              formState.isSubmitting ||
              status === "pending"
            }
          >
            {status === "pending" && <Loader className="mr-2 animate-spin" />}
            Upload File
          </Button>
        </div>
      </form>
    </Form>
  );
}
