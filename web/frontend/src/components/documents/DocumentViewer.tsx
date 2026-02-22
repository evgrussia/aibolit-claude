import { useState } from 'react';
import { Copy, Download } from 'lucide-react';
import Card from '../shared/Card.tsx';

export default function DocumentViewer({ content }: { content: string }) {
  const [copied, setCopied] = useState(false);
  const copy = () => { navigator.clipboard.writeText(content); setCopied(true); setTimeout(() => setCopied(false), 2000); };
  const download = () => {
    const b = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(b);
    a.download = 'document.txt'; a.click();
  };

  return (
    <Card title="Сгенерированный документ">
      <div className="flex gap-2 mb-3">
        <button onClick={copy} className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-medical-teal border border-gray-200 px-3 py-1.5 rounded-lg transition-colors">
          <Copy size={14} />{copied ? 'Скопировано!' : 'Копировать'}
        </button>
        <button onClick={download} className="flex items-center gap-1.5 text-sm text-gray-600 hover:text-medical-teal border border-gray-200 px-3 py-1.5 rounded-lg transition-colors">
          <Download size={14} />Скачать .txt
        </button>
      </div>
      <pre className="whitespace-pre-wrap font-mono text-xs bg-gray-50 border border-gray-200 rounded-lg p-4 max-h-96 overflow-y-auto text-gray-800">
        {content}
      </pre>
      <p className="text-xs text-gray-400 mt-2">
        Документ носит информационный характер. Требует подписи и печати уполномоченного врача.
      </p>
    </Card>
  );
}
