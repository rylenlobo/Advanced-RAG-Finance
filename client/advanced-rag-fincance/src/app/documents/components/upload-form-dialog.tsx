"use client";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from "@/components/ui/dialog";

import UploadForm from "../components/upload-form";
import { Button } from "@/components/ui/button";
import { Upload } from "lucide-react";
import useModalStore from "@/store/modalStore";

export default function UploadFormDialog() {
  const { isUploadDialogOpen, openUploadDialog, closeUploadDialog } =
    useModalStore();

  return (
    <>
      <Dialog
        open={isUploadDialogOpen}
        onOpenChange={(open) =>
          open ? openUploadDialog() : closeUploadDialog()
        }
      >
        <DialogTrigger asChild>
          <Button
            variant="outline"
            className="gap-2 text-white sm:w-auto"
            onClick={openUploadDialog}
          >
            <Upload className="h-4 w-4" />
            <span className="sm:inline">Upload a Document</span>
          </Button>
        </DialogTrigger>
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
