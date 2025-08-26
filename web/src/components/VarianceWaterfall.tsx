import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine } from "recharts";
import { ForecastPoint } from "../services/api";

function sum(points: ForecastPoint[]) {
  return points.reduce((a, b) => a + (Number(b.nilai) || 0), 0);
}

type WfRow = { name: string; value: number; delta?: number };

export default function VarianceWaterfall({
  baseline,
  scenario
}: {
  baseline: ForecastPoint[];
  scenario: ForecastPoint[];
}) {
  // himpun jenis pajak
  const kinds = Array.from(new Set([...baseline, ...scenario].map((p) => p.jenis_pajak)));

  // delta per jenis
  const deltas = kinds.map((k) => ({
    name: k,
    delta:
      (scenario.find((p) => p.jenis_pajak === k)?.nilai ?? 0) -
      (baseline.find((p) => p.jenis_pajak === k)?.nilai ?? 0),
  }));

  // total awal & akhir
  const start = sum(baseline);
  const end = sum(scenario);

  // running value (kalau nanti ingin dipakai tooltip lanjutan)
  let running = start;
  const wf: WfRow[] = [{ name: "Baseline", value: start }];
  for (const d of deltas) {
    running += d.delta;
    wf.push({ name: d.name, value: running, delta: d.delta });
  }
  wf.push({ name: "Skenario", value: end });

  // data ke chart = hanya nilai delta per jenis
  const chartData = deltas.map((d) => ({ name: d.name, delta: d.delta }));

  const fmtIDR = (n: number) => new Intl.NumberFormat("id-ID").format(Number(n || 0));

  return (
    <div className="bg-white rounded-2xl p-4 shadow">
      <div className="text-sm font-semibold mb-2">Variance Waterfall (Total)</div>
      <div className="text-xs text-gray-500 mb-2">
        Total Baseline: {fmtIDR(start)} → Total Skenario: {fmtIDR(end)} (Δ {fmtIDR(end - start)})
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <XAxis dataKey="name" />
            <YAxis tickFormatter={fmtIDR} />
            <Tooltip formatter={(v: any) => fmtIDR(Number(v))} />
            <ReferenceLine y={0} stroke="#9CA3AF" />
            <Bar dataKey="delta">
              {chartData.map((d, i) => (
                <Cell key={i} fill={d.delta >= 0 ? "#10b981" : "#ef4444"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
