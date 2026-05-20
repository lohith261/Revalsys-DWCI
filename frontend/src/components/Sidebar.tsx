import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { PanelLeftClose, PanelLeft, MessageSquare, Trash2, Plus } from 'lucide-react';
import { listSessions, deleteSession, getSession } from '../services/api';
import { SessionInfo, Message, UploadedFile } from '../types';

interface Props {
  currentSessionId: string;
  onChangeSession: (id: string) => void;
  onNewChat: () => void;
  onLoadMessages: (msgs: Message[]) => void;
  onLoadFiles: (files: UploadedFile[]) => void;
}

export default function Sidebar({
  currentSessionId,
  onChangeSession,
  onNewChat,
  onLoadMessages,
  onLoadFiles,
}: Props) {
  const [collapsed, setCollapsed] = useState(false);
  const [sessions, setSessions] = useState<SessionInfo[]>([]);

  const fetchSessions = async () => {
    try {
      const data = await listSessions();
      setSessions(data);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchSessions();
    const interval = setInterval(fetchSessions, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSelect = async (sid: string) => {
    onChangeSession(sid);
    try {
      const data = await getSession(sid);
      const msgs: Message[] = data.messages.map((m: any) => ({
        role: m.role,
        content: m.content,
        source: m.source,
        timestamp: m.timestamp,
      }));
      onLoadMessages(msgs);
      onLoadFiles(data.files || []);
    } catch {
      onLoadMessages([]);
      onLoadFiles([]);
    }
  };

  const handleDelete = async (e: React.MouseEvent, sid: string) => {
    e.stopPropagation();
    await deleteSession(sid);
    if (sid === currentSessionId) {
      onNewChat();
    }
    fetchSessions();
  };

  return (
    <motion.aside
      initial={false}
      animate={{ width: collapsed ? 72 : 280 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="relative h-screen glass-strong border-r border-white/10 flex flex-col shrink-0 z-20"
    >
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-2"
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center">
              <MessageSquare size={16} className="text-white" />
            </div>
            <span className="font-semibold text-sm text-white">Chat AI</span>
          </motion.div>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-2 rounded-lg hover:bg-white/10 transition-colors text-slate-400 hover:text-white"
        >
          {collapsed ? <PanelLeft size={18} /> : <PanelLeftClose size={18} />}
        </button>
      </div>

      <div className="p-3">
        <button
          onClick={onNewChat}
          className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-xl bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 hover:text-indigo-200 transition-all ${
            collapsed ? 'justify-center' : ''
          }`}
        >
          <Plus size={18} />
          {!collapsed && <span className="text-sm font-medium">New Chat</span>}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-1">
        {!collapsed && (
          <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider px-2 mb-2">
            Recent Conversations
          </p>
        )}
        <AnimatePresence>
          {sessions.map((s) => (
            <motion.button
              key={s.session_id}
              layout
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => handleSelect(s.session_id)}
              className={`w-full group flex items-center gap-2 px-3 py-2.5 rounded-xl text-left transition-all ${
                s.session_id === currentSessionId
                  ? 'bg-white/10 text-white'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-white/5'
              } ${collapsed ? 'justify-center' : ''}`}
            >
              <MessageSquare size={16} className="shrink-0" />
              {!collapsed && (
                <>
                  <span className="text-sm truncate flex-1">{s.title}</span>
                  <Trash2
                    size={14}
                    onClick={(e) => handleDelete(e, s.session_id)}
                    className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-red-400 transition-all shrink-0"
                  />
                </>
              )}
            </motion.button>
          ))}
        </AnimatePresence>
      </div>
    </motion.aside>
  );
}
