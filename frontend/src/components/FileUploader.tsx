import { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { useUpload } from '../hooks/useUpload';
import { UploadedFile } from '../types';

interface Props {
  sessionId: string;
  onUploadComplete?: (file: UploadedFile) => void;
}

export default function FileUploader({ sessionId, onUploadComplete }: Props) {
  const { uploads, uploadedFiles, upload, clearUploads } = useUpload(sessionId, onUploadComplete);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      const files = Array.from(e.dataTransfer.files).filter((f) =>
        ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'].includes(f.type)
      );
      if (files.length) upload(files);
    },
    [upload]
  );

  const handleSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const files = Array.from(e.target.files || []);
      if (files.length) upload(files);
      e.target.value = '';
    },
    [upload]
  );

  return (
    <div className="space-y-4">
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`relative cursor-pointer rounded-2xl border-2 border-dashed transition-all duration-300 p-8 text-center ${
          isDragging
            ? 'border-indigo-400 bg-indigo-500/10'
            : 'border-white/20 hover:border-white/40 hover:bg-white/5'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.docx"
          className="hidden"
          onChange={handleSelect}
        />
        <motion.div
          animate={{ y: isDragging ? -5 : 0 }}
          className="flex flex-col items-center gap-2"
        >
          <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center">
            <Upload className="text-indigo-400" size={24} />
          </div>
          <p className="text-sm text-slate-300 font-medium">
            Drop files here or click to browse
          </p>
          <p className="text-xs text-slate-500">PDF and DOCX only</p>
        </motion.div>
      </div>

      <AnimatePresence>
        {uploads.map((u, i) => (
          <motion.div
            key={`${u.file.name}-${i}`}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="glass rounded-xl p-3 flex items-center gap-3"
          >
            <div className="w-9 h-9 rounded-lg bg-white/5 flex items-center justify-center shrink-0">
              <FileText size={18} className="text-indigo-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-slate-200 truncate">{u.file.name}</p>
              <div className="w-full h-1.5 bg-white/5 rounded-full mt-1.5 overflow-hidden">
                <motion.div
                  className={`h-full rounded-full ${
                    u.status === 'error'
                      ? 'bg-red-500'
                      : u.status === 'done'
                      ? 'bg-emerald-500'
                      : 'bg-indigo-500'
                  }`}
                  initial={{ width: 0 }}
                  animate={{ width: `${u.progress}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </div>
            <div className="shrink-0">
              {u.status === 'uploading' && <Loader2 size={16} className="text-indigo-400 animate-spin" />}
              {u.status === 'done' && <CheckCircle size={16} className="text-emerald-400" />}
              {u.status === 'error' && <AlertCircle size={16} className="text-red-400" />}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Documents</p>
            <button onClick={clearUploads} className="text-xs text-slate-500 hover:text-slate-300 transition-colors">
              Clear completed
            </button>
          </div>
          {uploadedFiles.map((f) => (
            <div key={f.file_id} className="glass rounded-xl p-3 flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-emerald-500/10 flex items-center justify-center shrink-0">
                <FileText size={18} className="text-emerald-400" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-200 truncate">{f.file_name}</p>
                <p className="text-xs text-slate-500">{f.chunks_indexed} chunks indexed</p>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
                Ready
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
