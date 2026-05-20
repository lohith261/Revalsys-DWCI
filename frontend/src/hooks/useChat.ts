import { useState, useCallback } from 'react';
import { sendChat, getSession } from '../services/api';
import { Message, ChatResponse } from '../types';

export function useChat(sessionId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSession = useCallback(async () => {
    try {
      const data = await getSession(sessionId);
      const msgs: Message[] = data.messages.map((m: any) => ({
        role: m.role,
        content: m.content,
        source: m.source,
        timestamp: m.timestamp,
      }));
      setMessages(msgs);
    } catch {
      // Session may not exist yet
    }
  }, [sessionId]);

  const sendMessage = useCallback(
    async (query: string, fileIds?: string[]) => {
      setIsLoading(true);
      setError(null);

      const userMsg: Message = {
        role: 'user',
        content: query,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      try {
        const res: ChatResponse = await sendChat(query, sessionId, fileIds);
        const assistantMsg: Message = {
          role: 'assistant',
          content: res.answer,
          source: res.source,
          timestamp: res.generated_at,
          cached: res.cached,
          referenced_files: res.referenced_files,
        };
        setMessages((prev) => [...prev, assistantMsg]);
        return res;
      } catch (err: any) {
        const errMsg = err?.response?.data?.detail || err.message || 'Unknown error';
        setError(errMsg);
        const failMsg: Message = {
          role: 'assistant',
          content: `Error: ${errMsg}`,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, failMsg]);
      } finally {
        setIsLoading(false);
      }
    },
    [sessionId]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    loadSession,
    clearMessages,
  };
}
