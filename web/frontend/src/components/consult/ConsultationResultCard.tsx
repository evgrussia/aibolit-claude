import { Stethoscope, FlaskConical, BookOpen, AlertTriangle, Sparkles } from 'lucide-react';
import DOMPurify from 'dompurify';
import Card from '../shared/Card';
import Badge from '../shared/Badge';
import EmergencyBanner from '../shared/EmergencyBanner';
import type { ConsultationResult } from '../../types/patient';

const FALLBACK_DISCLAIMER = '⚠️ Информация предоставлена AI-ассистентом и носит исключительно информационный характер. Не является медицинской консультацией, диагнозом или назначением лечения. Обратитесь к врачу для получения квалифицированной медицинской помощи.';

interface Props {
  result: ConsultationResult;
}

export default function ConsultationResultCard({ result }: Props) {
  return (
    <div className="space-y-4">
      {/* Doctor card */}
      <Card>
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-medical-teal/10 rounded-full flex items-center justify-center">
            <Stethoscope size={28} className="text-medical-teal" />
          </div>
          <div className="flex-1">
            <h3 className="text-lg font-bold text-gray-800">{result.doctor.name}</h3>
            <p className="text-sm text-gray-500">{result.doctor.qualification}</p>
          </div>
          {result.ai_generated && (
            <div className="flex items-center gap-1.5 px-3 py-1 bg-violet-50 border border-violet-200 rounded-full">
              <Sparkles size={14} className="text-violet-500" />
              <span className="text-xs font-medium text-violet-600">Claude AI</span>
            </div>
          )}
        </div>
      </Card>

      {/* Emergency banner — when red flags detected (shown first!) */}
      {result.emergency && (
        <EmergencyBanner message={result.emergency.message} />
      )}

      {/* Red flags list */}
      {result.red_flags && result.red_flags.length > 0 && (
        <Card>
          <div className="flex items-center gap-2 mb-3" role="alert">
            <AlertTriangle size={16} className="text-red-500" />
            <span className="text-sm font-medium text-red-700">Обнаруженные тревожные признаки</span>
          </div>
          <div className="space-y-2">
            {result.red_flags.map((f, i) => (
              <div key={i} className="flex items-start gap-2 p-2 bg-red-50 rounded-lg">
                <span className="text-xs font-semibold text-red-600 uppercase shrink-0">{f.category}</span>
                <div className="flex-1">
                  <p className="text-sm text-red-700">{f.description}</p>
                  <p className="text-xs text-red-500 mt-0.5">{f.action}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Summary — main content */}
      {result.consultation.summary && (
        <Card>
          {result.ai_generated ? (
            <div
              className="text-sm text-gray-700 leading-relaxed prose prose-sm max-w-none
                         prose-headings:text-gray-800 prose-strong:text-gray-800
                         prose-ul:my-1 prose-li:my-0.5"
              dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(markdownToHtml(result.consultation.summary)) }}
            />
          ) : (
            <div className="text-sm text-gray-700 leading-relaxed whitespace-pre-line">
              {result.consultation.summary}
            </div>
          )}
        </Card>
      )}

      {/* Recommended tests — only for template responses */}
      {!result.ai_generated && result.consultation.recommended_tests.length > 0 && (
        <Card>
          <div className="flex items-center gap-2 mb-3">
            <FlaskConical size={16} className="text-medical-teal" />
            <span className="text-sm font-medium text-gray-700">Рекомендуемые обследования</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {result.consultation.recommended_tests.map(test => (
              <Badge key={test} variant="info">{test}</Badge>
            ))}
          </div>
        </Card>
      )}

      {/* ICD codes — only for template responses */}
      {!result.ai_generated && result.consultation.relevant_icd_prefixes.length > 0 && (
        <Card>
          <div className="flex items-center gap-2 mb-3">
            <BookOpen size={16} className="text-medical-teal" />
            <span className="text-sm font-medium text-gray-700">Коды МКБ</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {result.consultation.relevant_icd_prefixes.map(code => (
              <Badge key={code} variant="gray">{code}</Badge>
            ))}
          </div>
        </Card>
      )}

      {/* Instructions — only for template responses */}
      {!result.ai_generated && (
        <p className="text-xs text-gray-400 leading-relaxed whitespace-pre-line px-1">
          {result.instructions}
        </p>
      )}

      {/* Disclaimer */}
      <div className="flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
        <AlertTriangle size={16} className="text-amber-500 shrink-0 mt-0.5" />
        <p className="text-xs text-amber-700">{result.disclaimer || FALLBACK_DISCLAIMER}</p>
      </div>
    </div>
  );
}


/** Lightweight markdown → HTML (bold, italic, headers, lists, line breaks). */
function markdownToHtml(md: string): string {
  return md
    // Headers
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold & italic
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Unordered lists
    .replace(/^[•\-\*] (.+)$/gm, '<li>$1</li>')
    // Numbered lists
    .replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>')
    // Wrap consecutive <li> in <ul>
    .replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>')
    // Paragraphs (double newlines)
    .replace(/\n\n/g, '</p><p>')
    // Single newlines → <br>
    .replace(/\n/g, '<br>')
    // Wrap in paragraph
    .replace(/^(.+)$/, '<p>$1</p>')
    // Clean up empty paragraphs
    .replace(/<p><\/p>/g, '')
    .replace(/<p><(h[123]|ul)>/g, '<$1>')
    .replace(/<\/(h[123]|ul)><\/p>/g, '</$1>');
}
