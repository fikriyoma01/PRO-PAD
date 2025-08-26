import { Pie, PieChart, Cell, Legend, Tooltip, ResponsiveContainer } from "recharts";
import { ForecastPoint } from "../services/api";
import { ORDER, colorFor } from "../lib/palette";

export default function CompositionDonut({ points }: { points: ForecastPoint[] }) {
  const data = ORDER.map(j => {
    const v = points.find(p => p.jenis_pajak === j)?.nilai ?? 0;
    return { name: j, value: v };
  });
  return (
    <div className="bg-white rounded-2xl p-4 shadow">
      <div className="text-sm font-semibold mb-2">Komposisi Proyeksi per Jenis Pajak</div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90}>
              {data.map((d, i) => <Cell key={i} fill={colorFor(d.name)} />)}
            </Pie>
            <Legend />
            <Tooltip formatter={(v: any) => new Intl.NumberFormat('id-ID').format(Number(v))} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
