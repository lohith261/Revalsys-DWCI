import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Command, Sparkles } from 'lucide-react';
import { useChat } from '../hooks/useChat';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import PromptSuggestions from './PromptSuggestions';
import FileUploader from './FileUploader';
import { Message, UploadedFile } from '../types';

interface Props {
  sessionId: string;
  onSessionChange: (id: string) => void;
  externalMessages?: Message[];
  uploadedFiles?: UploadedFile[];
}

export default function ChatWindow({
  sessionId,
  onSessionChange,
  externalMessages,
  uploadedFiles,
}: Props) {
  const { messages, isLoading, sendMessage, loadSession, clearMessages } =
    useChat(sessionId);
  const [input, setInput] = useState('');
  const [showUploader, setShowUploader] = useState(false);
  const [sessionFiles, setSessionFiles] = useState<UploadedFile[]>(uploadedFiles || []);
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Sync external files/messages when session changes
  useEffect(() => {
    setSessionFiles(uploadedFiles || []);
  }, [uploadedFiles, sessionId]);

  // Merge external messages if provided (from sidebar restore)
  const displayMessages = externalMessages && externalMessages.length > 0
    ? externalMessages
    : messages;

  useEffect(() => {
    loadSession();
  }, [sessionId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [displayMessages, isLoading]);

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        handleSend();
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [input]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isLoading) return;
    setInput('');
    const fileIds = sessionFiles.map((f) => f.file_id);
    await sendMessage(text, fileIds);
  };

  const handleResize = () => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 200) + 'px';
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen relative overflow-hidden">
      {/* Top bar */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 glass-strong shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
            <Sparkles size={16} className="text-white" />
          </div>
          <div>
            <h1 className="text-sm font-semibold text-white">Document Intelligence</h1>
            <p className="text-xs text-slate-400">Ask about your documents or the web</p>
          </div>
        </div>
        <button
          onClick={() => setShowUploader(!showUploader)}
          className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
            showUploader
              ? 'bg-indigo-500/30 text-indigo-300'
              : 'glass text-slate-300 hover:text-white'
          }`}
        >
          {showUploader ? 'Close Uploads' : 'Upload Documents'}
        </button>
      </div>

      {/* Upload panel */}
      <AnimatePresence>
        {showUploader && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden border-b border-white/10"
          >
            <div className="p-6 max-w-2xl mx-auto">
              <FileUploader
                sessionId={sessionId}
                onUploadComplete={(f) => setSessionFiles((prev) => [...prev, f])}
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Messages area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 md:px-8 py-6 space-y-5"
      >
        {displayMessages.length === 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center h-full text-center py-20"
          >
            <div className="w-24 h-24 mb-6 relative">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                className="absolute inset-0 rounded-full border border-indigo-500/20 border-dashed"
              />
              <div className="absolute inset-4 rounded-full bg-gradient-to-br from-indigo-500/20 to-violet-500/20 flex items-center justify-center">
                <Sparkles size={32} className="text-indigo-400" />
              </div>
            </div>
            <h2 className="text-xl font-semibold text-white mb-2">
              Start a conversation
            </h2>
            <p className="text-sm text-slate-400 max-w-md mb-6">
              Upload PDF or DOCX files and ask questions about them, or search the web for anything else.
            </p>
            <PromptSuggestions onSelect={(p) => setInput(p)} />
          </motion.div>
        )}

        {displayMessages.map((msg, i) => (
          <MessageBubble key={i} message={msg} index={i} />
        ))}

        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex justify-start"
          >
            <div className="glass rounded-2xl px-5 py-3">
              <TypingIndicator />
            </div>
          </motion.div>
        )}
      </div>

      {/* Input area */}
      <div className="px-4 md:px-8 pb-6 pt-2 shrink-0">
        <div className="max-w-3xl mx-auto">
          <div className="glass rounded-2xl p-2 glow-focus transition-shadow duration-300">
            <div className="flex items-end gap-2">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  handleResize();
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder="Ask anything..."
                rows={1}
                className="flex-1 bg-transparent text-white placeholder-slate-500 text-[15px] px-3 py-2.5 resize-none outline-none max-h-[200px]"
              />
              <button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                className="p-2.5 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-500 text-white hover:opacity-90 disabled:opacity-30 disabled:cursor-not-allowed transition-all shrink-0"
              >
                <Send size={18} />
              </button>
            </div>
            <div className="flex items-center justify-between px-3 pb-1 pt-0.5">
              <span className="text-[10px] text-slate-500 flex items-center gap-1">
                <Command size={10} /> + Enter to send
              </span>
              {sessionFiles.length > 0 && (
                <span className="text-[10px] text-emerald-400">
                  {sessionFiles.length} document{sessionFiles.length > 1 ? 's' : ''} attached
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
