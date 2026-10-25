
import { useEffect, useRef, useState } from "react";
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

import {
  AlertCircle,
  ArrowLeft,
  CalendarDays,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  ClipboardCopy,
  FileText,
  Image as ImageIcon,
  LoaderCircle,
  RefreshCw,
  ShieldAlert,
  Table2,
  Trash2,
  X,
} from "lucide-react";

import { ApiError } from "../../../lib/api";
import {
  deleteHistoryEntry,
  getHistoryDetail,
  type HistorySource,
} from "../api/historyApi";

interface HistoryDetailProps {
  historyId: string;
  onBack: () => void;
}

const EVIDENCE_PREVIEW_LENGTH = 500;

function formatDate(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Unknown date";
  }

  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 401:
        return "Your Microsoft session has expired. Please sign in again.";
      case 403:
        return "You do not have permission to perform this action.";
      case 404:
        return "This saved answer was not found. It may have been deleted.";
      case 500:
      case 502:
      case 503:
        return "The history service is temporarily unavailable.";
      default:
        return error.message;
    }
  }

  return error instanceof Error
    ? error.message
    : "An unexpected error occurred.";
}

function getCitationIndex(
  label: string,
  sources: HistorySource[]
): number {
  const normalized = label.trim().toLowerCase();

  const directMatch = sources.findIndex(
    (source) =>
      source.source_id?.trim().toLowerCase() === normalized
  );

  if (directMatch !== -1) {
    return directMatch;
  }

  const match = normalized.match(/^source\s+(\d+)$/);

  if (match) {
    const index = Number(match[1]) - 1;

    if (index >= 0 && index < sources.length) {
      return index;
    }
  }

  return -1;
}

function CitationButton({
  label,
  onClick,
}: {
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={`View evidence for ${label}`}
      className="mx-0.5 inline-flex items-center rounded-md border border-blue-500/20 bg-blue-500/10 px-1.5 py-0.5 align-baseline text-xs font-semibold text-blue-600 transition-colors hover:border-blue-500/50 hover:bg-blue-500/20 focus-visible:outline-2 focus-visible:outline-blue-500 dark:text-blue-400"
    >
      {label}
    </button>
  );
}

function MarkdownContent({
  content,
  sources,
  onCitationClick,
}: {
  content: string;
  sources: HistorySource[];
  onCitationClick: (index: number) => void;
}) {
  // Convert citation markers into Markdown links.
  // The link renderer below turns only these special links
  // into buttons. Normal links retain their usual behavior.
  const linkedContent = content.replace(
    /\[(Source\s+\d+)\](?!\()/gi,
    (_, label: string) => {
      const index = getCitationIndex(label, sources);

      if (index === -1) {
        return `[${label}]`;
      }

      return `[${label}](#history-source-${index})`;
    }
  );

  return (
    <div className="min-w-0 break-words text-sm leading-7 text-[var(--app-text)]">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => (
            <h2 className="mb-3 mt-6 text-xl font-semibold text-[var(--app-text)]">
              {children}
            </h2>
          ),
          h2: ({ children }) => (
            <h3 className="mb-3 mt-6 text-lg font-semibold text-[var(--app-text)]">
              {children}
            </h3>
          ),
          h3: ({ children }) => (
            <h4 className="mb-2 mt-5 text-base font-semibold text-[var(--app-text)]">
              {children}
            </h4>
          ),
          p: ({ children }) => (
            <p className="my-3 leading-7">{children}</p>
          ),
          strong: ({ children }) => (
            <strong className="font-semibold text-[var(--app-text)]">
              {children}
            </strong>
          ),
          ul: ({ children }) => (
            <ul className="my-3 list-disc space-y-2 pl-6">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="my-3 list-decimal space-y-2 pl-6">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="pl-1">{children}</li>
          ),
          blockquote: ({ children }) => (
            <blockquote className="my-4 border-l-4 border-blue-500 bg-blue-500/5 py-2 pl-4 text-[var(--app-text-muted)]">
              {children}
            </blockquote>
          ),
          hr: () => (
            <hr className="my-5 border-[var(--app-border)]" />
          ),
          a: ({ href, children }) => {
            const citationMatch = href?.match(
              /^#history-source-(\d+)$/
            );

            if (citationMatch) {
              const index = Number(citationMatch[1]);

              return (
                <CitationButton
                  label={String(children)}
                  onClick={() => onCitationClick(index)}
                />
              );
            }

            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-blue-600 underline underline-offset-2 hover:text-blue-500 dark:text-blue-400"
              >
                {children}
              </a>
            );
          },
          table: ({ children }) => (
            <div className="my-4 overflow-x-auto rounded-lg border border-[var(--app-border)]">
              <table className="min-w-full text-left text-sm">
                {children}
              </table>
            </div>
          ),
          th: ({ children }) => (
            <th className="border-b border-[var(--app-border)] bg-blue-500/5 px-3 py-2 font-semibold text-[var(--app-text)]">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border-t border-[var(--app-border)] px-3 py-2">
              {children}
            </td>
          ),
          code: ({ children, className }) => (
            <code
              className={`rounded bg-blue-500/10 px-1.5 py-0.5 font-mono text-xs ${className ?? ""}`}
            >
              {children}
            </code>
          ),
          pre: ({ children }) => (
            <pre className="my-4 overflow-x-auto rounded-lg bg-slate-950 p-4 text-xs leading-6 text-slate-100 [&_code]:bg-transparent [&_code]:p-0 [&_code]:text-inherit">
              {children}
            </pre>
          ),
        }}
      >
        {linkedContent}
      </ReactMarkdown>
    </div>
  );
}

function SourceCard({
  source,
  index,
  highlighted,
  onRegister,
}: {
  source: HistorySource;
  index: number;
  highlighted: boolean;
  onRegister: (
    index: number,
    element: HTMLDivElement | null
  ) => void;
}) {
  const [expanded, setExpanded] = useState(false);

  const evidence = source.evidence ?? "";
  const isLong = evidence.length > EVIDENCE_PREVIEW_LENGTH;

  const displayedEvidence =
    expanded || !isLong
      ? evidence
      : `${evidence.slice(0, EVIDENCE_PREVIEW_LENGTH).trimEnd()}...`;

  return (
    <div
      id={`history-source-${index}`}
      ref={(element) => onRegister(index, element)}
      className={`scroll-mt-24 rounded-xl border p-4 transition-colors duration-300 sm:p-5 ${
        highlighted
          ? "border-blue-500 bg-blue-500/10 ring-2 ring-blue-500/20"
          : "border-[var(--app-border)] bg-[var(--app-bg)]"
      }`}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <span className="inline-flex items-center gap-2 rounded-md bg-blue-500/10 px-2.5 py-1.5 text-xs font-semibold text-blue-600 dark:text-blue-400">
            <FileText className="h-3.5 w-3.5" />
            {source.source_id || `Source ${index + 1}`}
          </span>

          <p className="mt-3 break-words text-sm font-semibold text-[var(--app-text)]">
            {source.source_file || "Unknown document"}
          </p>
        </div>

        {source.page !== null &&
          source.page !== undefined && (
            <span className="rounded-md border border-[var(--app-border)] px-2 py-1 text-xs text-[var(--app-text-muted)]">
              Page {source.page}
            </span>
          )}
      </div>

      <div className="mt-4 rounded-lg border border-[var(--app-border)] bg-[var(--app-surface)] p-4">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[var(--app-text-muted)]">
          Supporting Evidence
        </p>

        <p className="whitespace-pre-wrap break-words text-sm leading-7 text-[var(--app-text)]">
          {evidence
            ? displayedEvidence
            : "No evidence excerpt was saved."}
        </p>

        {isLong && (
          <button
            type="button"
            onClick={() => setExpanded((current) => !current)}
            aria-expanded={expanded}
            className="mt-3 inline-flex items-center gap-1.5 text-xs font-semibold text-blue-600 hover:underline dark:text-blue-400"
          >
            {expanded ? (
              <>
                <ChevronUp className="h-4 w-4" />
                Show less
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4" />
                Show more
              </>
            )}
          </button>
        )}
      </div>

      {(Boolean(source.content_type) ||
        Boolean(source.table_ids?.length) ||
        Boolean(source.figure_ids?.length)) && (
        <div className="mt-3 flex flex-wrap gap-2 text-xs text-[var(--app-text-muted)]">
          {source.content_type && (
            <span className="rounded-md border border-[var(--app-border)] px-2 py-1">
              {source.content_type}
            </span>
          )}

          {source.table_ids && source.table_ids.length > 0 && (
            <span className="inline-flex items-center gap-1 rounded-md border border-[var(--app-border)] px-2 py-1">
              <Table2 className="h-3.5 w-3.5" />
              {source.table_ids.length} table references
            </span>
          )}

          {source.figure_ids && source.figure_ids.length > 0 && (
            <span className="inline-flex items-center gap-1 rounded-md border border-[var(--app-border)] px-2 py-1">
              <ImageIcon className="h-3.5 w-3.5" />
              {source.figure_ids.length} figure references
            </span>
          )}
        </div>
      )}
    </div>
  );
}

function DeleteConfirmation({
  open,
  isDeleting,
  error,
  onClose,
  onConfirm,
}: {
  open: boolean;
  isDeleting: boolean;
  error: string | null;
  onClose: () => void;
  onConfirm: () => void;
}) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (open && !dialog.open) {
      dialog.showModal();
    } else if (!open && dialog.open) {
      dialog.close();
    }
  }, [open]);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby="delete-history-title"
      aria-describedby="delete-history-description"
      onCancel={(event) => {
        if (isDeleting) {
          event.preventDefault();
        } else {
          onClose();
        }
      }}
      onClose={() => {
        if (!isDeleting) onClose();
      }}
      className="fixed inset-0 m-auto w-[calc(100%-2rem)] max-w-md rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] p-0 text-[var(--app-text)] shadow-2xl backdrop:bg-slate-950/65"
    >
      <div className="p-6">
        <div className="flex items-start justify-between gap-3">
          <div className="rounded-xl bg-red-500/10 p-3">
            <ShieldAlert className="h-6 w-6 text-red-500" />
          </div>

          <button
            type="button"
            onClick={onClose}
            disabled={isDeleting}
            aria-label="Close confirmation"
            className="rounded-lg p-1.5 text-[var(--app-text-muted)] hover:bg-red-500/10 disabled:opacity-50"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <h2
          id="delete-history-title"
          className="mt-5 text-xl font-semibold"
        >
          Delete saved answer?
        </h2>

        <p
          id="delete-history-description"
          className="mt-2 text-sm leading-6 text-[var(--app-text-muted)]"
        >
          This question, its generated answer, and saved source
          references will be permanently removed from your history.
        </p>

        <p className="mt-3 text-xs leading-5 text-[var(--app-text-muted)]">
          Your uploaded documents and their indexed knowledge content
          will not be affected.
        </p>

        {error && (
          <div
            role="alert"
            className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-500"
          >
            {error}
          </div>
        )}

        <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={onClose}
            disabled={isDeleting}
            className="rounded-lg border border-[var(--app-border)] px-4 py-2.5 text-sm font-medium disabled:opacity-50"
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={onConfirm}
            disabled={isDeleting}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-60"
          >
            {isDeleting ? (
              <>
                <LoaderCircle className="h-4 w-4 animate-spin" />
                Deleting...
              </>
            ) : (
              <>
                <Trash2 className="h-4 w-4" />
                Delete Answer
              </>
            )}
          </button>
        </div>
      </div>
    </dialog>
  );
}

export default function HistoryDetail({
  historyId,
  onBack,
}: HistoryDetailProps) {
  const queryClient = useQueryClient();

  const [showDeleteConfirm, setShowDeleteConfirm] =
    useState(false);
  const [copied, setCopied] = useState(false);
  const [activeSource, setActiveSource] =
    useState<number | null>(null);

  const sourceRefs = useRef<
    Record<number, HTMLDivElement | null>
  >({});

  const detailQuery = useQuery({
    queryKey: ["answer-history-detail", historyId],
    queryFn: () => getHistoryDetail(historyId),
    staleTime: 30_000,
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteHistoryEntry(historyId),
    onSuccess: async () => {
      queryClient.removeQueries({
        queryKey: ["answer-history-detail", historyId],
      });

      await queryClient.invalidateQueries({
        queryKey: ["answer-history"],
      });

      setShowDeleteConfirm(false);
      onBack();
    },
  });

  const answer = detailQuery.data;

  function registerSource(
    index: number,
    element: HTMLDivElement | null
  ) {
    sourceRefs.current[index] = element;
  }

  function navigateToSource(index: number) {
    const element = sourceRefs.current[index];

    if (!element) return;

    setActiveSource(index);

    element.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  }

  async function copyAnswer() {
    if (!answer) return;

    try {
      await navigator.clipboard.writeText(answer.answer);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  function closeDelete() {
    if (deleteMutation.isPending) return;

    setShowDeleteConfirm(false);
    deleteMutation.reset();
  }

  return (
    <section className="w-full min-w-0 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-2 rounded-lg px-2 py-2 text-sm font-medium text-[var(--app-text-muted)] hover:bg-blue-500/10 hover:text-blue-500"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to History
        </button>

        {detailQuery.isSuccess && answer && (
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => void copyAnswer()}
              className="inline-flex items-center gap-2 rounded-lg border border-[var(--app-border)] bg-[var(--app-surface)] px-3 py-2 text-sm font-medium text-[var(--app-text)] hover:border-blue-500/50"
            >
              {copied ? (
                <Check className="h-4 w-4 text-emerald-500" />
              ) : (
                <ClipboardCopy className="h-4 w-4" />
              )}
              {copied ? "Copied" : "Copy Answer"}
            </button>

            <button
              type="button"
              onClick={() => setShowDeleteConfirm(true)}
              disabled={deleteMutation.isPending}
              className="inline-flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/5 px-3 py-2 text-sm font-medium text-red-500 hover:bg-red-500/10 disabled:opacity-50"
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </button>
          </div>
        )}
      </div>

      {detailQuery.isPending && (
        <div
          role="status"
          className="rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] px-6 py-16 text-center"
        >
          <LoaderCircle className="mx-auto h-8 w-8 animate-spin text-blue-500" />
          <p className="mt-4 text-sm text-[var(--app-text-muted)]">
            Loading saved answer...
          </p>
        </div>
      )}

      {detailQuery.isError && (
        <div
          role="alert"
          className="rounded-2xl border border-red-500/30 bg-red-500/5 p-6"
        >
          <AlertCircle className="h-6 w-6 text-red-500" />
          <p className="mt-3 font-medium text-[var(--app-text)]">
            Unable to load saved answer
          </p>
          <p className="mt-2 text-sm text-[var(--app-text-muted)]">
            {getErrorMessage(detailQuery.error)}
          </p>
          <button
            type="button"
            onClick={() => void detailQuery.refetch()}
            className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-blue-500"
          >
            <RefreshCw className="h-4 w-4" />
            Try again
          </button>
        </div>
      )}

      {answer && detailQuery.isSuccess && (
        <>
          <div className="rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] p-5 sm:p-6">
            <div className="flex flex-wrap items-center gap-3">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-medium text-emerald-600 dark:text-emerald-400">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Saved Answer
              </span>

              <span className="inline-flex items-center gap-1.5 text-xs text-[var(--app-text-muted)]">
                <CalendarDays className="h-4 w-4" />
                {formatDate(answer.created_at)}
              </span>
            </div>

            <h1 className="mt-5 break-words text-xl font-semibold leading-8 text-[var(--app-text)] sm:text-2xl">
              {answer.question}
            </h1>
          </div>

          <div className="rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] p-5 sm:p-6">
            <div className="flex items-center gap-3 border-b border-[var(--app-border)] pb-4">
              <div className="rounded-lg bg-blue-500/10 p-2.5">
                <FileText className="h-5 w-5 text-blue-500" />
              </div>

              <h2 className="text-lg font-semibold text-[var(--app-text)]">
                Generated Answer
              </h2>
            </div>

            <div className="mt-5">
              <MarkdownContent
                content={answer.answer}
                sources={answer.sources}
                onCitationClick={navigateToSource}
              />
            </div>
          </div>

          <div className="rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] p-5 sm:p-6">
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--app-border)] pb-4">
              <h2 className="text-lg font-semibold text-[var(--app-text)]">
                Supporting Sources
              </h2>

              <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-600 dark:text-blue-400">
                {answer.sources.length}{" "}
                {answer.sources.length === 1
                  ? "source"
                  : "sources"}
              </span>
            </div>

            {answer.sources.length === 0 ? (
              <p className="mt-5 text-sm text-[var(--app-text-muted)]">
                No supporting sources were saved with this answer.
              </p>
            ) : (
              <div className="mt-5 space-y-4">
                {answer.sources.map((source, index) => (
                  <SourceCard
                    key={`${source.chunk_id}-${index}`}
                    source={source}
                    index={index}
                    highlighted={activeSource === index}
                    onRegister={registerSource}
                  />
                ))}
              </div>
            )}
          </div>
        </>
      )}

      <DeleteConfirmation
        open={showDeleteConfirm}
        isDeleting={deleteMutation.isPending}
        error={
          deleteMutation.isError
            ? getErrorMessage(deleteMutation.error)
            : null
        }
        onClose={closeDelete}
        onConfirm={() => deleteMutation.mutate()}
      />
    </section>
  );
}
