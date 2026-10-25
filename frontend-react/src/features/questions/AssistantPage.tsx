
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  AlertCircle,
  BrainCircuit,
  RefreshCw,
  Sparkles,
} from "lucide-react";

import { ApiError } from "../../lib/api";
import {
  askQuestion,
  type QuestionRequest,
} from "./api/questionsApi";

import QuestionForm from "./components/QuestionForm";
import AnswerPanel from "./components/AnswerPanel";

function getQuestionErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    switch (error.status) {
      case 400:
      case 422:
        return error.message;
      case 401:
        return "Your session has expired. Please sign in again.";
      case 403:
        return "You do not have permission to use the AI Assistant.";
      case 429:
        return "Too many requests. Please wait and try again.";
      case 500:
      case 502:
      case 503:
        return "The AI service is temporarily unavailable. Please try again later.";
      default:
        return error.message;
    }
  }

  if (error instanceof TypeError) {
    return "Unable to connect to FastAPI. Check that the backend is running.";
  }

  return error instanceof Error
    ? error.message
    : "Unable to generate an answer.";
}

export default function AssistantPage() {
  const queryClient = useQueryClient();
  const [lastQuestion, setLastQuestion] = useState("");

  const questionMutation = useMutation({
    mutationFn: (payload: QuestionRequest) =>
      askQuestion(payload),

    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey: ["answer-history"],
      });

      void queryClient.invalidateQueries({
        queryKey: ["dashboard", "overview"],
      });
    },
  });

  function handleAskQuestion(question: string) {
    if (questionMutation.isPending) return;

    setLastQuestion(question);
    questionMutation.mutate({ question });
  }

  function handleRetry() {
    if (!lastQuestion || questionMutation.isPending) return;

    questionMutation.mutate({
      question: lastQuestion,
    });
  }

  return (
    <section className="mx-auto w-full max-w-6xl space-y-6 pb-8">
      <header>
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-blue-500">
          Proposal intelligence
        </p>

        <div className="mt-2 flex items-center gap-3">
          <Sparkles
            className="h-7 w-7 text-blue-500"
            aria-hidden="true"
          />

          <h1 className="text-2xl font-bold tracking-tight text-[var(--app-text)] sm:text-3xl">
            AI Assistant
          </h1>
        </div>

        <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--app-text-muted)]">
          Research your proposal knowledge base and generate
          answers with supporting evidence.
        </p>
      </header>

      <QuestionForm
        onSubmit={handleAskQuestion}
        isSubmitting={questionMutation.isPending}
      />

      {questionMutation.isIdle && (
        <div className="rounded-2xl border border-dashed border-[var(--app-border)] bg-[var(--app-surface)] px-6 py-14 text-center">
          <BrainCircuit
            className="mx-auto h-10 w-10 text-blue-500/60"
            aria-hidden="true"
          />

          <h2 className="mt-4 text-base font-semibold text-[var(--app-text)]">
            Ready to explore your knowledge base
          </h2>

          <p className="mx-auto mt-2 max-w-lg text-sm leading-6 text-[var(--app-text-muted)]">
            Ask a specific question to retrieve relevant proposal
            evidence and generate a structured answer.
          </p>
        </div>
      )}

      {questionMutation.isPending && (
        <div
          role="status"
          className="rounded-2xl border border-[var(--app-border)] bg-[var(--app-surface)] p-6 sm:p-8"
        >
          <div className="flex items-center gap-3">
            <Sparkles
              className="h-6 w-6 animate-pulse text-blue-500"
              aria-hidden="true"
            />

            <div>
              <p className="text-sm font-semibold text-[var(--app-text)]">
                Generating your answer
              </p>

              <p className="mt-1 text-xs text-[var(--app-text-muted)]">
                Retrieving evidence and preparing a response...
              </p>
            </div>
          </div>

          <div className="mt-6 space-y-3">
            <div className="h-3 w-full animate-pulse rounded bg-slate-500/15" />
            <div className="h-3 w-5/6 animate-pulse rounded bg-slate-500/15" />
            <div className="h-3 w-2/3 animate-pulse rounded bg-slate-500/15" />
          </div>
        </div>
      )}

      {questionMutation.isError && (
        <div
          role="alert"
          className="rounded-2xl border border-red-500/25 bg-red-500/5 p-5"
        >
          <div className="flex items-start gap-3">
            <AlertCircle
              className="mt-0.5 h-5 w-5 shrink-0 text-red-500"
              aria-hidden="true"
            />

            <div className="min-w-0 flex-1">
              <h2 className="text-sm font-semibold text-[var(--app-text)]">
                Unable to generate answer
              </h2>

              <p className="mt-1 text-sm leading-6 text-red-500">
                {getQuestionErrorMessage(questionMutation.error)}
              </p>

              <button
                type="button"
                onClick={handleRetry}
                disabled={questionMutation.isPending}
                className="mt-4 inline-flex items-center gap-2 rounded-lg border border-red-500/30 px-3 py-2 text-sm font-medium text-red-500 hover:bg-red-500/10"
              >
                <RefreshCw className="h-4 w-4" />
                Retry question
              </button>
            </div>
          </div>
        </div>
      )}

      {questionMutation.isSuccess && (
        <AnswerPanel result={questionMutation.data} />
      )}
    </section>
  );
}
