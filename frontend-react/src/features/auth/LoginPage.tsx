
import { useState } from "react";
import { useMsal } from "@azure/msal-react";
import {
  ArrowRight,
  BookOpenText,
  CheckCircle2,
  FileSearch,
  LockKeyhole,
  LoaderCircle,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import { loginRequest } from "../../auth/msalConfig";
import sigmoidLogo from "../../assets/sigmoid-logo.png";

const capabilities = [
  {
    icon: FileSearch,
    title: "Knowledge discovery",
    description: "Find relevant information across historical proposals.",
  },
  {
    icon: Sparkles,
    title: "Intelligent responses",
    description: "Generate answers grounded in your source documents.",
  },
  {
    icon: BookOpenText,
    title: "Traceable evidence",
    description: "Review supporting passages and source citations.",
  },
];

export default function LoginPage() {
  const { instance } = useMsal();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLogin() {
    if (loading) return;

    setLoading(true);
    setError(null);

    try {
      const result = await instance.loginPopup(loginRequest);

      instance.setActiveAccount(result.account);

      navigate("/", { replace: true });
    } catch (err) {
      console.error("Microsoft sign-in failed:", err);

      setError(
        "Unable to complete Microsoft sign-in. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="relative flex min-h-dvh items-center justify-center overflow-hidden bg-[#F4F7FB] px-4 py-8 font-sans sm:px-6 lg:px-8">
      {/* Background decoration */}
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -left-32 -top-32 h-96 w-96 rounded-full bg-blue-100/70 blur-3xl"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-sky-100/70 blur-3xl"
      />

      <div className="relative z-10 w-full max-w-[1080px]">
        <div className="grid overflow-hidden rounded-[28px] border border-slate-200/80 bg-white shadow-[0_24px_80px_-32px_rgba(15,23,42,0.28)] lg:min-h-[640px] lg:grid-cols-[1.05fr_0.95fr]">
          {/* Brand panel */}
          <section className="relative flex flex-col justify-between overflow-hidden bg-[#193C7A] p-7 text-white sm:p-10 lg:p-12">
            <div
              aria-hidden="true"
              className="pointer-events-none absolute -right-24 -top-24 h-80 w-80 rounded-full border border-white/10"
            />
            <div
              aria-hidden="true"
              className="pointer-events-none absolute -right-10 -top-10 h-64 w-64 rounded-full border border-white/10"
            />

            <div className="relative">
              <div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-medium text-blue-100">
                <Sparkles className="h-3.5 w-3.5" />
                AI-Powered Proposal Intelligence
              </div>

              <h1 className="mt-8 text-4xl font-bold tracking-tight sm:text-5xl">
                Propos<span className="text-[#93C5FD]">IQ</span>
              </h1>

              <p className="mt-4 max-w-md text-lg font-medium leading-relaxed text-white">
                Better proposals.
                <br />
                Built on trusted knowledge.
              </p>

              <p className="mt-4 max-w-md text-sm leading-7 text-blue-100/85">
                Transform historical proposal documents into
                accurate, evidence-backed RFP responses using
                intelligent search and AI-assisted drafting.
              </p>
            </div>

            <div className="relative mt-10 space-y-5">
              {capabilities.map(({ icon: Icon, title, description }) => (
                <div key={title} className="flex items-start gap-3">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/15 bg-white/10">
                    <Icon className="h-5 w-5 text-blue-100" />
                  </div>

                  <div>
                    <h2 className="text-sm font-semibold text-white">
                      {title}
                    </h2>
                    <p className="mt-1 text-xs leading-5 text-blue-100/80">
                      {description}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <p className="relative mt-10 border-t border-white/15 pt-5 text-xs text-blue-100/75">
              A Sigmoid initiative · Internal proposal intelligence
            </p>
          </section>

          {/* Authentication panel */}
          <section className="flex flex-col justify-center px-7 py-12 sm:px-12 lg:px-14">
            <div className="mx-auto w-full max-w-[360px]">
              {/* Company logo */}
              <div className="mb-12">
                <img
                  src={sigmoidLogo}
                  alt="Sigmoid"
                  className="h-14 w-auto max-w-[200px] object-contain object-left"
                />
              </div>

              <div className="mb-8">
                <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50">
                  <ShieldCheck className="h-6 w-6 text-[#193C7A]" />
                </div>

                <h2 className="text-3xl font-bold tracking-tight text-slate-900">
                  Welcome back
                </h2>

                <p className="mt-3 text-sm leading-6 text-slate-500">
                  Sign in with your Microsoft organization account
                  to access the ProposIQ workspace.
                </p>
              </div>

              <button
                type="button"
                onClick={() => void handleLogin()}
                disabled={loading}
                aria-busy={loading}
                className="group flex min-h-12 w-full items-center justify-center gap-3 rounded-xl bg-[#193C7A] px-5 py-3 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-[#102C60] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#193C7A] disabled:cursor-not-allowed disabled:opacity-65"
              >
                {loading ? (
                  <>
                    <LoaderCircle className="h-5 w-5 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  <>
                    Continue with Microsoft
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </>
                )}
              </button>

              {error && (
                <div
                  role="alert"
                  className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700"
                >
                  {error}
                </div>
              )}

              <div className="mt-8 space-y-4 border-t border-slate-100 pt-7">
                <div className="flex items-center gap-3 text-sm text-slate-600">
                  <LockKeyhole className="h-4 w-4 shrink-0 text-slate-400" />
                  Protected by Microsoft Entra ID
                </div>

                <div className="flex items-center gap-3 text-sm text-slate-600">
                  <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600" />
                  Organization account required
                </div>
              </div>

              <p className="mt-12 text-xs leading-5 text-slate-400">
                Access is subject to your organization's
                authentication and application permissions.
              </p>
            </div>
          </section>
        </div>

        <p className="mt-6 text-center text-xs text-slate-400">
          ProposIQ · AI-Powered Proposal Intelligence
        </p>
      </div>
    </main>
  );
}
