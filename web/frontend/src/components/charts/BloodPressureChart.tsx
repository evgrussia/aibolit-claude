import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ReferenceLine, Legend,
} from 'recharts';
import Card from '../shared/Card';
import { HeartPulse } from 'lucide-react';
import type { VitalSigns } from '../../types/patient';

interface Props {
  data: VitalSigns[];
}

export default function BloodPressureChart({ data }: Props) {
  const filtered = data.filter(v => v.systolic_bp && v.diastolic_bp);
  if (filtered.length === 0) return null;

  const chartData = [...filtered].reverse().map(v => ({
    date: new Date(v.timestamp).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit' }),
    systolic: v.systolic_bp,
    diastolic: v.diastolic_bp,
    hr: v.heart_rate,
  }));

  return (
    <Card title="Артериальное давление" icon={<HeartPulse size={18} />}>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#94a3b8" />
          <YAxis domain={[50, 200]} tick={{ fontSize: 12 }} stroke="#94a3b8" />
          <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0' }} />
          <Legend />
          <ReferenceLine y={140} stroke="#dc2626" strokeDasharray="4 4" />
          <ReferenceLine y={90} stroke="#f59e0b" strokeDasharray="4 4" />
          <Line type="monotone" dataKey="systolic" stroke="#1e3a5f" strokeWidth={2.5}
            name="Систолическое" dot={{ fill: '#1e3a5f', r: 4 }} />
          <Line type="monotone" dataKey="diastolic" stroke="#0891b2" strokeWidth={2.5}
            name="Диастолическое" dot={{ fill: '#0891b2', r: 4 }} />
          <Line type="monotone" dataKey="hr" stroke="#f59e0b" strokeWidth={1.5}
            name="Пульс" dot={{ fill: '#f59e0b', r: 3 }} strokeDasharray="5 5" />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
