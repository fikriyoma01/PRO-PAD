import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { ForecastPoint } from "../services/api";
import { ORDER, PALETTE } from "../lib/palette";

export default function CompareBars({ baseline, scenario }: { baseline: ForecastPoint[]; scenario: ForecastPoint[] }) {
  const data = ORDER.map(j => ({
    jenis: j,
    baseline: baseline.find(p => p.jenis_pajak === j)?.nilai ?? 0,
    scenario: scenario.find(p => p.jenis_pajak === j)?.nilai ?? 0,
  }));
  return (
    <div className="bg-white rounded-2xl p-4 shadow">
      <div className="text-sm font-semibold mb-2">Perbandingan Baseline vs Skenario</div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <XAxis dataKey="jenis" />
            <YAxis tickFormatter={(v)=> new Intl.NumberFormat('id-ID').format(Number(v))} />
            <Tooltip formatter={(v:any)=> new Intl.NumberFormat('id-ID').format(Number(v))}/>
            <Legend />
            <Bar dataKey="baseline" fill={PALETTE.baseline} />
            <Bar dataKey="scenario" fill={PALETTE.scenario} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
