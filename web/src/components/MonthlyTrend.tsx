import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { ForecastPoint } from "../services/api";
import { ORDER, colorFor } from "../lib/palette";

export default function MonthlyTrend({ monthly }: { monthly: ForecastPoint[] }) {
  // pivot ke per bulan
  const months = Array.from(new Set(monthly.map(m => m.periode))).sort();
  const data = months.map(m => {
    const row: any = { month: new Date(m).toLocaleDateString('id-ID', { month: 'short' }) };
    ORDER.forEach(j => {
      row[j] = monthly.find(p => p.periode === m && p.jenis_pajak === j)?.nilai ?? 0;
    });
    return row;
  });

  return (
    <div className="bg-white rounded-2xl p-4 shadow">
      <div className="text-sm font-semibold mb-2">Tren Bulanan (Forecast)</div>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <XAxis dataKey="month"/>
            <YAxis tickFormatter={(v)=> new Intl.NumberFormat('id-ID').format(Number(v))}/>
            <Tooltip formatter={(v:any)=> new Intl.NumberFormat('id-ID').format(Number(v))}/>
            <Legend />
            {ORDER.map(j => <Line key={j} type="monotone" dataKey={j} stroke={colorFor(j)} dot={false} />)}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
