
import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  AlertCircle,
  CheckCircle2,
  Clock3,
  FileText,
  Files,
  RefreshCw,
  Search,
  X,
} from "lucide-react";

import { useAppAuth } from "../../auth/AuthContext";
import { ApiError } from "../../lib/api";
import {
  getDocuments,
  type DocumentItem,
  type DocumentStatus,
} from "./api/documentsApi";

import DocumentUpload from "./components/DocumentUpload";
import DeleteDocumentButton from "./components/DeleteDocumentButton";

type StatusFilter = "all" | DocumentStatus;
type SortOption = "newest" | "oldest" | "name";

const panel =
  "rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] shadow-sm";

const text = "text-[var(--app-text)]";
const muted = "text-[var(--app-text-muted)]";

function getErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "Your session has expired. Please sign in again.";
    }

    if (error.status === 403) {
      return "You do not have permission to view documents.";
    }

    return error.message;
  }

  return error instanceof Error
    ? error.message
    : "Unable to load documents.";
}

function formatDate(value: string | null): string {
  if (!value) return "Date unavailable";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Date unavailable";
  }

  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}

function getStatusConfig(status: DocumentStatus) {
  switch (status) {
    case "ready":
      return {
        label: "Ready",
        classes:
          "bg-teal-500/10 text-teal-600 dark:text-teal-400",
        Icon: CheckCircle2,
      };

    case "processing":
      return {
        label: "Processing",
        classes:
          "bg-blue-500/10 text-blue-600 dark:text-blue-400",
        Icon: Clock3,
      };

    case "failed":
      return {
        label: "Failed",
        classes:
          "bg-red-500/10 text-red-600 dark:text-red-400",
        Icon: AlertCircle,
      };

    default:
      return {
        label: "Legacy",
        classes:
          "bg-slate-500/10 text-[var(--app-text-muted)]",
        Icon: FileText,
      };
  }
}

function StatusBadge({
  status,
}: {
  status: DocumentStatus;
}) {
  const { label, classes, Icon } = getStatusConfig(status);

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ${classes}`}
    >
      <Icon
        className={`h-3.5 w-3.5 ${
          status === "processing" ? "animate-pulse" : ""
        }`}
        aria-hidden="true"
      />
      {label}
    </span>
  );
}

function DocumentRow({
  document,
  isAdmin,
}: {
  document: DocumentItem;
  isAdmin: boolean;
}) {
  return (
    <div className="flex flex-wrap items-center gap-4 border-b border-[var(--app-border)] px-5 py-4 transition-colors last:border-b-0 hover:bg-blue-500/5 sm:px-6">
      <div className="flex min-w-0 flex-1 items-start gap-3">
        <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-500/10 text-blue-500">
          <FileText
            className="h-5 w-5"
            aria-hidden="true"
          />
        </div>

        <div className="min-w-0 flex-1">
          <p className={`break-all text-sm font-semibold ${text}`}>
            {document.filename}
          </p>

          <div className={`mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-1 text-xs ${muted}`}>
            <span>{formatDate(document.created_at)}</span>
            <span aria-hidden="true">·</span>
            <span>
              {document.chunk_count.toLocaleString("en-IN")}{" "}
              {document.chunk_count === 1 ? "chunk" : "chunks"}
            </span>
          </div>

          {document.status === "failed" && (
            <p className="mt-2 break-words text-xs leading-5 text-red-600 dark:text-red-400">
              {document.error_message?.trim() ||
                "Document processing failed. No additional details are available."}
            </p>
          )}
        </div>
      </div>

      <div className="ml-14 flex items-center gap-3 sm:ml-0">
        <StatusBadge status={document.status} />

        {isAdmin && (
          <DeleteDocumentButton document={document} />
        )}
      </div>
    </div>
  );
}

export default function DocumentsPage() {
  const { isAdmin } = useAppAuth();

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] =
    useState<StatusFilter>("all");
  const [sortBy, setSortBy] =
    useState<SortOption>("newest");

  const documentsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: getDocuments,
    staleTime: 30_000,

    retry: (failureCount, error) => {
      if (
        error instanceof ApiError &&
        [401, 403, 404].includes(error.status)
      ) {
        return false;
      }

      return failureCount < 2;
    },

    refetchInterval: (query) => {
      const hasProcessing = query.state.data?.documents.some(
        (document) => document.status === "processing",
      );

      return hasProcessing ? 10_000 : false;
    },
  });

  const documents = useMemo(
    () => documentsQuery.data?.documents ?? [],
    [documentsQuery.data],
  );

  const counts = useMemo(() => {
    return {
      all: documents.length,
      ready: documents.filter((d) => d.status === "ready").length,
      processing: documents.filter(
        (d) => d.status === "processing",
      ).length,
      failed: documents.filter((d) => d.status === "failed").length,
      legacy: documents.filter((d) => d.status === "legacy").length,
    };
  }, [documents]);

  const visibleDocuments = useMemo(() => {
    const term = search.trim().toLowerCase();

    const result = documents.filter((document) => {
      const matchesSearch = document.filename
        .toLowerCase()
        .includes(term);

      const matchesStatus =
        statusFilter === "all" ||
        document.status === statusFilter;

      return matchesSearch && matchesStatus;
    });

    result.sort((a, b) => {
      if (sortBy === "name") {
        return a.filename.localeCompare(b.filename);
      }

      const dateA = a.created_at
        ? new Date(a.created_at).getTime()
        : 0;

      const dateB = b.created_at
        ? new Date(b.created_at).getTime()
        : 0;

      const safeA = Number.isFinite(dateA) ? dateA : 0;
      const safeB = Number.isFinite(dateB) ? dateB : 0;

      return sortBy === "newest"
        ? safeB - safeA
        : safeA - safeB;
    });

    return result;
  }, [documents, search, statusFilter, sortBy]);

  const filters: {
    value: StatusFilter;
    label: string;
    count: number;
  }[] = [
    { value: "all", label: "All", count: counts.all },
    { value: "ready", label: "Ready", count: counts.ready },
    {
      value: "processing",
      label: "Processing",
      count: counts.processing,
    },
    { value: "failed", label: "Failed", count: counts.failed },
    ...(counts.legacy > 0
      ? [
          {
            value: "legacy" as const,
            label: "Legacy",
            count: counts.legacy,
          },
        ]
      : []),
  ];

  return (
    <section className="w-full min-w-0 space-y-6 pb-6">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-500">
            Knowledge management
          </p>

          <h1 className={`mt-2 text-2xl font-bold tracking-tight sm:text-3xl ${text}`}>
            Document library
          </h1>

          <p className={`mt-2 text-sm leading-6 ${muted}`}>
            Manage documents used by your AI Assistant.
          </p>
        </div>

        <button
          type="button"
          onClick={() => void documentsQuery.refetch()}
          disabled={documentsQuery.isFetching}
          className={`inline-flex min-h-10 items-center gap-2 rounded-xl border border-[var(--app-border)] bg-[var(--app-surface)] px-4 py-2 text-sm font-medium hover:bg-blue-500/5 disabled:opacity-50 ${text}`}
        >
          <RefreshCw
            className={`h-4 w-4 ${
              documentsQuery.isFetching ? "animate-spin" : ""
            }`}
            aria-hidden="true"
          />
          Refresh
        </button>
      </div>

      {/* Upload */}
      {isAdmin && <DocumentUpload />}

      {/* Library */}
      <div className={`${panel} overflow-hidden`}>
        <div className="border-b border-[var(--app-border)] p-5 sm:p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className={`text-base font-semibold ${text}`}>
                Knowledge sources
              </h2>

              <p className={`mt-1 text-xs ${muted}`}>
                {documentsQuery.isPending || documentsQuery.isError
                  ? "Review uploaded documents"
                  : `${counts.all} total documents`}
              </p>
            </div>

            {!documentsQuery.isPending && !documentsQuery.isError && (
              <span className={`text-xs ${muted}`}>
                {visibleDocuments.length} shown
              </span>
            )}
          </div>

          {/* Search */}
          <div className="relative mt-5">
            <Search
              className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--app-text-muted)]"
              aria-hidden="true"
            />

            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search documents..."
              aria-label="Search documents"
              className={`min-h-11 w-full rounded-xl border border-[var(--app-border)] bg-[var(--app-bg)] py-2.5 pl-10 pr-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15 ${text}`}
            />

            {search && (
              <button
                type="button"
                onClick={() => setSearch("")}
                aria-label="Clear search"
                className={`absolute right-3 top-1/2 -translate-y-1/2 p-1 ${muted}`}
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          {/* Status filters and sort */}
          <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
            <div
              className="flex flex-wrap gap-2"
              aria-label="Filter documents by status"
            >
              {filters.map((filter) => (
                <button
                  key={filter.value}
                  type="button"
                  onClick={() => setStatusFilter(filter.value)}
                  aria-pressed={statusFilter === filter.value}
                  className={`rounded-lg border px-3 py-2 text-xs font-semibold transition-colors ${
                    statusFilter === filter.value
                      ? "border-blue-500/40 bg-blue-500/10 text-blue-500"
                      : `border-[var(--app-border)] ${muted} hover:bg-blue-500/5`
                  }`}
                >
                  {filter.label} ({filter.count})
                </button>
              ))}
            </div>

            <select
              value={sortBy}
              onChange={(event) =>
                setSortBy(event.target.value as SortOption)
              }
              aria-label="Sort documents"
              className={`min-h-10 rounded-xl border border-[var(--app-border)] bg-[var(--app-bg)] px-3 text-xs font-medium ${text}`}
            >
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
              <option value="name">Filename A–Z</option>
            </select>
          </div>
        </div>

        {/* Content */}
        {documentsQuery.isPending ? (
          <div role="status" className="space-y-4 p-6">
            {[1, 2, 3].map((item) => (
              <div
                key={item}
                className="flex items-center gap-3"
              >
                <div className="h-11 w-11 animate-pulse rounded-xl bg-slate-500/15" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-2/3 animate-pulse rounded bg-slate-500/15" />
                  <div className="h-3 w-1/3 animate-pulse rounded bg-slate-500/10" />
                </div>
              </div>
            ))}
            <span className="sr-only">Loading documents</span>
          </div>
        ) : documentsQuery.isError ? (
          <div role="alert" className="px-5 py-14 text-center">
            <AlertCircle
              className="mx-auto h-9 w-9 text-red-500"
              aria-hidden="true"
            />

            <p className={`mt-4 text-sm font-semibold ${text}`}>
              Unable to load documents
            </p>

            <p className={`mx-auto mt-2 max-w-md text-sm ${muted}`}>
              {getErrorMessage(documentsQuery.error)}
            </p>

            <button
              type="button"
              onClick={() => void documentsQuery.refetch()}
              className="mt-5 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
            >
              Try again
            </button>
          </div>
        ) : documents.length === 0 ? (
          <div className="px-5 py-16 text-center">
            <Files
              className="mx-auto h-10 w-10 text-blue-500/50"
              aria-hidden="true"
            />

            <p className={`mt-4 text-sm font-semibold ${text}`}>
              No documents available
            </p>

            <p className={`mt-2 text-sm ${muted}`}>
              {isAdmin
                ? "Upload your first document to build the knowledge base."
                : "No documents have been uploaded yet."}
            </p>
          </div>
        ) : visibleDocuments.length === 0 ? (
          <div className="px-5 py-14 text-center">
            <Search
              className="mx-auto h-9 w-9 text-blue-500/50"
              aria-hidden="true"
            />

            <p className={`mt-4 text-sm font-semibold ${text}`}>
              No matching documents
            </p>

            <p className={`mt-2 text-sm ${muted}`}>
              Try another search or status filter.
            </p>

            <button
              type="button"
              onClick={() => {
                setSearch("");
                setStatusFilter("all");
              }}
              className="mt-4 text-sm font-semibold text-blue-500 hover:underline"
            >
              Clear filters
            </button>
          </div>
        ) : (
          <div>
            {visibleDocuments.map((document) => (
              <DocumentRow
                key={document.document_id}
                document={document}
                isAdmin={isAdmin}
              />
            ))}
          </div>
        )}
      </div>

      {counts.processing > 0 && (
        <p className={`flex items-center gap-2 text-xs ${muted}`}>
          <RefreshCw
            className="h-3.5 w-3.5 animate-spin"
            aria-hidden="true"
          />
          Checking processing documents every 10 seconds.
        </p>
      )}
    </section>
  );
}
