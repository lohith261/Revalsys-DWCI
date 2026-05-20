import { motion } from 'framer-motion';

interface Props {
  onSelect: (prompt: string) => void;
}

const suggestions = [
  'Summarize the uploaded documents',
  'What are the key takeaways?',
  'Compare the main points across files',
  'Find specific details about...',
];

export default function PromptSuggestions({ onSelect }: Props) {
  return (
    <div className="flex flex-wrap gap-2 mt-4 justify-center">
      {suggestions.map((s, i) => (
        <motion.button
          key={i}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
          onClick={() => onSelect(s)}
          className="px-4 py-2 rounded-xl glass text-sm text-slate-300 hover:text-white hover:bg-white/10 transition-all duration-200 cursor-pointer"
        >
          {s}
        </motion.button>
      ))}
    </div>
  );
}
