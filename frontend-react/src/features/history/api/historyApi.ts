
import { apiRequest } from "../../../lib/api";

export interface HistorySource {
  source_id: string;
  source_file: string;
  page: number | string | null;
  chunk_id: string;
  evidence: string;
  distance: number | null;
  document_id?: string;
  content_type?: string;
  table_ids?: string[];
  figure_ids?: string[];
  structured_elements?: unknown[];
}

export interface HistoryEntry {
  id: string;
  tenant_id: string;
  user_id: string;
  question: string;
  answer: string;
  sources: HistorySource[];
  created_at: string;
}

export type HistorySourceFilter =
  | "all"
  | "with_sources"
  | "without_sources";

export type HistorySort = "newest" | "oldest";

export interface HistoryListResponse {
  items: HistoryEntry[];
  total: number;
  limit: number;
  offset: number;
}

export interface HistoryListOptions {
  limit?: number;
  offset?: number;
  search?: string;
  sourceFilter?: HistorySourceFilter;
  sort?: HistorySort;
}

// Keep compatibility with dashboard's getAnswerHistory(5, 0).
export function getAnswerHistory(
  limit?: number,
  offset?: number
): Promise<HistoryListResponse>;

export function getAnswerHistory(
  options: HistoryListOptions
): Promise<HistoryListResponse>;

export function getAnswerHistory(
  limitOrOptions: number | HistoryListOptions = 20,
  offset = 0
): Promise<HistoryListResponse> {
  const options =
    typeof limitOrOptions === "number"
      ? { limit: limitOrOptions, offset }
      : limitOrOptions;

  const params = new URLSearchParams({
    limit: String(options.limit ?? 20),
    offset: String(options.offset ?? 0),
    search: options.search?.trim() ?? "",
    source_filter: options.sourceFilter ?? "all",
    sort: options.sort ?? "newest",
  });

  return apiRequest<HistoryListResponse>(
    `/api/history?${params.toString()}`
  );
}

export function getHistoryDetail(
  historyId: string
): Promise<HistoryEntry> {
  return apiRequest<HistoryEntry>(
    `/api/history/${encodeURIComponent(historyId)}`
  );
}

export interface DeleteHistoryResponse {
  message: string;
}

export function deleteHistoryEntry(
  historyId: string
): Promise<DeleteHistoryResponse> {
  return apiRequest<DeleteHistoryResponse>(
    `/api/history/${encodeURIComponent(historyId)}`,
    { method: "DELETE" }
  );
}
