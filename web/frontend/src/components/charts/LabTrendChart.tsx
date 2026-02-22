import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import Card from '../shared/Card';
import { FlaskConical } from 'lucide-react';

interface DataPoint {
  test_name: string;
  value: number | string;
  unit: string;
  date: string;
  reference_range: string;
  is_abnormal: boolean;
}

interface Props {
  data: DataPoint[];
  title?: string;
}

export default function LabTrendChart({ data, title }: Props) {
  if (data.length === 0) return null;

  const chartData = data
    .filter(d => typeof d.value === 'number')
    .map(d => ({
      date: new Date(d.date).toLocaleDateString('ru-RU', { day: '2-digit', month: '2-digit', year: '2-digit' }),
      value: d.value as number,
      name: d.test_name,
    }));

  if (chartData.length === 0) return null;

  // Parse reference range from first item (e.g. "8.6-29 нмоль/л")
  const ref = data[0]?.reference_range || '';
  const refMatch = ref.match(/([\d.]+)\s*[-–]\s*([\d.]+)/);
  const refMin = refMatch ? parseFloat(refMatch[1]) : undefined;
  const refMax = refMatch ? parseFloat(refMatch[2]) : undefined;

  const unit = data[0]?.unit || '';

  return (
    <Card title={title || 'Динамика анализа'} icon={<FlaskConical size={18} />}>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#94a3b8" />
          <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" unit={unit ? ` ${unit}` : ''} />
          <Tooltip
            contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0' }}
            formatter={(value: unknown) => [`${value} ${unit}`, 'Значение']}
          />
          {refMin !== undefined && (
            <ReferenceLine y={refMin} stroke="#10b981" strokeDasharray="5 5" label={{ value: 'Мин.', fill: '#10b981', fontSize: 11 }} />
          )}
          {refMax !== undefined && (
            <ReferenceLine y={refMax} stroke="#10b981" strokeDasharray="5 5" label={{ value: 'Макс.', fill: '#10b981', fontSize: 11 }} />
          )}
          <Line
            type="monotone" dataKey="value" stroke="#0891b2" strokeWidth={2.5}
            dot={{ fill: '#0891b2', r: 4 }} activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
