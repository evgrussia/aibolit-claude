import { useState, useRef, useCallback } from 'react';
import { Upload, Loader2, Trash2, AlertCircle, FileText } from 'lucide-react';

const ACCEPTED = '.csv,.tsv,.txt,.pdf,.jpg,.jpeg,.png,.webp';
const MAX_SIZE = 10 * 1024 * 1024; // 10 MB

interface ParsedResult {
  test_name: string;
  value: string | number;
  unit: string;
  reference_range: string;
  date: string;
}

interface Props {
  onParse: (file: File) => Promise<{ results: ParsedResult[]; warnings: string[]; parse_method: string }>;
  onConfirm: (results: Record<string, unknown>[]) => Promise<void>;
  onCancel: () => void;
  isParsing: boolean;
  isSaving: boolean;
}

export default function LabFileUpload({ onParse, onConfirm, onCancel, isParsing, isSaving }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const [results, setResults] = useState<ParsedResult[]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [parseMethod, setParseMethod] = useState('');
  const [error, setError] = useState('');
  const [parsed, setParsed] = useState(false);
  const [editIdx, setEditIdx] = useState<number | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(async (file: File) => {
    setError('');
    setWarnings([]);
    setResults([]);
    setParsed(false);

    if (file.size > MAX_SIZE) {
      setError('Файл слишком большой (максимум 10 МБ)');
      return;
    }

    try {
      const data = await onParse(file);
      setResults(data.results || []);
      setWarnings(data.warnings || []);
      setParseMethod(data.parse_method || '');
      setParsed(true);
      if (data.results.length === 0 && data.warnings.length === 0) {
        setError('Не удалось извлечь результаты анализов из файла');
      }
    } catch (err) {
      setError((err as Error).message || 'Ошибка при анализе файла');
    }
  }, [onParse]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  }, [handleFile]);

  const onFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
    e.target.value = '';
  }, [handleFile]);

  const removeRow = (idx: number) => {
    setResults(prev => prev.filter((_, i) => i !== idx));
  };

  const updateRow = (idx: number, field: keyof ParsedResult, value: string) => {
    setResults(prev => prev.map((r, i) => i === idx ? { ...r, [field]: value } : r));
  };

  const handleConfirm = async () => {
    await onConfirm(results.map(r => ({
      test_name: r.test_name,
      value: typeof r.value === 'number' ? r.value : (parseFloat(String(r.value).replace(',', '.')) || r.value),
      unit: r.unit,
      reference_range: r.reference_range,
    })));
  };

  // State: drop zone
  if (!parsed && !isParsing) {
    return (
      <div className="space-y-4">
        <div
          onDragOver={e => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={onDrop}
          onClick={() => fileRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors ${
            dragOver
              ? 'border-medical-teal bg-medical-teal/5'
              : 'border-gray-200 hover:border-medical-teal/50 hover:bg-gray-50'
          }`}
        >
          <div className="flex flex-col items-center gap-3">
            <Upload size={36} className="text-gray-400" />
            <span className="text-sm text-gray-600">
              Перетащите файл сюда или <span className="text-medical-teal font-medium">выберите</span>
            </span>
            <span className="text-xs text-gray-400">PDF, JPEG, PNG, CSV, TXT — до 10 МБ</span>
          </div>
          <input ref={fileRef} type="file" accept={ACCEPTED} onChange={onFileSelect} className="hidden" />
        </div>

        {error && (
          <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-lg px-4 py-2">
            <AlertCircle size={16} />
            {error}
          </div>
        )}
      </div>
    );
  }

  // State: parsing
  if (isParsing) {
    return (
      <div className="flex flex-col items-center gap-3 py-12">
        <Loader2 size={36} className="text-medical-teal animate-spin" />
        <span className="text-sm text-gray-500">Анализируем файл...</span>
        <span className="text-xs text-gray-400">Это может занять до 2 минут для PDF/изображений</span>
      </div>
    );
  }

  // State: preview results
  return (
    <div className="space-y-4">
      {warnings.length > 0 && (
        <div className="space-y-1">
          {warnings.map((w, i) => (
            <div key={i} className="flex items-center gap-2 text-xs text-amber-700 bg-amber-50 rounded-lg px-3 py-1.5">
              <AlertCircle size={14} className="shrink-0" />
              {w}
            </div>
          ))}
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-lg px-4 py-2">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {results.length > 0 && (
        <>
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <FileText size={14} />
            Распознано {results.length} результатов
            {parseMethod && <span>({parseMethod === 'csv' ? 'CSV' : 'AI'})</span>}
          </div>

          <div className="overflow-x-auto max-h-80 overflow-y-auto">
            <table className="w-full text-sm">
              <thead className="sticky top-0 bg-white">
                <tr className="text-left text-gray-500 border-b border-gray-100">
                  <th className="pb-2 font-medium">Анализ</th>
                  <th className="pb-2 font-medium">Значение</th>
                  <th className="pb-2 font-medium">Ед.</th>
                  <th className="pb-2 font-medium">Норма</th>
                  <th className="pb-2 font-medium w-8"></th>
                </tr>
              </thead>
              <tbody>
                {results.map((r, i) => (
                  <tr key={i} className="border-b border-gray-50 hover:bg-gray-50/50">
                    {editIdx === i ? (
                      <>
                        <td className="py-1.5">
                          <input value={r.test_name} onChange={e => updateRow(i, 'test_name', e.target.value)}
                            className="w-full px-2 py-1 border border-gray-200 rounded text-sm focus:outline-none focus:ring-1 focus:ring-medical-teal/30" />
                        </td>
                        <td className="py-1.5">
                          <input value={String(r.value)} onChange={e => updateRow(i, 'value', e.target.value)}
                            className="w-20 px-2 py-1 border border-gray-200 rounded text-sm font-mono focus:outline-none focus:ring-1 focus:ring-medical-teal/30" />
                        </td>
                        <td className="py-1.5">
                          <input value={r.unit} onChange={e => updateRow(i, 'unit', e.target.value)}
                            className="w-16 px-2 py-1 border border-gray-200 rounded text-sm focus:outline-none focus:ring-1 focus:ring-medical-teal/30" />
                        </td>
                        <td className="py-1.5">
                          <input value={r.reference_range} onChange={e => updateRow(i, 'reference_range', e.target.value)}
                            className="w-20 px-2 py-1 border border-gray-200 rounded text-sm focus:outline-none focus:ring-1 focus:ring-medical-teal/30"
                            onBlur={() => setEditIdx(null)} onKeyDown={e => e.key === 'Enter' && setEditIdx(null)} />
                        </td>
                      </>
                    ) : (
                      <>
                        <td className="py-1.5 text-gray-700 cursor-pointer" onClick={() => setEditIdx(i)}>{r.test_name}</td>
                        <td className="py-1.5 font-mono cursor-pointer" onClick={() => setEditIdx(i)}>{r.value}</td>
                        <td className="py-1.5 text-gray-400 cursor-pointer" onClick={() => setEditIdx(i)}>{r.unit}</td>
                        <td className="py-1.5 text-gray-400 text-xs cursor-pointer" onClick={() => setEditIdx(i)}>{r.reference_range}</td>
                      </>
                    )}
                    <td className="py-1.5">
                      <button onClick={() => removeRow(i)}
                        className="p-1 rounded hover:bg-red-50 text-gray-300 hover:text-red-500 transition-colors" title="Убрать">
                        <Trash2 size={14} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              onClick={handleConfirm}
              disabled={results.length === 0 || isSaving}
              className="flex-1 py-2.5 bg-medical-teal text-white rounded-lg font-medium text-sm hover:bg-medical-teal/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors"
            >
              {isSaving ? <><Loader2 size={16} className="animate-spin" /> Сохранение...</> : `Сохранить все (${results.length})`}
            </button>
            <button
              onClick={onCancel}
              disabled={isSaving}
              className="px-4 py-2.5 border border-gray-200 text-gray-600 rounded-lg text-sm hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              Отмена
            </button>
          </div>
        </>
      )}

      {results.length === 0 && parsed && !error && (
        <div className="text-center py-6">
          <p className="text-sm text-gray-400">Результаты не найдены</p>
          <button onClick={onCancel} className="mt-3 px-4 py-2 border border-gray-200 text-gray-600 rounded-lg text-sm hover:bg-gray-50 transition-colors">
            Закрыть
          </button>
        </div>
      )}
    </div>
  );
}
