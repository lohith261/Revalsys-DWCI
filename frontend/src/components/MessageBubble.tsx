import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { Message } from '../types';
import SourceBadge from './SourceBadge';
import { format } from 'date-fns';

interface Props {
  message: Message;
  index: number;
}

export default function MessageBubble({ message, index }: Props) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.96 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.35, delay: index * 0.05 }}
      className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-[85%] md:max-w-[75%] rounded-2xl px-5 py-3.5 ${
          isUser
            ? 'bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-500/20'
            : 'glass text-slate-200'
        }`}
      >
        {isUser ? (
          <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-invert max-w-none">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}

        {!isUser && message.source && (
          <SourceBadge
            source={message.source}
            fileName={
              message.referenced_files && message.referenced_files.length > 0
                ? message.referenced_files.map((f) => f.file_name).join(', ')
                : undefined
            }
          />
        )}

        {message.cached && (
          <span className="text-[10px] text-slate-500 mt-1 block">Cached</span>
        )}

        {message.timestamp && (
          <span className="text-[10px] text-slate-500 mt-1 block">
            {format(new Date(message.timestamp), 'h:mm a')}
          </span>
        )}
      </div>
    </motion.div>
  );
}
