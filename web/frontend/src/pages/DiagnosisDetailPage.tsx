import { useParams, Link } from 'react-router-dom';
import { usePatient } from '../hooks/usePatient';
import { useDiseaseInfo, useIcdSearch, useLiteratureSearch } from '../hooks/useDiseaseInfo';
import Card from '../components/shared/Card';
import Badge from '../components/shared/Badge';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import ApiError from '../components/shared/ApiError';
import { formatDate, statusLabel } from '../utils/formatters';
import {
  ShieldAlert, BookOpen, FlaskConical, FileText, ExternalLink, ArrowLeft,
} from 'lucide-react';

function statusVariant(s: string) {
  switch (s) {
    case 'active': return 'danger' as const;
    case 'chronic': return 'warning' as const;
    case 'resolved': return 'success' as const;
    default: return 'gray' as const;
  }
}

export default function DiagnosisDetailPage() {
  const { patientId, icdCode } = useParams();
  const { data: patient, isLoading, error, refetch } = usePatient(patientId);

  const diagnosis = patient?.diagnoses.find(d => d.icd10_code === icdCode);

  const { data: diseaseInfo, isLoading: loadingInfo } = useDiseaseInfo(diagnosis?.name);
  const { data: icdResults = [] } = useIcdSearch(diagnosis?.name);
  const { data: articles = [] } = useLiteratureSearch(diagnosis?.name);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ApiError message={(error as Error).message} onRetry={() => refetch()} />;
  if (!patient || !diagnosis) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Диагноз не найден</p>
        <Link to={`/patients/${patientId}`} className="text-medical-teal text-sm mt-2 inline-block hover:underline">
          Вернуться к пациенту
        </Link>
      </div>
    );
  }

  // Relevant labs — simple keyword match
  const relevantLabs = patient.lab_results.filter(lr => {
    const name = lr.test_name.toLowerCase();
    const diagName = diagnosis.name.toLowerCase();
    return diagName.includes('диабет') ? name.includes('глюкоз') || name.includes('hba1c') || name.includes('гликир') :
      diagName.includes('гипертен') ? name.includes('холестерин') || name.includes('креатинин') :
      diagName.includes('анеми') ? name.includes('гемоглобин') || name.includes('ферритин') || name.includes('железо') :
      false;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <Link
          to={`/patients/${patientId}`}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-500 shrink-0"
        >
          <ArrowLeft size={20} />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <span className="text-lg font-mono font-bold text-medical-teal">{diagnosis.icd10_code}</span>
            <Badge variant={statusVariant(diagnosis.status)}>{statusLabel(diagnosis.status)}</Badge>
          </div>
          <h1 className="text-2xl font-bold text-gray-800 mt-1">{diagnosis.name}</h1>
          <p className="text-sm text-gray-400 mt-1">
            Диагностирован: {formatDate(diagnosis.date_diagnosed)}
            {diagnosis.confidence > 0 && ` · Достоверность: ${(diagnosis.confidence * 100).toFixed(0)}%`}
          </p>
        </div>
      </div>

      {/* Disease info */}
      <Card title="О заболевании" icon={<BookOpen size={18} />}>
        {loadingInfo ? (
          <div className="animate-pulse space-y-2">
            <div className="h-4 bg-gray-100 rounded w-full" />
            <div className="h-4 bg-gray-100 rounded w-3/4" />
            <div className="h-4 bg-gray-100 rounded w-1/2" />
          </div>
        ) : diseaseInfo ? (
          <div className="space-y-4 text-sm text-gray-600">
            {diseaseInfo.description && (
              <p>{diseaseInfo.description}</p>
            )}
            {diseaseInfo.symptoms?.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-700 mb-1">Симптомы</h4>
                <div className="flex flex-wrap gap-1.5">
                  {diseaseInfo.symptoms.map((s: string, i: number) => (
                    <Badge key={i} variant="info">{s}</Badge>
                  ))}
                </div>
              </div>
            )}
            {diseaseInfo.risk_factors?.length > 0 && (
              <div>
                <h4 className="font-medium text-gray-700 mb-1">Факторы риска</h4>
                <div className="flex flex-wrap gap-1.5">
                  {diseaseInfo.risk_factors.map((r: string, i: number) => (
                    <Badge key={i} variant="warning">{r}</Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-400 text-sm">Информация недоступна</p>
        )}
      </Card>

      {/* ICD classification */}
      {(icdResults as { code?: string; title?: string; uri?: string }[]).length > 0 && (
        <Card title="Классификация МКБ-11" icon={<ShieldAlert size={18} />}>
          <div className="space-y-2">
            {(icdResults as { code?: string; title?: string; uri?: string }[]).slice(0, 5).map((r, i) => (
              <div key={i} className="flex items-center justify-between py-1.5 border-b border-gray-50 last:border-0">
                <div>
                  <span className="font-mono text-xs text-medical-teal font-semibold">{r.code}</span>
                  <span className="text-sm text-gray-700 ml-2">{r.title}</span>
                </div>
                {r.uri && (
                  <a href={r.uri} target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-medical-teal">
                    <ExternalLink size={14} />
                  </a>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Related labs */}
      {relevantLabs.length > 0 && (
        <Card title="Связанные анализы" icon={<FlaskConical size={18} />}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b border-gray-100">
                  <th className="pb-2 font-medium">Анализ</th>
                  <th className="pb-2 font-medium">Значение</th>
                  <th className="pb-2 font-medium">Дата</th>
                  <th className="pb-2 font-medium">Статус</th>
                </tr>
              </thead>
              <tbody>
                {relevantLabs.map((lr, i) => (
                  <tr key={i} className="border-b border-gray-50">
                    <td className="py-2 text-gray-700">{lr.test_name}</td>
                    <td className="py-2 font-mono">{lr.value} {lr.unit}</td>
                    <td className="py-2 text-gray-400">{formatDate(lr.date)}</td>
                    <td className="py-2">
                      <Badge variant={lr.is_abnormal ? 'danger' : 'success'}>
                        {lr.is_abnormal ? 'Отклонение' : 'Норма'}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* PubMed articles */}
      {(articles as { pmid?: string; title?: string; authors?: string; journal?: string; year?: string }[]).length > 0 && (
        <Card title="Научные публикации" icon={<FileText size={18} />}>
          <div className="space-y-3">
            {(articles as { pmid?: string; title?: string; authors?: string; journal?: string; year?: string }[]).slice(0, 8).map((a, i) => (
              <div key={i} className="border-b border-gray-50 pb-3 last:border-0 last:pb-0">
                <a
                  href={`https://pubmed.ncbi.nlm.nih.gov/${a.pmid}/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm font-medium text-gray-700 hover:text-medical-teal transition-colors inline-flex items-start gap-1"
                >
                  {a.title}
                  <ExternalLink size={12} className="shrink-0 mt-0.5" />
                </a>
                <p className="text-xs text-gray-400 mt-0.5">
                  {a.authors} · {a.journal} · {a.year}
                </p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Doctor notes */}
      {diagnosis.notes && (
        <Card title="Заметки врача" icon={<FileText size={18} />}>
          <p className="text-sm text-gray-600 whitespace-pre-wrap">{diagnosis.notes}</p>
        </Card>
      )}
    </div>
  );
}
