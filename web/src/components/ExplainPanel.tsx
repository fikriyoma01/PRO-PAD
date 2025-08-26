import { ExplainItem } from "../services/api";
import { colorFor } from "../lib/palette";

export default function ExplainPanel({ items }:{items: ExplainItem[]}) {
  return (
    <div className="bg-white rounded-2xl p-4 shadow">
      <div className="text-sm font-semibold mb-3">Transparansi Algoritma (Decomposition)</div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500">
              <th className="py-1 pr-4">Jenis</th>
              <th className="py-1 pr-4">Base</th>
              <th className="py-1 pr-4">Macro Effect</th>
              <th className="py-1 pr-4">Policy Effect</th>
              <th className="py-1 pr-4">Final</th>
              <th className="py-1">Rumus</th>
            </tr>
          </thead>
          <tbody>
            {items.map((it,i)=>(
              <tr key={i} className="border-t">
                <td className="py-1 pr-4 font-medium" style={{color:colorFor(it.jenis_pajak)}}>{it.jenis_pajak}</td>
                <td className="py-1 pr-4">{fmt(it.components["base"])}</td>
                <td className="py-1 pr-4">{fmt(it.components["macro_effect"])}</td>
                <td className="py-1 pr-4">{fmt(it.components["policy_effect"])}</td>
                <td className="py-1 pr-4 font-semibold">{fmt(it.components["final"])}</td>
                <td className="py-1 text-gray-600">{it.formula}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function fmt(n?: number){ return new Intl.NumberFormat('id-ID').format(Number(n||0)); }
