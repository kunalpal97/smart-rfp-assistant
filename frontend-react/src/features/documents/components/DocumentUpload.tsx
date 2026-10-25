
import { useRef, useState } from "react";
import type { ChangeEvent, DragEvent, KeyboardEvent } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  CheckCircle2,
  CloudUpload,
  FileText,
  LoaderCircle,
  Upload,
  X,
} from "lucide-react";

import { ApiError } from "../../../lib/api";
import { uploadDocument } from "../api/documentsApi";

const MAX_FILE_SIZE = 10 * 1024 * 1024;

const ALLOWED_EXTENSIONS = [".pdf", ".txt", ".md"];

function validateFile(file: File): string | null {
  const extension = file.name
    .slice(file.name.lastIndexOf("."))
    .toLowerCase();

  if (!ALLOWED_EXTENSIONS.includes(extension)) {
    return "Unsupported file type. Please select a PDF, TXT or MD document.";
  }

  if (file.size === 0) {
    return "This file is empty. Please select a document containing content.";
  }

  if (file.size > MAX_FILE_SIZE) {
    return "File size must not exceed 10 MB.";
  }

  return null;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function getUploadErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 400:
      case 409:
      case 422:
        return error.message;

      case 401:
        return "Your session has expired. Please sign out and sign in again.";

      case 403:
        return "Only authorized administrators can upload documents.";

      case 413:
        return "The selected file exceeds the server's upload size limit.";

      default:
        return error.message;
    }
  }

  if (error instanceof TypeError) {
    return "Unable to connect to the backend. Please check your connection.";
  }

  return error instanceof Error
    ? error.message
    : "Document upload failed. Please try again.";
}

export default function DocumentUpload() {
  const inputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const uploadMutation = useMutation({
    mutationFn: uploadDocument,

    onSuccess: async (result) => {
      setSuccessMessage(
        `${result.original_filename} uploaded successfully. ` +
          `${result.chunks_created} document chunks were created.`,
      );

      setSelectedFile(null);
      setValidationError(null);

      if (inputRef.current) {
        inputRef.current.value = "";
      }

      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: ["documents"],
        }),
        queryClient.invalidateQueries({
          queryKey: ["dashboard", "overview"],
        }),
      ]);
    },
  });

  function selectFile(file: File | null) {
    if (uploadMutation.isPending) return;

    setValidationError(null);
    setSuccessMessage(null);
    uploadMutation.reset();

    if (!file) {
      setSelectedFile(null);
      return;
    }

    const error = validateFile(file);

    if (error) {
      setSelectedFile(null);
      setValidationError(error);

      if (inputRef.current) {
        inputRef.current.value = "";
      }

      return;
    }

    setSelectedFile(file);
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    selectFile(event.target.files?.[0] ?? null);
  }

  function handleDragOver(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();

    if (!uploadMutation.isPending) {
      setIsDragging(true);
    }
  }

  function handleDragLeave(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();

    if (!event.currentTarget.contains(event.relatedTarget as Node)) {
      setIsDragging(false);
    }
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);

    if (uploadMutation.isPending) return;

    const files = event.dataTransfer.files;

    if (files.length > 1) {
      setSelectedFile(null);
      setSuccessMessage(null);
      uploadMutation.reset();
      setValidationError("Please upload one document at a time.");
      return;
    }

    selectFile(files[0] ?? null);
  }

  function handleDropzoneKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();

      if (!uploadMutation.isPending) {
        inputRef.current?.click();
      }
    }
  }

  function clearSelection() {
    if (uploadMutation.isPending) return;

    setSelectedFile(null);
    setValidationError(null);
    setSuccessMessage(null);
    uploadMutation.reset();

    if (inputRef.current) {
      inputRef.current.value = "";
    }
  }

  function handleUpload() {
    if (!selectedFile || uploadMutation.isPending) return;

    setValidationError(null);
    setSuccessMessage(null);

    uploadMutation.mutate(selectedFile);
  }

  return (
    <section className="rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] p-5 shadow-sm sm:p-6">
      {/* Header */}
      <div className="flex items-start gap-3">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-500/10 text-blue-500">
          <CloudUpload className="h-5 w-5" aria-hidden="true" />
        </div>

        <div className="min-w-0">
          <h2 className="text-base font-semibold text-[var(--app-text)]">
            Add knowledge sources
          </h2>

          <p className="mt-1 text-sm leading-6 text-[var(--app-text-muted)]">
            Upload reference documents to expand the knowledge available
            to your AI Assistant.
          </p>
        </div>
      </div>

      {/* Native file input */}
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.txt,.md"
        onChange={handleFileChange}
        disabled={uploadMutation.isPending}
        aria-label="Select a knowledge document"
        className="sr-only"
      />

      {/* Dropzone */}
      <div
        role="button"
        tabIndex={uploadMutation.isPending ? -1 : 0}
        aria-label="Choose or drop a document"
        aria-disabled={uploadMutation.isPending}
        onClick={() => {
          if (!uploadMutation.isPending) {
            inputRef.current?.click();
          }
        }}
        onKeyDown={handleDropzoneKeyDown}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`
          mt-6 flex min-h-[210px] flex-col
          items-center justify-center
          rounded-2xl border-2 border-dashed
          px-5 py-8 text-center
          transition-[background-color,border-color]
          duration-200
          focus-visible:outline-2
          focus-visible:outline-offset-2
          focus-visible:outline-blue-500
          ${
            uploadMutation.isPending
              ? "cursor-not-allowed opacity-60"
              : "cursor-pointer"
          }
          ${
            isDragging
              ? "border-blue-500 bg-blue-500/10"
              : "border-[var(--app-border)] bg-[var(--app-bg)] hover:border-blue-500/50 hover:bg-blue-500/5"
          }
        `}
      >
        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-500/10 text-blue-500">
          <CloudUpload className="h-7 w-7" aria-hidden="true" />
        </div>

        <p className="mt-4 text-sm font-semibold text-[var(--app-text)]">
          Drag and drop a document here
        </p>

        <p className="mt-1 text-xs text-[var(--app-text-muted)]">
          or click to browse your files
        </p>

        <span className="mt-4 rounded-full border border-[var(--app-border)] bg-[var(--app-surface)] px-3 py-1.5 text-xs font-medium text-[var(--app-text-muted)]">
          PDF, TXT, MD · Maximum 10 MB
        </span>
      </div>

      {/* Selected file */}
      {selectedFile && (
        <div className="mt-4 flex min-w-0 items-center gap-3 rounded-xl border border-blue-500/20 bg-blue-500/5 p-3.5">
          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-500/10 text-blue-500">
            <FileText className="h-5 w-5" aria-hidden="true" />
          </div>

          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-semibold text-[var(--app-text)]">
              {selectedFile.name}
            </p>

            <p className="mt-1 text-xs text-[var(--app-text-muted)]">
              {formatFileSize(selectedFile.size)}
              {uploadMutation.isPending
                ? " · Uploading and processing..."
                : " · Ready to upload"}
            </p>
          </div>

          {uploadMutation.isPending ? (
            <LoaderCircle
              className="h-5 w-5 shrink-0 animate-spin text-blue-500"
              aria-label="Uploading"
            />
          ) : (
            <button
              type="button"
              onClick={clearSelection}
              aria-label={`Remove ${selectedFile.name}`}
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-[var(--app-text-muted)] transition-colors hover:bg-red-500/10 hover:text-red-500"
            >
              <X className="h-4 w-4" aria-hidden="true" />
            </button>
          )}
        </div>
      )}

      {/* Validation error */}
      {validationError && (
        <div
          role="alert"
          className="mt-4 flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-500/10 p-3.5 text-sm text-red-600 dark:text-red-400"
        >
          <AlertCircle
            className="mt-0.5 h-4 w-4 shrink-0"
            aria-hidden="true"
          />
          <span>{validationError}</span>
        </div>
      )}

      {/* API error */}
      {uploadMutation.isError && (
        <div
          role="alert"
          className="mt-4 flex items-start gap-3 rounded-xl border border-red-500/20 bg-red-500/10 p-3.5 text-sm text-red-600 dark:text-red-400"
        >
          <AlertCircle
            className="mt-0.5 h-4 w-4 shrink-0"
            aria-hidden="true"
          />
          <span>{getUploadErrorMessage(uploadMutation.error)}</span>
        </div>
      )}

      {/* Success */}
      {successMessage && (
        <div
          role="status"
          className="mt-4 flex items-start gap-3 rounded-xl border border-teal-500/20 bg-teal-500/10 p-3.5 text-sm text-teal-600 dark:text-teal-400"
        >
          <CheckCircle2
            className="mt-0.5 h-4 w-4 shrink-0"
            aria-hidden="true"
          />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Footer */}
      <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs leading-5 text-[var(--app-text-muted)]">
          One document per upload. Processing time depends on file content.
        </p>

        <button
          type="button"
          onClick={handleUpload}
          disabled={!selectedFile || uploadMutation.isPending}
          className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {uploadMutation.isPending ? (
            <LoaderCircle
              className="h-4 w-4 animate-spin"
              aria-hidden="true"
            />
          ) : (
            <Upload className="h-4 w-4" aria-hidden="true" />
          )}

          {uploadMutation.isPending
            ? "Processing document..."
            : "Upload document"}
        </button>
      </div>
    </section>
  );
}
