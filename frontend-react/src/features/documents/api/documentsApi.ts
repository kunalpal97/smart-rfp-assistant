
import { apiRequest } from "../../../lib/api";

export type DocumentStatus =
  | "processing"
  | "ready"
  | "failed"
  | "legacy";

export interface DocumentItem {
  document_id: string;
  filename: string;
  stored_filename: string | null;
  chunk_count: number;
  status: DocumentStatus;
  created_at: string | null;
  updated_at: string | null;
  error_message: string | null;
  storage_provider: "local" | "azure_blob";
}

export interface DocumentListResponse {
  total_documents: number;
  documents: DocumentItem[];
}

export function getDocuments(): Promise<DocumentListResponse> {
  return apiRequest<DocumentListResponse>("/api/documents");
}

export interface UploadDocumentResponse {
  message: string;
  document_id: string;
  original_filename: string;
  stored_filename: string;
  chunks_created: number;
  structured_elements_created: number;
  azure_search_indexed: boolean;
}

export function uploadDocument(
  file: File,
): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);

  return apiRequest<UploadDocumentResponse>(
    "/api/documents/upload",
    {
      method: "POST",
      body: formData,
    },
  );
}

export interface DeleteDocumentResponse {
  message: string;
  document_id: string;
  chunks_deleted: number;
}

export function deleteDocument(
  documentId: string,
): Promise<DeleteDocumentResponse> {
  return apiRequest<DeleteDocumentResponse>(
    `/api/documents/${encodeURIComponent(documentId)}`,
    {
      method: "DELETE",
    },
  );
}
