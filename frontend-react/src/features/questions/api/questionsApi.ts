
import { apiRequest } from "../../../lib/api";

export interface QuestionRequest {
  question: string;
}

export interface StructuredTable {
  table_id: string;
  content_type: "table";
  pages: number[];
  columns: string[];
  rows: string[][];
  merged_cells: {
    row: number;
    column: number;
    row_span: number;
    column_span: number;
  }[];
}

export interface StructuredFigure {
  figure_id: string;
  content_type: "figure";
  pages: number[];
  caption: string | null;
}

export interface StructuredElement {
  id: number;
  document_id: string;
  element_id: string;
  element_type: "table" | "figure";
  page_number: number;
  content: StructuredTable | StructuredFigure;
}

export interface AnswerSource {
  source_id: string;
  source_file: string;
  page: number | string | null;
  chunk_id: string;
  evidence: string;
  distance: number | null;

  document_id?: string | null;
  content_type?: string | null;
  table_ids?: string[];
  figure_ids?: string[];
  structured_elements?: StructuredElement[];
}

export interface RFPAnswerResponse {
  answer: string;
  sources: AnswerSource[];
}

export function askQuestion(
  payload: QuestionRequest,
): Promise<RFPAnswerResponse> {
  return apiRequest<RFPAnswerResponse>("/api/questions/ask", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}
