
import { AlertCircle, RefreshCw } from "lucide-react";

type ErrorStateProps = {
  title?: string;
  message?: string;
  onRetry?: () => void;
};

export default function ErrorState({
  title = "Something went wrong",
  message = "We couldn't complete your request. Please try again.",
  onRetry,
}: ErrorStateProps) {
  return (
    <section
      role="alert"
      className="mx-auto flex w-full max-w-lg flex-col items-center rounded-2xl border border-red-100 bg-white px-6 py-10 text-center shadow-sm"
    >
      <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-red-50">
        <AlertCircle className="h-7 w-7 text-red-600" />
      </div>

      <h2 className="text-xl font-semibold text-slate-900">
        {title}
      </h2>

      <p className="mt-3 text-sm leading-6 text-slate-500">
        {message}
      </p>

      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-6 inline-flex items-center gap-2 rounded-xl bg-[#193C7A] px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-[#102C60] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#193C7A]"
        >
          <RefreshCw className="h-4 w-4" />
          Try again
        </button>
      )}
    </section>
  );
}
