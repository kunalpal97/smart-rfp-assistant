
import { ArrowLeft, Compass, House } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <main className="flex min-h-dvh items-center justify-center bg-[#F4F7FB] px-5 py-12">
      <div className="w-full max-w-xl text-center">
        <div className="mx-auto mb-7 flex h-20 w-20 items-center justify-center rounded-3xl border border-blue-100 bg-white shadow-sm">
          <Compass className="h-10 w-10 text-[#193C7A]" />
        </div>

        <p className="text-sm font-semibold uppercase tracking-[0.25em] text-blue-700">
          Error 404
        </p>

        <h1 className="mt-4 text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          Page not found
        </h1>

        <p className="mx-auto mt-5 max-w-md text-base leading-7 text-slate-500">
          The page you're looking for doesn't exist or may have
          moved. Let's get you back to your workspace.
        </p>

        <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
          <Link
            to="/"
            className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-[#193C7A] px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-[#102C60]"
          >
            <House className="h-4 w-4" />
            Go to dashboard
          </Link>

          <button
            type="button"
            onClick={() => navigate(-1)}
            className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition-colors hover:bg-slate-50"
          >
            <ArrowLeft className="h-4 w-4" />
            Go back
          </button>
        </div>

        <p className="mt-12 text-xs text-slate-400">
          ProposIQ · AI-Powered Proposal Intelligence
        </p>
      </div>
    </main>
  );
}
