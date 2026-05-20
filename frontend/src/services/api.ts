import axios from 'axios';
import { ChatResponse, UploadResponse, SessionInfo } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function sendChat(
  query: string,
  sessionId: string,
  fileIds?: string[]
): Promise<ChatResponse> {
  const { data } = await api.post('/chat', {
    query,
    session_id: sessionId,
    file_ids: fileIds,
  });
  return data;
}

export async function uploadFile(
  file: File,
  sessionId?: string,
  onProgress?: (percent: number) => void
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  if (sessionId) {
    formData.append('session_id', sessionId);
  }

  const { data } = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total && onProgress) {
        onProgress(Math.round((e.loaded * 100) / e.total));
      }
    },
  });
  return data;
}

export async function getSession(sessionId: string) {
  const { data } = await api.get(`/session/${sessionId}`);
  return data;
}

export async function deleteSession(sessionId: string) {
  await api.delete(`/session/${sessionId}`);
}

export async function listSessions(): Promise<SessionInfo[]> {
  const { data } = await api.get('/sessions');
  return data;
}

export async function healthCheck() {
  const { data } = await api.get('/health');
  return data;
}
