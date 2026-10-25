
import { LoaderCircle } from "lucide-react";

type AppLoaderProps = {
  message?: string;
  fullScreen?: boolean;
};

export default function AppLoader({
  message = "Preparing your workspace...",
  fullScreen = false,
}: AppLoaderProps) {
  return (
    <div
      role="status"
      aria-live="polite"
      className={`flex flex-col items-center justify-center gap-5 px-6 text-center ${
        fullScreen ? "min-h-dvh" : "min-h-60"
      }`}
    >
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50">
        <LoaderCircle
          className="h-8 w-8 animate-spin text-[#193C7A]"
          aria-hidden="true"
        />
      </div>

      <div className="space-y-1">
        <p className="text-base font-semibold text-slate-900">
          ProposIQ
        </p>

        <p className="text-sm text-slate-500">
          {message}
        </p>
      </div>
    </div>
  );
}
