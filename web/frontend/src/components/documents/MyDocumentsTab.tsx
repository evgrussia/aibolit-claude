import { useState, useRef, useCallback } from 'react';
import { Upload, FileText, Image, File, Trash2, Download, Loader2, AlertCircle } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { uploadDocument, listMyDocuments, downloadDocument, deleteDocument } from '../../api/documents';
import type { UploadedDocument } from '../../api/documents';
import { useToast } from '../../contexts/ToastContext';

const MAX_SIZE = 10 * 1024 * 1024; // 10 MB
const ACCEPTED = '.pdf,.jpg,.jpeg,.png,.gif,.txt,.doc,.docx';

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} Б`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} КБ`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} МБ`;
}

function formatDate(iso: string): string {
  const d = new Date(iso + 'Z');
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

function fileIcon(type: string) {
  if (type.startsWith('image/')) return <Image size={18} className="text-purple-500" />;
  if (type.includes('pdf')) return <FileText size={18} className="text-red-500" />;
  return <File size={18} className="text-gray-400" />;
}

export default function MyDocumentsTab() {
  const [dragOver, setDragOver] = useState(false);
  const [sizeError, setSizeError] = useState('');
  const [confirmDelete, setConfirmDelete] = useState<number | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);
  const toast = useToast();
  const qc = useQueryClient();

  const { data: documents = [], isLoading } = useQuery({
    queryKey: ['my-documents'],
    queryFn: listMyDocuments,
  });

  const uploadMut = useMutation({
    mutationFn: (file: File) => uploadDocument(file),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['my-documents'] });
      toast.success('Файл загружен');
    },
    onError: (err: Error) => toast.error(err.message || 'Ошибка загрузки'),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) => deleteDocument(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['my-documents'] });
      toast.success('Файл удалён');
      setConfirmDelete(null);
    },
    onError: (err: Error) => toast.error(err.message || 'Ошибка удаления'),
  });

  const processFile = useCallback((file: File) => {
    setSizeError('');
    if (file.size > MAX_SIZE) {
      setSizeError(`Файл "${file.name}" превышает 10 МБ (${formatSize(file.size)})`);
      return;
    }
    uploadMut.mutate(file);
  }, [uploadMut]);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  }, [processFile]);

  const onFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) processFile(file);
    e.target.value = '';
  }, [processFile]);

  const handleDownload = async (doc: UploadedDocument) => {
    try {
      await downloadDocument(doc.id, doc.file_name);
    } catch {
      toast.error('Ошибка скачивания');
    }
  };

  return (
    <div className="space-y-6">
      {/* Drop zone */}
      <div
        onDragOver={e => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        onClick={() => fileRef.current?.click()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
          dragOver
            ? 'border-medical-teal bg-medical-teal/5'
            : 'border-gray-200 hover:border-medical-teal/50 hover:bg-gray-50'
        }`}
      >
        {uploadMut.isPending ? (
          <div className="flex flex-col items-center gap-2">
            <Loader2 size={32} className="text-medical-teal animate-spin" />
            <span className="text-sm text-gray-500">Загрузка...</span>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload size={32} className="text-gray-400" />
            <span className="text-sm text-gray-600">
              Перетащите файл сюда или <span className="text-medical-teal font-medium">выберите</span>
            </span>
            <span className="text-xs text-gray-400">PDF, изображения, текст, Word — до 10 МБ</span>
          </div>
        )}
        <input ref={fileRef} type="file" accept={ACCEPTED} onChange={onFileSelect} className="hidden" />
      </div>

      {/* Size error */}
      {sizeError && (
        <div className="flex items-center gap-2 text-sm text-red-600 bg-red-50 rounded-lg px-4 py-2">
          <AlertCircle size={16} />
          {sizeError}
        </div>
      )}

      {/* Document list */}
      {isLoading ? (
        <div className="flex justify-center py-8">
          <Loader2 size={24} className="animate-spin text-medical-teal" />
        </div>
      ) : documents.length === 0 ? (
        <div className="text-center py-12 text-gray-400">
          <FileText size={48} className="mx-auto mb-3 opacity-50" />
          <p className="text-sm">У вас пока нет загруженных документов</p>
        </div>
      ) : (
        <div className="space-y-2">
          {documents.map(doc => (
            <div
              key={doc.id}
              className="flex items-center gap-3 px-4 py-3 bg-white border border-gray-100 rounded-xl hover:shadow-sm transition-shadow"
            >
              {fileIcon(doc.file_type)}
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-gray-800 truncate">{doc.file_name}</div>
                <div className="text-xs text-gray-400">
                  {formatSize(doc.file_size)} &middot; {formatDate(doc.uploaded_at)}
                </div>
              </div>
              <button
                onClick={() => handleDownload(doc)}
                title="Скачать"
                className="p-2 rounded-lg text-gray-400 hover:text-medical-teal hover:bg-medical-teal/5 transition-colors"
              >
                <Download size={16} />
              </button>
              {confirmDelete === doc.id ? (
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => deleteMut.mutate(doc.id)}
                    disabled={deleteMut.isPending}
                    className="px-2 py-1 text-xs bg-red-500 text-white rounded hover:bg-red-600 transition-colors"
                  >
                    Да
                  </button>
                  <button
                    onClick={() => setConfirmDelete(null)}
                    className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200 transition-colors"
                  >
                    Нет
                  </button>
                </div>
              ) : (
                <button
                  onClick={() => setConfirmDelete(doc.id)}
                  title="Удалить"
                  className="p-2 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
