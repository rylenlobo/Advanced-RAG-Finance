"use client";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";

import { useRouter } from "next/navigation";
import UploadForm from "../components/upload-form";

export default function UploadFormDialog() {
  const router = useRouter();

  function handleOpenChange() {
    router.back();
  }

  return (
    <>
      <Dialog defaultOpen={true} open={true} onOpenChange={handleOpenChange}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload File</DialogTitle>
            <DialogDescription>
              Upload a document to start chatting. Click &quot;Upload&quot; when
              done. The upload may take a few minutes, depending on the
              document.
            </DialogDescription>
            <UploadForm />
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </>
  );
}
