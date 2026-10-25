
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import type { ComponentType, SVGProps } from "react";
import {
  AlertCircle,
  ArrowRight,
  BookOpenCheck,
  CheckCircle2,
  Clock3,
  FileText,
  History,
  MessageSquareText,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  UploadCloud,
} from "lucide-react";

import { getDashboardOverview } from "./api/dashboardApi";
import { getAnswerHistory } from "../history/api/historyApi";

type IconType = ComponentType<SVGProps<SVGSVGElement>>;

const panel =
  "rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] shadow-sm";

const muted = "text-[var(--app-text-muted)]";
const text = "text-[var(--app-text)]";


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
    hour12: true,
  }).format(date);
}


function MetricCard({
  title,
  value,
  description,
  icon: Icon,
  loading = false,
  accent = "blue",
}: {
  title: string;
  value: string;
  description: string;
  icon: IconType;
  loading?: boolean;
  accent?: "blue" | "teal" | "amber";
}) {
  const iconColors = {
    blue: "bg-blue-500/10 text-blue-500",
    teal: "bg-teal-500/10 text-teal-500",
    amber: "bg-amber-500/10 text-amber-500",
  };

  return (
    <article
      className={`${panel} min-w-0 p-5 transition-[border-color,box-shadow] duration-200 hover:border-blue-500/30 hover:shadow-md`}
    >
      <div className="flex items-start justify-between gap-3">
        <p className={`text-sm font-medium ${muted}`}>
          {title}
        </p>

        <div
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${iconColors[accent]}`}
        >
          <Icon className="h-5 w-5" aria-hidden="true" />
        </div>
      </div>

      {loading ? (
        <div className="mt-5 h-9 w-24 animate-pulse rounded-lg bg-slate-500/15" />
      ) : (
        <p
          className={`mt-4 text-3xl font-bold tracking-tight tabular-nums ${text}`}
        >
          {value}
        </p>
      )}

      <p className={`mt-2 text-xs leading-5 ${muted}`}>
        {description}
      </p>
    </article>
  );
}

function SectionHeading({
  icon: Icon,
  title,
  description,
}: {
  icon: IconType;
  title: string;
  description?: string;
}) {
  return (
    <div className="flex items-start gap-3">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-500/10 text-blue-500">
        <Icon className="h-5 w-5" aria-hidden="true" />
      </div>

      <div className="min-w-0">
        <h2 className={`text-base font-semibold ${text}`}>
          {title}
        </h2>

        {description && (
          <p className={`mt-1 text-xs leading-5 ${muted}`}>
            {description}
          </p>
        )}
      </div>
    </div>
  );
}

function StatusRow({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string;
  value: number;
  icon: IconType;
  color: string;
}) {
  return (
    <div className="flex items-center justify-between gap-3 py-3">
      <div className="flex min-w-0 items-center gap-3">
        <Icon
          className={`h-4 w-4 shrink-0 ${color}`}
          aria-hidden="true"
        />
        <span className={`text-sm ${muted}`}>{label}</span>
      </div>

      <span className={`text-sm font-semibold tabular-nums ${text}`}>
        {value.toLocaleString("en-IN")}
      </span>
    </div>
  );
}

function QuickAction({
  title,
  description,
  to,
  icon: Icon,
}: {
  title: string;
  description: string;
  to: string;
  icon: IconType;
}) {
  return (
    <Link
      to={to}
      className="group flex min-w-0 items-center gap-3 rounded-xl border border-[var(--app-border)] p-3.5 transition-[background-color,border-color] duration-200 hover:border-blue-500/40 hover:bg-blue-500/5 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
    >
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-blue-500/10 text-blue-500">
        <Icon className="h-5 w-5" aria-hidden="true" />
      </div>

      <div className="min-w-0 flex-1">
        <p className={`text-sm font-semibold ${text}`}>
          {title}
        </p>

        <p className={`mt-0.5 text-xs ${muted}`}>
          {description}
        </p>
      </div>

      <ArrowRight
        className={`h-4 w-4 shrink-0 transition-transform duration-200 group-hover:translate-x-1 ${muted}`}
        aria-hidden="true"
      />
    </Link>
  );
}

export default function DashboardPage() {
  const overviewQuery = useQuery({
    queryKey: ["dashboard", "overview"],
    queryFn: getDashboardOverview,
    staleTime: 30_000,
  });

  const historyQuery = useQuery({
    queryKey: ["answer-history", 5, 0],
    queryFn: () => getAnswerHistory(5, 0),
    staleTime: 30_000,
  });

  const knowledge = overviewQuery.data?.knowledge;
  const answers = overviewQuery.data?.answers;

  const isRefreshing =
    overviewQuery.isFetching || historyQuery.isFetching;

  const coverage = answers?.evidence_coverage_percent;

  const readyPercent =
    knowledge && knowledge.total_documents > 0
      ? Math.min(
          100,
          (knowledge.ready_documents /
            knowledge.total_documents) *
            100
        )
      : 0;

  function handleRefresh() {
    void Promise.all([
      overviewQuery.refetch(),
      historyQuery.refetch(),
    ]);
  }

  return (
    <section className="w-full min-w-0 space-y-6 pb-6">
      {/* Dashboard introduction */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-500">
            Workspace overview
          </p>

          <h1
            className={`mt-2 text-2xl font-bold tracking-tight sm:text-3xl ${text}`}
          >
            Proposal intelligence
          </h1>

          <p className={`mt-2 text-sm leading-6 ${muted}`}>
            Monitor your knowledge base, supporting evidence,
            and recent AI activity.
          </p>
        </div>

        <button
          type="button"
          onClick={handleRefresh}
          disabled={isRefreshing}
          className={`inline-flex min-h-10 items-center gap-2 rounded-xl border border-[var(--app-border)] bg-[var(--app-surface)] px-4 py-2 text-sm font-medium transition-colors hover:bg-blue-500/5 disabled:opacity-60 ${text}`}
        >
          <RefreshCw
            className={`h-4 w-4 ${
              isRefreshing ? "animate-spin" : ""
            }`}
            aria-hidden="true"
          />
          Refresh
        </button>
      </div>

      {/* API error messages */}
      {overviewQuery.isError && (
        <div
          role="alert"
          className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-red-500/25 bg-red-500/10 p-4"
        >
          <div className="flex items-start gap-3">
            <AlertCircle
              className="mt-0.5 h-5 w-5 shrink-0 text-red-500"
              aria-hidden="true"
            />

            <div>
              <p className={`text-sm font-semibold ${text}`}>
                Dashboard metrics are unavailable
              </p>

              <p className={`mt-1 text-xs ${muted}`}>
                {overviewQuery.error instanceof Error
                  ? overviewQuery.error.message
                  : "Please try again."}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={() => void overviewQuery.refetch()}
            className="rounded-lg bg-red-500/10 px-3 py-2 text-sm font-medium text-red-500 hover:bg-red-500/20"
          >
            Retry
          </button>
        </div>
      )}

      {/* Key metrics */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          title="Knowledge Sources"
          value={
            knowledge
              ? `${knowledge.ready_documents} / ${knowledge.total_documents}`
              : "—"
          }
          description="Documents ready out of all uploaded"
          icon={BookOpenCheck}
          accent="blue"
          loading={overviewQuery.isPending}
        />

        <MetricCard
          title="Evidence Coverage"
          value={
            coverage == null
              ? "—"
              : `${coverage.toLocaleString("en-IN")}%`
          }
          description="Saved answers containing citations"
          icon={ShieldCheck}
          accent="teal"
          loading={overviewQuery.isPending}
        />

        <MetricCard
          title="Needs Attention"
          value={
            knowledge
              ? knowledge.documents_needing_attention.toLocaleString(
                  "en-IN"
                )
              : "—"
          }
          description="Failed or empty ready documents"
          icon={AlertCircle}
          accent="amber"
          loading={overviewQuery.isPending}
        />

        <MetricCard
          title="Answers This Week"
          value={
            answers
              ? answers.answers_last_7_days.toLocaleString("en-IN")
              : "—"
          }
          description="Answers generated in the last 7 days"
          icon={MessageSquareText}
          accent="blue"
          loading={overviewQuery.isPending}
        />
      </div>

      {/* Knowledge readiness and evidence summary */}
      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <article className={`${panel} min-w-0 p-5 sm:p-6`}>
          <div className="flex flex-wrap items-start justify-between gap-3">
            <SectionHeading
              icon={BookOpenCheck}
              title="Knowledge readiness"
              description="Processing status of your reference documents"
            />

            <Link
              to="/documents"
              className="inline-flex items-center gap-1 text-xs font-semibold text-blue-500 hover:text-blue-400"
            >
              Manage documents
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          {overviewQuery.isPending ? (
            <div className="mt-7 space-y-4" role="status">
              <div className="h-3 w-full animate-pulse rounded-full bg-slate-500/15" />
              <div className="h-24 animate-pulse rounded-xl bg-slate-500/10" />
              <span className="sr-only">
                Loading knowledge readiness
              </span>
            </div>
          ) : knowledge ? (
            <>
              <div className="mt-7 flex items-end justify-between gap-3">
                <div>
                  <p className={`text-sm ${muted}`}>
                    Ready documents
                  </p>

                  <p className={`mt-1 text-2xl font-bold tabular-nums ${text}`}>
                    {knowledge.ready_documents}
                    <span className={`ml-1 text-sm font-normal ${muted}`}>
                      of {knowledge.total_documents}
                    </span>
                  </p>
                </div>

                <span className="text-sm font-semibold text-teal-500">
                  {Math.round(readyPercent)}%
                </span>
              </div>

              <div
                role="progressbar"
                aria-label="Documents marked ready"
                aria-valuenow={knowledge.ready_documents}
                aria-valuemin={0}
                aria-valuemax={Math.max(knowledge.total_documents, 1)}
                className="mt-3 h-2.5 overflow-hidden rounded-full bg-slate-500/15"
              >
                <div
                  className="h-full rounded-full bg-teal-500 transition-[width] duration-500 motion-reduce:transition-none"
                  style={{ width: `${readyPercent}%` }}
                />
              </div>

              <div className="mt-5 divide-y divide-[var(--app-border)]">
                <StatusRow
                  label="Ready"
                  value={knowledge.ready_documents}
                  icon={CheckCircle2}
                  color="text-teal-500"
                />
                <StatusRow
                  label="Processing"
                  value={knowledge.processing_documents}
                  icon={Clock3}
                  color="text-blue-500"
                />
                <StatusRow
                  label="Failed"
                  value={knowledge.failed_documents}
                  icon={AlertCircle}
                  color="text-red-500"
                />
              </div>

              {knowledge.total_documents === 0 ? (
                <Link
                  to="/documents"
                  className="mt-4 flex items-center gap-2 rounded-xl bg-blue-500/10 px-4 py-3 text-sm font-medium text-blue-500"
                >
                  <UploadCloud className="h-4 w-4" />
                  Upload your first reference document
                </Link>
              ) : knowledge.documents_needing_attention > 0 ? (
                <Link
                  to="/documents"
                  className="mt-4 flex items-center gap-2 rounded-xl border border-amber-500/25 bg-amber-500/10 px-4 py-3 text-sm font-medium text-amber-600 dark:text-amber-400"
                >
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  Review documents needing attention
                  <ArrowRight className="ml-auto h-4 w-4 shrink-0" />
                </Link>
              ) : null}
            </>
          ) : (
            <p className={`mt-6 text-sm ${muted}`}>
              Knowledge information is unavailable.
            </p>
          )}
        </article>

        <article className={`${panel} min-w-0 p-5 sm:p-6`}>
          <SectionHeading
            icon={ShieldCheck}
            title="Answer evidence"
            description="Understand how often saved answers include sources"
          />

          {overviewQuery.isPending ? (
            <div className="mt-7 space-y-4" role="status">
              <div className="h-10 w-28 animate-pulse rounded-lg bg-slate-500/15" />
              <div className="h-24 animate-pulse rounded-xl bg-slate-500/10" />
              <span className="sr-only">
                Loading answer evidence
              </span>
            </div>
          ) : answers ? (
            <>
              <div className="mt-7">
                <p className={`text-sm ${muted}`}>
                  Citation coverage
                </p>

                <p className={`mt-1 text-3xl font-bold tabular-nums ${text}`}>
                  {coverage == null
                    ? "No answers yet"
                    : `${coverage.toLocaleString("en-IN")}%`}
                </p>

                <p className={`mt-2 text-xs leading-5 ${muted}`}>
                  A citation indicates a linked source, not
                  a guarantee of factual accuracy.
                </p>
              </div>

              <div className="mt-5 divide-y divide-[var(--app-border)]">
                <StatusRow
                  label="Answers with sources"
                  value={answers.answers_with_sources}
                  icon={CheckCircle2}
                  color="text-teal-500"
                />
                <StatusRow
                  label="Answers without sources"
                  value={answers.answers_without_sources}
                  icon={AlertCircle}
                  color="text-amber-500"
                />
                <StatusRow
                  label="Total saved answers"
                  value={answers.total_answers}
                  icon={MessageSquareText}
                  color="text-blue-500"
                />
              </div>

              {answers.answers_without_sources > 0 && (
                <Link
                  to="/history"
                  className="mt-4 flex items-center justify-between gap-3 rounded-xl bg-amber-500/10 px-4 py-3 text-sm font-medium text-amber-600 dark:text-amber-400"
                >
                  Review saved answers without citations
                  <ArrowRight className="h-4 w-4 shrink-0" />
                </Link>
              )}
            </>
          ) : (
            <p className={`mt-6 text-sm ${muted}`}>
              Answer evidence information is unavailable.
            </p>
          )}
        </article>
      </div>

      {/* Recent answers and quick actions */}
      <div className="grid grid-cols-1 gap-5 xl:grid-cols-3">
        <article className={`${panel} min-w-0 xl:col-span-2`}>
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--app-border)] p-5 sm:px-6">
            <SectionHeading
              icon={History}
              title="Recent answers"
              description="Your latest saved AI responses"
            />

            <Link
              to="/history"
              className="inline-flex items-center gap-1 text-xs font-semibold text-blue-500 hover:text-blue-400"
            >
              View all
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          <div className="p-5 sm:px-6">
            {historyQuery.isPending ? (
              <div className="space-y-4" role="status">
                {[1, 2, 3].map((item) => (
                  <div
                    key={item}
                    className="space-y-2 border-b border-[var(--app-border)] pb-4 last:border-0"
                  >
                    <div className="h-4 w-4/5 animate-pulse rounded bg-slate-500/15" />
                    <div className="h-3 w-2/5 animate-pulse rounded bg-slate-500/10" />
                  </div>
                ))}
                <span className="sr-only">
                  Loading recent answers
                </span>
              </div>
            ) : historyQuery.isError ? (
              <div role="alert" className="py-5">
                <p className={`text-sm ${muted}`}>
                  Recent answers could not be loaded.
                </p>

                <button
                  type="button"
                  onClick={() => void historyQuery.refetch()}
                  className="mt-3 text-sm font-semibold text-blue-500 hover:underline"
                >
                  Try again
                </button>
              </div>
            ) : historyQuery.data.items.length === 0 ? (
              <div className="py-10 text-center">
                <MessageSquareText
                  className="mx-auto h-9 w-9 text-blue-500/50"
                  aria-hidden="true"
                />

                <p className={`mt-3 text-sm font-semibold ${text}`}>
                  No answers yet
                </p>

                <p className={`mt-1 text-xs ${muted}`}>
                  Ask your first question to start building answer history.
                </p>

                <Link
                  to="/assistant"
                  className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-blue-500"
                >
                  Open AI Assistant
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-[var(--app-border)]">
                {historyQuery.data.items.map((entry) => (
                  <div
                    key={entry.id}
                    className="min-w-0 py-4 first:pt-0 last:pb-0"
                  >
                    <p className={`break-words text-sm font-semibold leading-6 ${text}`}>
                      {entry.question}
                    </p>

                    <div className={`mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs ${muted}`}>
                      <span>{formatDate(entry.created_at)}</span>
                      <span>
                        {entry.sources.length}{" "}
                        {entry.sources.length === 1
                          ? "source"
                          : "sources"}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </article>

        <aside className={`${panel} min-w-0 p-5 sm:p-6`}>
          <SectionHeading
            icon={Sparkles}
            title="Quick actions"
            description="Continue your proposal workflow"
          />

          <div className="mt-5 space-y-3">
            <QuickAction
              to="/assistant"
              title="Ask AI Assistant"
              description="Generate a source-backed response"
              icon={Sparkles}
            />

            <QuickAction
              to="/documents"
              title="Manage Documents"
              description="Upload and review knowledge sources"
              icon={FileText}
            />

            <QuickAction
              to="/history"
              title="Answer History"
              description="Review your previous responses"
              icon={History}
            />
          </div>
        </aside>
      </div>
    </section>
  );
}
