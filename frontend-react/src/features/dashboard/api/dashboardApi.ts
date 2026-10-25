
import { apiRequest } from "../../../lib/api";

export interface KnowledgeOverview {
  total_documents: number;
  ready_documents: number;
  processing_documents: number;
  failed_documents: number;
  documents_needing_attention: number;
  total_chunks: number;
  latest_upload_at: string | null;
}

export interface AnswerOverview {
  total_answers: number;
  answers_last_7_days: number;
  answers_with_sources: number;
  answers_without_sources: number;
  evidence_coverage_percent: number | null;
}

export interface DashboardOverviewResponse {
  knowledge: KnowledgeOverview;
  answers: AnswerOverview;
}

export function getDashboardOverview(): Promise<DashboardOverviewResponse> {
  return apiRequest<DashboardOverviewResponse>(
    "/api/dashboard/overview",
  );
}
