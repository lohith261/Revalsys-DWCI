import { useState, useCallback } from 'react';
import { uploadFile } from '../services/api';
import { UploadResponse, UploadedFile } from '../types';

interface UploadProgress {
  file: File;
  progress: number;
  status: 'uploading' | 'done' | 'error';
  response?: UploadResponse;
}

export function useUpload(sessionId: string, onUploadComplete?: (file: UploadedFile) => void) {
  const [uploads, setUploads] = useState<UploadProgress[]>([]);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  const upload = useCallback(
    async (files: File[]) => {
      const newUploads: UploadProgress[] = files.map((f) => ({
        file: f,
        progress: 0,
        status: 'uploading',
      }));
      setUploads((prev) => [...prev, ...newUploads]);

      const promises = files.map(async (file) => {
        try {
          const response = await uploadFile(file, sessionId, (pct) => {
            setUploads((prev) => {
              const copy = [...prev];
              const item = copy.find((u) => u.file === file);
              if (item) item.progress = pct;
              return copy;
            });
          });

          setUploads((prev) => {
            const copy = [...prev];
            const item = copy.find((u) => u.file === file);
            if (item) {
              item.status = 'done';
              item.response = response;
            }
            return copy;
          });

          const uf: UploadedFile = {
            file_id: response.file_id,
            file_name: response.file_name,
            uploaded_at: response.timestamp,
            chunks_indexed: response.chunks_indexed,
            status: response.status,
          };
          setUploadedFiles((prev) => [...prev, uf]);
          if (onUploadComplete) {
            onUploadComplete(uf);
          }
          return response;
        } catch {
          setUploads((prev) => {
            const copy = [...prev];
            const item = copy.find((u) => u.file === file);
            if (item) item.status = 'error';
            return copy;
          });
          return null;
        }
      });

      return Promise.all(promises);
    },
    [sessionId, onUploadComplete]
  );

  const clearUploads = useCallback(() => {
    setUploads([]);
  }, []);

  return {
    uploads,
    uploadedFiles,
    upload,
    clearUploads,
  };
}
