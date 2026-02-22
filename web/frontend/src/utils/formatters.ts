export function formatDate(iso: string): string {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

export function formatDateTime(iso: string): string {
  if (!iso) return '—';
  const d = new Date(iso);
  return d.toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

export function genderLabel(g: string): string {
  return g === 'male' ? 'Мужской' : g === 'female' ? 'Женский' : g;
}

export function statusColor(status: string): string {
  switch (status) {
    case 'active': return 'bg-red-100 text-red-700';
    case 'chronic': return 'bg-amber-100 text-amber-700';
    case 'resolved': return 'bg-green-100 text-green-700';
    default: return 'bg-gray-100 text-gray-700';
  }
}

export function statusLabel(status: string): string {
  switch (status) {
    case 'active': return 'Активный';
    case 'chronic': return 'Хронический';
    case 'resolved': return 'Вылечен';
    default: return status;
  }
}

export function severityColor(severity: string): string {
  switch (severity) {
    case 'mild': return 'bg-yellow-100 text-yellow-700';
    case 'moderate': return 'bg-orange-100 text-orange-700';
    case 'severe': return 'bg-red-100 text-red-700';
    default: return 'bg-gray-100 text-gray-700';
  }
}
