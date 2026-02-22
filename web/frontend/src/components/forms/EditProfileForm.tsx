import { useState } from 'react';
import { Plus, Trash2, Loader2 } from 'lucide-react';
import type { PatientFull } from '../../types/patient';

interface Props {
  patient: PatientFull;
  onSubmit: (data: Record<string, unknown>) => Promise<void>;
  isPending: boolean;
}

const BLOOD_TYPES = ['', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

export default function EditProfileForm({ patient, onSubmit, isPending }: Props) {
  const [bloodType, setBloodType] = useState(patient.blood_type || '');
  const [notes, setNotes] = useState(patient.notes || '');
  const [familyHistory, setFamilyHistory] = useState<string[]>([...patient.family_history]);
  const [surgicalHistory, setSurgicalHistory] = useState<string[]>([...patient.surgical_history]);
  const [lifestyle, setLifestyle] = useState<Record<string, string>>({ ...patient.lifestyle });
  const [newFH, setNewFH] = useState('');
  const [newSH, setNewSH] = useState('');
  const [newLKey, setNewLKey] = useState('');
  const [newLVal, setNewLVal] = useState('');

  const addFH = () => {
    if (newFH.trim()) {
      setFamilyHistory([...familyHistory, newFH.trim()]);
      setNewFH('');
    }
  };

  const addSH = () => {
    if (newSH.trim()) {
      setSurgicalHistory([...surgicalHistory, newSH.trim()]);
      setNewSH('');
    }
  };

  const addLifestyle = () => {
    if (newLKey.trim() && newLVal.trim()) {
      setLifestyle({ ...lifestyle, [newLKey.trim()]: newLVal.trim() });
      setNewLKey('');
      setNewLVal('');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({
      blood_type: bloodType || null,
      notes,
      family_history: familyHistory,
      surgical_history: surgicalHistory,
      lifestyle,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Blood type */}
      <div>
        <label htmlFor="profile-blood" className="block text-xs font-medium text-gray-600 mb-1">
          Группа крови
        </label>
        <select
          id="profile-blood"
          value={bloodType}
          onChange={e => setBloodType(e.target.value)}
          disabled={isPending}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30"
        >
          {BLOOD_TYPES.map(bt => (
            <option key={bt} value={bt}>{bt || 'Не указана'}</option>
          ))}
        </select>
      </div>

      {/* Family history */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Семейный анамнез</label>
        <div className="space-y-1.5 mb-2">
          {familyHistory.map((item, i) => (
            <div key={i} className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-1.5 text-sm">
              <span className="flex-1">{item}</span>
              <button type="button" onClick={() => setFamilyHistory(familyHistory.filter((_, idx) => idx !== i))} className="text-gray-400 hover:text-red-500">
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            value={newFH}
            onChange={e => setNewFH(e.target.value)}
            placeholder="Диабет 2 типа у матери..."
            onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addFH())}
            disabled={isPending}
            className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
          />
          <button type="button" onClick={addFH} className="px-3 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
            <Plus size={16} className="text-gray-500" />
          </button>
        </div>
      </div>

      {/* Surgical history */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Хирургический анамнез</label>
        <div className="space-y-1.5 mb-2">
          {surgicalHistory.map((item, i) => (
            <div key={i} className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-1.5 text-sm">
              <span className="flex-1">{item}</span>
              <button type="button" onClick={() => setSurgicalHistory(surgicalHistory.filter((_, idx) => idx !== i))} className="text-gray-400 hover:text-red-500">
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            value={newSH}
            onChange={e => setNewSH(e.target.value)}
            placeholder="Аппендэктомия, 2015..."
            onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addSH())}
            disabled={isPending}
            className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
          />
          <button type="button" onClick={addSH} className="px-3 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
            <Plus size={16} className="text-gray-500" />
          </button>
        </div>
      </div>

      {/* Lifestyle */}
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Образ жизни</label>
        <div className="space-y-1.5 mb-2">
          {Object.entries(lifestyle).map(([k, v]) => (
            <div key={k} className="flex items-center gap-2 bg-gray-50 rounded-lg px-3 py-1.5 text-sm">
              <span className="font-medium text-gray-700">{k}:</span>
              <span className="flex-1 text-gray-600">{v}</span>
              <button type="button" onClick={() => {
                const copy = { ...lifestyle };
                delete copy[k];
                setLifestyle(copy);
              }} className="text-gray-400 hover:text-red-500">
                <Trash2 size={14} />
              </button>
            </div>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            value={newLKey}
            onChange={e => setNewLKey(e.target.value)}
            placeholder="Ключ (курение)"
            disabled={isPending}
            className="w-1/3 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
          />
          <input
            value={newLVal}
            onChange={e => setNewLVal(e.target.value)}
            placeholder="Значение (не курит)"
            onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addLifestyle())}
            disabled={isPending}
            className="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 disabled:opacity-50"
          />
          <button type="button" onClick={addLifestyle} className="px-3 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
            <Plus size={16} className="text-gray-500" />
          </button>
        </div>
      </div>

      {/* Notes */}
      <div>
        <label htmlFor="profile-notes" className="block text-xs font-medium text-gray-600 mb-1">
          Заметки
        </label>
        <textarea
          id="profile-notes"
          value={notes}
          onChange={e => setNotes(e.target.value)}
          disabled={isPending}
          rows={3}
          className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-medical-teal/30 resize-none disabled:opacity-50"
        />
      </div>

      <button
        type="submit"
        disabled={isPending}
        className="w-full py-2.5 bg-medical-teal text-white rounded-lg font-medium text-sm hover:bg-medical-teal/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors"
      >
        {isPending ? <><Loader2 size={16} className="animate-spin" /> Сохранение...</> : 'Сохранить изменения'}
      </button>
    </form>
  );
}
