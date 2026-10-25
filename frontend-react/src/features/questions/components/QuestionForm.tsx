
import { useState, type FormEvent, type KeyboardEvent } from "react";
import { ArrowUp, LoaderCircle } from "lucide-react";

interface QuestionFormProps {
  onSubmit: (question: string) => void;
  isSubmitting: boolean;
}

const MAX_LENGTH = 2000;

export default function QuestionForm({
  onSubmit,
  isSubmitting,
}: QuestionFormProps) {
  const [question, setQuestion] = useState("");
  const [error, setError] = useState<string | null>(null);

  const trimmed = question.trim();

  function submitQuestion() {
    if (isSubmitting) return;

    if (!trimmed) {
      setError("Please enter a question.");
      return;
    }

    if (trimmed.length > MAX_LENGTH) {
      setError(`Maximum ${MAX_LENGTH} characters allowed.`);
      return;
    }

    setError(null);
    onSubmit(trimmed);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    submitQuestion();
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (
      event.key === "Enter" &&
      (event.ctrlKey || event.metaKey)
    ) {
      event.preventDefault();
      submitQuestion();
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] p-5 shadow-sm sm:p-6"
    >
      <label
        htmlFor="rfp-question"
        className="text-base font-semibold text-[var(--app-text)]"
      >
        Ask ProposIQ
      </label>

      <p className="mt-1.5 text-sm text-[var(--app-text-muted)]">
        Ask about delivery approaches, capabilities, security,
        compliance or historical proposals.
      </p>

      <textarea
        id="rfp-question"
        value={question}
        onChange={(event) => {
          setQuestion(event.target.value);
          setError(null);
        }}
        onKeyDown={handleKeyDown}
        rows={4}
        maxLength={MAX_LENGTH}
        disabled={isSubmitting}
        placeholder="How do we approach cloud migration for financial services?"
        aria-invalid={Boolean(error)}
        aria-describedby="question-hint question-count"
        className="mt-5 w-full resize-y rounded-xl border border-[var(--app-border)] bg-[var(--app-bg)] p-4 text-sm leading-6 text-[var(--app-text)] outline-none transition-colors placeholder:text-[var(--app-text-muted)] focus:border-blue-500 focus:ring-2 focus:ring-blue-500/15 disabled:cursor-wait disabled:opacity-60"
      />

      <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
        <div className="space-y-1">
          <p
            id="question-hint"
            className="text-xs text-[var(--app-text-muted)]"
          >
            Ctrl + Enter to generate
          </p>

          <p
            id="question-count"
            className="text-xs text-[var(--app-text-muted)]"
          >
            {question.length} / {MAX_LENGTH}
          </p>
        </div>

        <button
          type="submit"
          disabled={isSubmitting || !trimmed}
          className="inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-blue-700 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? (
            <LoaderCircle className="h-4 w-4 animate-spin" />
          ) : (
            <ArrowUp className="h-4 w-4" />
          )}

          {isSubmitting ? "Generating..." : "Generate answer"}
        </button>
      </div>

      {error && (
        <p role="alert" className="mt-3 text-sm text-red-500">
          {error}
        </p>
      )}
    </form>
  );
}
