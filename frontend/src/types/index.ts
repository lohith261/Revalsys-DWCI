export interface Message {
  role: 'user' | 'assistant';
  content: string;
  source?: 'document' | 'web';
  timestamp?: string;
  cached?: boolean;
  referenced_files?: ReferencedFile[];
}

export interface ReferencedFile {
  file_id: string;
  file_name: string;
  relevance_score: number;
}

export interface ChatResponse {
  answer: string;
  source: 'document' | 'web';
  session_id: string;
  cached: boolean;
  referenced_files: ReferencedFile[];
  generated_at: string;
}

export interface UploadResponse {
  file_id: string;
  file_name: string;
  chunks_indexed: number;
  status: string;
  timestamp: string;
}

export interface SessionInfo {
  session_id: string;
  title: string;
  updated_at: string;
}

export interface UploadedFile {
  file_id: string;
  file_name: string;
  uploaded_at: string;
  chunks_indexed: number;
  status?: string;
}
