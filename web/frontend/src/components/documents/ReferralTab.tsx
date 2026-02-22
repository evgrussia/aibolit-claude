import { useState, useCallback } from 'react';
import { UserCheck } from 'lucide-react';
import Card from '../shared/Card.tsx';
import InfoBanner from '../shared/InfoBanner.tsx';
import HelpTooltip from '../shared/HelpTooltip.tsx';
import DocumentViewer from './DocumentViewer.tsx';
import { SPECIALTIES_RU, URGENCY_LABELS, URGENCY_HINTS } from '../../constants/documents.ts';
import { generateReferral, type ReferralRequest } from '../../api/documents.ts';

export default function ReferralTab() {
  const [form, setForm] = useState({
    patient_name: '', patient_age: '', from_specialty: 'Терапевт',
    to_specialty: 'Кардиолог', reason: '', current_diagnoses: '',
    relevant_results: '', urgency: 'routine',
  });
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const set = (key: string, val: string) => setForm(f => ({ ...f, [key]: val }));

  const handleSubmit = useCallback(async () => {
    if (!form.patient_name.trim() || !form.reason.trim()) {
      setError('Заполните ФИО пациента и причину направления'); return;
    }
    setLoading(true); setError('');
    try {
      const req: ReferralRequest = {
        patient_name: form.patient_name,
        patient_age: Number(form.patient_age) || 0,
        from_specialty: form.from_specialty,
        to_specialty: form.to_specialty,
        reason: form.reason,
        current_diagnoses: form.current_diagnoses.split('\n').map(d => d.trim()).filter(Boolean),
        relevant_results: form.relevant_results || undefined,
        urgency: form.urgency,
      };
      const doc = await generateReferral(req);
      setResult(doc.content);
    } catch { setError('Ошибка генерации. Проверьте подключение к серверу.'); }
    finally { setLoading(false); }
  }, [form]);

  return (
    <div className="space-y-4">
      <InfoBanner variant="tip" title="Как заполнить направление" collapsible defaultOpen>
        <ol className="list-decimal list-inside space-y-1">
          <li>Укажите <strong>ФИО и возраст</strong> пациента</li>
          <li>Выберите <strong>от кого</strong> (ваша специальность) и <strong>к кому</strong> направляете</li>
          <li>Укажите <strong>срочность</strong>: Плановое (1–2 нед.) / Срочное (1–3 дня) / Экстренное (сегодня)</li>
          <li>Опишите <strong>причину направления</strong> — жалобы, предварительный диагноз</li>
          <li>Добавьте имеющиеся <strong>результаты обследований</strong> — кратко, числами</li>
        </ol>
      </InfoBanner>

      <Card title="Данные для направления" icon={<UserCheck size={16} />}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="ref-patient" className="block text-xs text-gray-500 mb-1">ФИО пациента *</label>
            <input id="ref-patient" value={form.patient_name} onChange={e => set('patient_name', e.target.value)}
              placeholder="Иванов Иван Иванович"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300" />
          </div>
          <div>
            <label htmlFor="ref-age" className="block text-xs text-gray-500 mb-1">Возраст (лет)</label>
            <input id="ref-age" type="number" min="0" max="150" value={form.patient_age} onChange={e => set('patient_age', e.target.value)}
              placeholder="45"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300" />
          </div>
          <div>
            <label htmlFor="ref-from" className="block text-xs text-gray-500 mb-1">Направляет (специальность)</label>
            <select id="ref-from" value={form.from_specialty} onChange={e => set('from_specialty', e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal">
              {SPECIALTIES_RU.map(s => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="ref-to" className="block text-xs text-gray-500 mb-1">К специалисту</label>
            <select id="ref-to" value={form.to_specialty} onChange={e => set('to_specialty', e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal">
              {SPECIALTIES_RU.map(s => <option key={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label htmlFor="ref-urgency" className="flex items-center gap-1 text-xs text-gray-500 mb-1">
              Срочность
              <HelpTooltip text={URGENCY_HINTS[form.urgency]} />
            </label>
            <select id="ref-urgency" value={form.urgency} onChange={e => set('urgency', e.target.value)}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal">
              {Object.entries(URGENCY_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div className="md:col-span-2">
            <label htmlFor="ref-reason" className="block text-xs text-gray-500 mb-1">Причина направления * (жалобы, предварительный диагноз)</label>
            <textarea id="ref-reason" value={form.reason} onChange={e => set('reason', e.target.value)} rows={3}
              placeholder="Жалобы на боли в грудной клетке при нагрузке, одышку. Подозрение на ИБС. АД 150/95 мм рт.ст. Прошу консультацию и ЭКГ."
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300" />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="ref-diagnoses" className="block text-xs text-gray-500 mb-1">Текущие диагнозы (каждый с новой строки)</label>
            <textarea id="ref-diagnoses" value={form.current_diagnoses} onChange={e => set('current_diagnoses', e.target.value)} rows={2}
              placeholder={"Гипертоническая болезнь II ст. (I10)\nДислипидемия (E78)"}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300" />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="ref-results" className="flex items-center gap-1 text-xs text-gray-500 mb-1">
              Результаты обследований
              <HelpTooltip text="Кратко: анализы, ЭКГ, УЗИ — значимые отклонения числами" />
            </label>
            <textarea id="ref-results" value={form.relevant_results} onChange={e => set('relevant_results', e.target.value)} rows={2}
              placeholder="ОАК: гемоглобин 110 г/л. ЭКГ: синусовый ритм, признаки гипертрофии ЛЖ. Холестерин 6.8 ммоль/л."
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300" />
          </div>
        </div>
        {error && <p role="alert" className="text-red-500 text-sm mb-3">{error}</p>}
        <button onClick={handleSubmit} disabled={loading}
          className="bg-medical-teal text-white px-6 py-2 rounded-lg hover:bg-medical-navy transition-colors disabled:opacity-50">
          {loading ? 'Генерирую...' : 'Сформировать направление'}
        </button>
      </Card>
      {result && <DocumentViewer content={result} />}
    </div>
  );
}
