import Badge from '../shared/Badge.tsx';

export function statusBadge(status: string) {
  if (!status) return null;
  const s = status.toLowerCase();
  if (s.includes('норм') || s === 'normal') return <Badge variant="success">{status}</Badge>;
  if (s.includes('крит') || s.includes('critical')) return <Badge variant="danger">{status}</Badge>;
  return <Badge variant="warning">{status}</Badge>;
}
