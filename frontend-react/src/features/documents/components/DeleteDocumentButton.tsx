
import { useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  LoaderCircle,
  Trash2,
  X,
} from "lucide-react";

import { ApiError } from "../../../lib/api";
import {
  deleteDocument,
  type DocumentItem,
} from "../api/documentsApi";

type DeleteDocumentButtonProps = {
  document: DocumentItem;
};

function getDeleteErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
        return "Your session has expired. Please sign out and sign in again.";

      case 403:
        return "You do not have permission to delete documents.";

      case 404:
        return "This document no longer exists. Refresh the document list.";

      case 409:
        return error.message;

      default:
        return error.message;
    }
  }

  if (error instanceof TypeError) {
    return "Unable to connect to the server. Please check your connection.";
  }

  return error instanceof Error
    ? error.message
    : "Unable to delete the document. Please try again.";
}

export default function DeleteDocumentButton({
  document,
}: DeleteDocumentButtonProps) {
  const queryClient = useQueryClient();

  const [isOpen, setIsOpen] = useState(false);

  const titleId = useId();
  const descriptionId = useId();

  const triggerRef = useRef<HTMLButtonElement>(null);
  const cancelRef = useRef<HTMLButtonElement>(null);
  const dialogRef = useRef<HTMLDivElement>(null);

  const deleteMutation = useMutation({
    mutationFn: () => deleteDocument(document.document_id),

    onSuccess: async () => {
      setIsOpen(false);

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

  function openDialog() {
    deleteMutation.reset();
    setIsOpen(true);
  }

  function closeDialog() {
    if (deleteMutation.isPending) return;

    setIsOpen(false);
    triggerRef.current?.focus();
  }

  useEffect(() => {
    if (!isOpen) return;

    const previousOverflow =
      window.document.body.style.overflow;

    const previousFocus =
      window.document.activeElement instanceof HTMLElement
        ? window.document.activeElement
        : null;

    window.document.body.style.overflow = "hidden";

    cancelRef.current?.focus();

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        if (!deleteMutation.isPending) {
          event.preventDefault();
          setIsOpen(false);
        }

        return;
      }

      if (event.key !== "Tab") return;

      const dialog = dialogRef.current;

      if (!dialog) return;

      const focusableElements = Array.from(
        dialog.querySelectorAll<HTMLButtonElement>(
          "button:not(:disabled)",
        ),
      );

      if (focusableElements.length === 0) {
        event.preventDefault();
        return;
      }

      const first = focusableElements[0];
      const last = focusableElements[focusableElements.length - 1];

      if (
        event.shiftKey &&
        window.document.activeElement === first
      ) {
        event.preventDefault();
        last.focus();
      } else if (
        !event.shiftKey &&
        window.document.activeElement === last
      ) {
        event.preventDefault();
        first.focus();
      }
    }

    window.document.addEventListener(
      "keydown",
      handleKeyDown,
    );

    return () => {
      window.document.body.style.overflow = previousOverflow;

      window.document.removeEventListener(
        "keydown",
        handleKeyDown,
      );

      if (previousFocus?.isConnected) {
        previousFocus.focus();
      }
    };
  }, [isOpen, deleteMutation.isPending]);

  return (
    <>
      {/* Delete trigger */}
      <button
        ref={triggerRef}
        type="button"
        onClick={openDialog}
        aria-label={`Delete ${document.filename}`}
        title={`Delete ${document.filename}`}
        className="
          inline-flex h-9 w-9 items-center justify-center
          rounded-lg
          text-[var(--app-text-muted)]
          transition-colors duration-200
          hover:bg-red-500/10 hover:text-red-500
          focus-visible:outline-2
          focus-visible:outline-offset-2
          focus-visible:outline-red-500
        "
      >
        <Trash2 className="h-4 w-4" aria-hidden="true" />
      </button>

      {isOpen &&
        createPortal(
          <div
            className="
              fixed inset-0 z-[100]
              flex items-center justify-center
              bg-slate-950/70 p-4
              backdrop-blur-[3px]
            "
            onMouseDown={(event) => {
              if (event.target === event.currentTarget) {
                closeDialog();
              }
            }}
          >
            <div
              ref={dialogRef}
              role="dialog"
              aria-modal="true"
              aria-labelledby={titleId}
              aria-describedby={descriptionId}
              className="
                w-full max-w-[440px]
                rounded-2xl
                border border-[var(--app-border)]
                bg-[var(--app-surface)]
                p-5 shadow-2xl
                sm:p-7
              "
            >
              {/* Header */}
              <div className="flex items-start justify-between gap-4">
                <div
                  className="
                    flex h-12 w-12 shrink-0
                    items-center justify-center
                    rounded-2xl bg-red-500/10
                    text-red-500
                  "
                >
                  <Trash2
                    className="h-6 w-6"
                    aria-hidden="true"
                  />
                </div>

                <button
                  type="button"
                  onClick={closeDialog}
                  disabled={deleteMutation.isPending}
                  aria-label="Close confirmation"
                  className="
                    inline-flex h-9 w-9
                    items-center justify-center
                    rounded-lg
                    text-[var(--app-text-muted)]
                    transition-colors
                    hover:bg-slate-500/10
                    hover:text-[var(--app-text)]
                    disabled:opacity-50
                  "
                >
                  <X className="h-5 w-5" aria-hidden="true" />
                </button>
              </div>

              {/* Confirmation details */}
              <h2
                id={titleId}
                className="
                  mt-5 text-xl font-semibold
                  tracking-tight text-[var(--app-text)]
                "
              >
                Delete document?
              </h2>

              <p
                id={descriptionId}
                className="
                  mt-2 text-sm leading-6
                  text-[var(--app-text-muted)]
                "
              >
                You are about to permanently delete the following
                document from your knowledge base.
              </p>

              {/* Selected document */}
              <div
                className="
                  mt-5 rounded-xl
                  border border-[var(--app-border)]
                  bg-[var(--app-bg)]
                  p-4
                "
              >
                <p className="text-xs font-medium text-[var(--app-text-muted)]">
                  Selected document
                </p>

                <p
                  className="
                    mt-1 break-all text-sm
                    font-semibold text-[var(--app-text)]
                  "
                >
                  {document.filename}
                </p>

                <p className="mt-2 text-xs text-[var(--app-text-muted)]">
                  {document.chunk_count.toLocaleString("en-IN")}{" "}
                  {document.chunk_count === 1
                    ? "recorded chunk"
                    : "recorded chunks"}
                </p>
              </div>

              {/* Warning */}
              <div
                className="
                  mt-4 flex items-start gap-3
                  rounded-xl
                  border border-amber-500/20
                  bg-amber-500/10
                  p-3.5
                "
              >
                <AlertTriangle
                  className="
                    mt-0.5 h-4 w-4 shrink-0
                    text-amber-500
                  "
                  aria-hidden="true"
                />

                <p className="text-xs leading-5 text-[var(--app-text-muted)]">
                  This action cannot be undone. The document and its
                  associated searchable content will be removed.
                </p>
              </div>

              {/* Error */}
              {deleteMutation.isError && (
                <div
                  role="alert"
                  className="
                    mt-4 flex items-start gap-2
                    rounded-xl
                    border border-red-500/20
                    bg-red-500/10
                    p-3 text-sm
                    text-red-600 dark:text-red-400
                  "
                >
                  <AlertTriangle
                    className="mt-0.5 h-4 w-4 shrink-0"
                    aria-hidden="true"
                  />

                  <span>
                    {getDeleteErrorMessage(
                      deleteMutation.error,
                    )}
                  </span>
                </div>
              )}

              {/* Actions */}
              <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
                <button
                  ref={cancelRef}
                  type="button"
                  onClick={closeDialog}
                  disabled={deleteMutation.isPending}
                  className="
                    inline-flex min-h-11
                    items-center justify-center
                    rounded-xl
                    border border-[var(--app-border)]
                    bg-[var(--app-surface)]
                    px-5 py-2.5
                    text-sm font-semibold
                    text-[var(--app-text)]
                    transition-colors
                    hover:bg-blue-500/5
                    focus-visible:outline-2
                    focus-visible:outline-blue-500
                    disabled:opacity-50
                  "
                >
                  Cancel
                </button>

                <button
                  type="button"
                  onClick={() => deleteMutation.mutate()}
                  disabled={deleteMutation.isPending}
                  className="
                    inline-flex min-h-11
                    items-center justify-center gap-2
                    rounded-xl
                    bg-red-600 px-5 py-2.5
                    text-sm font-semibold text-white
                    transition-colors
                    hover:bg-red-700
                    focus-visible:outline-2
                    focus-visible:outline-red-500
                    disabled:cursor-not-allowed
                    disabled:opacity-60
                  "
                >
                  {deleteMutation.isPending ? (
                    <LoaderCircle
                      className="h-4 w-4 animate-spin"
                      aria-hidden="true"
                    />
                  ) : (
                    <Trash2
                      className="h-4 w-4"
                      aria-hidden="true"
                    />
                  )}

                  {deleteMutation.isPending
                    ? "Deleting..."
                    : "Delete document"}
                </button>
              </div>
            </div>
          </div>,
          window.document.body,
        )}
    </>
  );
}
