
import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  ArrowRight,
  CalendarDays,
  ChevronLeft,
  ChevronRight,
  FileText,
  History,
  LoaderCircle,
  RefreshCw,
  Search,
  X,
} from "lucide-react";

import { ApiError } from "../../lib/api";
import {
  getAnswerHistory,
  type HistoryEntry,
  type HistorySort,
  type HistorySourceFilter,
} from "./api/historyApi";
import HistoryDetail from "./components/HistoryDetail";

const PAGE_SIZE = 10;

function formatDate(value: string) {
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

function getErrorMessage(error: unknown) {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return "Your session has expired. Please sign in again.";
    }

    if (error.status === 403) {
      return "You do not have permission to view history.";
    }

    return error.message;
  }

  return error instanceof Error
    ? error.message
    : "Unable to load saved answers.";
}

function getPreview(answer: string) {
  return answer
    .replace(/```[\s\S]*?```/g, "Code example")
    .replace(/\[Source\s+\d+(?:\s*,\s*Source\s+\d+)*\]/gi, "")
    .replace(/[#*_`~]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function HistoryCard({
  entry,
  onOpen,
}: {
  entry: HistoryEntry;
  onOpen: (id: string) => void;
}) {
  const sourceCount = entry.sources.length;

  return (
    <button
      type="button"
      onClick={() => onOpen(entry.id)}
      className="group w-full rounded-xl border border-[var(--app-border)] bg-[var(--app-surface)] p-4 text-left transition-colors hover:border-blue-500/50 focus-visible:outline-2 focus-visible:outline-blue-500 sm:p-5"
    >
      <div className="flex items-start gap-3">
        <div className="shrink-0 rounded-lg bg-blue-500/10 p-2.5">
          <FileText className="h-5 w-5 text-blue-500" />
        </div>

        <div className="min-w-0 flex-1">
          <h3 className="break-words text-sm font-semibold leading-6 text-[var(--app-text)] sm:text-base">
            {entry.question}
          </h3>

          <p className="mt-2 line-clamp-2 break-words text-sm leading-6 text-[var(--app-text-muted)]">
            {getPreview(entry.answer)}
          </p>

          <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-[var(--app-text-muted)]">
            <span className="inline-flex items-center gap-1.5">
              <CalendarDays className="h-3.5 w-3.5" />
              {formatDate(entry.created_at)}
            </span>

            <span
              className={
                sourceCount > 0
                  ? "rounded-full bg-emerald-500/10 px-2.5 py-1 font-medium text-emerald-600 dark:text-emerald-400"
                  : "rounded-full bg-amber-500/10 px-2.5 py-1 font-medium text-amber-600 dark:text-amber-400"
              }
            >
              {sourceCount > 0
                ? `${sourceCount} supporting ${
                    sourceCount === 1 ? "source" : "sources"
                  }`
                : "No citations"}
            </span>
          </div>
        </div>

        <ArrowRight className="mt-1 h-4 w-4 shrink-0 text-[var(--app-text-muted)] transition-transform group-hover:translate-x-1" />
      </div>
    </button>
  );
}

export default function HistoryPage() {
  const queryClient = useQueryClient();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [sourceFilter, setSourceFilter] =
    useState<HistorySourceFilter>("all");
  const [sort, setSort] = useState<HistorySort>("newest");
  const [page, setPage] = useState(1);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setSearch(searchInput.trim());
      setPage(1);
    }, 350);

    return () => window.clearTimeout(timer);
  }, [searchInput]);

  const offset = (page - 1) * PAGE_SIZE;

  const historyQuery = useQuery({
    queryKey: [
      "answer-history",
      "filtered",
      PAGE_SIZE,
      offset,
      search,
      sourceFilter,
      sort,
    ],
    queryFn: () =>
      getAnswerHistory({
        limit: PAGE_SIZE,
        offset,
        search,
        sourceFilter,
        sort,
      }),
    staleTime: 30_000,
    retry: (failureCount, error) => {
      if (
        error instanceof ApiError &&
        [401, 403, 422].includes(error.status)
      ) {
        return false;
      }

      return failureCount < 2;
    },
  });

  const entries = historyQuery.data?.items ?? [];
  const total = historyQuery.data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const hasPrevious = page > 1;
  const hasNext = page < totalPages;

  function refreshHistory() {
    void queryClient.invalidateQueries({
      queryKey: ["answer-history"],
    });
  }

  function clearFilters() {
    setSearchInput("");
    setSearch("");
    setSourceFilter("all");
    setSort("newest");
    setPage(1);
  }

  // A deletion can leave the current page empty.
  // Move to the previous valid page after fresh data arrives.
  useEffect(() => {
    if (
      historyQuery.isSuccess &&
      !historyQuery.isFetching &&
      page > totalPages
    ) {
      setPage(totalPages);
    }
  }, [
    historyQuery.isSuccess,
    historyQuery.isFetching,
    page,
    totalPages,
  ]);

  if (selectedId) {
    return (
      <section className="w-full min-w-0">
        <HistoryDetail
          historyId={selectedId}
          onBack={() => setSelectedId(null)}
        />
      </section>
    );
  }

  return (
    <section className="w-full min-w-0 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-[0.15em] text-blue-500">
            Proposal Intelligence
          </p>

          <div className="flex items-center gap-3">
            <History className="h-7 w-7 text-blue-500" />
            <h1 className="text-2xl font-semibold text-[var(--app-text)] sm:text-3xl">
              Answer History
            </h1>
          </div>

          <p className="mt-2 text-sm text-[var(--app-text-muted)]">
            Search, review and reuse previously generated answers.
          </p>
        </div>

        <button
          type="button"
          onClick={refreshHistory}
          disabled={historyQuery.isFetching}
          className="inline-flex items-center gap-2 rounded-lg border border-[var(--app-border)] bg-[var(--app-surface)] px-4 py-2.5 text-sm font-medium text-[var(--app-text)] hover:border-blue-500/50 disabled:opacity-50"
        >
          <RefreshCw
            className={`h-4 w-4 ${
              historyQuery.isFetching ? "animate-spin" : ""
            }`}
          />
          Refresh
        </button>
      </div>

      <div className="overflow-hidden rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)]">
        <div className="space-y-4 p-4 sm:p-5">
          <div className="relative">
            <Search className="absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--app-text-muted)]" />

            <input
              type="search"
              value={searchInput}
              onChange={(event) =>
                setSearchInput(event.target.value)
              }
              placeholder="Search questions and answers..."
              aria-label="Search answer history"
              maxLength={200}
              className="w-full rounded-xl border border-[var(--app-border)] bg-[var(--app-bg)] py-3 pl-10 pr-10 text-sm text-[var(--app-text)] outline-none placeholder:text-[var(--app-text-muted)] focus:border-blue-500"
            />

            {searchInput && (
              <button
                type="button"
                onClick={() => {
                  setSearchInput("");
                  setSearch("");
                  setPage(1);
                }}
                aria-label="Clear search"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--app-text-muted)] hover:text-[var(--app-text)]"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>

          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap gap-2">
              {(
                [
                  ["all", "All answers"],
                  ["with_sources", "With sources"],
                  ["without_sources", "Without sources"],
                ] as const
              ).map(([value, label]) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => {
                    setSourceFilter(value);
                    setPage(1);
                  }}
                  aria-pressed={sourceFilter === value}
                  className={`rounded-lg border px-3 py-2 text-xs font-medium transition-colors ${
                    sourceFilter === value
                      ? "border-blue-500 bg-blue-500/10 text-blue-600 dark:text-blue-400"
                      : "border-[var(--app-border)] text-[var(--app-text-muted)] hover:text-[var(--app-text)]"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            <select
              value={sort}
              onChange={(event) => {
                setSort(event.target.value as HistorySort);
                setPage(1);
              }}
              aria-label="Sort answer history"
              className="rounded-lg border border-[var(--app-border)] bg-[var(--app-bg)] px-3 py-2 text-sm text-[var(--app-text)] outline-none focus:border-blue-500"
            >
              <option value="newest">Newest first</option>
              <option value="oldest">Oldest first</option>
            </select>
          </div>
        </div>

        <div className="flex items-center justify-between border-t border-[var(--app-border)] px-4 py-3 text-xs text-[var(--app-text-muted)] sm:px-5">
          <span>
            {historyQuery.isSuccess
              ? `${total} matching ${
                  total === 1 ? "answer" : "answers"
                }`
              : "Saved answers"}
          </span>

          {(search || sourceFilter !== "all" || sort !== "newest") && (
            <button
              type="button"
              onClick={clearFilters}
              className="font-medium text-blue-500 hover:underline"
            >
              Clear filters
            </button>
          )}
        </div>

        <div className="space-y-3 p-4 sm:p-5">
          {historyQuery.isPending && (
            <div
              role="status"
              className="flex items-center justify-center gap-3 py-16 text-sm text-[var(--app-text-muted)]"
            >
              <LoaderCircle className="h-5 w-5 animate-spin text-blue-500" />
              Loading saved answers...
            </div>
          )}

          {historyQuery.isError && (
            <div role="alert" className="py-12 text-center">
              <AlertCircle className="mx-auto h-8 w-8 text-red-500" />

              <p className="mt-3 font-semibold text-[var(--app-text)]">
                Unable to load history
              </p>

              <p className="mt-2 text-sm text-[var(--app-text-muted)]">
                {getErrorMessage(historyQuery.error)}
              </p>

              <button
                type="button"
                onClick={() => void historyQuery.refetch()}
                className="mt-4 text-sm font-medium text-blue-500 hover:underline"
              >
                Try again
              </button>
            </div>
          )}

          {historyQuery.isSuccess && entries.length === 0 && (
            <div className="py-14 text-center">
              <History className="mx-auto h-9 w-9 text-[var(--app-text-muted)]" />

              <p className="mt-4 font-medium text-[var(--app-text)]">
                {search || sourceFilter !== "all"
                  ? "No matching answers"
                  : "No saved answers yet"}
              </p>

              <p className="mt-2 text-sm text-[var(--app-text-muted)]">
                {search || sourceFilter !== "all"
                  ? "Try a different search or filter."
                  : "Answers generated by the AI Assistant will appear here."}
              </p>
            </div>
          )}

          {historyQuery.isSuccess &&
            entries.map((entry) => (
              <HistoryCard
                key={entry.id}
                entry={entry}
                onOpen={setSelectedId}
              />
            ))}
        </div>

        {historyQuery.isSuccess && total > PAGE_SIZE && (
          <div className="flex items-center justify-between gap-3 border-t border-[var(--app-border)] px-4 py-4 sm:px-5">
            <button
              type="button"
              onClick={() =>
                setPage((current) => Math.max(1, current - 1))
              }
              disabled={!hasPrevious}
              className="inline-flex items-center gap-1 rounded-lg border border-[var(--app-border)] px-3 py-2 text-sm text-[var(--app-text)] disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </button>

            <span className="text-sm text-[var(--app-text-muted)]">
              Page {page} of {totalPages}
            </span>

            <button
              type="button"
              onClick={() =>
                setPage((current) => current + 1)
              }
              disabled={!hasNext}
              className="inline-flex items-center gap-1 rounded-lg border border-[var(--app-border)] px-3 py-2 text-sm text-[var(--app-text)] disabled:opacity-40"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
