import { FileText, Globe } from 'lucide-react';

interface Props {
  source: 'document' | 'web';
  fileName?: string;
}

export default function SourceBadge({ source, fileName }: Props) {
  const isDoc = source === 'document';
  return (
    <div className="flex items-center gap-2 mt-2">
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
          isDoc
            ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/20'
            : 'bg-amber-500/15 text-amber-400 border border-amber-500/20'
        }`}
      >
        {isDoc ? <FileText size={12} /> : <Globe size={12} />}
        {isDoc ? `Source: Document${fileName ? ` - ${fileName}` : ''}` : 'Source: Web'}
      </span>
    </div>
  );
}
