import { useState, useCallback } from 'react';
import { ClipboardList } from 'lucide-react';
import Card from '../shared/Card.tsx';
import InfoBanner from '../shared/InfoBanner.tsx';
import HelpTooltip from '../shared/HelpTooltip.tsx';
import DocumentViewer from './DocumentViewer.tsx';
import { ROUTES, FREQUENCIES } from '../../constants/documents.ts';
import { generatePrescription, type PrescriptionRequest } from '../../api/documents.ts';

export default function PrescriptionTab() {
  const [patientName, setPatientName] = useState('');
  const [diagnoses, setDiagnoses] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [notes, setNotes] = useState('');
  const [medications, setMedications] = useState([
    { name: '', dosage: '', frequency: '2 раза/сут', route: 'per os', duration: '', notes: '' },
  ]);
  const [result, setResult] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const addMed = () => setMedications(m => [...m, { name: '', dosage: '', frequency: '2 раза/сут', route: 'per os', duration: '', notes: '' }]);
  const removeMed = (i: number) => setMedications(m => m.filter((_, idx) => idx !== i));
  const updateMed = (i: number, key: string, val: string) =>
    setMedications(m => m.map((x, idx) => idx === i ? { ...x, [key]: val } : x));

  const handleSubmit = useCallback(async () => {
    if (!patientName.trim()) { setError('Введите имя пациента'); return; }
    const filledMeds = medications.filter(m => m.name.trim() && m.dosage.trim());
    if (filledMeds.length === 0) { setError('Добавьте хотя бы один препарат с названием и дозировкой'); return; }
    setLoading(true); setError('');
    try {
      const req: PrescriptionRequest = {
        patient_name: patientName,
        medications: filledMeds,
        diagnoses: diagnoses.split('\n').map(d => d.trim()).filter(Boolean),
        doctor_specialty: specialty || undefined,
        notes: notes || undefined,
      };
      const doc = await generatePrescription(req);
      setResult(doc.content);
    } catch { setError('Ошибка генерации. Проверьте подключение к серверу.'); }
    finally { setLoading(false); }
  }, [patientName, diagnoses, specialty, notes, medications]);

  return (
    <div className="space-y-4">
      <InfoBanner variant="tip" title="Как заполнить рецепт" collapsible defaultOpen>
        <ol className="list-decimal list-inside space-y-1">
          <li>Введите <strong>ФИО пациента</strong> — обязательное поле</li>
          <li>Укажите <strong>диагноз</strong> — желательно с кодом МКБ-10 (например: <em>Гипертоническая болезнь II ст. (I10)</em>)</li>
          <li>Добавьте <strong>препараты</strong> — для каждого укажите название, дозу и кратность</li>
          <li>Нажмите <strong>«Сформировать рецепт»</strong> — документ появится ниже</li>
        </ol>
        <p className="mt-2">
          Готовый документ можно скопировать или скачать как текстовый файл.
        </p>
      </InfoBanner>

      <Card title="Данные для рецепта" icon={<ClipboardList size={16} />}>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label htmlFor="rx-patient" className="flex items-center gap-1 text-xs text-gray-500 mb-1">
              ФИО пациента *
              <HelpTooltip text="Полностью: Фамилия Имя Отчество" />
            </label>
            <input id="rx-patient" value={patientName} onChange={e => setPatientName(e.target.value)}
              placeholder="Иванов Иван Иванович"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300" />
          </div>
          <div>
            <label htmlFor="rx-specialty" className="flex items-center gap-1 text-xs text-gray-500 mb-1">
              Специализация врача
              <HelpTooltip text="Необязательно. Например: Терапевт, Кардиолог, Эндокринолог" />
            </label>
            <input id="rx-specialty" value={specialty} onChange={e => setSpecialty(e.target.value)}
              placeholder="Например: Кардиолог"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300" />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="rx-diagnoses" className="flex items-center gap-1 text-xs text-gray-500 mb-1">
              Диагнозы
              <HelpTooltip text="Каждый диагноз с новой строки. Рекомендуется указать код МКБ-10." />
            </label>
            <textarea id="rx-diagnoses" value={diagnoses} onChange={e => setDiagnoses(e.target.value)} rows={2}
              placeholder={"Гипертоническая болезнь II ст. (I10)\nСахарный диабет 2 типа (E11)"}
              className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300" />
          </div>
        </div>

        <div className="space-y-3 mb-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Назначения</span>
            <button onClick={addMed} className="text-medical-teal text-sm hover:text-medical-navy transition-colors">+ Добавить препарат</button>
          </div>
          {medications.map((m, i) => (
            <div key={i} className="border border-gray-100 rounded-lg p-3 space-y-2 bg-gray-50">
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                <div className="md:col-span-2">
                  <label htmlFor={`rx-med-name-${i}`} className="block text-xs text-gray-500 mb-1">Препарат *</label>
                  <input id={`rx-med-name-${i}`} value={m.name} onChange={e => updateMed(i, 'name', e.target.value)}
                    placeholder="Метформин / Лизиноприл / Атеровастат"
                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:border-medical-teal bg-white placeholder:text-gray-300" />
                </div>
                <div>
                  <label htmlFor={`rx-med-dose-${i}`} className="flex items-center gap-1 text-xs text-gray-500 mb-1">
                    Доза *
                    <HelpTooltip text="Укажите дозу с единицами: 500мг, 10мг, 0.5мл" />
                  </label>
                  <input id={`rx-med-dose-${i}`} value={m.dosage} onChange={e => updateMed(i, 'dosage', e.target.value)}
                    placeholder="500мг"
                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:border-medical-teal bg-white placeholder:text-gray-300" />
                </div>
                <div>
                  <label htmlFor={`rx-med-freq-${i}`} className="block text-xs text-gray-500 mb-1">Кратность</label>
                  <select id={`rx-med-freq-${i}`} value={m.frequency} onChange={e => updateMed(i, 'frequency', e.target.value)}
                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:border-medical-teal bg-white">
                    {FREQUENCIES.map(f => <option key={f}>{f}</option>)}
                  </select>
                </div>
                <div>
                  <label htmlFor={`rx-med-route-${i}`} className="block text-xs text-gray-500 mb-1">Путь введения</label>
                  <select id={`rx-med-route-${i}`} value={m.route} onChange={e => updateMed(i, 'route', e.target.value)}
                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:border-medical-teal bg-white">
                    {ROUTES.map(r => <option key={r}>{r}</option>)}
                  </select>
                </div>
                <div>
                  <label htmlFor={`rx-med-dur-${i}`} className="flex items-center gap-1 text-xs text-gray-500 mb-1">
                    Длительность
                    <HelpTooltip text="Например: 14 дней, 1 месяц, 3 недели" />
                  </label>
                  <input id={`rx-med-dur-${i}`} value={m.duration} onChange={e => updateMed(i, 'duration', e.target.value)}
                    placeholder="30 дней"
                    className="w-full border border-gray-200 rounded-lg px-2 py-1.5 text-sm focus:outline-none focus:border-medical-teal bg-white placeholder:text-gray-300" />
                </div>
              </div>
              {medications.length > 1 && (
                <button onClick={() => removeMed(i)} className="text-xs text-gray-400 hover:text-red-500">Удалить</button>
              )}
            </div>
          ))}
        </div>

        <div className="mb-4">
          <label htmlFor="rx-notes" className="block text-xs text-gray-500 mb-1">Примечания</label>
          <textarea id="rx-notes" value={notes} onChange={e => setNotes(e.target.value)} rows={2}
            placeholder="Принимать после еды. Контроль АД ежедневно. Повторный приём через 1 месяц."
            className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-medical-teal placeholder:text-gray-300" />
        </div>

        {error && <p role="alert" className="text-red-500 text-sm mb-3">{error}</p>}
        <button onClick={handleSubmit} disabled={loading}
          className="bg-medical-teal text-white px-6 py-2 rounded-lg hover:bg-medical-navy transition-colors disabled:opacity-50">
          {loading ? 'Генерирую...' : 'Сформировать рецепт'}
        </button>
      </Card>
      {result && <DocumentViewer content={result} />}
    </div>
  );
}
