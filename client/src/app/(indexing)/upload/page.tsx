"use client";

import React, { useState, useCallback, useRef } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle
} from "@/components/ui/card";
import { toast } from "sonner";

import { X, Upload, CheckCircle } from "lucide-react";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);

  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const ALLOWED_FILE_TYPES = ["application/pdf"];

  const validateFile = (file: File) => {
    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
      setError("Invalid file type. Please upload a PDF file.");
      toast("Invalid file type. Please upload a PDF file.");
      return false;
    }
    return true;
  };

  const handleFile = (file: File) => {
    setError(null);
    if (validateFile(file)) {
      setFile(file);
      uploadFile(file);
    }
  };

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFile(droppedFile);
    }
  }, []);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFile(selectedFile);
    }
  };

  const removeFile = () => {
    setFile(null);
    setError(null);
    setIsUploading(false);
  };

  const uploadFile = (file: File) => {
    setIsUploading(true);
    const uploadPromise = new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/upload"); // Replace with your upload URL
      xhr.onload = () => {
        if (xhr.status === 200) {
          resolve({ name: file.name });
        } else {
          setError("Upload Failed");
          reject(new Error("Upload failed"));
        }
      };
      xhr.onerror = () => reject(new Error("Upload failed"));
      const formData = new FormData();
      formData.append("file", file);
      xhr.send(formData);
    });

    toast.promise(uploadPromise, {
      loading: "Uploading...",
      success: (data) => {
        setIsUploading(false);
        return `${data.name} uploaded successfully`;
      },
      error: "Upload failed"
    });
  };

  return (
    <div className="h-dvh w-dvh flex items-center justify-center">
      <Card className="w-full max-w-md mx-auto ">
        <CardHeader className="text-center">
          <CardTitle>Upload your Financial Document</CardTitle>
        </CardHeader>
        <CardContent className="text-center pb-0">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center ${
              isDragging ? "border-primary bg-primary/10" : "border-gray-300"
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {file ? (
              <div className="flex items-center justify-between">
                <span className="text-sm truncate flex-1">{file.name}</span>
                <Button variant="ghost" size="icon" onClick={removeFile}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <>
                <Upload className="mx-auto h-12 w-12 text-gray-400" />
                <p className="mt-2 text-sm text-gray-500">
                  Drag and drop your file here, or click to select a file
                </p>
                <p className="mt-1 text-xs text-gray-400">Allowed types: PDF</p>
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileInput}
                  accept={ALLOWED_FILE_TYPES.join(",")}
                />
                <Button
                  variant="outline"
                  className="mt-5"
                  onClick={() => fileInputRef.current?.click()}
                >
                  Select File
                </Button>
                <input
                  type="file"
                  className="hidden"
                  ref={fileInputRef}
                  onChange={handleFileInput}
                  accept={ALLOWED_FILE_TYPES.join(",")}
                />
              </>
            )}
          </div>
        </CardContent>
        <CardFooter className="flex justify-between">
          {error && <p className="text-sm text-red-500">{error}</p>}
          {file && !error && (
            <p className="text-sm text-green-500 flex items-center mx-auto mt-5 ">
              <CheckCircle className="h-4 w-4 mr-2" />
              {isUploading ? "Upload in Progress" : "Done"}
            </p>
          )}
        </CardFooter>
      </Card>
    </div>
  );
}
