
import { useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  AlertCircle,
  BookOpen,
  Check,
  ChevronDown,
  ChevronUp,
  ClipboardCopy,
  FileText,
  Image as ImageIcon,
  Sparkles,
  Table2,
} from "lucide-react";

import type {
  AnswerSource,
  RFPAnswerResponse,
  StructuredElement,
  StructuredTable,
  StructuredFigure,
} from "../api/questionsApi";

interface AnswerPanelProps {
  result: RFPAnswerResponse;
}

const panel =
  "overflow-hidden rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] shadow-sm";

const text = "text-[var(--app-text)]";
const muted = "text-[var(--app-text-muted)]";
const PREVIEW_LENGTH = 450;

type TableElement = StructuredElement & {
  content: StructuredTable;
};

type FigureElement = StructuredElement & {
  content: StructuredFigure;
};

function isTable(element: StructuredElement): element is TableElement {
  return element.element_type === "table";
}

function isFigure(element: StructuredElement): element is FigureElement {
  return element.element_type === "figure";
}

function sourceLabel(source: AnswerSource, index: number) {
  return source.source_id?.trim() || `Source ${index + 1}`;
}

function validPage(page: number | string | null | undefined) {
  if (page == null) return null;

  const value = String(page).trim();

  return value && value.toUpperCase() !== "N/A"
    ? value
    : null;
}

/**
 * Clean Azure layout markup for presentation.
 *
 * Do not remove the content inside figures/tables unless
 * that content is separately available as structured data.
 */
function cleanEvidence(
  value: string,
  hasStructuredTables: boolean,
  hasStructuredFigures: boolean,
) {
  let cleaned = value
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/<\/?figure\b[^>]*>/gi, "")
    .replace(/<\/?figcaption\b[^>]*>/gi, "");

  if (hasStructuredFigures) {
    // Remove captions already represented by structured figure metadata.
    cleaned = cleaned.replace(
      /(?:^|\n)\s*Figure\s+\d+(?:[.:]\d+)*\s*:\s*[^\n]+/gi,
      "",
    );
  }

  if (hasStructuredTables) {
    // Structured table grids are rendered separately.
    cleaned = cleaned.replace(
      /<table\b[^>]*>[\s\S]*?<\/table>/gi,
      "",
    );
  } else {
    // Avoid displaying raw HTML tags when structured tables are absent.
    cleaned = cleaned.replace(/<\/?table\b[^>]*>/gi, "");
    cleaned = cleaned.replace(/<\/?(?:thead|tbody|tr|th|td)\b[^>]*>/gi, " ");
  }

  return cleaned.replace(/\n{3,}/g, "\n\n").trim();
}

function MarkdownContent({
  content,
  onSourceClick,
  evidence = false,
}: {
  content: string;
  onSourceClick?: (index: number) => void;
  evidence?: boolean;
}) {
  return (
    <div
      className={`min-w-0 break-words text-sm leading-7 ${
        evidence ? muted : text
      }`}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        skipHtml
        components={{
          h1: ({ children }) => (
            <h3 className={`mb-3 mt-5 text-lg font-semibold ${text}`}>
              {children}
            </h3>
          ),
          h2: ({ children }) => (
            <h3 className={`mb-3 mt-5 text-base font-semibold ${text}`}>
              {children}
            </h3>
          ),
          h3: ({ children }) => (
            <h4 className={`mb-2 mt-4 text-sm font-semibold ${text}`}>
              {children}
            </h4>
          ),
          p: ({ children }) => (
            <p className="my-3 whitespace-pre-wrap">{children}</p>
          ),
          ul: ({ children }) => (
            <ul className="my-3 list-disc space-y-1 pl-5">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="my-3 list-decimal space-y-1 pl-5">
              {children}
            </ol>
          ),
          strong: ({ children }) => (
            <strong className={`font-semibold ${text}`}>
              {children}
            </strong>
          ),
          blockquote: ({ children }) => (
            <blockquote className="my-4 border-l-2 border-blue-500 bg-blue-500/5 px-4 py-2">
              {children}
            </blockquote>
          ),
          table: ({ children }) => (
            <div className="my-4 max-w-full overflow-x-auto rounded-lg border border-[var(--app-border)]">
              <table className="w-full min-w-max border-collapse text-left text-sm">
                {children}
              </table>
            </div>
          ),
          th: ({ children }) => (
            <th
              className={`border border-[var(--app-border)] bg-blue-500/5 px-3 py-2 font-semibold ${text}`}
            >
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border border-[var(--app-border)] px-3 py-2">
              {children}
            </td>
          ),
          a: ({ href, children }) => {
            const match = href?.match(/^#rfp-source-(\d+)$/);

            if (match && onSourceClick) {
              const index = Number(match[1]) - 1;

              return (
                <button
                  type="button"
                  onClick={() => onSourceClick(index)}
                  className="inline rounded-md bg-blue-500/10 px-1.5 py-0.5 font-semibold text-blue-500 underline underline-offset-2 hover:bg-blue-500/20 focus-visible:outline-2 focus-visible:outline-blue-500"
                >
                  {children}
                </button>
              );
            }

            // Do not allow AI-generated external links to navigate.
            return <span>{children}</span>;
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

function StructuredTableView({
  element,
}: {
  element: TableElement;
}) {
  const table = element.content;

  return (
    <div className="overflow-hidden rounded-xl border border-[var(--app-border)]">
      <div className="flex items-center gap-2 border-b border-[var(--app-border)] bg-blue-500/5 px-4 py-3">
        <Table2 className="h-4 w-4 text-blue-500" />

        <span className={`text-sm font-semibold ${text}`}>
          Table {element.element_id}
        </span>

        <span className={`ml-auto text-xs ${muted}`}>
          Page {element.page_number}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-max border-collapse text-left text-sm">
          {table.columns.length > 0 && (
            <thead className="bg-blue-500/5">
              <tr>
                {table.columns.map((column, index) => (
                  <th
                    key={index}
                    scope="col"
                    className={`border-b border-r border-[var(--app-border)] px-4 py-3 font-semibold last:border-r-0 ${text}`}
                  >
                    {column || "—"}
                  </th>
                ))}
              </tr>
            </thead>
          )}

          <tbody>
            {table.rows.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className="border-b border-[var(--app-border)] last:border-b-0"
              >
                {row.map((cell, columnIndex) => (
                  <td
                    key={columnIndex}
                    className={`border-r border-[var(--app-border)] px-4 py-3 align-top last:border-r-0 ${muted}`}
                  >
                    {cell || "—"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {table.merged_cells.length > 0 && (
        <p className={`border-t border-[var(--app-border)] px-4 py-2 text-xs ${muted}`}>
          This is an extracted table grid. Some cells were merged in
          the original document.
        </p>
      )}
    </div>
  );
}

function FigureReference({
  element,
}: {
  element: FigureElement;
}) {
  const caption = element.content.caption?.trim();

  if (!caption) return null;

  return (
    <div className="flex items-start gap-3 rounded-lg border border-[var(--app-border)] bg-blue-500/5 px-3 py-3">
      <ImageIcon
        className="mt-0.5 h-4 w-4 shrink-0 text-blue-500"
        aria-hidden="true"
      />

      <div className="min-w-0">
        <p className={`text-xs font-semibold ${text}`}>
          Figure {element.element_id}
          <span className={`ml-2 font-normal ${muted}`}>
            Page {element.page_number}
          </span>
        </p>

        <p className={`mt-1 text-xs leading-5 ${muted}`}>
          {caption}
        </p>
      </div>
    </div>
  );
}

function SourceCard({
  source,
  index,
  expanded,
  highlighted,
  onToggle,
}: {
  source: AnswerSource;
  index: number;
  expanded: boolean;
  highlighted: boolean;
  onToggle: () => void;
}) {
  const elements = source.structured_elements || [];
  const tables = elements.filter(isTable);
  const figures = elements.filter(isFigure);

  const evidence = cleanEvidence(
    source.evidence || "",
    tables.length > 0,
    figures.length > 0,
  );

  const isLong = evidence.length > PREVIEW_LENGTH;

  const visibleEvidence =
    expanded || !isLong
      ? evidence
      : `${evidence.slice(0, PREVIEW_LENGTH).trimEnd()}…`;

  const page = validPage(source.page);

  return (
    <article
      id={`rfp-source-${index + 1}`}
      tabIndex={-1}
      className={`scroll-mt-28 border-b border-[var(--app-border)] p-5 outline-none transition-colors last:border-b-0 sm:p-6 ${
        highlighted ? "bg-blue-500/10" : ""
      }`}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="rounded-lg bg-blue-500/10 px-2.5 py-1 text-xs font-semibold text-blue-500">
          {sourceLabel(source, index)}
        </span>

        {page && (
          <span className={`text-xs ${muted}`}>Page {page}</span>
        )}
      </div>

      <div className="mt-3 flex items-start gap-2">
        <FileText
          className="mt-0.5 h-4 w-4 shrink-0 text-blue-500"
          aria-hidden="true"
        />

        <p className={`min-w-0 break-all text-sm font-semibold ${text}`}>
          {source.source_file || "Unknown document"}
        </p>
      </div>

      <div className="mt-4 space-y-3">
        {evidence && (
          <div className="rounded-xl border border-[var(--app-border)] bg-[var(--app-bg)] p-4">
            <MarkdownContent content={visibleEvidence} evidence />

            {isLong && (
              <button
                type="button"
                onClick={onToggle}
                aria-expanded={expanded}
                className="mt-3 inline-flex items-center gap-1.5 text-xs font-semibold text-blue-500 hover:underline"
              >
                {expanded ? (
                  <ChevronUp className="h-3.5 w-3.5" />
                ) : (
                  <ChevronDown className="h-3.5 w-3.5" />
                )}

                {expanded ? "Show less" : "Show more"}
              </button>
            )}
          </div>
        )}

        {tables.length > 0 && (
          <div className="space-y-3">
            <p className={`text-xs font-semibold uppercase tracking-wide ${muted}`}>
              Referenced tables
            </p>

            {tables.map((element) => (
              <StructuredTableView
                key={`table-${element.id}`}
                element={element}
              />
            ))}
          </div>
        )}

        {figures.length > 0 && (
          <div className="space-y-2">
            {figures.map((element) => (
              <FigureReference
                key={`figure-${element.id}`}
                element={element}
              />
            ))}
          </div>
        )}

        {!evidence && tables.length === 0 && figures.length === 0 && (
          <p className={`text-sm ${muted}`}>
            No evidence preview is available.
          </p>
        )}
      </div>
    </article>
  );
}

export default function AnswerPanel({ result }: AnswerPanelProps) {
  const [expandedSources, setExpandedSources] = useState<number[]>([]);
  const [highlightedSource, setHighlightedSource] =
    useState<number | null>(null);
  const [copied, setCopied] = useState(false);
  const [showFullAnswer, setShowFullAnswer] = useState(true);

  const sourceRefs = useRef<Map<number, HTMLDivElement>>(new Map());

  const sourceIndexes = new Map<string, number>();

  result.sources.forEach((source, index) => {
    sourceIndexes.set(sourceLabel(source, index).toLowerCase(), index);
  });

  function toggleSource(index: number) {
    setExpandedSources((previous) =>
      previous.includes(index)
        ? previous.filter((item) => item !== index)
        : [...previous, index],
    );
  }

  function navigateToSource(index: number) {
    if (index < 0 || index >= result.sources.length) return;

    setExpandedSources((previous) =>
      previous.includes(index) ? previous : [...previous, index],
    );

    setHighlightedSource(index);

    const target = sourceRefs.current.get(index);

    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });

      target.focus({ preventScroll: true });
    }
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(result.answer);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  const answerWithLinks = result.answer.replace(
    /\[(Source\s+\d+(?:\s*,\s*Source\s+\d+)*)\]/gi,
    (original, group: string) => {
      const labels = group.split(/\s*,\s*/);

      if (
        labels.some(
          (label) => !sourceIndexes.has(label.toLowerCase()),
        )
      ) {
        return original;
      }

      return labels
        .map((label) => {
          const index = sourceIndexes.get(label.toLowerCase())!;

          return `[${label}](#rfp-source-${index + 1})`;
        })
        .join(" ");
    },
  );

  return (
    <div className="space-y-5">
      <section className={panel}>
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--app-border)] px-5 py-4 sm:px-6">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-500" />

            <h2 className={`text-base font-semibold ${text}`}>
              Generated answer
            </h2>
          </div>

          <button
            type="button"
            onClick={() => void handleCopy()}
            className={`inline-flex items-center gap-2 rounded-lg border border-[var(--app-border)] px-3 py-2 text-xs font-medium hover:bg-blue-500/5 ${text}`}
          >
            {copied ? (
              <Check className="h-4 w-4 text-teal-500" />
            ) : (
              <ClipboardCopy className="h-4 w-4" />
            )}

            {copied ? "Copied" : "Copy answer"}
          </button>
        </div>

        <div className="p-5 sm:p-6">
          <div
            id="generated-answer-content"
            className={`relative min-w-0 ${
              showFullAnswer ? "" : "max-h-72 overflow-hidden"
            }`}
          >
            <MarkdownContent
              content={answerWithLinks}
              onSourceClick={navigateToSource}
            />

            {!showFullAnswer && (
              <div className="pointer-events-none absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-[var(--app-surface)] to-transparent" />
            )}
          </div>

          {result.answer.length > 1200 && (
            <button
              type="button"
              onClick={() => setShowFullAnswer((value) => !value)}
              aria-expanded={showFullAnswer}
              aria-controls="generated-answer-content"
              className="mt-4 inline-flex items-center gap-2 text-sm font-semibold text-blue-500 hover:underline"
            >
              {showFullAnswer ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}

              {showFullAnswer ? "Show less" : "Show full answer"}
            </button>
          )}
        </div>
      </section>

      <section className={panel}>
        <div className="flex items-center gap-2 border-b border-[var(--app-border)] px-5 py-4 sm:px-6">
          <BookOpen className="h-5 w-5 text-blue-500" />

          <h2 className={`text-base font-semibold ${text}`}>
            Supporting sources
          </h2>

          <span className={`ml-auto rounded-full bg-slate-500/10 px-2.5 py-1 text-xs font-medium ${muted}`}>
            {result.sources.length}
          </span>
        </div>

        {result.sources.length === 0 ? (
          <div className="flex items-start gap-3 p-5 sm:p-6">
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-amber-500" />

            <p className={`text-sm leading-6 ${muted}`}>
              No supporting document passages were returned.
              Verify important claims before using this answer in a proposal.
            </p>
          </div>
        ) : (
          <div>
            {result.sources.map((source, index) => (
              <div
                key={`${source.chunk_id}-${index}`}
                ref={(element) => {
                  if (element) {
                    sourceRefs.current.set(index, element);
                  } else {
                    sourceRefs.current.delete(index);
                  }
                }}
              >
                <SourceCard
                  source={source}
                  index={index}
                  expanded={expandedSources.includes(index)}
                  highlighted={highlightedSource === index}
                  onToggle={() => toggleSource(index)}
                />
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
